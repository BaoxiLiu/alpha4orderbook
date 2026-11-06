"""圣堂雪 (stx) factor ports — panel-computable adaptations only.

Source MD: ~/Downloads/清单_圣堂雪因子.md
Only formulas that map to 1s top-K book + trades_features are implemented.
A-share session / chip / graph / FF3 factors are intentionally omitted.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _mid_ret(panel: pd.DataFrame) -> np.ndarray:
    mid = panel["mid"].to_numpy(dtype=np.float64)
    prev = np.roll(mid, 1)
    prev[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (mid - prev) / prev
    r[~np.isfinite(r)] = np.nan
    return r


def _amount(panel: pd.DataFrame) -> np.ndarray:
    """1s notional from trades enrich; no-trade seconds → 0 (not NaN) for rolling stats."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    if "nh_log_amount1" in panel.columns:
        a = np.expm1(panel["nh_log_amount1"].to_numpy(dtype=np.float64))
        return np.where(np.isfinite(a), np.maximum(a, 0.0), 0.0)
    if "nh_vol_1s" in panel.columns:
        vol = panel["nh_vol_1s"].to_numpy(dtype=np.float64)
        amt = np.where(np.isfinite(vol), vol, 0.0) * mid
        amt[~np.isfinite(amt)] = 0.0
        return np.maximum(amt, 0.0)
    bb = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    ba = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    return (bb + ba) * mid


def _mean_amt(panel: pd.DataFrame) -> np.ndarray:
    """Per-second mean trade notional; forward-fill short gaps so Δ is defined."""
    if "nh_log_mean_amount_1s" in panel.columns:
        a = np.expm1(panel["nh_log_mean_amount_1s"].to_numpy(dtype=np.float64))
        s = pd.Series(np.where(np.isfinite(a), np.maximum(a, 0.0), np.nan))
        s = s.ffill(limit=60)
        return s.to_numpy(dtype=np.float64)
    amt = _amount(panel)
    if "nh_log_count1" in panel.columns:
        cnt = np.expm1(panel["nh_log_count1"].to_numpy(dtype=np.float64))
        cnt = np.where(np.isfinite(cnt), np.maximum(cnt, 1.0), np.nan)
        with np.errstate(divide="ignore", invalid="ignore"):
            m = amt / cnt
        s = pd.Series(m).ffill(limit=60)
        return s.to_numpy(dtype=np.float64)
    return amt


def stx_mpc(panel: pd.DataFrame, *, lag: int, out: str) -> pd.Series:
    """#22 MPC: mid change rate over k seconds."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    prev = np.roll(mid, lag)
    prev[:lag] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        val = (mid - prev) / prev
    val[~np.isfinite(val)] = np.nan
    return pd.Series(val, index=panel.index, name=out)


def stx_mlqs(panel: pd.DataFrame, *, levels: int, out: str, eps: float = 1e-12) -> pd.Series:
    """#31 MLQS: depth-weighted LogQuoteSlope over levels 1..L with w_i=i/L."""
    n = len(panel)
    acc = np.zeros(n, dtype=np.float64)
    wsum = 0.0
    L = max(1, levels)
    for i in range(L):
        bp = f"bid_px_{i}"
        ap = f"ask_px_{i}"
        bs = f"bid_sz_{i}"
        a_s = f"ask_sz_{i}"
        if bp not in panel.columns:
            break
        pa = panel[ap].to_numpy(dtype=np.float64)
        pb = panel[bp].to_numpy(dtype=np.float64)
        va = panel[a_s].to_numpy(dtype=np.float64)
        vb = panel[bs].to_numpy(dtype=np.float64)
        with np.errstate(divide="ignore", invalid="ignore"):
            slope = (np.log(np.maximum(pa, eps)) - np.log(np.maximum(pb, eps))) / (
                np.log(np.maximum(va, eps)) + np.log(np.maximum(vb, eps))
            )
        slope[~np.isfinite(slope)] = np.nan
        w = (i + 1) / L
        acc = np.where(np.isfinite(slope), acc + w * slope, acc)
        wsum += w
    val = acc / max(wsum, eps)
    return pd.Series(val, index=panel.index, name=out)


