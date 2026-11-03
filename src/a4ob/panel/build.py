"""Panel helpers (full (symbol, day) builder arrives in M2)."""

from __future__ import annotations

import pandas as pd


def attach_meta(
    panel: pd.DataFrame,
    *,
    symbol: str,
    date: str,
    hour: str,
) -> pd.DataFrame:
    out = panel.copy()
    out.insert(0, "symbol", symbol)
    out.insert(1, "date", date)
    out.insert(2, "hour", hour)
    return out
