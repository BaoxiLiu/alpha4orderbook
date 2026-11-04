"""Panel-ready universe factor computes (dual-library HF expansion).

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


def _max_lvl(panel: pd.DataFrame, side: str = "bid") -> int:
    n = 0
    while f"{side}_sz_{n}" in panel.columns:
        n += 1
    return n


def _level_stack(panel: pd.DataFrame, side: str, levels: int) -> np.ndarray:
    avail = _max_lvl(panel, side)
    use = min(levels, avail)
    if use <= 0:
        return np.zeros((len(panel), 0), dtype=np.float64)
    return np.column_stack([_sz(panel, side, i) for i in range(use)])


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


def log_ret_bp(panel: pd.DataFrame, *, lag: int, out: str) -> pd.Series:
    mid = panel["mid"].to_numpy(dtype=np.float64)
    past = np.roll(mid, lag)
    past[:lag] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.log(mid / past) * 1e4
    return pd.Series(val, index=panel.index, name=out)


def realized_vol_bp(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    """std of 1s log-mid returns over ``window`` seconds × 1e4."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.diff(np.log(np.where(mid > 0, mid, np.nan)), prepend=np.nan)
    s = pd.Series(lr, index=panel.index)
    # window=1 → |r|; still use at least 2 pts for std when window≥2
    min_p = 1 if window <= 1 else max(2, min(window, max(2, window // 5)))
    if window <= 1:
        vol = s.abs() * 1e4
    else:
        vol = s.rolling(window, min_periods=min_p).std() * 1e4
    vol.name = out
    return vol


def sum_sq_rv_bp(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    """sqrt(sum of squared 1s bp mid Δ) over window — author rv_*_bp2 style."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        d_bp = np.diff(mid, prepend=np.nan) / mid * 1e4
    s = pd.Series(d_bp ** 2, index=panel.index)
    val = np.sqrt(s.rolling(window, min_periods=max(5, window // 5)).sum())
    return pd.Series(val.to_numpy(dtype=np.float64), index=panel.index, name=out)


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


def microprice_spread_frac(panel: pd.DataFrame, *, out: str) -> pd.Series:
    """(micro − mid) / spread — micro:microprice_bid_signed_bp style (spread denom)."""
    off, _ = _micro_raw(panel)
    return pd.Series(off, index=panel.index, name=out)


def spread_dev(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    sp = spread_bp(panel, out="_sp")
    med = sp.rolling(window, min_periods=max(30, window // 20)).median()
    return pd.Series((sp - med).to_numpy(dtype=np.float64), index=panel.index, name=out)


def spread_ticks(panel: pd.DataFrame, *, tick_size: float, out: str) -> pd.Series:
    spread = panel["spread"].to_numpy(dtype=np.float64)
    if not np.isfinite(spread).any():
        spread = panel["best_ask"].to_numpy(dtype=np.float64) - panel["best_bid"].to_numpy(dtype=np.float64)
    ts = float(tick_size) if tick_size > 0 else np.nan
    val = spread / ts if np.isfinite(ts) else np.full_like(spread, np.nan)
    return pd.Series(val, index=panel.index, name=out)


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
    max_lvl = _max_lvl(panel)
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


def depth_imb_bp(panel: pd.DataFrame, *, n_bp: float, out: str) -> pd.Series:
    """Signed notional-ish imbalance within ±n_bp of mid (top-K approx)."""
    n = len(panel)
    mid = panel["mid"].to_numpy(dtype=np.float64)
    band = mid * (float(n_bp) * 1e-4)
    bid_sum = np.zeros(n, dtype=np.float64)
    ask_sum = np.zeros(n, dtype=np.float64)
    max_lvl = _max_lvl(panel)
    for i in range(max_lvl):
        bp = _px(panel, "bid", i)
        ap = _px(panel, "ask", i)
        bsz = _sz(panel, "bid", i)
        asz = _sz(panel, "ask", i)
        bid_ok = np.isfinite(bp) & np.isfinite(mid) & ((mid - bp) <= band + 1e-12)
        ask_ok = np.isfinite(ap) & np.isfinite(mid) & ((ap - mid) <= band + 1e-12)
        bid_sum = np.where(bid_ok, bid_sum + np.nan_to_num(bsz, nan=0.0) * mid, bid_sum)
        ask_sum = np.where(ask_ok, ask_sum + np.nan_to_num(asz, nan=0.0) * mid, ask_sum)
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
    max_lvl = _max_lvl(panel, side)
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


def side_hhi(panel: pd.DataFrame, *, side: str, levels: int, out: str) -> pd.Series:
    sizes = np.nan_to_num(_level_stack(panel, side, levels), nan=0.0)
    if sizes.shape[1] == 0:
        return pd.Series(np.full(len(panel), np.nan), index=panel.index, name=out)
    tot = sizes.sum(axis=1)
    share = np.divide(sizes, tot[:, None], out=np.zeros_like(sizes), where=tot[:, None] > 0)
    hhi = (share * share).sum(axis=1)
    hhi = np.where(tot > 0, hhi, np.nan)
    return pd.Series(hhi, index=panel.index, name=out)


def side_outer_share(
    panel: pd.DataFrame, *, side: str, levels: int, out: str, outer_from: int = 2
) -> pd.Series:
    sizes = np.nan_to_num(_level_stack(panel, side, levels), nan=0.0)
    n = len(panel)
    if sizes.shape[1] == 0:
        return pd.Series(np.full(n, np.nan), index=panel.index, name=out)
    tot = sizes.sum(axis=1)
    outer = sizes[:, outer_from:].sum(axis=1) if outer_from < sizes.shape[1] else np.zeros(n)
    val = np.divide(outer, tot, out=np.full(n, np.nan), where=tot > 0)
    return pd.Series(val, index=panel.index, name=out)


def side_uniformity(panel: pd.DataFrame, *, side: str, levels: int, out: str) -> pd.Series:
    """1 / (1 + std/mean) over top-L sizes (microstructure shape)."""
    sizes = np.nan_to_num(_level_stack(panel, side, levels), nan=0.0)
    if sizes.shape[1] == 0:
        return pd.Series(np.full(len(panel), np.nan), index=panel.index, name=out)
    mean = sizes.mean(axis=1)
    std = sizes.std(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        cv = np.divide(std, mean, out=np.full_like(mean, np.nan), where=mean > 0)
    val = 1.0 / (1.0 + cv)
    return pd.Series(val, index=panel.index, name=out)


def side_log_touch_back_ratio(panel: pd.DataFrame, *, side: str, levels: int, out: str) -> pd.Series:
    """log1p(q0 / sum(q1..q_{L-1}))."""
    sizes = np.nan_to_num(_level_stack(panel, side, levels), nan=0.0)
    if sizes.shape[1] < 2:
        return pd.Series(np.full(len(panel), np.nan), index=panel.index, name=out)
    q0 = sizes[:, 0]
    back = sizes[:, 1:].sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.log1p(np.divide(q0, back, out=np.full_like(q0, np.nan), where=back > 0))
    return pd.Series(val, index=panel.index, name=out)


def side_touch_share(panel: pd.DataFrame, *, side: str, levels: int, out: str) -> pd.Series:
    sizes = np.nan_to_num(_level_stack(panel, side, levels), nan=0.0)
    if sizes.shape[1] == 0:
        return pd.Series(np.full(len(panel), np.nan), index=panel.index, name=out)
    tot = sizes.sum(axis=1)
    val = np.divide(sizes[:, 0], tot, out=np.full(len(panel), np.nan), where=tot > 0)
    return pd.Series(val, index=panel.index, name=out)


def side_log_notional(panel: pd.DataFrame, *, side: str, levels: int, out: str) -> pd.Series:
    sizes = np.nan_to_num(_level_stack(panel, side, levels), nan=0.0)
    if sizes.shape[1] == 0:
        return pd.Series(np.full(len(panel), np.nan), index=panel.index, name=out)
    px = np.column_stack([_px(panel, side, i) for i in range(sizes.shape[1])])
    px = np.nan_to_num(px, nan=0.0)
    notional = (sizes * px).sum(axis=1)
    val = np.log1p(np.maximum(notional, 0.0))
    val = np.where(notional > 0, val, np.nan)
    return pd.Series(val, index=panel.index, name=out)


def log_touch_total_notional(panel: pd.DataFrame, *, out: str) -> pd.Series:
    bp = panel["best_bid"].to_numpy(dtype=np.float64)
    ap = panel["best_ask"].to_numpy(dtype=np.float64)
    bq = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    aq = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    tot = np.nan_to_num(bp * bq, nan=0.0) + np.nan_to_num(ap * aq, nan=0.0)
    val = np.log1p(np.maximum(tot, 0.0))
    val = np.where(tot > 0, val, np.nan)
    return pd.Series(val, index=panel.index, name=out)


def side_width_ticks(
    panel: pd.DataFrame, *, side: str, levels: int, tick_size: float, out: str
) -> pd.Series:
    """|px_{L-1} − px_0| / tick_size."""
    avail = _max_lvl(panel, side)
    use = min(levels, avail)
    if use < 2:
        return pd.Series(np.full(len(panel), np.nan), index=panel.index, name=out)
    p0 = _px(panel, side, 0)
    pL = _px(panel, side, use - 1)
    ts = float(tick_size) if tick_size > 0 else np.nan
    val = np.abs(pL - p0) / ts
    return pd.Series(val, index=panel.index, name=out)


def lag_delta_of(series: pd.Series, *, lag: int, out: str) -> pd.Series:
    arr = series.to_numpy(dtype=np.float64)
    past = np.roll(arr, lag)
    past[:lag] = np.nan
    return pd.Series(arr - past, index=series.index, name=out)


def half_rv_bp(panel: pd.DataFrame, *, window: int, direction: str, out: str) -> pd.Series:
    """sqrt(sum r^2) over window for positive (up) or negative (down) 1s log returns ×1e4 scale."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.diff(np.log(mid), prepend=np.nan)
    if direction == "up":
        part = np.where(lr > 0, lr * lr, 0.0)
    elif direction == "down":
        part = np.where(lr < 0, lr * lr, 0.0)
    else:
        raise ValueError("direction must be up|down")
    s = pd.Series(part, index=panel.index)
    min_p = max(1, min(window, max(1, window // 5)))
    val = np.sqrt(s.rolling(window, min_periods=min_p).sum()) * 1e4
    return pd.Series(val.to_numpy(dtype=np.float64), index=panel.index, name=out)



def signed_semivar(panel: pd.DataFrame, *, window: int, out: str, eps: float = 1e-12) -> pd.Series:
    up = half_rv_bp(panel, window=window, direction="up", out="_u").to_numpy(dtype=np.float64)
    dn = half_rv_bp(panel, window=window, direction="down", out="_d").to_numpy(dtype=np.float64)
    val = (up - dn) / (up + dn + eps)
    return pd.Series(val, index=panel.index, name=out)


def jump_count(panel: pd.DataFrame, *, window: int, mult: float, out: str) -> pd.Series:
    """Count of |1s ret| > mult × rolling median(|1s ret|) inside window."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.abs(np.diff(np.log(np.where(mid > 0, mid, np.nan)), prepend=np.nan))
    s = pd.Series(lr, index=panel.index)
    min_p = max(10, window // 5)
    med = s.rolling(window, min_periods=min_p).median()
    thr = mult * med
    flag = (s > thr) & thr.notna() & (thr > 0) & s.notna()
    cnt = flag.astype(np.float64).rolling(window, min_periods=min_p).sum()
    return pd.Series(cnt.to_numpy(dtype=np.float64), index=panel.index, name=out)


def hour_cycle(panel: pd.DataFrame, *, component: str, out: str) -> pd.Series:
    """UTC hour sin/cos from ts_ms."""
    ts = panel["ts_ms"].to_numpy(dtype=np.float64)
    hour = ((ts / 1000.0) % 86400.0) / 3600.0
    ang = 2.0 * np.pi * hour / 24.0
    if component == "sin":
        val = np.sin(ang)
    elif component == "cos":
        val = np.cos(ang)
    else:
        raise ValueError("component must be sin|cos")
    return pd.Series(val, index=panel.index, name=out)


def notional_change_frac(
    panel: pd.DataFrame, *, side: str, levels: int, lag: int, out: str, eps: float = 1e-12
) -> pd.Series:
    """sum(sz*px)_t / sum(sz*px)_{t-lag} − 1."""
    cur = side_log_notional(panel, side=side, levels=levels, out="_n")
    # recover notional via expm1 of log1p
    sizes = np.nan_to_num(_level_stack(panel, side, levels), nan=0.0)
    if sizes.shape[1] == 0:
        return pd.Series(np.full(len(panel), np.nan), index=panel.index, name=out)
    px = np.nan_to_num(np.column_stack([_px(panel, side, i) for i in range(sizes.shape[1])]), nan=0.0)
    notional = (sizes * px).sum(axis=1)
    past = np.roll(notional, lag)
    past[:lag] = np.nan
    val = np.divide(notional, past + eps, out=np.full_like(notional, np.nan), where=np.isfinite(past) & (past > 0)) - 1.0
    return pd.Series(val, index=panel.index, name=out)


def spread_change_ticks(panel: pd.DataFrame, *, lag: int, tick_size: float, out: str) -> pd.Series:
    sp = spread_ticks(panel, tick_size=tick_size, out="_s")
    return lag_delta_of(sp, lag=lag, out=out)


# ---- Spec op wrappers -------------------------------------------------------

def op_imbalance_levels(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 1))
    out = str(params.get("out", f"imbalance_l{levels}"))
    return {out: imbalance_levels(panel, levels=levels, out=out)}


def op_ret_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lag = int(params.get("lag", 5))
    out = str(params.get("out", f"ret_{lag}s_bp"))
    return {out: ret_bp(panel, lag=lag, out=out)}


def op_log_ret_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lag = int(params.get("lag", 2))
    out = str(params.get("out", f"log_ret_{lag}s_bp"))
    return {out: log_ret_bp(panel, lag=lag, out=out)}


def op_realized_vol_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 30))
    out = str(params.get("out", f"rv_{window}s"))
    return {out: realized_vol_bp(panel, window=window, out=out)}


def op_sum_sq_rv_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 60))
    out = str(params.get("out", f"rv_{window}s_bp2"))
    return {out: sum_sq_rv_bp(panel, window=window, out=out)}


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


def op_microprice_spread_frac(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "microprice_spread_frac"))
    return {out: microprice_spread_frac(panel, out=out)}


def op_spread_dev(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 3600))
    out = str(params.get("out", "spread_dev_1h"))
    return {out: spread_dev(panel, window=window, out=out)}


def op_spread_ticks(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    tick_size = float(params.get("tick_size", 0.01))
    out = str(params.get("out", "spread_ticks"))
    return {out: spread_ticks(panel, tick_size=tick_size, out=out)}


def op_depth_imb_ticks(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    n_ticks = int(params.get("n_ticks", 3))
    tick_size = float(params.get("tick_size", 0.01))
    out = str(params.get("out", f"depth_imb_{n_ticks}t"))
    return {out: depth_imb_ticks(panel, n_ticks=n_ticks, tick_size=tick_size, out=out)}


def op_depth_imb_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    n_bp = float(params.get("n_bp", 5))
    out = str(params.get("out", f"depth_imb_{int(n_bp)}bp"))
    return {out: depth_imb_bp(panel, n_bp=n_bp, out=out)}


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


def op_side_hhi(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"{side}_hhi_l{levels}"))
    return {out: side_hhi(panel, side=side, levels=levels, out=out)}


def op_side_outer_share(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 5))
    outer_from = int(params.get("outer_from", 2))
    out = str(params.get("out", f"{side}_outer_share_l{levels}"))
    return {out: side_outer_share(panel, side=side, levels=levels, out=out, outer_from=outer_from)}


def op_side_uniformity(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"{side}_uniformity_l{levels}"))
    return {out: side_uniformity(panel, side=side, levels=levels, out=out)}


def op_side_log_touch_back_ratio(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"log_{side}_touch_back_ratio_l{levels}"))
    return {out: side_log_touch_back_ratio(panel, side=side, levels=levels, out=out)}


def op_side_touch_share(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 10))
    out = str(params.get("out", f"{side}_touch_share_l{levels}"))
    return {out: side_touch_share(panel, side=side, levels=levels, out=out)}


def op_side_log_notional(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 1))
    out = str(params.get("out", f"log_{side}_notional_l{levels}"))
    return {out: side_log_notional(panel, side=side, levels=levels, out=out)}


def op_log_touch_total_notional(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "log_touch_total_notional"))
    return {out: log_touch_total_notional(panel, out=out)}


def op_side_width_ticks(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 10))
    tick_size = float(params.get("tick_size", 0.01))
    out = str(params.get("out", f"{side}_l{levels}_width_ticks"))
    return {out: side_width_ticks(panel, side=side, levels=levels, tick_size=tick_size, out=out)}


def op_factor_delta(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    """Compute base op then lag-delta. params: base_op, lag, plus base params; out."""
    base_op = str(params["base_op"])
    lag = int(params.get("lag", 1))
    out = str(params.get("out"))
    base_params = {k: v for k, v in params.items() if k not in ("base_op", "lag", "out")}
    base_params.setdefault("out", "_base")
    if base_op not in BATCH_OPS:
        raise KeyError(f"unknown base_op for factor_delta: {base_op}")
    base = BATCH_OPS[base_op](panel, base_params)
    series = next(iter(base.values()))
    return {out: lag_delta_of(series, lag=lag, out=out)}


def op_half_rv_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 30))
    direction = str(params.get("direction", "up"))
    out = str(params.get("out", f"{direction}_rv_{window}s"))
    return {out: half_rv_bp(panel, window=window, direction=direction, out=out)}


def op_signed_semivar(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 30))
    out = str(params.get("out", f"signed_semivar_{window}s"))
    return {out: signed_semivar(panel, window=window, out=out)}


def op_jump_count(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 60))
    mult = float(params.get("mult", 4.0))
    out = str(params.get("out", f"jump_count_{window}s"))
    return {out: jump_count(panel, window=window, mult=mult, out=out)}


def op_hour_cycle(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    component = str(params.get("component", "sin"))
    out = str(params.get("out", f"hour_{component}"))
    return {out: hour_cycle(panel, component=component, out=out)}


def op_notional_change_frac(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    side = str(params.get("side", "bid"))
    levels = int(params.get("levels", 5))
    lag = int(params.get("lag", 1))
    out = str(params.get("out", f"{side}_l{levels}_change_frac_{lag}s"))
    return {out: notional_change_frac(panel, side=side, levels=levels, lag=lag, out=out)}


def op_spread_change_ticks(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lag = int(params.get("lag", 1))
    tick_size = float(params.get("tick_size", 0.01))
    out = str(params.get("out", f"spread_change_ticks_{lag}s"))
    return {out: spread_change_ticks(panel, lag=lag, tick_size=tick_size, out=out)}


# back-compat aliases
def op_bid_hhi(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    p = dict(params)
    p.setdefault("side", "bid")
    return op_side_hhi(panel, p)


def op_bid_outer_share(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    p = dict(params)
    p.setdefault("side", "bid")
    return op_side_outer_share(panel, p)



def weighted_depth_imb(panel: pd.DataFrame, *, levels: int, decay: float, out: str, eps: float = 1e-12) -> pd.Series:
    """Geometric depth-decay size imbalance (orderflow-metrics / lobkit-style).

    w_i = decay**i; I = (Σ w·bid_sz − Σ w·ask_sz) / (Σ w·bid_sz + Σ w·ask_sz).
    """
    bid = _level_stack(panel, "bid", levels)
    ask = _level_stack(panel, "ask", levels)
    L = max(bid.shape[1], ask.shape[1])
    if L == 0:
        return pd.Series(np.nan, index=panel.index, name=out)
    w = (float(decay) ** np.arange(L, dtype=np.float64)).reshape(1, -1)
    if bid.shape[1] < L:
        bid = np.pad(bid, ((0, 0), (0, L - bid.shape[1])))
    if ask.shape[1] < L:
        ask = np.pad(ask, ((0, 0), (0, L - ask.shape[1])))
    wb = (bid * w).sum(axis=1)
    wa = (ask * w).sum(axis=1)
    val = (wb - wa) / np.maximum(wb + wa, eps)
    return pd.Series(val, index=panel.index, name=out)


def liquidity_pressure(panel: pd.DataFrame, *, levels: int, out: str, eps: float = 1e-12) -> pd.Series:
    """Depth imbalance scaled by inverse relative spread (NightCoderLJ-style pressure).

    ((Σbid − Σask)/(Σbid+Σask)) / ((ask−bid)/mid + eps)
    """
    bid = _level_stack(panel, "bid", levels).sum(axis=1)
    ask = _level_stack(panel, "ask", levels).sum(axis=1)
    mid = panel["mid"].to_numpy(dtype=np.float64)
    bb = panel["best_bid"].to_numpy(dtype=np.float64)
    ba = panel["best_ask"].to_numpy(dtype=np.float64)
    imb = (bid - ask) / np.maximum(bid + ask, eps)
    rel_spread = (ba - bb) / np.maximum(mid, eps)
    val = imb / np.maximum(rel_spread, eps)
    return pd.Series(val, index=panel.index, name=out)


def ofi_over_depth(panel: pd.DataFrame, *, out: str, eps: float = 1e-12) -> pd.Series:
    """Cont panel OFI normalized by average touch depth (Cont universal β∝1/depth)."""
    ofi = cont_ofi_panel_1s(panel, out="_ofi").to_numpy(dtype=np.float64)
    depth = 0.5 * (
        panel["best_bid_sz"].to_numpy(dtype=np.float64)
        + panel["best_ask_sz"].to_numpy(dtype=np.float64)
    )
    val = ofi / np.maximum(depth, eps)
    return pd.Series(val, index=panel.index, name=out)


def book_vwap_offset_bp(panel: pd.DataFrame, *, levels: int, out: str, eps: float = 1e-12) -> pd.Series:
    """Multi-level book VWAP (both sides) vs mid, in bp — deep microprice proxy."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    num = np.zeros(len(panel), dtype=np.float64)
    den = np.zeros(len(panel), dtype=np.float64)
    for side in ("bid", "ask"):
        for i in range(min(levels, _max_lvl(panel, side))):
            px = _px(panel, side, i)
            sz = _sz(panel, side, i)
            num += px * sz
            den += sz
    vwap = num / np.maximum(den, eps)
    val = (vwap - mid) / np.maximum(mid, eps) * 1e4
    return pd.Series(val, index=panel.index, name=out)


def relative_spread_depth(panel: pd.DataFrame, *, out: str, eps: float = 1e-12) -> pd.Series:
    """Quoted spread / touch depth (liquidity thinness); higher = thinner book."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    bb = panel["best_bid"].to_numpy(dtype=np.float64)
    ba = panel["best_ask"].to_numpy(dtype=np.float64)
    depth = panel["best_bid_sz"].to_numpy(dtype=np.float64) + panel["best_ask_sz"].to_numpy(dtype=np.float64)
    spread = ba - bb
    val = spread / np.maximum(mid * depth, eps) * 1e4
    return pd.Series(val, index=panel.index, name=out)


def trade_vs_depth(panel: pd.DataFrame, *, out: str, eps: float = 1e-12) -> pd.Series:
    """Taker imbalance / log touch depth — needs nh_ti_1s joined (trades sidecar)."""
    if "nh_ti_1s" not in panel.columns:
        return pd.Series(np.nan, index=panel.index, name=out)
    ti = panel["nh_ti_1s"].to_numpy(dtype=np.float64)
    depth = panel["best_bid_sz"].to_numpy(dtype=np.float64) + panel["best_ask_sz"].to_numpy(dtype=np.float64)
    val = ti / np.log1p(np.maximum(depth, 0.0) + eps)
    return pd.Series(val, index=panel.index, name=out)


def kyle_lambda_proxy(panel: pd.DataFrame, *, window: int, out: str, eps: float = 1e-12) -> pd.Series:
    """Rolling |Δmid_bp| / |signed aggressor volume| — Kyle λ proxy (needs nh_signed_volume1)."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    d_bp = np.abs(np.diff(mid, prepend=np.nan) / mid * 1e4)
    if "nh_signed_volume1" not in panel.columns:
        return pd.Series(np.nan, index=panel.index, name=out)
    vol = np.abs(panel["nh_signed_volume1"].to_numpy(dtype=np.float64))
    num = pd.Series(d_bp, index=panel.index).rolling(window, min_periods=max(5, window // 5)).sum()
    den = pd.Series(vol, index=panel.index).rolling(window, min_periods=max(5, window // 5)).sum()
    val = num.to_numpy(dtype=np.float64) / np.maximum(den.to_numpy(dtype=np.float64), eps)
    return pd.Series(val, index=panel.index, name=out)


def op_weighted_depth_imb(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 5))
    decay = float(params.get("decay", 0.5))
    out = str(params.get("out", f"weighted_depth_imb_l{levels}"))
    return {out: weighted_depth_imb(panel, levels=levels, decay=decay, out=out)}


def op_liquidity_pressure(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"liquidity_pressure_l{levels}"))
    return {out: liquidity_pressure(panel, levels=levels, out=out)}


def op_ofi_over_depth(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "ofi_over_depth"))
    return {out: ofi_over_depth(panel, out=out)}


def op_book_vwap_offset_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"book_vwap_offset_bp_l{levels}"))
    return {out: book_vwap_offset_bp(panel, levels=levels, out=out)}


def op_relative_spread_depth(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "relative_spread_depth"))
    return {out: relative_spread_depth(panel, out=out)}


def op_trade_vs_depth(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "trade_vs_depth"))
    return {out: trade_vs_depth(panel, out=out)}


def op_kyle_lambda_proxy(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 30))
    out = str(params.get("out", f"kyle_lambda_{window}s"))
    return {out: kyle_lambda_proxy(panel, window=window, out=out)}


BATCH_OPS = {
    "imbalance_levels": op_imbalance_levels,
    "ret_bp": op_ret_bp,
    "log_ret_bp": op_log_ret_bp,
    "realized_vol_bp": op_realized_vol_bp,
    "sum_sq_rv_bp": op_sum_sq_rv_bp,
    "rv_ratio": op_rv_ratio,
    "range_position": op_range_position,
    "microprice_mom": op_microprice_mom,
    "microprice_spread_frac": op_microprice_spread_frac,
    "spread_dev": op_spread_dev,
    "spread_ticks": op_spread_ticks,
    "depth_imb_ticks": op_depth_imb_ticks,
    "depth_imb_bp": op_depth_imb_bp,
    "depth_slope_imb": op_depth_slope_imb,
    "near_depth_imbalance": op_near_depth_imbalance,
    "depth_symmetry": op_depth_symmetry,
    "side_hhi": op_side_hhi,
    "side_outer_share": op_side_outer_share,
    "side_uniformity": op_side_uniformity,
    "side_log_touch_back_ratio": op_side_log_touch_back_ratio,
    "side_touch_share": op_side_touch_share,
    "side_log_notional": op_side_log_notional,
    "log_touch_total_notional": op_log_touch_total_notional,
    "side_width_ticks": op_side_width_ticks,
    "factor_delta": op_factor_delta,
    "half_rv_bp": op_half_rv_bp,
    "signed_semivar": op_signed_semivar,
    "jump_count": op_jump_count,
    "hour_cycle": op_hour_cycle,
    "notional_change_frac": op_notional_change_frac,
    "spread_change_ticks": op_spread_change_ticks,
    "bid_hhi": op_bid_hhi,
    "bid_outer_share": op_bid_outer_share,
    "spread_bp": lambda p, params: {
        str(params.get("out", "spread_bp")): spread_bp(p, out=str(params.get("out", "spread_bp")))
    },
    "microprice_offset_bp": lambda p, params: {
        str(params.get("out", "microprice_offset_bp")): microprice_offset_bp(
            p, out=str(params.get("out", "microprice_offset_bp"))
        )
    },
    "cont_ofi_panel_1s": lambda p, params: {
        str(params.get("out", "cont_ofi_panel_1s")): cont_ofi_panel_1s(
            p, out=str(params.get("out", "cont_ofi_panel_1s"))
        )
    },
    "mid_return_1s": lambda p, params: {
        str(params.get("out", "mid_return_1s")): mid_return_1s(
            p, out=str(params.get("out", "mid_return_1s")), lag=int(params.get("lag", 1))
        )
    },
    "imbalance_l3": lambda p, params: {
        str(params.get("out", "imbalance_l3")): imbalance_l3(p, out=str(params.get("out", "imbalance_l3")))
    },
    "weighted_depth_imb": op_weighted_depth_imb,
    "liquidity_pressure": op_liquidity_pressure,
    "ofi_over_depth": op_ofi_over_depth,
    "book_vwap_offset_bp": op_book_vwap_offset_bp,
    "relative_spread_depth": op_relative_spread_depth,
    "trade_vs_depth": op_trade_vs_depth,
    "kyle_lambda_proxy": op_kyle_lambda_proxy,
}
