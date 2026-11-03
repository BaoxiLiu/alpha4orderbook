"""Factor–factor Spearman correlation (within symbol, then average)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..eval.metrics import _spearman


def spearman_corr_matrix(frame: pd.DataFrame, cols: list[str], *, min_obs: int = 50) -> pd.DataFrame:
    """Pairwise Spearman on columns of ``frame`` (pairwise complete)."""
    n = len(cols)
    mat = np.eye(n, dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            a = pd.to_numeric(frame[cols[i]], errors="coerce")
            b = pd.to_numeric(frame[cols[j]], errors="coerce")
            mask = a.notna() & b.notna()
            if int(mask.sum()) < min_obs:
                rho = float("nan")
            else:
                rho = _spearman(a[mask].to_numpy(dtype=np.float64), b[mask].to_numpy(dtype=np.float64))
            mat[i, j] = mat[j, i] = rho
    return pd.DataFrame(mat, index=cols, columns=cols)


def average_corr_matrices(mats: list[pd.DataFrame]) -> pd.DataFrame:
    """Nan-mean of aligned correlation matrices."""
    if not mats:
        raise ValueError("no corr matrices")
    cols = list(mats[0].columns)
    stack = np.stack([m.reindex(index=cols, columns=cols).to_numpy(dtype=np.float64) for m in mats], axis=0)
    with np.errstate(all="ignore"):
        mean = np.nanmean(stack, axis=0)
    return pd.DataFrame(mean, index=cols, columns=cols)
