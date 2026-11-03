"""Greedy absolute-correlation clustering → Core representatives."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def greedy_abs_corr_clusters(
    corr: pd.DataFrame,
    scores: dict[str, float],
    *,
    threshold: float = 0.70,
) -> list[dict[str, Any]]:
    """
    Greedy: sort factors by score desc; assign to first cluster whose
    representative has |ρ| >= threshold; else start new cluster.
    """
    factors = sorted(scores.keys(), key=lambda f: scores[f], reverse=True)
    clusters: list[dict[str, Any]] = []
    for f in factors:
        placed = False
        for cl in clusters:
            rep = cl["representative"]
            if f not in corr.columns or rep not in corr.columns:
                rho = 0.0
            else:
                rho = corr.loc[rep, f]
                if not np.isfinite(rho):
                    rho = 0.0
            if abs(float(rho)) >= threshold:
                cl["members"].append(f)
                cl["corr_to_rep"][f] = float(rho)
                placed = True
                break
        if not placed:
            clusters.append(
                {
                    "cluster_id": len(clusters),
                    "representative": f,
                    "members": [f],
                    "corr_to_rep": {f: 1.0},
                    "score": float(scores[f]),
                }
            )
    return clusters
