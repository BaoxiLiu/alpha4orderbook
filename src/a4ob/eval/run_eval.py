"""run_eval: Factor Spec → panel factors → metrics → experiment report."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ..config import default_config_path, load_config
from ..factors.adapter import apply_factor_spec
from ..factors.spec import load_factor_spec
from ..labels.forward import mid_forward_returns
from ..panel.build import resolve_day_panel
from ..report.eval_report import write_eval_report
from .suite import run_metric_suite


def run_eval(
    *,
    factor_spec: str | Path,
    symbol: str,
    date: str,
    config_path: str | Path | None = None,
    panel_path: str | Path | None = None,
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_config(config_path or default_config_path())
    spec = load_factor_spec(factor_spec)
    dt_s = int(cfg["panel"]["dt_seconds"])
    top_k = int(cfg["panel"]["top_k"])
    min_obs = int(cfg.get("eval", {}).get("min_obs", 30))

    if panel_path is None:
        found = resolve_day_panel(symbol=symbol, date=date, dt_seconds=dt_s, top_k=top_k)
        if found is None:
            raise FileNotFoundError(
                f"day panel not found for {symbol} {date} under panels/dt={dt_s}s/K={top_k}/. "
                "Run build-panel first."
            )
        panel_path = found
    panel_path = Path(panel_path)
    panel = pd.read_parquet(panel_path)

    # Restrict to symbol/date if multi-day panel ever appears
    if "symbol" in panel.columns:
        panel = panel[panel["symbol"] == symbol]
    if "date" in panel.columns:
        panel = panel[panel["date"] == date]
    panel = panel.reset_index(drop=True)
    if panel.empty:
        raise RuntimeError(f"empty panel after filters: {panel_path}")

    panel, apply_meta = apply_factor_spec(panel, spec)

    horizons = list(spec.horizons_seconds)
    price_col = spec.price_col
    labels = mid_forward_returns(panel, horizons, price_col=price_col, dt_seconds=dt_s)
    for c in labels.columns:
        panel[c] = labels[c]
    label_cols = list(labels.columns)
    factor_cols = spec.factor_cols

    suite = run_metric_suite(
        panel,
        factor_cols=factor_cols,
        label_cols=label_cols,
        horizons_seconds=horizons,
        primary_factor=spec.primary_factor,
        metrics=spec.metrics,
        splits=spec.splits,
        min_obs=min_obs,
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    repo_root = Path(__file__).resolve().parents[3]
    out = (
        Path(out_dir)
        if out_dir
        else repo_root / "experiments" / f"eval_{spec.name}_{symbol}_{date}_{ts}"
    )
    out.mkdir(parents=True, exist_ok=True)

    # Persist artifacts
    if "rank_ic" in suite:
        suite["rank_ic"].to_csv(out / "rank_ic.csv")
    if "coverage" in suite:
        suite["coverage"].to_csv(out / "coverage.csv", index=False)
    if "ic_decay" in suite:
        suite["ic_decay"].to_csv(out / "ic_decay.csv", index=False)
    if "time_split" in suite:
        suite["time_split"].to_csv(out / "time_split.csv", index=False)

    scored = panel[["ts_ms"] + factor_cols + label_cols].copy()
    scored_path = out / "scored_panel.parquet"
    scored.to_parquet(scored_path, index=False)

    report_path = write_eval_report(
        out / "report.md",
        spec=spec,
        meta={
            "symbol": symbol,
            "date": date,
            "panel_path": str(panel_path),
            "n_rows": len(panel),
            "dt_seconds": dt_s,
            "top_k": top_k,
            "factor_spec": spec.path,
            "apply": apply_meta,
        },
        suite=suite,
    )

    # Compact IC sample for CLI JSON
    ic_sample: dict[str, Any] = {}
    if "rank_ic" in suite:
        ic_df = suite["rank_ic"]
        ic_cols = [c for c in ic_df.columns if not c.endswith("__n")]
        ic_sample = ic_df[ic_cols].to_dict()

    return {
        "out_dir": str(out),
        "report_path": str(report_path),
        "panel_path": str(panel_path),
        "scored_panel": str(scored_path),
        "factor": spec.name,
        "factor_version": spec.version,
        "n_rows": len(panel),
        "factor_cols": factor_cols,
        "rank_ic": ic_sample,
        "primary_factor": suite.get("primary_factor"),
    }
