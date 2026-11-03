"""rank-universe: evaluate Spec set → scorecard → leaderboard."""

from __future__ import annotations

import json
import time
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from ..eval.layering import DEFAULT_N_QUANTILES, layering_one_day
from ..eval.metrics import rank_ic
from ..factors.adapter import apply_factor_spec
from ..factors.spec import FactorSpec, FactorStep, load_factor_spec
from ..labels.forward import mid_forward_returns
from ..panel.day import default_panels_root, panel_day_dir
from ..panel.range import iter_dates
from .correlate import average_corr_matrices, spearman_corr_matrix
from .html_leaderboard import write_leaderboard_html
from .score import load_scoring, score_factor_row


def _discover_specs(factors: Iterable[str | Path] | None, glob_pat: str | None) -> list[Path]:
    repo = Path(__file__).resolve().parents[3]
    paths: list[Path] = []
    if factors:
        for f in factors:
            p = Path(f)
            if not p.is_absolute():
                p = (repo / p).resolve()
            paths.append(p)
    elif glob_pat:
        paths = sorted(repo.glob(glob_pat))
        paths = [p for p in paths if not p.name.startswith("._") and p.suffix == ".yaml"]
    else:
        paths = sorted((repo / "configs/factors/universe").glob("*.yaml"))
        paths = [p for p in paths if not p.name.startswith("._")]
    if not paths:
        raise FileNotFoundError("no factor specs found for universe ranking")
    return paths


_TICK_OPS = frozenset(
    {
        "depth_imb_ticks",
        "depth_slope_imb",
        "near_depth_imbalance",
        "spread_ticks",
        "side_width_ticks",
        "spread_change_ticks",
    }
)


def _inject_tick(spec: FactorSpec, tick: float) -> FactorSpec:
    """Return a copy with tick_size set on depth-band / tick-unit ops for this symbol."""
    new_steps: list[FactorStep] = []
    for step in spec.steps:
        params = dict(step.params)
        if step.op in _TICK_OPS:
            params["tick_size"] = float(tick)
        if step.op == "factor_delta" and str(params.get("base_op", "")) in _TICK_OPS:
            params["tick_size"] = float(tick)
        new_steps.append(
            FactorStep(
                id=step.id,
                op=step.op,
                outputs=list(step.outputs),
                params=params,
                inputs=list(step.inputs),
                expr=step.expr,
            )
        )
    return replace(spec, steps=new_steps, raw=deepcopy(spec.raw))