def stx_max_dd(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    """#23 intraday max drawdown on mid path over rolling window; in (-1, 0]."""
    mid = pd.Series(panel["mid"].to_numpy(dtype=np.float64), index=panel.index)
    roll_max = mid.rolling(window, min_periods=max(5, window // 5)).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = mid / roll_max - 1.0
    dd = dd.clip(upper=0.0)
    dd.name = out
    return dd


def stx_rtv(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    """#25 RTV proxy: rolling tripower |r|^{2/3} product mean × μ_{2/3}^{-3}."""
    r = _mid_ret(panel)
    abs_r = np.abs(r)
    # μ_p = E[|Z|^p] for Z~N(0,1); μ_{2/3} ≈ 0.830860...
    mu = 0.830860595
    a = pd.Series(np.power(abs_r, 2.0 / 3.0), index=panel.index)
    # tripower needs three consecutive; use product of lags 0,1,2
    prod = a * a.shift(1) * a.shift(2)
    roll = prod.rolling(window, min_periods=max(5, window // 5)).mean()
    val = roll.to_numpy(dtype=np.float64) * (mu ** -3)
    return pd.Series(val, index=panel.index, name=out)


def stx_cora_r(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    """#34 CORA_R: rolling corr(|Ret_{t-1}|, Amount_t)."""
    r = pd.Series(_mid_ret(panel), index=panel.index)
    amt = pd.Series(_amount(panel), index=panel.index)
    x = r.abs().shift(1)
    val = x.rolling(window, min_periods=max(10, window // 5)).corr(amt)
    val.name = out
    return val


def stx_adj_cora_a(panel: pd.DataFrame, *, window: int, z_window: int, out: str) -> pd.Series:
    """#5 adj_CORA_A: corr(|Ret_t|, zscored Amount_{t-1}).

    MD excludes zero-ret minutes; on sparse 1s crypto mid that drops coverage to ~0,
    so we keep zeros (dilution) rather than NaN-mask.
    """
    r = pd.Series(_mid_ret(panel), index=panel.index)
    amt = pd.Series(_amount(panel), index=panel.index)
    mu = amt.rolling(z_window, min_periods=max(10, z_window // 5)).mean()
    sd = amt.rolling(z_window, min_periods=max(10, z_window // 5)).std()
    adj = (amt - mu) / sd.replace(0.0, np.nan)
    x = r.abs()
    y = adj.shift(1)
    val = x.rolling(window, min_periods=max(10, window // 5)).corr(y)
    val.name = out
    return val


def stx_mte(panel: pd.DataFrame, *, window: int, out: str) -> pd.Series:
    """#26 MTE proxy: rolling Pearson(amount, mid) as TE (rank-corr needs denser tape)."""
    amt = pd.Series(_amount(panel), index=panel.index)
    mid = pd.Series(panel["mid"].to_numpy(dtype=np.float64), index=panel.index)
    val = amt.rolling(window, min_periods=max(10, window // 5)).corr(mid)
    val.name = out
    return val


def stx_tcv(panel: pd.DataFrame, *, bar: int, window: int, alpha: float, out: str) -> pd.Series:
    """#19 TCV: share of volume in 'consistent' bars (|c-o| <= α|h-l|), rolled."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    amt = _amount(panel)
    n = len(panel)
    # rolling OHLC over `bar` seconds ending at t
    s_mid = pd.Series(mid)
    o = s_mid.shift(bar - 1)
    h = s_mid.rolling(bar, min_periods=max(2, bar // 3)).max()
    lo = s_mid.rolling(bar, min_periods=max(2, bar // 3)).min()
    c = s_mid
    rng = (h - lo).to_numpy(dtype=np.float64)
    body = np.abs(c.to_numpy(dtype=np.float64) - o.to_numpy(dtype=np.float64))
    consistent = body <= (alpha * np.maximum(rng, 0.0))
    consistent[~np.isfinite(body) | ~np.isfinite(rng)] = False
    vol = pd.Series(np.where(np.isfinite(amt), amt, 0.0), index=panel.index)
    cons_vol = vol.where(consistent, 0.0)
    num = cons_vol.rolling(window, min_periods=max(5, window // 5)).sum()
    den = vol.rolling(window, min_periods=max(5, window // 5)).sum()
    val = num / den.replace(0.0, np.nan)
    val.name = out
    return val


def _vol_regimes(amt: np.ndarray, lookback: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return boolean masks: peak, ridge, valley (1s adaptation of 峰/岭/谷)."""
    s = pd.Series(amt)
    mu = s.rolling(lookback, min_periods=max(10, lookback // 5)).mean()
    sd = s.rolling(lookback, min_periods=max(10, lookback // 5)).std()
    erupt = (s > (mu + sd)).fillna(False).to_numpy(dtype=bool)
    calm = (s < (mu + sd)).fillna(False).to_numpy(dtype=bool) & ~erupt
    n = len(amt)
    peak = np.zeros(n, dtype=bool)
    ridge = np.zeros(n, dtype=bool)
    valley = calm.copy()
    for i in range(1, n - 1):
        if not erupt[i]:
            continue
        if calm[i - 1] and calm[i + 1]:
            peak[i] = True
        elif erupt[i - 1] or erupt[i + 1]:
            ridge[i] = True
        else:
            peak[i] = True
    return peak, ridge, valley


def stx_vol_peak_count(panel: pd.DataFrame, *, lookback: int, out: str) -> pd.Series:
    """#8 / #11 family: rolling count of volume peaks (erupt + calm neighbors)."""
    amt = _amount(panel)
    peak, _, _ = _vol_regimes(amt, lookback)
    cnt = pd.Series(peak.astype(np.float64), index=panel.index).rolling(
        lookback, min_periods=max(10, lookback // 5)
    ).sum()
    cnt.name = out
    return cnt


def stx_vol_ridge_ret(panel: pd.DataFrame, *, lookback: int, out: str) -> pd.Series:
    """#45: rolling sum of mid returns on volume-ridge bars."""
    amt = _amount(panel)
    r = _mid_ret(panel)
    _, ridge, _ = _vol_regimes(amt, lookback)
    rr = np.where(ridge & np.isfinite(r), r, 0.0)
    val = pd.Series(rr, index=panel.index).rolling(lookback, min_periods=max(10, lookback // 5)).sum()
    val.name = out
    return val


def stx_vol_valley_rel_vwap(panel: pd.DataFrame, *, lookback: int, out: str, eps: float = 1e-12) -> pd.Series:
    """#17: valley VWAP / full-window VWAP over lookback."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    amt = _amount(panel)
    _, _, valley = _vol_regimes(amt, lookback)
    a = np.where(np.isfinite(amt), np.maximum(amt, 0.0), 0.0)
    px_a = mid * a
    valley_a = np.where(valley, a, 0.0)
    valley_px = np.where(valley, px_a, 0.0)
    s_a = pd.Series(a, index=panel.index)
    s_px = pd.Series(px_a, index=panel.index)
    s_va = pd.Series(valley_a, index=panel.index)
    s_vpx = pd.Series(valley_px, index=panel.index)
    full_vwap = s_px.rolling(lookback, min_periods=max(10, lookback // 5)).sum() / s_a.rolling(
        lookback, min_periods=max(10, lookback // 5)
    ).sum().replace(0.0, np.nan)
    val_vwap = s_vpx.rolling(lookback, min_periods=max(10, lookback // 5)).sum() / s_va.rolling(
        lookback, min_periods=max(10, lookback // 5)
    ).sum().replace(0.0, np.nan)
    val = val_vwap / full_vwap.replace(0.0, np.nan)
    val.name = out
    return val


def stx_mean_amt_diff_mad(panel: pd.DataFrame, *, lookback: int, out: str, eps: float = 1e-12) -> pd.Series:
    """#37: mean |Δ mean-trade-amount| / mean, rolled."""
    m = pd.Series(_mean_amt(panel), index=panel.index)
    d = m.diff().abs()
    rel = d / m.replace(0.0, np.nan).abs().clip(lower=eps)
    val = rel.rolling(lookback, min_periods=max(10, lookback // 5)).mean()
    val.name = out
    return val


def _jump_mask(r: np.ndarray, lookback: int, mult: float = 4.0) -> np.ndarray:
    abs_r = pd.Series(np.abs(r))
    med = abs_r.rolling(lookback, min_periods=max(10, lookback // 5)).median()
    return (abs_r > (mult * med)).fillna(False).to_numpy(dtype=bool)


def stx_pos_jump_ret(panel: pd.DataFrame, *, lookback: int, out: str) -> pd.Series:
    """#14 proxy: rolling sum of positive jump mid-returns."""
    r = _mid_ret(panel)
    jumps = _jump_mask(r, lookback)
    pos = np.where(jumps & np.isfinite(r) & (r > 0), r, 0.0)
    val = pd.Series(pos, index=panel.index).rolling(lookback, min_periods=max(10, lookback // 5)).sum()
    val.name = out
    return val


def stx_jar_abs(panel: pd.DataFrame, *, lookback: int, out: str) -> pd.Series:
    """#13 JAR proxy: exp(sum log1p(|jump ret|)) over lookback — cumulative abs jump shock."""
    r = _mid_ret(panel)
    jumps = _jump_mask(r, lookback)
    shock = np.where(jumps & np.isfinite(r), np.log1p(np.abs(r)), 0.0)
    s = pd.Series(shock, index=panel.index).rolling(lookback, min_periods=max(10, lookback // 5)).sum()
    val = np.exp(s.to_numpy(dtype=np.float64)) - 1.0
    return pd.Series(val, index=panel.index, name=out)


def stx_amp_cut(panel: pd.DataFrame, *, lookback: int, bar: int, lam: float, out: str) -> pd.Series:
    """#42 amplitude cut: high-λ minus low-λ mean bar amplitude, z-scored in lookback."""
    mid = pd.Series(panel["mid"].to_numpy(dtype=np.float64), index=panel.index)
    hi = mid.rolling(bar, min_periods=max(2, bar // 3)).max()
    lo = mid.rolling(bar, min_periods=max(2, bar // 3)).min()
    amp = ((hi - lo) / mid.replace(0.0, np.nan)).abs()
    # within lookback, mean of top-λ vs bottom-λ amplitudes via expanding quantiles approx
    q_hi = amp.rolling(lookback, min_periods=max(10, lookback // 5)).quantile(lam)
    q_lo = amp.rolling(lookback, min_periods=max(10, lookback // 5)).quantile(1.0 - lam)
    high_part = amp.where(amp >= q_hi)
    low_part = amp.where(amp <= q_lo)
    v_high = high_part.rolling(lookback, min_periods=max(5, lookback // 10)).mean()
    v_low = low_part.rolling(lookback, min_periods=max(5, lookback // 10)).mean()
    raw = v_high - v_low
    mu = raw.rolling(lookback, min_periods=max(10, lookback // 5)).mean()
    sd = raw.rolling(lookback, min_periods=max(10, lookback // 5)).std()
    val = (raw - mu) / sd.replace(0.0, np.nan)
    val.name = out
    return val


def stx_t_active_share(panel: pd.DataFrame, *, window: int, df: float, out: str) -> pd.Series:
    """#29 proxy: Amount × Student-t density(ret/σ) share within rolling window."""
    r = pd.Series(_mid_ret(panel), index=panel.index)
    amt = pd.Series(_amount(panel), index=panel.index).clip(lower=0.0)
    sig = r.rolling(window, min_periods=max(10, window // 5)).std()
    z = r / sig.replace(0.0, np.nan)
    # t pdf kernel (unnormalized ok for share)
    # c * (1 + z^2/df)^(-(df+1)/2)
    dens = (1.0 + (z * z) / df) ** (-0.5 * (df + 1.0))
    w = amt * dens
    num = w.rolling(window, min_periods=max(10, window // 5)).sum()
    den = amt.rolling(window, min_periods=max(10, window // 5)).sum()
    val = num / den.replace(0.0, np.nan)
    val.name = out
    return val


# ---- op wrappers -------------------------------------------------------------

def op_stx_mpc(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lag = int(params.get("lag", 1))
    out = str(params.get("out", f"stx_mpc_{lag}s"))
    return {out: stx_mpc(panel, lag=lag, out=out)}


def op_stx_mlqs(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 5))
    out = str(params.get("out", f"stx_mlqs_l{levels}"))
    return {out: stx_mlqs(panel, levels=levels, out=out)}


def op_stx_max_dd(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 300))
    out = str(params.get("out", f"stx_max_dd_{window}s"))
    return {out: stx_max_dd(panel, window=window, out=out)}


def op_stx_rtv(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 60))
    out = str(params.get("out", f"stx_rtv_{window}s"))
    return {out: stx_rtv(panel, window=window, out=out)}


def op_stx_cora_r(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 120))
    out = str(params.get("out", f"stx_cora_r_{window}s"))
    return {out: stx_cora_r(panel, window=window, out=out)}


def op_stx_adj_cora_a(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 120))
    z_window = int(params.get("z_window", 1200))
    out = str(params.get("out", f"stx_adj_cora_a_{window}s"))
    return {out: stx_adj_cora_a(panel, window=window, z_window=z_window, out=out)}


def op_stx_mte(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 1200))
    out = str(params.get("out", f"stx_mte_{window}s"))
    return {out: stx_mte(panel, window=window, out=out)}


def op_stx_tcv(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    bar = int(params.get("bar", 60))
    window = int(params.get("window", 1200))
    alpha = float(params.get("alpha", 0.3))
    out = str(params.get("out", f"stx_tcv_{window}s"))
    return {out: stx_tcv(panel, bar=bar, window=window, alpha=alpha, out=out)}


def op_stx_vol_peak_count(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lookback = int(params.get("lookback", 1200))
    out = str(params.get("out", f"stx_vol_peak_count_{lookback}s"))
    return {out: stx_vol_peak_count(panel, lookback=lookback, out=out)}


def op_stx_vol_ridge_ret(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lookback = int(params.get("lookback", 1200))
    out = str(params.get("out", f"stx_vol_ridge_ret_{lookback}s"))
    return {out: stx_vol_ridge_ret(panel, lookback=lookback, out=out)}


def op_stx_vol_valley_rel_vwap(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lookback = int(params.get("lookback", 1200))
    out = str(params.get("out", f"stx_vol_valley_rel_vwap_{lookback}s"))
    return {out: stx_vol_valley_rel_vwap(panel, lookback=lookback, out=out)}


def op_stx_mean_amt_diff_mad(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lookback = int(params.get("lookback", 1200))
    out = str(params.get("out", f"stx_mean_amt_diff_mad_{lookback}s"))
    return {out: stx_mean_amt_diff_mad(panel, lookback=lookback, out=out)}


def op_stx_pos_jump_ret(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lookback = int(params.get("lookback", 1200))
    out = str(params.get("out", f"stx_pos_jump_ret_{lookback}s"))
    return {out: stx_pos_jump_ret(panel, lookback=lookback, out=out)}


def op_stx_jar_abs(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lookback = int(params.get("lookback", 1200))
    out = str(params.get("out", f"stx_jar_abs_{lookback}s"))
    return {out: stx_jar_abs(panel, lookback=lookback, out=out)}


def op_stx_amp_cut(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    lookback = int(params.get("lookback", 600))
    bar = int(params.get("bar", 60))
    lam = float(params.get("lam", 0.8))
    out = str(params.get("out", f"stx_amp_cut_{lookback}s"))
    return {out: stx_amp_cut(panel, lookback=lookback, bar=bar, lam=lam, out=out)}


def op_stx_t_active_share(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    window = int(params.get("window", 60))
    df = float(params.get("df", 5.0))
    out = str(params.get("out", f"stx_t_active_share_{window}s"))
    return {out: stx_t_active_share(panel, window=window, df=df, out=out)}


STX_OPS = {
    "stx_mpc": op_stx_mpc,
    "stx_mlqs": op_stx_mlqs,
    "stx_max_dd": op_stx_max_dd,
    "stx_rtv": op_stx_rtv,
    "stx_cora_r": op_stx_cora_r,
    "stx_adj_cora_a": op_stx_adj_cora_a,
    "stx_mte": op_stx_mte,
    "stx_tcv": op_stx_tcv,
    "stx_vol_peak_count": op_stx_vol_peak_count,
    "stx_vol_ridge_ret": op_stx_vol_ridge_ret,
    "stx_vol_valley_rel_vwap": op_stx_vol_valley_rel_vwap,
    "stx_mean_amt_diff_mad": op_stx_mean_amt_diff_mad,
    "stx_pos_jump_ret": op_stx_pos_jump_ret,
    "stx_jar_abs": op_stx_jar_abs,
    "stx_amp_cut": op_stx_amp_cut,
    "stx_t_active_share": op_stx_t_active_share,
}
