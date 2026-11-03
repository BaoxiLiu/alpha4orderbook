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
from .panel.build import attach_meta, resolve_day_panel
from .report.markdown import write_smoke_report


def run_smoke(
    config_path: str | Path | None = None,
    *,
    symbol: str | None = None,
    date: str | None = None,
    hour: str | None = None,
    out_dir: str | Path | None = None,
    panel: str | Path | None = None,
    prefer_day_panel: bool = True,
) -> dict[str, Any]:
    cfg = load_config(config_path or default_config_path())
    data_root = resolve_data_root(cfg["data"]["root"])
    smoke_cfg = cfg.get("smoke", {})
    symbol = symbol or smoke_cfg.get("symbol", "BTCUSDC")
    date = date or smoke_cfg.get("date", cfg["window"]["start_date"])
    prefer = HourKey(
        date=date,
        hour=hour or str(smoke_cfg.get("hour", "00")).zfill(2),
    )
    top_k = int(cfg["panel"]["top_k"])
    dt_s = int(cfg["panel"]["dt_seconds"])
    horizons = list(cfg["labels"]["horizons_seconds"])
    min_obs = int(cfg.get("eval", {}).get("min_obs", 30))

    source = "hour_rebuild"
    resolved_hour = str(prefer)
    stats_dict: dict[str, Any] = {}
    source_parquet = None

    # Prefer an existing day panel when present (M2+).
    day_path = Path(panel) if panel else None
    if day_path is None and prefer_day_panel and hour is None:
        day_path = resolve_day_panel(symbol=symbol, date=date, dt_seconds=dt_s, top_k=top_k)

    if day_path is not None and day_path.is_file():
        panel_df = pd.read_parquet(day_path)
        source = "day_panel"
        resolved_hour = "day"
        source_parquet = str(day_path)
        stats_dict = {"n_rows": len(panel_df), "source": "day_panel"}
    else:
        key, path = find_hour_with_snapshot(
            data_root,
            symbol,
            prefer=prefer,
            start_date=cfg["window"]["start_date"],
            end_date=cfg["window"]["end_date"],
        )
        df = read_orderbook_hour(path)
        panel_df, stats, _carry = sample_top_k_timeline(df, dt_ms=dt_s * 1000, top_k=top_k)
        if panel_df.empty:
            raise RuntimeError(
                f"empty panel after rebuild for {symbol} {key} (path={path}). "
                f"stats={stats}"
            )
        panel_df = attach_meta(panel_df, symbol=symbol, date=key.date, hour=key.hour)
        resolved_hour = str(key)
        source_parquet = str(path)
        stats_dict = asdict(stats)

    if "imb_1" not in panel_df.columns:
        panel_df["imb_1"] = imbalance(panel_df, levels=1)
    if "imb_5" not in panel_df.columns:
        panel_df["imb_5"] = imbalance(panel_df, levels=min(5, top_k))
    label_cols = [f"ret_fwd_{h}s" for h in horizons]
    if any(c not in panel_df.columns for c in label_cols):
        labels = mid_forward_returns(panel_df, horizons, dt_seconds=dt_s)
        panel_df = pd.concat([panel_df, labels], axis=1)

    factor_cols = ["imb_1", "imb_5"]
    ic = rank_ic_table(panel_df, factor_cols, label_cols, min_obs=min_obs)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    repo_root = Path(__file__).resolve().parents[2]
    out = Path(out_dir) if out_dir else repo_root / "experiments" / f"smoke_{symbol}_{date}_{ts}"
    out.mkdir(parents=True, exist_ok=True)

    panel_path = out / "panel.parquet"
    panel_df.to_parquet(panel_path, index=False)
    ic_path = out / "rank_ic.csv"
    ic.to_csv(ic_path)

    report_path = write_smoke_report(
        out / "report.md",
        meta={
            "symbol": symbol,
            "source": source,
            "requested_hour": str(prefer),
            "resolved_hour": resolved_hour,
            "source_parquet": source_parquet,
            "dt_seconds": dt_s,
            "top_k": top_k,
            "horizons_seconds": horizons,
            "n_panel_rows": len(panel_df),
            "panel_parquet": str(panel_path),
        },
        stats=stats_dict,
        ic_table=ic,
        panel_head=panel_df,
    )

    return {
        "out_dir": str(out),
        "report_path": str(report_path),
        "panel_path": str(panel_path),
        "ic_path": str(ic_path),
        "resolved_hour": resolved_hour,
        "source": source,
        "n_panel_rows": len(panel_df),
        "stats": stats_dict,
    }
