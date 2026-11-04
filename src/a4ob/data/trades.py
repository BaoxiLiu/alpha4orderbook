"""CryptoHFTData trades reader + 1s bars for panel alignment."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .paths import HourKey, trades_path


def read_trades_hour(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.name.startswith("._"):
        raise ValueError(f"refusing AppleDouble sidecar: {path}")
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pq.read_table(path).to_pandas()
    missing = [c for c in ("price", "quantity", "trade_time", "is_buyer_maker") if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    out = pd.DataFrame(
        {
            "trade_time_ms": pd.to_numeric(df["trade_time"], errors="coerce").astype("int64"),
            "price": pd.to_numeric(df["price"], errors="coerce").astype("float64"),
            "quantity": pd.to_numeric(df["quantity"], errors="coerce").astype("float64"),
            "is_buy_aggressor": (~df["is_buyer_maker"].astype(bool)).to_numpy(),
        }
    )
    out = out.dropna(subset=["trade_time_ms", "price", "quantity"])
    out = out[out["quantity"] > 0]
    return out.reset_index(drop=True)


def load_trades_day(
    root: Path,
    symbol: str,
    date: str,
    *,
    hours: list[str] | None = None,
) -> pd.DataFrame:
    """Concat all available ``{symbol}_trades.parquet`` hours for a UTC date."""
    hours = hours or [f"{h:02d}" for h in range(24)]
    frames: list[pd.DataFrame] = []
    for hh in hours:
        path = trades_path(root, symbol, HourKey(date=date, hour=hh))
        if not path.is_file() or path.name.startswith("._"):
            continue
        frames.append(read_trades_hour(path))
    if not frames:
        return pd.DataFrame(
            columns=["trade_time_ms", "price", "quantity", "is_buy_aggressor"]
        )
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values("trade_time_ms", kind="mergesort").reset_index(drop=True)


def trades_to_1s_bars(trades: pd.DataFrame, ts_ms: np.ndarray) -> dict[str, np.ndarray]:
    """
    Aggregate trades into each panel second ``ts_ms[i]`` as (ts_ms[i]-1000, ts_ms[i]].

    Vectorized via bucket-id groupby (much faster than per-second Python loops).
    """
    n = len(ts_ms)
    empty = {
        "n_buy": np.zeros(n, dtype=np.float64),
        "n_sell": np.zeros(n, dtype=np.float64),
        "amt_buy": np.zeros(n, dtype=np.float64),
        "amt_sell": np.zeros(n, dtype=np.float64),
        "vol_buy": np.zeros(n, dtype=np.float64),
        "vol_sell": np.zeros(n, dtype=np.float64),
        "sum_rel": np.zeros(n, dtype=np.float64),
        "sum_rel2": np.zeros(n, dtype=np.float64),
        "sum_lr2": np.zeros(n, dtype=np.float64),
        "n_up": np.zeros(n, dtype=np.float64),
        "last_px": np.full(n, np.nan),
        "n_trades": np.zeros(n, dtype=np.float64),
        "first_px": np.full(n, np.nan),
    }
    if trades.empty or n == 0:
        return empty

    t = trades["trade_time_ms"].to_numpy(dtype=np.int64)
    px = trades["price"].to_numpy(dtype=np.float64)
    qty = trades["quantity"].to_numpy(dtype=np.float64)
    buy = trades["is_buy_aggressor"].to_numpy(dtype=bool)
    first_px = float(px[0])
    empty["first_px"][:] = first_px

    # Map each trade to the panel index whose right edge is the first ts_ms >= trade_time
    # and require trade in (ts-1000, ts].
    idx = np.searchsorted(ts_ms, t, side="left")
    ok = (idx >= 0) & (idx < n)
    # refine: trade must be > ts_ms[idx]-1000
    idx_ok = idx[ok]
    t_ok = t[ok]
    in_bucket = t_ok > (ts_ms[idx_ok] - 1000)
    # also drop trades after last panel tick that landed on n
    final_mask = np.zeros(len(t), dtype=bool)
    final_mask[np.flatnonzero(ok)[in_bucket]] = True
    if not final_mask.any():
        return empty

    t = t[final_mask]
    px = px[final_mask]
    qty = qty[final_mask]
    buy = buy[final_mask]
    bucket = np.searchsorted(ts_ms, t, side="left").astype(np.int64)

    prev_px = np.empty(len(px), dtype=np.float64)
    prev_px[0] = np.nan
    if len(px) > 1:
        prev_px[1:] = px[:-1]
    rel = px / first_px - 1.0 if first_px > 0 else np.zeros_like(px)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr2 = np.where(np.isfinite(prev_px) & (prev_px > 0) & (px > 0), np.log(px / prev_px) ** 2, 0.0)
    up = (px > prev_px) & np.isfinite(prev_px)

    amt = px * qty
    df = pd.DataFrame(
        {
            "bucket": bucket,
            "n_buy": buy.astype(np.float64),
            "n_sell": (~buy).astype(np.float64),
            "amt_buy": np.where(buy, amt, 0.0),
            "amt_sell": np.where(~buy, amt, 0.0),
            "vol_buy": np.where(buy, qty, 0.0),
            "vol_sell": np.where(~buy, qty, 0.0),
            "sum_rel": rel,
            "sum_rel2": rel * rel,
            "sum_lr2": lr2,
            "n_up": up.astype(np.float64),
            "last_px": px,
            "n_trades": 1.0,
        }
    )
    g = df.groupby("bucket", sort=False)
    agg = g.agg(
        {
            "n_buy": "sum",
            "n_sell": "sum",
            "amt_buy": "sum",
            "amt_sell": "sum",
            "vol_buy": "sum",
            "vol_sell": "sum",
            "sum_rel": "sum",
            "sum_rel2": "sum",
            "sum_lr2": "sum",
            "n_up": "sum",
            "last_px": "last",
            "n_trades": "sum",
        }
    )
    for col in (
        "n_buy",
        "n_sell",
        "amt_buy",
        "amt_sell",
        "vol_buy",
        "vol_sell",
        "sum_rel",
        "sum_rel2",
        "sum_lr2",
        "n_up",
        "n_trades",
    ):
        empty[col][agg.index.to_numpy()] = agg[col].to_numpy(dtype=np.float64)
    empty["last_px"][agg.index.to_numpy()] = agg["last_px"].to_numpy(dtype=np.float64)
    return empty
