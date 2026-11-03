"""L2 evaluation suite: Rank IC, coverage, decay, time-split stubs."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .metrics import rank_ic, rank_ic_table


def coverage_stats(frame: pd.DataFrame, factor_cols: list[str], label_cols: list[str]) -> pd.DataFrame:
    rows = []
    n = len(frame)
    for f in factor_cols:
        f_ok = int(frame[f].notna().sum())
        for lab in label_cols:
            pair = frame[[f, lab]].dropna()
            rows.append(
                {
                    "factor": f,
                    "label": lab,
                    "n_panel": n,
                    "n_factor_nonnull": f_ok,
                    "factor_coverage": f_ok / n if n else float("nan"),
                    "n_pairwise": len(pair),
                    "pairwise_coverage": len(pair) / n if n else float("nan"),
                }
            )
    return pd.DataFrame(rows)


def ic_decay_curve(
    frame: pd.DataFrame,
    factor_col: str,
    horizons_seconds: list[int],
    *,
    min_obs: int = 30,
) -> pd.DataFrame:
    """Rank IC of one factor vs ret_fwd_{h}s for each horizon (decay view)."""
    rows = []
    for h in horizons_seconds:
        lab = f"ret_fwd_{h}s"
        if lab not in frame.columns:
            rows.append({"horizon_s": h, "rank_ic": float("nan"), "n": 0})
            continue
        pair = frame[[factor_col, lab]].dropna()
        n = len(pair)
        ic = float("nan") if n < min_obs else rank_ic(pair[factor_col], pair[lab])
        rows.append({"horizon_s": h, "rank_ic": ic, "n": n})
    return pd.DataFrame(rows)


def time_split_ic(
    frame: pd.DataFrame,
    factor_col: str,
    label_col: str,
    fractions: list[float],
    *,
    min_obs: int = 30,
) -> pd.DataFrame:
    """
    Row-order time split (UTC panel clock). Stub for multi-day walk-forward.

    ``fractions`` should sum to ~1 (e.g. [0.6, 0.2, 0.2] → train/val/test).
    """
    fr = np.asarray(fractions, dtype=np.float64)
    if fr.ndim != 1 or fr.size < 1:
        raise ValueError("fractions must be a non-empty list")
    fr = fr / fr.sum()
    n = len(frame)
    cuts = (np.cumsum(fr) * n).astype(int)
    cuts[-1] = n
    starts = np.concatenate([[0], cuts[:-1]])
    names = ["train", "val", "test"] + [f"split_{i}" for i in range(3, len(fr))]
    rows = []
    for i, (a, b) in enumerate(zip(starts, cuts)):
        sl = frame.iloc[int(a) : int(b)]
        pair = sl[[factor_col, label_col]].dropna()
        nn = len(pair)
        ic = float("nan") if nn < min_obs else rank_ic(pair[factor_col], pair[label_col])
        rows.append(
            {
                "split": names[i],
                "frac": float(fr[i]),
                "row_start": int(a),
                "row_end": int(b),
                "n": nn,
                "rank_ic": ic,
                "label": label_col,
                "factor": factor_col,
            }
        )
    return pd.DataFrame(rows)


def run_metric_suite(
    frame: pd.DataFrame,
    *,
    factor_cols: list[str],
    label_cols: list[str],
    horizons_seconds: list[int],
    primary_factor: str | None,
    metrics: list[str],
    splits: dict[str, Any] | None,
    min_obs: int = 30,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    metrics_l = [m.lower() for m in metrics]

    if "rank_ic" in metrics_l:
        result["rank_ic"] = rank_ic_table(frame, factor_cols, label_cols, min_obs=min_obs)

    if "coverage" in metrics_l:
        result["coverage"] = coverage_stats(frame, factor_cols, label_cols)

    primary = primary_factor or (factor_cols[0] if factor_cols else None)
    if primary and "ic_decay" in metrics_l:
        result["ic_decay"] = ic_decay_curve(
            frame, primary, horizons_seconds, min_obs=min_obs
        )
        result["primary_factor"] = primary

    if primary and splits and splits.get("method") == "time":
        fr = list(splits.get("fractions") or [0.6, 0.2, 0.2])
        # Use mid-horizon label if present else first label
        mid_h = 10 if 10 in horizons_seconds else horizons_seconds[len(horizons_seconds) // 2]
        lab = f"ret_fwd_{mid_h}s"
        if lab not in frame.columns and label_cols:
            lab = label_cols[0]
        result["time_split"] = time_split_ic(frame, primary, lab, fr, min_obs=min_obs)
        result["time_split_note"] = splits.get(
            "note",
            "Time split is a single-panel row-order stub; replace with multi-day folds in M4.",
        )

    return result
