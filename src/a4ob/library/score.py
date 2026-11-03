"""Scorecard: pack IC + layering → composite Universe score."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


def load_scoring(path: str | Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parents[3] / "configs" / "scoring.yaml"
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _clip01(x: float) -> float:
    if not np.isfinite(x):
        return 0.0
    return float(max(0.0, min(1.0, x)))


def score_factor_row(
    *,
    ic_by_h_sym: pd.DataFrame,
    split_df: pd.DataFrame,
    ls_by_sym: pd.DataFrame,
    coverage: float,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """
    Parameters
    ----------
    ic_by_h_sym : columns factor, horizon_s, symbol, rank_ic (day-averaged)
    split_df : factor, horizon_s, split, mean_rank_ic
    ls_by_sym : symbol, mean_ret (LS at primary horizon)
    """
    w = cfg["weights"]
    norm = cfg["normalization"]
    h0 = int(cfg["primary_horizon_s"])
    h_sec = [int(x) for x in cfg.get("secondary_horizons_s") or [5, 10]]
    ic_cap = float(norm["ic_cap"])
    ls_cap = float(norm["ls_cap"])
    std_cap = float(norm["ic_std_cap"])
    drop_cap = float(norm["test_drop_cap"])

    prim = ic_by_h_sym[ic_by_h_sym["horizon_s"] == h0]
    ic_syms = prim["rank_ic"].to_numpy(dtype=np.float64)
    ic_syms = ic_syms[np.isfinite(ic_syms)]
    mean_ic = float(np.mean(ic_syms)) if len(ic_syms) else float("nan")
    abs_ic = abs(mean_ic) if np.isfinite(mean_ic) else 0.0
    s_ic = _clip01(abs_ic / ic_cap)

    sec_vals = []
    for h in h_sec:
        sub = ic_by_h_sym[ic_by_h_sym["horizon_s"] == h]["rank_ic"]
        if len(sub):
            sec_vals.append(float(np.nanmean(np.abs(sub.to_numpy(dtype=np.float64)))))
    mean_sec = float(np.mean(sec_vals)) if sec_vals else 0.0
    s_sec = _clip01(mean_sec / ic_cap)

    # decay: share of primary |IC| vs max |IC| across horizons (prefer short)
    by_h = (
        ic_by_h_sym.groupby("horizon_s")["rank_ic"]
        .apply(lambda s: float(np.nanmean(np.abs(s.to_numpy(dtype=np.float64)))))
    )
    max_abs = float(by_h.max()) if len(by_h) else 0.0
    prim_abs = float(by_h.get(h0, 0.0)) if h0 in by_h.index else abs_ic
    s_decay = _clip01(prim_abs / max_abs) if max_abs > 0 else 0.0

    # cross-symbol
    if len(ic_syms) >= 2:
        signs = np.sign(ic_syms)
        # treat zeros as missing agreement
        nonzero = signs[signs != 0]
        if len(nonzero):
            agree = float(np.mean(nonzero == nonzero[0]))
        else:
            agree = 0.0
        std = float(np.std(ic_syms))
        s_cross = 0.5 * agree + 0.5 * (1.0 - _clip01(std / std_cap))
    elif len(ic_syms) == 1:
        s_cross = 0.5
        agree = 1.0
        std = 0.0
    else:
        s_cross = 0.0
        agree = 0.0
        std = float("nan")

    # time split at primary
    sp = split_df[split_df["horizon_s"] == h0]
    tr = sp[sp["split"] == "train"]["mean_rank_ic"]
    te = sp[sp["split"] == "test"]["mean_rank_ic"]
    train_ic = float(tr.mean()) if len(tr) else float("nan")
    test_ic = float(te.mean()) if len(te) else float("nan")
    if np.isfinite(train_ic) and np.isfinite(test_ic) and abs(train_ic) > 1e-12:
        same = 1.0 if np.sign(train_ic) == np.sign(test_ic) or test_ic == 0 else 0.0
        ratio = abs(test_ic) / abs(train_ic)
        s_time = same * _clip01(ratio / drop_cap if ratio < drop_cap else 1.0)
    else:
        s_time = 0.0

    ls_vals = ls_by_sym["mean_ret"].to_numpy(dtype=np.float64) if len(ls_by_sym) else np.array([])
    ls_vals = ls_vals[np.isfinite(ls_vals)]
    mean_ls = float(np.mean(ls_vals)) if len(ls_vals) else float("nan")
    s_ls = _clip01(abs(mean_ls) / ls_cap) if np.isfinite(mean_ls) else 0.0

    s_cov = _clip01(float(coverage)) if np.isfinite(coverage) else 0.0

    composite = (
        float(w["ic_primary"]) * s_ic
        + float(w["ic_secondary"]) * s_sec
        + float(w["decay_short_share"]) * s_decay
        + float(w["cross_symbol"]) * s_cross
        + float(w["time_split"]) * s_time
        + float(w["layering_ls"]) * s_ls
        + float(w["coverage"]) * s_cov
    )

    return {
        "score": composite,
        "mean_ic_primary": mean_ic,
        "abs_ic_primary": abs_ic,
        "mean_ic_secondary_abs": mean_sec,
        "decay_short_share": s_decay,
        "cross_sign_agree": agree,
        "cross_ic_std": std,
        "train_ic_primary": train_ic,
        "test_ic_primary": test_ic,
        "mean_ls_primary": mean_ls,
        "coverage": coverage,
        "s_ic": s_ic,
        "s_sec": s_sec,
        "s_decay": s_decay,
        "s_cross": s_cross,
        "s_time": s_time,
        "s_ls": s_ls,
        "s_cov": s_cov,
    }
