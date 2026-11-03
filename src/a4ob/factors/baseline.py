"""Baseline panel factors (formulas, not live book replay)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def imbalance(panel: pd.DataFrame, *, levels: int = 1, prefix: str = "imb") -> pd.Series:
    """
    Size imbalance over top ``levels``:

        (sum bid_sz - sum ask_sz) / (sum bid_sz + sum ask_sz)

    Returns a Series named ``{prefix}_{levels}``.
    """
    if levels < 1:
        raise ValueError("levels must be >= 1")
    bid = np.zeros(len(panel), dtype=np.float64)
    ask = np.zeros(len(panel), dtype=np.float64)
    for i in range(levels):
        bid += panel[f"bid_sz_{i}"].to_numpy(dtype=np.float64)
        ask += panel[f"ask_sz_{i}"].to_numpy(dtype=np.float64)
    denom = bid + ask
    out = np.divide(bid - ask, denom, out=np.full_like(denom, np.nan), where=denom > 0)
    return pd.Series(out, index=panel.index, name=f"{prefix}_{levels}")
