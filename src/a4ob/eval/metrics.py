"""L2 evaluation metrics (q1-lob-alpha style protocols, reimplemented)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _rankdata(x: np.ndarray) -> np.ndarray:
    """Average-rank transform without scipy."""
    sorter = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=np.float64)
    ranks[sorter] = np.arange(1, len(x) + 1, dtype=np.float64)
    # Average ties
    sx = x[sorter]
    i = 0
    n = len(x)
    while i < n:
        j = i + 1
        while j < n and sx[j] == sx[i]:
            j += 1
        if j - i > 1:
            avg = 0.5 * (i + 1 + j)
            ranks[sorter[i:j]] = avg
        i = j
    return ranks


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = _rankdata(a)
    rb = _rankdata(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom <= 0:
        return float("nan")
    return float((ra * rb).sum() / denom)


def rank_ic(factor: pd.Series, label: pd.Series) -> float:
    """Spearman rank correlation between factor and label (pairwise complete)."""
    a = pd.to_numeric(factor, errors="coerce")
    b = pd.to_numeric(label, errors="coerce")
    mask = a.notna() & b.notna()
    if int(mask.sum()) < 3:
        return float("nan")
    return _spearman(a[mask].to_numpy(dtype=np.float64), b[mask].to_numpy(dtype=np.float64))


def rank_ic_table(
    frame: pd.DataFrame,
    factor_cols: list[str],
    label_cols: list[str],
    *,
    min_obs: int = 30,
) -> pd.DataFrame:
    """Matrix of Rank IC: rows=factors, cols=labels (+ n_obs)."""
    records = []
    for f in factor_cols:
        row = {"factor": f}
        for lab in label_cols:
            pair = frame[[f, lab]].dropna()
            n = len(pair)
            row[f"{lab}__n"] = n
            if n < min_obs:
                row[lab] = float("nan")
            else:
                row[lab] = rank_ic(pair[f], pair[lab])
        records.append(row)
    return pd.DataFrame.from_records(records).set_index("factor")
