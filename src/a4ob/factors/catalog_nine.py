"""Panel ports of cryptocurrency_quant '已有九特征' (FACTOR_CATALOG / feature_cache).

Source of truth (formulas):
  - doc: cryptocurrency_quant/app/backtesting/research/FACTOR_CATALOG.md
  - code: cryptocurrency_quant/app/backtesting/feature_cache.py
          (FeatureStore.lookup: spread_bp, l1_imbalance, microprice_offset_bp;
           add_ofi Cont-style L1 change)

Notes
-----
- ``spread_bp`` / ``microprice_offset_bp`` match the catalog at the panel clock.
- ``cont_ofi_panel_1s`` applies the same Cont L1 *change* formula as ``add_ofi``
  between consecutive 1s panel BBO states, then uses that 1-step change as the
  factor (panel approximation of event-level OFI prefix-diff over 1s). It is
  **not** bit-identical to event-stream OFI in feature_cache.
- Trade-window factors (buy_qty, sell_qty, signed_notional) and book_age_ms are
  not available on the L1 panel alone.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def spread_bp(panel: pd.DataFrame, *, out: str = "spread_bp") -> pd.Series:
    """(ask − bid) / mid × 10000."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    spread = panel["spread"].to_numpy(dtype=np.float64)
    # Prefer best_ask/best_bid if spread missing
    if not np.isfinite(spread).any():
        spread = panel["best_ask"].to_numpy(dtype=np.float64) - panel["best_bid"].to_numpy(
            dtype=np.float64
        )
    val = np.divide(
        spread, mid, out=np.full_like(mid, np.nan), where=np.isfinite(mid) & (mid != 0)
    ) * 10000.0
    return pd.Series(val, index=panel.index, name=out)


def microprice_offset_bp(panel: pd.DataFrame, *, out: str = "microprice_offset_bp") -> pd.Series:
    """((bid*ask_sz + ask*bid_sz)/(bid_sz+ask_sz) − mid) / mid × 10000."""
    bid = panel["best_bid"].to_numpy(dtype=np.float64)
    ask = panel["best_ask"].to_numpy(dtype=np.float64)
    bq = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    aq = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    mid = panel["mid"].to_numpy(dtype=np.float64)
    denom = bq + aq
    micro = np.divide(
        bid * aq + ask * bq, denom, out=np.full_like(denom, np.nan), where=denom > 0
    )
    val = np.divide(
        micro - mid, mid, out=np.full_like(mid, np.nan), where=np.isfinite(mid) & (mid != 0)
    ) * 10000.0
    return pd.Series(val, index=panel.index, name=out)


def mid_return_1s(panel: pd.DataFrame, *, out: str = "mid_return_1s", lag: int = 1) -> pd.Series:
    """m(t)/m(t−L) − 1 on the panel clock (catalog mid_return, L=1s → lag=1)."""
    mid = panel["mid"].to_numpy(dtype=np.float64)
    past = np.roll(mid, lag)
    past[:lag] = np.nan
    val = np.divide(
        mid, past, out=np.full_like(mid, np.nan), where=np.isfinite(past) & (past != 0)
    ) - 1.0
    return pd.Series(val, index=panel.index, name=out)


def cont_ofi_panel_1s(panel: pd.DataFrame, *, out: str = "cont_ofi_panel_1s") -> pd.Series:
    """
    Cont L1 OFI change between consecutive panel rows (feature_cache.add_ofi).

    change = I(b≥b′)B − I(b≤b′)B′ − I(a≤a′)A + I(a≥a′)A′
    """
    b = panel["best_bid"].to_numpy(dtype=np.float64)
    a = panel["best_ask"].to_numpy(dtype=np.float64)
    B = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    A = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    n = len(panel)
    out_arr = np.full(n, np.nan, dtype=np.float64)
    if n < 2:
        return pd.Series(out_arr, index=panel.index, name=out)

    b0, a0, B0, A0 = b[:-1], a[:-1], B[:-1], A[:-1]
    b1, a1, B1, A1 = b[1:], a[1:], B[1:], A[1:]
    valid = (
        np.isfinite(b0)
        & np.isfinite(a0)
        & np.isfinite(b1)
        & np.isfinite(a1)
        & np.isfinite(B0)
        & np.isfinite(A0)
        & np.isfinite(B1)
        & np.isfinite(A1)
    )
    if "ts_ms" in panel.columns:
        ts = panel["ts_ms"].to_numpy(dtype=np.int64)
        dt = ts[1:] - ts[:-1]
        valid &= (dt > 0) & (dt <= 2000)

    change = (
        (b1 >= b0).astype(np.float64) * B1
        - (b1 <= b0).astype(np.float64) * B0
        - (a1 <= a0).astype(np.float64) * A1
        + (a1 >= a0).astype(np.float64) * A0
    )
    out_arr[1:] = np.where(valid, change, np.nan)
    return pd.Series(out_arr, index=panel.index, name=out)


def imbalance_l3(panel: pd.DataFrame, *, out: str = "imbalance_l3") -> pd.Series:
    """
    Depth imbalance over top-3 levels (factor_library/microstructure.py shape).

    (Σ bid_sz_0..2 − Σ ask_sz_0..2) / (Σ bid + Σ ask)
    """
    bid = np.zeros(len(panel), dtype=np.float64)
    ask = np.zeros(len(panel), dtype=np.float64)
    for i in range(3):
        bid += panel[f"bid_sz_{i}"].to_numpy(dtype=np.float64)
        ask += panel[f"ask_sz_{i}"].to_numpy(dtype=np.float64)
    denom = bid + ask
    val = np.divide(bid - ask, denom, out=np.full_like(denom, np.nan), where=denom > 0)
    return pd.Series(val, index=panel.index, name=out)


# ---- Spec ops wrappers ------------------------------------------------------

def op_spread_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "spread_bp"))
    return {out: spread_bp(panel, out=out)}


def op_microprice_offset_bp(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "microprice_offset_bp"))
    return {out: microprice_offset_bp(panel, out=out)}


def op_mid_return_1s(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "mid_return_1s"))
    lag = int(params.get("lag", 1))
    return {out: mid_return_1s(panel, out=out, lag=lag)}


def op_cont_ofi_panel_1s(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "cont_ofi_panel_1s"))
    return {out: cont_ofi_panel_1s(panel, out=out)}


def op_imbalance_l3(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "imbalance_l3"))
    return {out: imbalance_l3(panel, out=out)}
