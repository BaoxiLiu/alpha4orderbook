"""Panel-ready universe factor computes (dual-library Phase 1 batch).

All functions take a 1s top-K panel and return a float Series.
Tick-band depth uses ``tick_size`` (price units); defaults come from scoring.yaml.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .catalog_nine import (
    cont_ofi_panel_1s,
    imbalance_l3,
    microprice_offset_bp,
    mid_return_1s,
    spread_bp,
)
from .baseline import imbalance


def _sz(panel: pd.DataFrame, side: str, i: int) -> np.ndarray:
    return panel[f"{side}_sz_{i}"].to_numpy(dtype=np.float64)


def _px(panel: pd.DataFrame, side: str, i: int) -> np.ndarray:
    return panel[f"{side}_px_{i}"].to_numpy(dtype=np.float64)


def imbalance_levels(panel: pd.DataFrame, *, levels: int, out: str) -> pd.Series:
    s = imbalance(panel, levels=levels, prefix="imb")
    s.name = out
    return s


def ret_bp(panel: pd.DataFrame, *, lag: int, out: str) -> pd.Series:
    """(mid(t)/mid(t−lag)−1)×1e4 on the panel clock."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    past = np.roll(mid, lag)
    past[:lag] = np.nan
    ret = np.divide(mid, past, out=np.full_like(mid, np.nan), where=np.isfinite(past) & (past != 0)) - 1.0
    return pd.Series(ret * 1e4, index=panel.index, name=out)