def rank_universe(
    *,
    factors: Iterable[str | Path] | None = None,
    symbols: Iterable[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    scoring_path: str | Path | None = None,
    panels_root: str | Path | None = None,
    out_dir: str | Path | None = None,
    train_days: int | None = None,
    test_days: int | None = None,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    cfg = load_scoring(scoring_path)
    uni = cfg.get("universe") or {}
    symbols_l = [str(s) for s in (symbols or uni.get("symbols") or ["BTCUSDC"])]
    start = start_date or uni.get("start_date") or "2026-08-01"
    end = end_date or uni.get("end_date") or "2026-08-07"
    train_days = int(train_days if train_days is not None else uni.get("train_days", 5))
    test_days = int(test_days if test_days is not None else uni.get("test_days", 2))
    min_obs = int(cfg.get("normalization", {}).get("min_obs", 30))
    n_quantiles = int(DEFAULT_N_QUANTILES)
    h0 = int(cfg["primary_horizon_s"])
    tick_map = cfg.get("tick_size_usdc") or {}

    spec_paths = _discover_specs(factors, uni.get("factors_glob"))
    specs = [load_factor_spec(p) for p in spec_paths]

    root = Path(panels_root) if panels_root else default_panels_root()
    dates = iter_dates(start, end)
    if train_days + test_days > len(dates):
        test_days = min(test_days, max(1, len(dates) // 3))
        train_days = max(1, len(dates) - test_days)
    train_dates = set(dates[:train_days])
    test_dates = set(dates[-test_days:])

    dt_s = 1
    top_k = 20
    # Infer from first available manifest if present
    for sym in symbols_l:
        for d in dates:
            man = panel_day_dir(root, symbol=sym, date=d, dt_seconds=dt_s, top_k=top_k) / "manifest.json"
            if man.is_file():
                try:
                    m = json.loads(man.read_text())
                    dt_s = int(m.get("dt_seconds", dt_s))
                    top_k = int(m.get("top_k", top_k))
                except Exception:  # noqa: BLE001
                    pass
                break

    ic_rows: list[dict[str, Any]] = []
    layer_rows: list[dict[str, Any]] = []
    # factor series samples for correlation: concat per symbol across days
    series_by_symbol: dict[str, list[pd.DataFrame]] = {s: [] for s in symbols_l}
    failures: list[dict[str, Any]] = []

    for sym in symbols_l:
        tick = float(tick_map.get(sym, tick_map.get("default", 0.01)))
        for d in dates:
            pdir = panel_day_dir(root, symbol=sym, date=d, dt_seconds=dt_s, top_k=top_k)
            panel_path = pdir / "panel.parquet"
            if not panel_path.is_file():
                failures.append({"symbol": sym, "date": d, "reason": "missing_panel"})
                continue
            panel = pd.read_parquet(panel_path)
            # labels once per panel
            horizons = sorted({h for s in specs for h in s.horizons_seconds})
            labels = mid_forward_returns(panel, horizons, price_col="mid", dt_seconds=dt_s)
            work = panel.copy()
            for c in labels.columns:
                work[c] = labels[c]

            factor_cols: dict[str, pd.Series] = {}
            split = "train" if d in train_dates else ("test" if d in test_dates else "hold")
            # Scorecard only needs LS at primary horizon; IC still uses full Spec horizons.
            layer_horizons = [h0]

            for spec in specs:
                try:
                    sp = _inject_tick(spec, tick)
                    scored, _ = apply_factor_spec(work, sp)
                    for fcol in sp.factor_cols:
                        factor_cols[fcol] = scored[fcol]
                        for h in sp.horizons_seconds:
                            lab = f"ret_fwd_{h}s"
                            pair = scored[[fcol, lab]].dropna()
                            n = len(pair)
                            ic = float("nan") if n < min_obs else rank_ic(pair[fcol], pair[lab])
                            ic_rows.append(
                                {
                                    "spec": sp.name,
                                    "factor": fcol,
                                    "symbol": sym,
                                    "date": d,
                                    "split": split,
                                    "horizon_s": h,
                                    "rank_ic": ic,
                                    "n": n,
                                }
                            )
                        for lrow in layering_one_day(
                            scored,
                            fcol,
                            layer_horizons,
                            n_quantiles=n_quantiles,
                            min_obs=min_obs,
                        ):
                            layer_rows.append(
                                {
                                    "spec": sp.name,
                                    "factor": fcol,
                                    "symbol": sym,
                                    "date": d,
                                    "split": split,
                                    **lrow,
                                }
                            )
                except Exception as exc:  # noqa: BLE001
                    failures.append(
                        {
                            "symbol": sym,
                            "date": d,
                            "spec": spec.name,
                            "reason": f"{type(exc).__name__}: {exc}",
                        }
                    )
            if factor_cols:
                factor_frame = pd.concat(
                    [work["ts_ms"].rename("ts_ms"), pd.DataFrame(factor_cols)],
                    axis=1,
                )
                # Downsample for correlation to keep memory/CPU bounded at ~111 factors.
                step = max(1, len(factor_frame) // 8000)
                series_by_symbol[sym].append(factor_frame.iloc[::step].reset_index(drop=True))

    detail = pd.DataFrame(ic_rows)
    if detail.empty:
        raise RuntimeError(f"universe ranking produced no IC rows; failures={failures[:5]}")

    mean_sym = (
        detail.groupby(["factor", "horizon_s", "symbol"], as_index=False)
        .agg(rank_ic=("rank_ic", "mean"), n_days=("date", "nunique"), n_obs_sum=("n", "sum"))
    )

    split_rows = []
    for (factor, horizon), g in detail.groupby(["factor", "horizon_s"]):
        for split_name, dateset in (("train", train_dates), ("test", test_dates)):
            sub = g[g["date"].isin(dateset)]
            split_rows.append(
                {
                    "factor": factor,
                    "horizon_s": horizon,
                    "split": split_name,
                    "n_days": sub["date"].nunique(),
                    "mean_rank_ic": float(sub["rank_ic"].mean()) if len(sub) else float("nan"),
                }
            )
    split_df = pd.DataFrame(split_rows)

    layer_detail = pd.DataFrame(layer_rows)
    ls_mean = pd.DataFrame()
    if not layer_detail.empty:
        ls = layer_detail[
            (layer_detail["quantile"].astype(str) == "LS")
            & (layer_detail["horizon_s"] == h0)
        ]
        ls_mean = (
            ls.groupby(["factor", "symbol"], as_index=False)
            .agg(mean_ret=("mean_ret", "mean"), n_days=("date", "nunique"))
        )

    # coverage: mean pairwise n / theoretical at primary
    cov_map: dict[str, float] = {}
    for factor, g in detail[detail["horizon_s"] == h0].groupby("factor"):
        # approximate coverage as mean(n) / median positive n
        ns = g["n"].to_numpy(dtype=np.float64)
        med = float(np.median(ns[ns > 0])) if np.any(ns > 0) else 1.0
        cov_map[factor] = float(np.mean(np.clip(ns / med, 0, 1))) if med > 0 else 0.0

    # score each factor
    rank_rows = []
    for factor in sorted(detail["factor"].unique()):
        ic_f = mean_sym[mean_sym["factor"] == factor]
        sp_f = split_df[split_df["factor"] == factor]
        ls_f = ls_mean[ls_mean["factor"] == factor] if not ls_mean.empty else pd.DataFrame(columns=["symbol", "mean_ret"])
        sc = score_factor_row(
            ic_by_h_sym=ic_f,
            split_df=sp_f,
            ls_by_sym=ls_f,
            coverage=cov_map.get(factor, 0.0),
            cfg=cfg,
        )
        rank_rows.append({"factor": factor, **sc})
    ranking = pd.DataFrame(rank_rows).sort_values("score", ascending=False).reset_index(drop=True)
    ranking.insert(0, "rank", np.arange(1, len(ranking) + 1))

    # correlation matrices per symbol (concat days)
    corr_mats = []
    factor_cols = [c for c in ranking["factor"].tolist()]
    for sym, parts in series_by_symbol.items():
        if not parts:
            continue
        big = pd.concat(parts, axis=0, ignore_index=True)
        cols = [c for c in factor_cols if c in big.columns]
        if len(cols) < 2:
            continue
        corr_mats.append(spearman_corr_matrix(big, cols, min_obs=min_obs))
    corr_avg = average_corr_matrices(corr_mats) if corr_mats else pd.DataFrame()

    repo = Path(__file__).resolve().parents[3]
    out = Path(out_dir) if out_dir else repo / "library" / "runs" / (
        f"universe_{start}_{end}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    out.mkdir(parents=True, exist_ok=True)

    detail.to_csv(out / "ic_by_day.csv", index=False)
    mean_sym.to_csv(out / "ic_mean_by_symbol.csv", index=False)
    split_df.to_csv(out / "ic_calendar_split.csv", index=False)
    ranking.to_csv(out / "universe_ranking.csv", index=False)
    if not layer_detail.empty:
        layer_detail.to_csv(out / "layering_by_day.csv", index=False)
        ls_mean.to_csv(out / "layering_ls_primary.csv", index=False)
    if not corr_avg.empty:
        corr_avg.to_csv(out / "factor_corr_avg.csv")

    registry = {
        "schema_version": 1,
        "library": "universe",
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "scoring": cfg.get("version"),
        "symbols": symbols_l,
        "start_date": start,
        "end_date": end,
        "train_dates": sorted(train_dates),
        "test_dates": sorted(test_dates),
        "n_factors": len(ranking),
        "factors": ranking.to_dict(orient="records"),
        "spec_paths": [str(p) for p in spec_paths],
        "n_failures": len(failures),
    }
    (out / "universe_registry.json").write_text(
        json.dumps(registry, indent=2, default=str), encoding="utf-8"
    )

    meta = {
        "symbols": symbols_l,
        "start_date": start,
        "end_date": end,
        "n_factors": len(ranking),
        "primary_horizon_s": h0,
        "scoring_version": cfg.get("version"),
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
        "n_failures": len(failures),
    }
    html_path = write_leaderboard_html(out / "universe_leaderboard.html", ranking=ranking, meta=meta)

    # also write package-level snapshot for build-core convenience
    snap = repo / "library" / "universe_latest"
    snap.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(snap / "universe_ranking.csv", index=False)
    if not corr_avg.empty:
        corr_avg.to_csv(snap / "factor_corr_avg.csv")
    (snap / "universe_registry.json").write_text(
        json.dumps(registry, indent=2, default=str), encoding="utf-8"
    )
    write_leaderboard_html(snap / "universe_leaderboard.html", ranking=ranking, meta=meta)

    return {
        "out_dir": str(out),
        "ranking_csv": str(out / "universe_ranking.csv"),
        "leaderboard_html": str(html_path),
        "corr_csv": str(out / "factor_corr_avg.csv") if not corr_avg.empty else None,
        "n_factors": len(ranking),
        "n_failures": len(failures),
        "failures": failures[:20],
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
        "top10": ranking.head(10)[["rank", "factor", "score", "mean_ic_primary"]].to_dict(
            orient="records"
        ),
    }
