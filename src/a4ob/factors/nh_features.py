"""NH market-make 23 alpha + 28 value features on a4ob 1s panels + trades.

Ports formulas from ``Cryptocurrency_quant-marketmake_nh/crypto_mm/{features,value_features}.py``
onto the existing day panel clock (no book rebuild).

Value features that need a private quote use a **bid-touch probe**:
side=+1, px=best_bid, qty=queue=best_bid_sz (documented approximation for Universe IC).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..config import default_config_path, load_config
from ..data.paths import resolve_data_root
from ..data.trades import load_trades_day, trades_to_1s_bars
from ..panel.day import default_panels_root, panel_day_dir

# Alpha NAMES (23) — same order as NH features.py
NH_ALPHA_NAMES = (
    ["nh_book_offset_bp", "nh_ofi_original_tanh", "nh_ti_1s"]
    + [
        f"nh_{n}_{w}s"
        for w in (1, 5)
        for n in (
            "count_imb",
            "amount_imb",
            "volume_imb",
            "mean_last_momentum",
            "vwap_side_imb_bp",
            "log_mean_amount",
            "log_count_rate",
            "price_cv_bp",
            "trade_rv_bp",
            "posret_fraction",
        )
    ]
)

# Value NAMES (28)
NH_VALUE_NAMES = [
    "nh_signed_book_offset",
    "nh_signed_ofi_tanh",
    "nh_signed_ti",
    "nh_signed_count1",
    "nh_signed_amount1",
    "nh_signed_volume1",
    "nh_signed_momentum1",
    "nh_signed_vwap1",
    "nh_signed_count5",
    "nh_signed_amount5",
    "nh_signed_volume5",
    "nh_signed_momentum5",
    "nh_signed_vwap5",
    "nh_log_count1",
    "nh_log_amount1",
    "nh_rv1",
    "nh_log_count5",
    "nh_log_amount5",
    "nh_rv5",
    "nh_vol_1s",
    "nh_spread_bp",
    "nh_tick_bp",
    "nh_distance_bp",
    "nh_log_queue_notional",
    "nh_log_order_notional",
    "nh_distance_tick",
    "nh_distance_tick_sq",
    "nh_signed_ti_x_distance",
]

MOMENTUM_SCALE = 0.000169129652112
EPS = 1e-12


def _rolling_sum(x: np.ndarray, window: int) -> np.ndarray:
    s = pd.Series(x)
    return s.rolling(window, min_periods=1).sum().to_numpy(dtype=np.float64)


def _window_features(bars: dict[str, np.ndarray], window: int) -> np.ndarray:
    """NH window_values for one window length (seconds) → (n, 10)."""
    n = len(bars["n_buy"])
    out = np.full((n, 10), np.nan, dtype=np.float64)
    nb = _rolling_sum(bars["n_buy"], window)
    ns = _rolling_sum(bars["n_sell"], window)
    ab = _rolling_sum(bars["amt_buy"], window)
    ass = _rolling_sum(bars["amt_sell"], window)
    vb = _rolling_sum(bars["vol_buy"], window)
    vs = _rolling_sum(bars["vol_sell"], window)
    sum_rel = _rolling_sum(bars["sum_rel"], window)
    sum_rel2 = _rolling_sum(bars["sum_rel2"], window)
    sum_lr2 = _rolling_sum(bars["sum_lr2"], window)
    n_up = _rolling_sum(bars["n_up"], window)
    count = nb + ns
    # last price: use current bar's last_px (NH uses last trade in ring)
    last = bars["last_px"]
    first_px = bars["first_px"]

    for i in range(n):
        c = count[i]
        if not (c > 0):
            continue
        out[i, 0] = (nb[i] - ns[i]) / c
        amount = ab[i] + ass[i]
        volume = vb[i] + vs[i]
        if amount > 0:
            out[i, 1] = (ab[i] - ass[i]) / amount
        if volume > 0:
            out[i, 2] = (vb[i] - vs[i]) / volume
        mean_rel = sum_rel[i] / c
        fp = first_px[i]
        mean = fp * (1.0 + mean_rel) if np.isfinite(fp) else np.nan
        last_i = last[i]
        if np.isfinite(mean) and np.isfinite(last_i) and last_i != 0:
            out[i, 3] = -math.asinh((mean / last_i - 1.0) / MOMENTUM_SCALE)
        if nb[i] > 0 and ns[i] > 0 and vb[i] > 0 and vs[i] > 0:
            bp = ab[i] / vb[i]
            sp = ass[i] / vs[i]
            out[i, 4] = (bp - sp) / (bp + sp) * 1e4
        out[i, 5] = math.log1p(amount / c)
        out[i, 6] = math.log1p(c / float(window))
        if c > 1:
            variance = max(0.0, (sum_rel2[i] - c * mean_rel * mean_rel) / (c - 1.0))
            out[i, 7] = math.sqrt(variance) / (1.0 + mean_rel) * 1e4
            out[i, 8] = math.sqrt(max(0.0, sum_lr2[i])) * 1e4
        out[i, 9] = max(0.0, min(1.0, n_up[i] / c))
    return out


def _book_offset_bp(panel: pd.DataFrame) -> np.ndarray:
    bid = panel["best_bid"].to_numpy(dtype=np.float64)
    ask = panel["best_ask"].to_numpy(dtype=np.float64)
    bq = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    aq = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    mid = panel["mid"].to_numpy(dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 0.5 * (ask - bid) / mid * 1e4 * (bq - aq) / np.maximum(bq + aq, EPS)


def _cont_ofi_tanh(panel: pd.DataFrame) -> np.ndarray:
    """Panel Cont-style OFI with NH tanh + light EMA normalize."""
    bid = panel["best_bid"].to_numpy(dtype=np.float64)
    ask = panel["best_ask"].to_numpy(dtype=np.float64)
    bq = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    aq = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    n = len(panel)
    ofi = np.zeros(n, dtype=np.float64)
    ema = np.zeros(n, dtype=np.float64)
    decay = math.exp(-1.0)  # ~1s step vs NH 100ms*10
    e_ofi = 0.0
    e_ema = 0.0
    old_bid = bid[0]
    old_ask = ask[0]
    old_bq = bq[0]
    old_aq = aq[0]
    for i in range(n):
        if i > 0 and np.isfinite(bid[i]) and np.isfinite(ask[i]):
            e = (bq[i] if bid[i] >= old_bid else 0.0) - (old_bq if bid[i] <= old_bid else 0.0)
            e -= (aq[i] if ask[i] <= old_ask else 0.0) - (old_aq if ask[i] >= old_ask else 0.0)
            e_ofi = e_ofi * decay + e
            e_ema = 0.99 * e_ema + 0.01 * 0.5 * (bq[i] + aq[i])
            old_bid, old_ask, old_bq, old_aq = bid[i], ask[i], bq[i], aq[i]
        ofi[i] = e_ofi
        ema[i] = e_ema
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.tanh(ofi / np.maximum(ema, EPS))


def _ti_1s(bars: dict[str, np.ndarray]) -> np.ndarray:
    """1s taker imbalance from 1s bars (NH uses EMA; 1s bucket is causal approx)."""
    vb = bars["vol_buy"]
    vs = bars["vol_sell"]
    denom = vb + vs
    return np.divide(vb - vs, denom, out=np.full_like(denom, np.nan), where=denom > 0)


def compute_nh_alpha(panel: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    ts = panel["ts_ms"].to_numpy(dtype=np.int64)
    bars = trades_to_1s_bars(trades, ts)
    w1 = _window_features(bars, 1)
    w5 = _window_features(bars, 5)
    cols: dict[str, np.ndarray] = {
        "nh_book_offset_bp": _book_offset_bp(panel),
        "nh_ofi_original_tanh": _cont_ofi_tanh(panel),
        "nh_ti_1s": _ti_1s(bars),
    }
    names_1 = [
        "count_imb",
        "amount_imb",
        "volume_imb",
        "mean_last_momentum",
        "vwap_side_imb_bp",
        "log_mean_amount",
        "log_count_rate",
        "price_cv_bp",
        "trade_rv_bp",
        "posret_fraction",
    ]
    for j, name in enumerate(names_1):
        cols[f"nh_{name}_1s"] = w1[:, j]
        cols[f"nh_{name}_5s"] = w5[:, j]
    return pd.DataFrame(cols, index=panel.index)


def compute_nh_value(
    panel: pd.DataFrame,
    alpha: pd.DataFrame,
    *,
    tick_size: float,
) -> pd.DataFrame:
    """Bid-touch probe value features (side=+1)."""
    side = 1.0
    mid = panel["mid"].to_numpy(dtype=np.float64)
    bid = panel["best_bid"].to_numpy(dtype=np.float64)
    ask = panel["best_ask"].to_numpy(dtype=np.float64)
    bq = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    tick = float(tick_size) if tick_size > 0 else np.nan
    px = bid  # touch
    qty = bq
    queue = bq
    # vol_1s ≈ trade RV 1s from alpha
    vol = alpha["nh_trade_rv_bp_1s"].to_numpy(dtype=np.float64)

    # alpha vector indices used by NH action_features
    x = np.column_stack(
        [
            alpha["nh_book_offset_bp"],
            alpha["nh_ofi_original_tanh"],
            alpha["nh_ti_1s"],
            alpha["nh_count_imb_1s"],
            alpha["nh_amount_imb_1s"],
            alpha["nh_volume_imb_1s"],
            alpha["nh_mean_last_momentum_1s"],
            alpha["nh_vwap_side_imb_bp_1s"],
            alpha["nh_log_mean_amount_1s"],  # 8
            alpha["nh_log_count_rate_1s"],  # 9
            alpha["nh_price_cv_bp_1s"],
            alpha["nh_trade_rv_bp_1s"],  # 11
            alpha["nh_posret_fraction_1s"],
            alpha["nh_count_imb_5s"],
            alpha["nh_amount_imb_5s"],
            alpha["nh_volume_imb_5s"],
            alpha["nh_mean_last_momentum_5s"],
            alpha["nh_vwap_side_imb_bp_5s"],
            alpha["nh_log_mean_amount_5s"],  # 18
            alpha["nh_log_count_rate_5s"],  # 19
            alpha["nh_price_cv_bp_5s"],
            alpha["nh_trade_rv_bp_5s"],  # 21
            alpha["nh_posret_fraction_5s"],
        ]
    )
    # signed indices (0,1,2,3,4,5,6,7,13,14,15,16,17) * side
    signed_idx = (0, 1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17)
    signed = side * x[:, list(signed_idx)]
    z = np.empty((len(panel), 28), dtype=np.float64)
    z[:, :13] = signed
    z[:, 13] = x[:, 9]  # log_count1
    z[:, 14] = x[:, 8]  # log_amount1
    z[:, 15] = x[:, 11]  # rv1
    z[:, 16] = x[:, 19]  # log_count5
    z[:, 17] = x[:, 18]  # log_amount5
    z[:, 18] = x[:, 21]  # rv5
    z[:, 19] = vol
    with np.errstate(divide="ignore", invalid="ignore"):
        z[:, 20] = (ask - bid) / mid * 1e4
        z[:, 21] = tick / mid * 1e4
        z[:, 22] = side * (mid - px) / mid * 1e4
    z[:, 23] = np.log1p(np.maximum(0.0, queue * px))
    z[:, 24] = np.log1p(np.maximum(0.0, qty * px))
    with np.errstate(divide="ignore", invalid="ignore"):
        distance = (bid - px) / tick  # side>0
    z[:, 25] = distance
    z[:, 26] = distance * distance
    z[:, 27] = side * x[:, 2] * distance
    return pd.DataFrame({name: z[:, j] for j, name in enumerate(NH_VALUE_NAMES)}, index=panel.index)


def compute_nh_all(
    panel: pd.DataFrame,
    trades: pd.DataFrame,
    *,
    tick_size: float,
) -> pd.DataFrame:
    alpha = compute_nh_alpha(panel, trades)
    value = compute_nh_value(panel, alpha, tick_size=tick_size)
    return pd.concat([alpha, value], axis=1)


def enrich_day_trades_features(
    *,
    symbol: str,
    date: str,
    panels_root: str | Path | None = None,
    data_root: str | Path | None = None,
    config_path: str | Path | None = None,
    tick_size: float | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Write ``trades_features.parquet`` beside the existing day panel (no book rebuild)."""
    cfg = load_config(Path(config_path) if config_path else default_config_path())
    root = resolve_data_root(data_root or cfg["data"]["root"])
    dt_s = int(cfg["panel"]["dt_seconds"])
    top_k = int(cfg["panel"]["top_k"])
    out_root = Path(panels_root) if panels_root else default_panels_root()
    pdir = panel_day_dir(out_root, symbol=symbol, date=date, dt_seconds=dt_s, top_k=top_k)
    panel_path = pdir / "panel.parquet"
    out_path = pdir / "trades_features.parquet"
    if out_path.is_file() and not force:
        return {"status": "exists", "path": str(out_path), "symbol": symbol, "date": date}
    if not panel_path.is_file():
        return {"status": "missing_panel", "path": str(panel_path), "symbol": symbol, "date": date}

    panel = pd.read_parquet(panel_path)
    trades = load_trades_day(root, symbol, date)
    if tick_size is None:
        try:
            from ..library.score import load_scoring

            tick_map = load_scoring().get("tick_size_usdc") or {}
        except Exception:  # noqa: BLE001
            tick_map = {"BTCUSDC": 0.1, "ETHUSDC": 0.01, "SOLUSDC": 0.001, "default": 0.01}
        tick_size = float(tick_map.get(symbol, tick_map.get("default", 0.01)))

    feats = compute_nh_all(panel, trades, tick_size=float(tick_size))
    feats.insert(0, "ts_ms", panel["ts_ms"].to_numpy())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    feats.to_parquet(out_path, index=False)
    return {
        "status": "ok",
        "path": str(out_path),
        "symbol": symbol,
        "date": date,
        "n_rows": int(len(feats)),
        "n_trades": int(len(trades)),
        "n_cols": int(feats.shape[1]),
        "tick_size": float(tick_size),
    }


def join_trades_features(panel: pd.DataFrame, trades_features_path: Path) -> pd.DataFrame:
    feats = pd.read_parquet(trades_features_path)
    if "ts_ms" not in feats.columns:
        raise ValueError(f"{trades_features_path}: missing ts_ms")
    cols = [c for c in feats.columns if c != "ts_ms"]
    merged = panel.merge(feats[["ts_ms", *cols]], on="ts_ms", how="left", suffixes=("", "_tr"))
    return merged