def realized_vol_bp(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    """std of 1s log-mid returns over ``window`` seconds × 1e4."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.diff(np.log(mid), prepend=np.nan)
    s = pd.Series(lr, index=panel.index)
    vol = s.rolling(window, min_periods=max(5, window // 5)).std() * 1e4
    vol.name = out
    return vol


def rv_ratio(panel: pd.DataFrame, *, short: int, long: int, out: str, eps: float = 1e-12) -> pd.Series:
    a = realized_vol_bp(panel, window=short, out="_a").to_numpy(dtype=np.float64)
    b = realized_vol_bp(panel, window=long, out="_b").to_numpy(dtype=np.float64)
    val = np.divide(a, b + eps, out=np.full_like(a, np.nan), where=np.isfinite(a) & np.isfinite(b))
    return pd.Series(val, index=panel.index, name=out)


def range_position(panel: pd.DataFrame, *, window: int, out: str, eps: float = 1e-12) -> pd.Series:
    mid = panel["mid"]
    lo = mid.rolling(window, min_periods=max(5, window // 5)).min()
    hi = mid.rolling(window, min_periods=max(5, window // 5)).max()
    val = (mid - lo) / (hi - lo + eps)
    return pd.Series(val.to_numpy(dtype=np.float64), index=panel.index, name=out)


def _micro_raw(panel: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    bid = panel["best_bid"].to_numpy(dtype=np.float64)
    ask = panel["best_ask"].to_numpy(dtype=np.float64)
    bq = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    aq = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    mid = panel["mid"].to_numpy(dtype=np.float64)
    spread = panel["spread"].to_numpy(dtype=np.float64)
    if not np.isfinite(spread).any():
        spread = ask - bid
    denom = bq + aq
    micro = np.divide(bid * aq + ask * bq, denom, out=np.full_like(denom, np.nan), where=denom > 0)
    # (micro-mid)/spread  — D13 style
    off = np.divide(
        micro - mid,
        spread,
        out=np.full_like(mid, np.nan),
        where=np.isfinite(spread) & (np.abs(spread) > 0),
    )
    return off, mid


def microprice_mom(panel: pd.DataFrame, *, lag: int, out: str) -> pd.Series:
    off, _ = _micro_raw(panel)
    past = np.roll(off, lag)
    past[:lag] = np.nan
    return pd.Series(off - past, index=panel.index, name=out)


def spread_dev(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    sp = spread_bp(panel, out="_sp")
    med = sp.rolling(window, min_periods=max(30, window // 20)).median()
    return pd.Series((sp - med).to_numpy(dtype=np.float64), index=panel.index, name=out)


def depth_imb_ticks(
    panel: pd.DataFrame,
    *,
    n_ticks: int,
    tick_size: float,
    out: str,
) -> pd.Series:
    """Signed depth imbalance within ±n_ticks of BBO (top-K approx)."""
    n = len(panel)
    best_bid = panel["best_bid"].to_numpy(dtype=np.float64)
    best_ask = panel["best_ask"].to_numpy(dtype=np.float64)
    bid_sum = np.zeros(n, dtype=np.float64)
    ask_sum = np.zeros(n, dtype=np.float64)
    # Infer available levels
    max_lvl = 0
    while f"bid_sz_{max_lvl}" in panel.columns:
        max_lvl += 1
    band = float(n_ticks) * float(tick_size)
    for i in range(max_lvl):
        bp = _px(panel, "bid", i)
        ap = _px(panel, "ask", i)
        bsz = _sz(panel, "bid", i)
        asz = _sz(panel, "ask", i)
        bid_ok = np.isfinite(bp) & np.isfinite(best_bid) & ((best_bid - bp) <= band + 1e-12) & (bp <= best_bid + 1e-12)
        ask_ok = np.isfinite(ap) & np.isfinite(best_ask) & ((ap - best_ask) <= band + 1e-12) & (ap >= best_ask - 1e-12)
        bid_sum = np.where(bid_ok, bid_sum + np.nan_to_num(bsz, nan=0.0), bid_sum)
        ask_sum = np.where(ask_ok, ask_sum + np.nan_to_num(asz, nan=0.0), ask_sum)
    denom = bid_sum + ask_sum
    val = np.divide(bid_sum - ask_sum, denom, out=np.full(n, np.nan), where=denom > 0)
    return pd.Series(val, index=panel.index, name=out)


def depth_slope_imb(panel: pd.DataFrame, *, tick_size: float, out: str, eps: float = 1e-12) -> pd.Series:
    """(slope_bid − slope_ask) / (|slope_bid|+|slope_ask|+ε); slope = (qty@10t − qty@3t)/7."""
    q3_b = depth_qty_band(panel, side="bid", n_ticks=3, tick_size=tick_size)
    q10_b = depth_qty_band(panel, side="bid", n_ticks=10, tick_size=tick_size)
    q3_a = depth_qty_band(panel, side="ask", n_ticks=3, tick_size=tick_size)
    q10_a = depth_qty_band(panel, side="ask", n_ticks=10, tick_size=tick_size)
    sb = (q10_b - q3_b) / 7.0
    sa = (q10_a - q3_a) / 7.0
    val = (sb - sa) / (np.abs(sb) + np.abs(sa) + eps)
    return pd.Series(val, index=panel.index, name=out)


def depth_qty_band(
    panel: pd.DataFrame, *, side: str, n_ticks: int, tick_size: float
) -> np.ndarray:
    n = len(panel)
    best = panel[f"best_{side}"].to_numpy(dtype=np.float64)
    out = np.zeros(n, dtype=np.float64)
    max_lvl = 0
    while f"{side}_sz_{max_lvl}" in panel.columns:
        max_lvl += 1
    band = float(n_ticks) * float(tick_size)
    for i in range(max_lvl):
        px = _px(panel, side, i)
        sz = _sz(panel, side, i)
        if side == "bid":
            ok = np.isfinite(px) & np.isfinite(best) & ((best - px) <= band + 1e-12)
        else:
            ok = np.isfinite(px) & np.isfinite(best) & ((px - best) <= band + 1e-12)
        out = np.where(ok, out + np.nan_to_num(sz, nan=0.0), out)
    return out


def near_depth_imbalance(
    panel: pd.DataFrame, *, near_ticks: int, tick_size: float, out: str
) -> pd.Series:
    """Notional-ish imbalance using size×mid proxy within near_ticks of BBO."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    b = depth_qty_band(panel, side="bid", n_ticks=near_ticks, tick_size=tick_size) * mid
    a = depth_qty_band(panel, side="ask", n_ticks=near_ticks, tick_size=tick_size) * mid
    denom = b + a
    val = np.divide(b - a, denom, out=np.full_like(denom, np.nan), where=denom > 0)
    return pd.Series(val, index=panel.index, name=out)


def depth_symmetry(panel: pd.DataFrame, *, levels: int, out: str) -> pd.Series:
    imb = imbalance(panel, levels=levels, prefix="imb").to_numpy(dtype=np.float64)
    return pd.Series(1.0 - np.abs(imb), index=panel.index, name=out)


def bid_hhi(panel: pd.DataFrame, *, levels: int, out: str) -> pd.Series:
    n = len(panel)
    sizes = np.column_stack([_sz(panel, "bid", i) for i in range(levels)])
    sizes = np.nan_to_num(sizes, nan=0.0)
    tot = sizes.sum(axis=1)
    share = np.divide(sizes, tot[:, None], out=np.zeros_like(sizes), where=tot[:, None] > 0)
    hhi = (share * share).sum(axis=1)
    hhi = np.where(tot > 0, hhi, np.nan)
    return pd.Series(hhi, index=panel.index, name=out)


def bid_outer_share(panel: pd.DataFrame, *, levels: int, out: str, outer_from: int = 2) -> pd.Series:
    """Share of depth in levels [outer_from .. levels) / sum levels 0..levels-1."""
    n = len(panel)
    sizes = np.column_stack([_sz(panel, "bid", i) for i in range(levels)])
    sizes = np.nan_to_num(sizes, nan=0.0)
    tot = sizes.sum(axis=1)
    outer = sizes[:, outer_from:].sum(axis=1) if outer_from < levels else np.zeros(n)
    val = np.divide(outer, tot, out=np.full(n, np.nan), where=tot > 0)
    return pd.Series(val, index=panel.index, name=out)


# ---- Spec op wrappers -------------------------------------------------------

def op_imbalance_levels(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 1))
    out = str(params.get("out", f"imbalance_l{levels}"))
    return {out: imbalance_levels(panel, levels=levels, out=out)}


