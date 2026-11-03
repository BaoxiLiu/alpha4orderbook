"""Factor pack evaluation across symbols × days (M4 slice)."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from ..config import default_config_path, load_config
from ..factors.adapter import apply_factor_spec
from ..factors.spec import FactorSpec, load_factor_spec
from ..labels.forward import mid_forward_returns
from ..panel.day import default_panels_root, panel_day_dir
from ..panel.manifest import read_manifest
from ..panel.range import iter_dates
from ..report.html_report import write_pack_html_report
from ..report.pack_report import write_pack_report
from .layering import (
    DEFAULT_N_QUANTILES,
    LAYERING_METHOD,
    aggregate_layering_days,
    layering_one_day,
)
from .metrics import rank_ic


def _load_day_panel(
    *,
    symbol: str,
    date: str,
    dt_seconds: int,
    top_k: int,
    panels_root: Path,
) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    out_dir = panel_day_dir(
        panels_root, symbol=symbol, date=date, dt_seconds=dt_seconds, top_k=top_k
    )
    man_path = out_dir / "manifest.json"
    panel_path = out_dir / "panel.parquet"
    meta: dict[str, Any] = {"symbol": symbol, "date": date, "dir": str(out_dir)}
    if man_path.is_file():
        try:
            man = read_manifest(man_path)
            meta["manifest_status"] = man.get("status", "ok")
            meta["n_rows_manifest"] = man.get("n_rows")
        except Exception as exc:  # noqa: BLE001
            meta["manifest_error"] = str(exc)
    if not panel_path.is_file():
        meta["status"] = "missing_panel"
        return None, meta
    df = pd.read_parquet(panel_path)
    meta["status"] = "ok"
    meta["panel_path"] = str(panel_path)
    meta["n_rows"] = len(df)
    return df, meta


def _score_frame(
    panel: pd.DataFrame,
    spec: FactorSpec,
    *,
    dt_seconds: int,
) -> pd.DataFrame:
    scored, _ = apply_factor_spec(panel, spec)
    labels = mid_forward_returns(
        scored, spec.horizons_seconds, price_col=spec.price_col, dt_seconds=dt_seconds
    )
    for c in labels.columns:
        scored[c] = labels[c]
    return scored


def _ic_for_cols(
    frame: pd.DataFrame,
    factor_cols: list[str],
    horizons: list[int],
    *,
    min_obs: int,
) -> list[dict[str, Any]]:
    rows = []
    for f in factor_cols:
        for h in horizons:
            lab = f"ret_fwd_{h}s"
            if f not in frame.columns or lab not in frame.columns:
                rows.append(
                    {"factor": f, "horizon_s": h, "rank_ic": float("nan"), "n": 0}
                )
                continue
            pair = frame[[f, lab]].dropna()
            n = len(pair)
            ic = float("nan") if n < min_obs else rank_ic(pair[f], pair[lab])
            rows.append({"factor": f, "horizon_s": h, "rank_ic": ic, "n": n})
    return rows


def run_eval_pack(
    *,
    factor_specs: Iterable[str | Path],
    symbols: Iterable[str],
    start_date: str,
    end_date: str,
    config_path: str | Path | None = None,
    panels_root: str | Path | None = None,
    out_dir: str | Path | None = None,
    train_days: int = 5,
    test_days: int = 2,
) -> dict[str, Any]:
    """
    Evaluate one or more Factor Specs over built day panels.

    Produces a long matrix (factor × horizon × symbol × day) plus:
    - mean IC across days per (factor, horizon, symbol)
    - calendar-day split: first ``train_days`` vs last ``test_days``
    """
    t0 = time.perf_counter()
    cfg = load_config(config_path or default_config_path())
    dt_s = int(cfg["panel"]["dt_seconds"])
    top_k = int(cfg["panel"]["top_k"])
    min_obs = int(cfg.get("eval", {}).get("min_obs", 30))
    root = Path(panels_root) if panels_root else default_panels_root()

    specs = [load_factor_spec(p) for p in factor_specs]
    symbols_l = [str(s) for s in symbols]
    dates = iter_dates(start_date, end_date)
    if train_days + test_days > len(dates):
        # shrink but keep at least 1 test day when possible
        test_days = min(test_days, max(1, len(dates) // 3))
        train_days = max(1, len(dates) - test_days)

    train_dates = set(dates[:train_days])
    test_dates = set(dates[-test_days:])

    n_quantiles = int(cfg.get("eval", {}).get("n_quantiles", DEFAULT_N_QUANTILES))

    day_rows: list[dict[str, Any]] = []
    layer_rows: list[dict[str, Any]] = []
    load_log: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for sym in symbols_l:
        for d in dates:
            panel, meta = _load_day_panel(
                symbol=sym, date=d, dt_seconds=dt_s, top_k=top_k, panels_root=root
            )
            load_log.append(meta)
            if panel is None:
                failures.append({**meta, "reason": "missing_or_no_snapshot"})
                continue
            for spec in specs:
                try:
                    scored = _score_frame(panel, spec, dt_seconds=dt_s)
                    split = (
                        "train"
                        if d in train_dates
                        else ("test" if d in test_dates else "hold")
                    )
                    for row in _ic_for_cols(
                        scored, spec.factor_cols, spec.horizons_seconds, min_obs=min_obs
                    ):
                        day_rows.append(
                            {
                                "spec": spec.name,
                                "symbol": sym,
                                "date": d,
                                "split": split,
                                **row,
                            }
                        )
                    for fcol in spec.factor_cols:
                        for lrow in layering_one_day(
                            scored,
                            fcol,
                            spec.horizons_seconds,
                            n_quantiles=n_quantiles,
                            min_obs=min_obs,
                        ):
                            layer_rows.append(
                                {
                                    "spec": spec.name,
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

    detail = pd.DataFrame(day_rows)
    if detail.empty:
        raise RuntimeError(
            f"pack eval produced no IC rows (symbols={symbols_l}, "
            f"dates={dates}, failures={len(failures)})"
        )

    # Mean across days: factor × horizon × symbol
    mean_sym = (
        detail.groupby(["spec", "factor", "horizon_s", "symbol"], as_index=False)
        .agg(rank_ic=("rank_ic", "mean"), n_days=("date", "nunique"), n_obs_sum=("n", "sum"))
    )

    # Wide-ish matrix for report: factor × horizon × symbol (mean)
    pivot = mean_sym.pivot_table(
        index=["spec", "factor", "horizon_s"],
        columns="symbol",
        values="rank_ic",
        aggfunc="mean",
    )

    # Calendar-day split IC (concat panels conceptually via mean of day ICs)
    split_rows = []
    for (spec_name, factor, horizon), g in detail.groupby(["spec", "factor", "horizon_s"]):
        for split_name, dateset in (("train", train_dates), ("test", test_dates)):
            sub = g[g["date"].isin(dateset)]
            split_rows.append(
                {
                    "spec": spec_name,
                    "factor": factor,
                    "horizon_s": horizon,
                    "split": split_name,
                    "n_days": sub["date"].nunique(),
                    "mean_rank_ic": float(sub["rank_ic"].mean()) if len(sub) else float("nan"),
                    "mean_n": float(sub["n"].mean()) if len(sub) else 0.0,
                }
            )
    split_df = pd.DataFrame(split_rows)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    repo_root = Path(__file__).resolve().parents[3]
    out = (
        Path(out_dir)
        if out_dir
        else repo_root
        / "experiments"
        / f"pack_{'-'.join(s.name for s in specs)}_{start_date}_{end_date}_{ts}"
    )
    out.mkdir(parents=True, exist_ok=True)

    layer_detail = pd.DataFrame(layer_rows)
    layer_mean = (
        aggregate_layering_days(layer_detail)
        if not layer_detail.empty
        else pd.DataFrame()
    )

    detail.to_csv(out / "ic_by_day.csv", index=False)
    mean_sym.to_csv(out / "ic_mean_by_symbol.csv", index=False)
    pivot.to_csv(out / "ic_matrix_symbol.csv")
    split_df.to_csv(out / "ic_calendar_split.csv", index=False)
    if not layer_detail.empty:
        layer_detail.to_csv(out / "layering_by_day.csv", index=False)
        layer_mean.to_csv(out / "layering_mean_by_symbol.csv", index=False)
        ls_only = layer_mean[layer_mean["quantile"].astype(str) == "LS"].copy()
        ls_only.to_csv(out / "layering_long_short.csv", index=False)

    elapsed = time.perf_counter() - t0
    layering_note = (
        f"分层 = time-series quantiles within each symbol-day "
        f"(method=`{LAYERING_METHOD}`, Q={n_quantiles}). "
        "Equal-day mean of per-day bucket mean forward mid returns; "
        "LS = Q_high − Q_low. "
        "Order-book depth tags (L3/L5) are unrelated to these quintiles."
    )
    meta = {
        "symbols": symbols_l,
        "start_date": start_date,
        "end_date": end_date,
        "dates": dates,
        "train_dates": sorted(train_dates),
        "test_dates": sorted(test_dates),
        "train_days": train_days,
        "test_days": test_days,
        "factor_specs": [s.path for s in specs],
        "factor_names": [s.name for s in specs],
        "panels_root": str(root),
        "dt_seconds": dt_s,
        "top_k": top_k,
        "min_obs": min_obs,
        "n_quantiles": n_quantiles,
        "layering_method": LAYERING_METHOD,
        "n_detail_rows": len(detail),
        "n_layering_rows": len(layer_detail),
        "n_failures": len(failures),
        "elapsed_seconds": round(elapsed, 3),
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    report_path = write_pack_report(
        out / "report.md",
        meta=meta,
        mean_by_symbol=mean_sym,
        pivot=pivot,
        calendar_split=split_df,
        failures=failures,
        load_log=load_log,
        layering_mean=layer_mean if not layer_mean.empty else None,
        layering_note=layering_note,
    )
    html_path = write_pack_html_report(
        out / "report.html",
        meta=meta,
        mean_by_symbol=mean_sym,
        calendar_split=split_df,
        layering_mean=layer_mean if not layer_mean.empty else None,
        layering_note=layering_note,
    )

    return {
        "out_dir": str(out),
        "report_path": str(report_path),
        "html_report_path": str(html_path),
        "elapsed_seconds": round(elapsed, 3),
        "n_detail_rows": len(detail),
        "n_layering_rows": len(layer_detail),
        "n_failures": len(failures),
        "failures": failures,
        "train_dates": sorted(train_dates),
        "test_dates": sorted(test_dates),
        "n_quantiles": n_quantiles,
        "layering_method": LAYERING_METHOD,
    }
