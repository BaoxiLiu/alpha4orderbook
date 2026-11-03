"""End-to-end smoke: one symbol-hour → panel → imbalance + labels → report."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .book.rebuild import sample_top_k_timeline
from .config import default_config_path, load_config
from .data.paths import HourKey, resolve_data_root
from .data.reader import find_hour_with_snapshot, read_orderbook_hour
from .eval.metrics import rank_ic_table
from .factors.baseline import imbalance
from .labels.forward import mid_forward_returns
from .panel.build import attach_meta
from .report.markdown import write_smoke_report


def run_smoke(
    config_path: str | Path | None = None,
    *,
    symbol: str | None = None,
    date: str | None = None,
    hour: str | None = None,
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    cfg = load_config(config_path or default_config_path())
    data_root = resolve_data_root(cfg["data"]["root"])
    smoke_cfg = cfg.get("smoke", {})
    symbol = symbol or smoke_cfg.get("symbol", "BTCUSDC")
    prefer = HourKey(
        date=date or smoke_cfg.get("date", cfg["window"]["start_date"]),
        hour=hour or str(smoke_cfg.get("hour", "00")).zfill(2),
    )
    top_k = int(cfg["panel"]["top_k"])
    dt_s = int(cfg["panel"]["dt_seconds"])
    horizons = list(cfg["labels"]["horizons_seconds"])
    min_obs = int(cfg.get("eval", {}).get("min_obs", 30))

    key, path = find_hour_with_snapshot(
        data_root,
        symbol,
        prefer=prefer,
        start_date=cfg["window"]["start_date"],
        end_date=cfg["window"]["end_date"],
    )
    df = read_orderbook_hour(path)
    panel, stats = sample_top_k_timeline(df, dt_ms=dt_s * 1000, top_k=top_k)
    if panel.empty:
        raise RuntimeError(
            f"empty panel after rebuild for {symbol} {key} (path={path}). "
            f"stats={stats}"
        )

    panel = attach_meta(panel, symbol=symbol, date=key.date, hour=key.hour)
    panel["imb_1"] = imbalance(panel, levels=1)
    panel["imb_5"] = imbalance(panel, levels=min(5, top_k))
    labels = mid_forward_returns(panel, horizons, dt_seconds=dt_s)
    panel = pd.concat([panel, labels], axis=1)

    factor_cols = ["imb_1", "imb_5"]
    label_cols = [f"ret_fwd_{h}s" for h in horizons]
    ic = rank_ic_table(panel, factor_cols, label_cols, min_obs=min_obs)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    repo_root = Path(__file__).resolve().parents[2]
    out = Path(out_dir) if out_dir else repo_root / "experiments" / f"smoke_{symbol}_{key.date}_{key.hour}_{ts}"
    out.mkdir(parents=True, exist_ok=True)

    panel_path = out / "panel.parquet"
    panel.to_parquet(panel_path, index=False)
    ic_path = out / "rank_ic.csv"
    ic.to_csv(ic_path)

    report_path = write_smoke_report(
        out / "report.md",
        meta={
            "symbol": symbol,
            "requested_hour": str(prefer),
            "resolved_hour": str(key),
            "source_parquet": str(path),
            "dt_seconds": dt_s,
            "top_k": top_k,
            "horizons_seconds": horizons,
            "n_panel_rows": len(panel),
            "panel_parquet": str(panel_path),
        },
        stats=asdict(stats),
        ic_table=ic,
        panel_head=panel,
    )

    return {
        "out_dir": str(out),
        "report_path": str(report_path),
        "panel_path": str(panel_path),
        "ic_path": str(ic_path),
        "resolved_hour": str(key),
        "n_panel_rows": len(panel),
        "stats": asdict(stats),
    }
