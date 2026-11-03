"""Quantile layering (分层收益) for single-symbol panel factors.

Naming note
-----------
- **分层 / quantile layering** here = bucket the *factor value* into Q equal-count
  groups and measure mean forward mid return per bucket (plus long-short Qmax−Qmin).
- Depth tags like ``imbalance_l3`` / ``imbalance_l5`` mean **order-book levels**,
  not IC quintiles.

Mode (a4ob today)
-----------------
Panels are single-symbol day clocks. Cross-sectional ranking across names at a
fixed timestamp is not available inside one panel. Therefore we use **time-series
quantiles within each calendar day** (``method="ts_within_day"``):

1. Take all non-null factor observations on that symbol-day.
2. Assign quantile labels ``1..Q`` via ``pandas.qcut`` on the day's factor
   distribution (``duplicates="drop"`` if ties collapse bins).
3. For each horizon, mean ``ret_fwd_{h}s`` inside each quantile.
4. Long-short = mean(Q_high) − mean(Q_low) on that day.
5. Pack aggregation = mean of per-day quantile means / LS across days
   (equal-day weight; not pooled ticks).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


DEFAULT_N_QUANTILES = 5
LAYERING_METHOD = "ts_within_day"


def assign_ts_quantiles(
    factor: pd.Series,
    *,
    n_quantiles: int = DEFAULT_N_QUANTILES,
) -> pd.Series:
    """
    Assign 1..n_quantiles within the sample (day) via equal-count qcut.

    Returns a float Series aligned to ``factor.index`` with NaN where factor is
    NaN or qcut cannot form bins.
    """
    out = pd.Series(np.nan, index=factor.index, dtype=np.float64)
    x = pd.to_numeric(factor, errors="coerce")
    valid = x.dropna()
    if len(valid) < n_quantiles:
        return out
    try:
        labels = pd.qcut(
            valid,
            q=n_quantiles,
            labels=False,
            duplicates="drop",
        )
    except ValueError:
        return out
    # labels are 0..k-1; map to 1..k
    out.loc[valid.index] = labels.astype(np.float64) + 1.0
    return out


def layering_one_day(
    frame: pd.DataFrame,
    factor_col: str,
    horizons_seconds: list[int],
    *,
    n_quantiles: int = DEFAULT_N_QUANTILES,
    min_obs: int = 30,
) -> list[dict[str, Any]]:
    """
    Per-day quantile mean forward returns for one factor.

    Emits one row per (horizon, quantile) plus one ``long_short`` row per horizon
    (quantile label ``LS``).
    """
    if factor_col not in frame.columns:
        return []
    q = assign_ts_quantiles(frame[factor_col], n_quantiles=n_quantiles)
    n_assigned = int(q.notna().sum())
    rows: list[dict[str, Any]] = []
    present = sorted({int(v) for v in q.dropna().unique()})
    q_low = present[0] if present else None
    q_high = present[-1] if present else None

    for h in horizons_seconds:
        lab = f"ret_fwd_{h}s"
        if lab not in frame.columns:
            continue
        pair = pd.DataFrame({"q": q, "ret": frame[lab]}).dropna()
        n = len(pair)
        base = {
            "factor": factor_col,
            "horizon_s": int(h),
            "n_quantiles_requested": int(n_quantiles),
            "n_quantiles_realized": len(present),
            "n_assigned": n_assigned,
            "n_pairwise": n,
            "method": LAYERING_METHOD,
        }
        if n < min_obs or q_low is None:
            rows.append(
                {
                    **base,
                    "quantile": "LS",
                    "mean_ret": float("nan"),
                    "n": 0,
                }
            )
            continue

        means: dict[int, float] = {}
        counts: dict[int, int] = {}
        for qi in present:
            sub = pair.loc[pair["q"] == qi, "ret"]
            means[qi] = float(sub.mean()) if len(sub) else float("nan")
            counts[qi] = int(len(sub))
            rows.append(
                {
                    **base,
                    "quantile": int(qi),
                    "mean_ret": means[qi],
                    "n": counts[qi],
                }
            )
        ls = means.get(q_high, float("nan")) - means.get(q_low, float("nan"))
        rows.append(
            {
                **base,
                "quantile": "LS",
                "mean_ret": float(ls) if np.isfinite(ls) else float("nan"),
                "n": int(counts.get(q_high, 0) + counts.get(q_low, 0)),
                "q_low": q_low,
                "q_high": q_high,
            }
        )
    return rows


def aggregate_layering_days(detail: pd.DataFrame) -> pd.DataFrame:
    """Equal-day mean of per-day quantile / LS rows."""
    if detail.empty:
        return detail
    keys = ["spec", "factor", "horizon_s", "symbol", "quantile"]
    have = [k for k in keys if k in detail.columns]
    grouped = detail.groupby(have, as_index=False)
    out = grouped.agg(mean_ret=("mean_ret", "mean"), n_obs_sum=("n", "sum"))
    if "date" in detail.columns:
        nd = detail.groupby(have, as_index=False)["date"].nunique().rename(
            columns={"date": "n_days"}
        )
        out = out.merge(nd, on=have, how="left")
    else:
        out["n_days"] = grouped.size().to_numpy()
    return out