def op_ret_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lag = int(params.get("lag", 5))
    out = str(params.get("out", f"ret_{lag}s_bp"))
    return {out: ret_bp(panel, lag=lag, out=out)}


def op_realized_vol_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 30))
    out = str(params.get("out", f"rv_{window}s"))
    return {out: realized_vol_bp(panel, window=window, out=out)}


def op_rv_ratio(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    short = int(params.get("short", 30))
    long = int(params.get("long", 300))
    out = str(params.get("out", f"rv_ratio_{short}_{long}"))
    return {out: rv_ratio(panel, short=short, long=long, out=out)}


def op_range_position(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 60))
    out = str(params.get("out", f"range_position_{window}s"))
    return {out: range_position(panel, window=window, out=out)}


def op_microprice_mom(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lag = int(params.get("lag", 10))
    out = str(params.get("out", f"microprice_mom_{lag}s"))
    return {out: microprice_mom(panel, lag=lag, out=out)}


def op_spread_dev(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 3600))
    out = str(params.get("out", "spread_dev_1h"))
    return {out: spread_dev(panel, window=window, out=out)}


def op_depth_imb_ticks(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    n_ticks = int(params.get("n_ticks", 3))
    tick_size = float(params.get("tick_size", 0.01))
    out = str(params.get("out", f"depth_imb_{n_ticks}t"))
    return {out: depth_imb_ticks(panel, n_ticks=n_ticks, tick_size=tick_size, out=out)}


def op_depth_slope_imb(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    tick_size = float(params.get("tick_size", 0.01))
    out = str(params.get("out", "depth_slope_imb"))
    return {out: depth_slope_imb(panel, tick_size=tick_size, out=out)}


def op_near_depth_imbalance(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    near_ticks = int(params.get("near_ticks", 2))
    tick_size = float(params.get("tick_size", 0.01))
    out = str(params.get("out", "near_depth_imbalance"))
    return {out: near_depth_imbalance(panel, near_ticks=near_ticks, tick_size=tick_size, out=out)}


def op_depth_symmetry(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"depth_symmetry_l{levels}"))
    return {out: depth_symmetry(panel, levels=levels, out=out)}


def op_bid_hhi(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"bid_hhi_l{levels}"))
    return {out: bid_hhi(panel, levels=levels, out=out)}


def op_bid_outer_share(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 5))
    outer_from = int(params.get("outer_from", 2))
    out = str(params.get("out", f"bid_outer_share_l{levels}"))
    return {out: bid_outer_share(panel, levels=levels, out=out, outer_from=outer_from)}


BATCH_OPS = {
    "imbalance_levels": op_imbalance_levels,
    "ret_bp": op_ret_bp,
    "realized_vol_bp": op_realized_vol_bp,
    "rv_ratio": op_rv_ratio,
    "range_position": op_range_position,
    "microprice_mom": op_microprice_mom,
    "spread_dev": op_spread_dev,
    "depth_imb_ticks": op_depth_imb_ticks,
    "depth_slope_imb": op_depth_slope_imb,
    "near_depth_imbalance": op_near_depth_imbalance,
    "depth_symmetry": op_depth_symmetry,
    "bid_hhi": op_bid_hhi,
    "bid_outer_share": op_bid_outer_share,
    # re-export catalog wrappers for registry completeness
    "spread_bp": lambda p, params: {"spread_bp" if not params.get("out") else params["out"]: spread_bp(p, out=str(params.get("out", "spread_bp")))},
    "microprice_offset_bp": lambda p, params: {str(params.get("out", "microprice_offset_bp")): microprice_offset_bp(p, out=str(params.get("out", "microprice_offset_bp")))},
    "cont_ofi_panel_1s": lambda p, params: {str(params.get("out", "cont_ofi_panel_1s")): cont_ofi_panel_1s(p, out=str(params.get("out", "cont_ofi_panel_1s")))},
    "mid_return_1s": lambda p, params: {str(params.get("out", "mid_return_1s")): mid_return_1s(p, out=str(params.get("out", "mid_return_1s")), lag=int(params.get("lag", 1)))},
    "imbalance_l3": lambda p, params: {str(params.get("out", "imbalance_l3")): imbalance_l3(p, out=str(params.get("out", "imbalance_l3")))},
}
