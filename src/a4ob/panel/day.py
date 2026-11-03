"""(symbol, day) research panel builder + manifest (M2)."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ..book.rebuild import CarryState, RebuildStats, sample_top_k_timeline
from ..config import default_config_path, load_config
from ..data.paths import HourKey, orderbook_path, resolve_data_root
from ..data.reader import hour_has_snapshot, read_orderbook_hour
from .manifest import config_hash, file_sha256, write_manifest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cross-hour policy (documented for operators / future M2+ work)
# ---------------------------------------------------------------------------
#
# CARRY_FORWARD_AFTER_SNAPSHOT (default):
#   1. Walk UTC hours 00–23 in order.
#   2. Missing files → skip (logged).
#   3. Hours with no snapshot AND book not yet ready → skip as update-only
#      (cannot invent a book from diffs alone).
#   4. First hour that contains a snapshot → L0 rebuild, start 1s sampling.
#   5. Later hours (snapshot or update-only) → apply onto the same in-memory
#      L2 book (pu/u continuity). A new snapshot resyncs the book.
#   6. We never tick-fill calendar gaps before the first ready snapshot.
#
POLICY = "CARRY_FORWARD_AFTER_SNAPSHOT"


def default_panels_root() -> Path:
    return Path(__file__).resolve().parents[3] / "panels"


def panel_day_dir(
    panels_root: Path,
    *,
    symbol: str,
    date: str,
    dt_seconds: int,
    top_k: int,
) -> Path:
    return (
        panels_root
        / f"dt={dt_seconds}s"
        / f"K={top_k}"
        / f"symbol={symbol}"
        / f"date={date}"
    )


def build_day_panel(
    *,
    symbol: str,
    date: str,
    config_path: str | Path | None = None,
    hour: str | None = None,
    panels_root: str | Path | None = None,
    data_root: str | Path | None = None,
    allow_empty: bool = True,
) -> dict[str, Any]:
    """
    Build one (symbol, day) [or single-hour debug] research panel + manifest.

    Parameters
    ----------
    hour:
        If set (``HH``), only that UTC hour is processed (debug). Otherwise 00–23.
    allow_empty:
        If True (default), days with no usable snapshot write a ``no_snapshot``
        manifest and return without raising (M4 range builds).
    """
    t0 = time.perf_counter()
    cfg_path = Path(config_path) if config_path else default_config_path()
    cfg = load_config(cfg_path)
    root = resolve_data_root(data_root or cfg["data"]["root"])
    dt_s = int(cfg["panel"]["dt_seconds"])
    top_k = int(cfg["panel"]["top_k"])
    dt_ms = dt_s * 1000
    cfg_h = config_hash(cfg)
    out_root = Path(panels_root) if panels_root else default_panels_root()
    out_dir = panel_day_dir(out_root, symbol=symbol, date=date, dt_seconds=dt_s, top_k=top_k)
    out_dir.mkdir(parents=True, exist_ok=True)

    if hour is not None:
        hours = [str(hour).zfill(2)]
    else:
        hours = [f"{h:02d}" for h in range(24)]

    carry: CarryState | None = None
    day_stats = RebuildStats()
    frames: list[pd.DataFrame] = []

    hours_missing: list[str] = []
    hours_skipped_update_only: list[str] = []
    hours_processed: list[str] = []
    snapshot_hours: list[str] = []
    carried_hours: list[str] = []
    hour_logs: list[dict[str, Any]] = []

    for hh in hours:
        key = HourKey(date=date, hour=hh)
        path = orderbook_path(root, symbol, key)
        entry: dict[str, Any] = {"hour": hh, "path": str(path)}

        if not path.is_file() or path.name.startswith("._"):
            logger.info("skip missing %s %s", symbol, key)
            hours_missing.append(hh)
            entry["status"] = "missing"
            hour_logs.append(entry)
            continue

        has_snap = hour_has_snapshot(path)
        ready = carry is not None and carry.book.ready

        if not has_snap and not ready:
            logger.info(
                "skip update-only (no prior book) %s %s", symbol, key
            )
            hours_skipped_update_only.append(hh)
            entry["status"] = "skipped_update_only"
            entry["has_snapshot"] = False
            hour_logs.append(entry)
            continue

        logger.info(
            "process %s %s snapshot=%s carry=%s",
            symbol,
            key,
            has_snap,
            ready,
        )
        df = read_orderbook_hour(path)
        panel_h, stats, carry = sample_top_k_timeline(
            df, dt_ms=dt_ms, top_k=top_k, carry=carry
        )
        day_stats.merge(stats)

        if has_snap:
            snapshot_hours.append(hh)
        elif ready:
            carried_hours.append(hh)

        hours_processed.append(hh)
        entry.update(
            {
                "status": "processed",
                "has_snapshot": has_snap,
                "n_rows_raw": int(stats.n_rows),
                "n_panel_rows": int(len(panel_h)),
                "n_gaps": int(stats.n_gaps),
                "n_snapshot_groups": int(stats.n_snapshot_groups),
            }
        )
        hour_logs.append(entry)

        if not panel_h.empty:
            panel_h = panel_h.copy()
            panel_h.insert(0, "symbol", symbol)
            panel_h.insert(1, "date", date)
            # hour from clock tick (UTC), not source file hour alone
            panel_h.insert(
                2,
                "hour",
                panel_h["ts_ms"].map(lambda t: f"{(int(t) // 1000) % 86400 // 3600:02d}"),
            )
            frames.append(panel_h)

    elapsed = time.perf_counter() - t0

    if not frames:
        msg = (
            f"no panel rows for {symbol} {date} "
            f"(processed={hours_processed}, snapshot_hours={snapshot_hours}, "
            f"skipped_update_only={hours_skipped_update_only}, missing={hours_missing})"
        )
        if not allow_empty:
            raise RuntimeError(msg)
        logger.warning("%s", msg)
        # Remove stale panel if any
        stale = out_dir / "panel.parquet"
        if stale.exists():
            stale.unlink()
        manifest = {
            "schema_version": 1,
            "status": "no_snapshot",
            "built_at_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(elapsed, 3),
            "policy": POLICY,
            "symbol": symbol,
            "date": date,
            "dt_seconds": dt_s,
            "top_k": top_k,
            "config_path": str(cfg_path.resolve()),
            "config_hash": cfg_h,
            "data_root": str(root),
            "panel_path": None,
            "n_rows": 0,
            "hours_requested": hours,
            "hours_missing": hours_missing,
            "hours_skipped_update_only": hours_skipped_update_only,
            "hours_processed": hours_processed,
            "snapshot_hours": snapshot_hours,
            "carried_hours": carried_hours,
            "rebuild_stats": asdict(day_stats),
            "hour_logs": hour_logs,
            "note": msg,
        }
        manifest_path = write_manifest(out_dir / "manifest.json", manifest)
        return {
            "status": "no_snapshot",
            "panel_path": None,
            "manifest_path": str(manifest_path),
            "out_dir": str(out_dir),
            "n_rows": 0,
            "elapsed_seconds": round(elapsed, 3),
            "snapshot_hours": snapshot_hours,
            "hours_processed": hours_processed,
            "hours_skipped_update_only": hours_skipped_update_only,
            "hours_missing": hours_missing,
            "sha256": None,
            "size_bytes": 0,
            "policy": POLICY,
            "config_hash": cfg_h,
        }

    panel = pd.concat(frames, ignore_index=True)
    panel = panel.drop_duplicates(subset=["ts_ms"], keep="last").sort_values("ts_ms")
    panel = panel.reset_index(drop=True)

    panel_path = out_dir / "panel.parquet"
    panel.to_parquet(panel_path, index=False)
    size_bytes = panel_path.stat().st_size
    sha = file_sha256(panel_path)

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "status": "ok",
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "policy": POLICY,
        "policy_notes": (
            "Carry L2 book across hours after first snapshot; skip update-only "
            "hours before the book is ready; resync on later snapshots."
        ),
        "symbol": symbol,
        "date": date,
        "dt_seconds": dt_s,
        "top_k": top_k,
        "config_path": str(cfg_path.resolve()),
        "config_hash": cfg_h,
        "data_root": str(root),
        "panel_path": str(panel_path),
        "n_rows": int(len(panel)),
        "ts_ms_min": int(panel["ts_ms"].iloc[0]),
        "ts_ms_max": int(panel["ts_ms"].iloc[-1]),
        "size_bytes": int(size_bytes),
        "sha256": sha,
        "hours_requested": hours,
        "hours_missing": hours_missing,
        "hours_skipped_update_only": hours_skipped_update_only,
        "hours_processed": hours_processed,
        "snapshot_hours": snapshot_hours,
        "carried_hours": carried_hours,
        "rebuild_stats": asdict(day_stats),
        "hour_logs": hour_logs,
        "debug_single_hour": hour,
    }
    manifest_path = write_manifest(out_dir / "manifest.json", manifest)

    return {
        "status": "ok",
        "panel_path": str(panel_path),
        "manifest_path": str(manifest_path),
        "out_dir": str(out_dir),
        "n_rows": int(len(panel)),
        "elapsed_seconds": round(elapsed, 3),
        "snapshot_hours": snapshot_hours,
        "hours_processed": hours_processed,
        "hours_skipped_update_only": hours_skipped_update_only,
        "hours_missing": hours_missing,
        "sha256": sha,
        "size_bytes": size_bytes,
        "policy": POLICY,
        "config_hash": cfg_h,
    }
