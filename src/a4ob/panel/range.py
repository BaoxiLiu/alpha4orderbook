"""Parallel (symbol, day) panel builds over a date range (M4 slice)."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date as Date
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from ..config import default_config_path, load_config
from .day import build_day_panel, default_panels_root, panel_day_dir
from .manifest import config_hash, read_manifest

logger = logging.getLogger(__name__)


def iter_dates(start: str, end: str) -> list[str]:
    """Inclusive UTC calendar dates ``YYYY-MM-DD``."""
    a = Date.fromisoformat(start)
    b = Date.fromisoformat(end)
    if b < a:
        raise ValueError(f"end_date {end} < start_date {start}")
    out: list[str] = []
    cur = a
    while cur <= b:
        out.append(cur.isoformat())
        cur += timedelta(days=1)
    return out


def panel_is_fresh(
    *,
    symbol: str,
    date: str,
    expected_hash: str,
    dt_seconds: int,
    top_k: int,
    panels_root: Path,
) -> tuple[bool, dict[str, Any] | None]:
    """True if panel.parquet + manifest exist and config_hash matches."""
    out_dir = panel_day_dir(
        panels_root, symbol=symbol, date=date, dt_seconds=dt_seconds, top_k=top_k
    )
    panel_path = out_dir / "panel.parquet"
    man_path = out_dir / "manifest.json"
    if not man_path.is_file():
        return False, None
    try:
        man = read_manifest(man_path)
    except Exception:
        return False, None
    if man.get("config_hash") != expected_hash:
        return False, man
    status = man.get("status", "ok")
    if status == "no_snapshot":
        # Fresh negative cache — skip rebuild unless forced
        return True, man
    if status == "ok" and panel_path.is_file():
        return True, man
    return False, man


def _build_one(payload: dict[str, Any]) -> dict[str, Any]:
    """Process-pool worker (must be top-level picklable)."""
    symbol = payload["symbol"]
    date = payload["date"]
    try:
        if payload.get("skip_fresh"):
            fresh, man = panel_is_fresh(
                symbol=symbol,
                date=date,
                expected_hash=payload["expected_hash"],
                dt_seconds=payload["dt_seconds"],
                top_k=payload["top_k"],
                panels_root=Path(payload["panels_root"]),
            )
            if fresh:
                return {
                    "status": "skipped_fresh",
                    "symbol": symbol,
                    "date": date,
                    "n_rows": (man or {}).get("n_rows", 0),
                    "panel_path": (man or {}).get("panel_path"),
                    "manifest_path": str(
                        panel_day_dir(
                            Path(payload["panels_root"]),
                            symbol=symbol,
                            date=date,
                            dt_seconds=payload["dt_seconds"],
                            top_k=payload["top_k"],
                        )
                        / "manifest.json"
                    ),
                    "elapsed_seconds": 0.0,
                    "prior_status": (man or {}).get("status"),
                }

        result = build_day_panel(
            symbol=symbol,
            date=date,
            config_path=payload["config_path"],
            panels_root=payload["panels_root"],
            allow_empty=True,
        )
        result["symbol"] = symbol
        result["date"] = date
        return result
    except Exception as exc:  # noqa: BLE001 — surface per-job failures in range summary
        return {
            "status": "error",
            "symbol": symbol,
            "date": date,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_seconds": 0.0,
        }


def build_panel_range(
    *,
    symbols: Iterable[str],
    start_date: str,
    end_date: str,
    config_path: str | Path | None = None,
    panels_root: str | Path | None = None,
    workers: int = 3,
    skip_fresh: bool = True,
) -> dict[str, Any]:
    """
    Build panels for each (symbol, date) in parallel.

    Skips jobs whose existing manifest ``config_hash`` matches the current config
    (and panel exists, or status is ``no_snapshot``).
    """
    t0 = time.perf_counter()
    cfg_path = Path(config_path) if config_path else default_config_path()
    cfg = load_config(cfg_path)
    dt_s = int(cfg["panel"]["dt_seconds"])
    top_k = int(cfg["panel"]["top_k"])
    expected = config_hash(cfg)
    root = Path(panels_root) if panels_root else default_panels_root()
    root.mkdir(parents=True, exist_ok=True)

    symbols_l = [str(s) for s in symbols]
    dates = iter_dates(start_date, end_date)
    jobs = [
        {
            "symbol": sym,
            "date": d,
            "config_path": str(cfg_path.resolve()),
            "panels_root": str(root.resolve()),
            "dt_seconds": dt_s,
            "top_k": top_k,
            "expected_hash": expected,
            "skip_fresh": skip_fresh,
        }
        for sym in symbols_l
        for d in dates
    ]

    results: list[dict[str, Any]] = []
    workers = max(1, int(workers))

    logger.info(
        "build-panel-range: %d jobs (%d symbols × %d days), workers=%d, skip_fresh=%s",
        len(jobs),
        len(symbols_l),
        len(dates),
        workers,
        skip_fresh,
    )

    if workers == 1:
        for job in jobs:
            results.append(_build_one(job))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futs = {pool.submit(_build_one, job): job for job in jobs}
            for fut in as_completed(futs):
                results.append(fut.result())

    # Stable order
    results.sort(key=lambda r: (r.get("symbol", ""), r.get("date", "")))

    summary = {
        "built_at_utc": datetime.now().astimezone().isoformat(),
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
        "symbols": symbols_l,
        "start_date": start_date,
        "end_date": end_date,
        "dates": dates,
        "workers": workers,
        "skip_fresh": skip_fresh,
        "config_path": str(cfg_path.resolve()),
        "config_hash": expected,
        "panels_root": str(root.resolve()),
        "n_jobs": len(jobs),
        "n_ok": sum(1 for r in results if r.get("status") == "ok"),
        "n_skipped_fresh": sum(1 for r in results if r.get("status") == "skipped_fresh"),
        "n_no_snapshot": sum(
            1
            for r in results
            if r.get("status") == "no_snapshot"
            or (r.get("status") == "skipped_fresh" and r.get("prior_status") == "no_snapshot")
        ),
        "n_error": sum(1 for r in results if r.get("status") == "error"),
        "results": results,
    }
    return summary
