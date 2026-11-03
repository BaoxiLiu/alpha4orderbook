"""Forward-return labels on the panel clock."""

from __future__ import annotations

import numpy as np
import pandas as pd


def mid_forward_returns(
    panel: pd.DataFrame,
    horizons_seconds: list[int],
    *,
    price_col: str = "mid",
    dt_seconds: int = 1,
) -> pd.DataFrame:
    """
    Mid-to-mid simple returns at each horizon.

    Horizon ``h`` seconds ⇒ shift by ``h // dt_seconds`` panel rows
    (assumes a regular panel clock with no gaps).
    """
    px = panel[price_col].to_numpy(dtype=np.float64)
    out = pd.DataFrame(index=panel.index)
    for h in horizons_seconds:
        steps = int(h) // int(dt_seconds)
        if steps < 1:
            raise ValueError(f"horizon {h}s too small for dt={dt_seconds}s")
        fwd = np.roll(px, -steps)
        fwd[-steps:] = np.nan
        ret = fwd / px - 1.0
        ret[~np.isfinite(px)] = np.nan
        out[f"ret_fwd_{h}s"] = ret
    return out
