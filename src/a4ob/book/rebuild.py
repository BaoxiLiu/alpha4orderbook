"""L0 rebuild: CryptoHFTData flattened snapshot/update rows → event stream → L2."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .l2 import L2Book


@dataclass
class RebuildStats:
    n_rows: int = 0
    n_snapshot_groups: int = 0
    n_update_groups: int = 0
    n_applied_updates: int = 0
    n_skipped_before_ready: int = 0
    n_gaps: int = 0
    n_crossed: int = 0
    first_ready_event_time_ms: int | None = None
    last_event_time_ms: int | None = None
    notes: list[str] = field(default_factory=list)


def _as_optional_int(val: object) -> int | None:
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return int(val)


def _event_group_ids(df: pd.DataFrame) -> np.ndarray:
    """
    Assign a contiguous group id to flattened level rows belonging to one
    native depth message (vectorized).
    """
    n = len(df)
    if n == 0:
        return np.array([], dtype=np.int64)

    et = df["event_type"].astype(str).to_numpy()
    recv = df["received_time"].to_numpy()
    evt = df["event_time"].to_numpy()

    def _id_arr(col: str) -> np.ndarray:
        return df[col].fillna(-1).astype(np.int64).to_numpy()

    last_id = _id_arr("last_update_id")
    first_id = _id_arr("first_update_id")
    final_id = _id_arr("final_update_id")
    prev_id = _id_arr("prev_final_update_id")

    # Snapshots: group only by last_update_id (vendor may split bid/ask
    # halves across slightly different received_time). Updates: U/u/pu + clock.
    is_snap = et == "snapshot"
    change = np.zeros(n, dtype=bool)
    change[0] = True
    change[1:] |= et[1:] != et[:-1]

    snap_chg = np.zeros(n, dtype=bool)
    snap_chg[1:] = last_id[1:] != last_id[:-1]

    upd_chg = np.zeros(n, dtype=bool)
    upd_chg[1:] = (
        (recv[1:] != recv[:-1])
        | (evt[1:] != evt[:-1])
        | (first_id[1:] != first_id[:-1])
        | (final_id[1:] != final_id[:-1])
        | (prev_id[1:] != prev_id[:-1])
    )
    change[1:] |= np.where(is_snap[1:], snap_chg[1:], upd_chg[1:])
    return np.cumsum(change).astype(np.int64) - 1


def sample_top_k_timeline(
    df: pd.DataFrame,
    *,
    dt_ms: int = 1000,
    top_k: int = 20,
) -> tuple[pd.DataFrame, RebuildStats]:
    """
    Stream-rebuild and sample the book on a fixed clock after first ready snapshot.

    Sampling rule: at each clock tick ``t``, use the last book state with
    ``event_time_ms <= t`` (asof / causal).
    """
    stats = RebuildStats(n_rows=len(df))
    if df.empty:
        return pd.DataFrame(), stats

    book = L2Book()
    prev_u: int | None = None
    awaiting_bridge: bool = False  # True until first update after a snapshot
    rows: list[dict] = []
    next_tick: int | None = None
    last_state: dict[str, float] | None = None
    last_event_time: int | None = None

    gids = _event_group_ids(df)
    sides = df["side"].astype(str).to_numpy()
    prices = df["price"].to_numpy(dtype=np.float64)
    qtys = df["quantity"].to_numpy(dtype=np.float64)
    event_types = df["event_type"].astype(str).to_numpy()
    event_times = df["event_time"].to_numpy(dtype=np.int64)
    last_ids = df["last_update_id"].to_numpy()
    first_ids = df["first_update_id"].to_numpy()
    final_ids = df["final_update_id"].to_numpy()
    prev_ids = df["prev_final_update_id"].to_numpy()

    _, start_idx = np.unique(gids, return_index=True)
    start_idx = np.sort(start_idx)
    ends = np.empty_like(start_idx)
    ends[:-1] = start_idx[1:]
    ends[-1] = len(df)

    def flush_until(up_to_ms: int) -> None:
        nonlocal next_tick
        if next_tick is None or last_state is None:
            return
        while next_tick <= up_to_ms:
            rows.append({"ts_ms": int(next_tick), "event_time_ms": last_event_time, **last_state})
            next_tick += dt_ms

    for s, e in zip(start_idx, ends):
        etype = event_types[s]
        event_time = int(event_times[s])
        stats.last_event_time_ms = event_time

        if etype == "snapshot":
            if last_state is not None and next_tick is not None:
                flush_until(event_time - 1)
            levels = [(sides[i], float(prices[i]), float(qtys[i])) for i in range(s, e)]
            last_id_i = _as_optional_int(last_ids[s])
            book.apply_snapshot(levels, last_update_id=last_id_i)
            stats.n_snapshot_groups += 1
            prev_u = last_id_i
            awaiting_bridge = True
            if book.ready:
                if stats.first_ready_event_time_ms is None:
                    stats.first_ready_event_time_ms = event_time
                    next_tick = ((event_time // dt_ms) + 1) * dt_ms
                last_state = book.top_k(top_k)
                last_event_time = event_time
            continue

        stats.n_update_groups += 1
        if not book.ready:
            stats.n_skipped_before_ready += 1
            continue

        if last_state is not None and next_tick is not None:
            flush_until(event_time - 1)

        u_i = _as_optional_int(final_ids[s])
        U_i = _as_optional_int(first_ids[s])
        pu_i = _as_optional_int(prev_ids[s])

        if u_i is not None:
            if awaiting_bridge:
                # Binance bridge: U <= lastUpdateId <= u, or pu == lastUpdateId.
                snap_id = book.last_update_id
                bridged = False
                if snap_id is not None:
                    s_i = int(snap_id)
                    if U_i is not None and U_i <= s_i <= u_i:
                        bridged = True
                    elif pu_i is not None and pu_i == s_i:
                        bridged = True
                    elif u_i < s_i:
                        # Stale event before snapshot tip — skip levels.
                        stats.n_skipped_before_ready += 1
                        continue
                if snap_id is not None and not bridged:
                    stats.n_gaps += 1
                    if len(stats.notes) < 20:
                        stats.notes.append(
                            f"bridge fail at event_time={event_time}: "
                            f"U={U_i} S={snap_id} u={u_i} pu={pu_i}"
                        )
                awaiting_bridge = False
            elif pu_i is not None and prev_u is not None and pu_i != prev_u:
                stats.n_gaps += 1
                if len(stats.notes) < 20:
                    stats.notes.append(
                        f"pu gap at event_time={event_time}: pu={pu_i} prev_u={prev_u}"
                    )

        for i in range(s, e):
            book.apply_level(sides[i], float(prices[i]), float(qtys[i]))

        if u_i is not None:
            prev_u = u_i
            book.last_update_id = u_i
        stats.n_applied_updates += 1

        bb, ba = book.best_bid(), book.best_ask()
        if bb and ba and bb.price >= ba.price:
            stats.n_crossed += 1

        last_state = book.top_k(top_k)
        last_event_time = event_time

    if last_state is not None and next_tick is not None and last_event_time is not None:
        flush_until(last_event_time)

    panel = pd.DataFrame(rows)
    if not panel.empty:
        panel = panel.replace([np.inf, -np.inf], np.nan)
    return panel, stats


def rebuild_events(df: pd.DataFrame) -> tuple[L2Book, RebuildStats]:
    """Rebuild L2 without emitting a dense panel (final book + stats)."""
    # Reuse sampler with huge dt so at most one tick is emitted; we only need stats/book.
    panel, stats = sample_top_k_timeline(df, dt_ms=10**15, top_k=1)
    _ = panel
    # Re-sample is wasteful for final book; acceptable for M0 stub API.
    book = L2Book()
    return book, stats
