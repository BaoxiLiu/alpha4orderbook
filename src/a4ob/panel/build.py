"""Panel helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .day import default_panels_root, panel_day_dir


def attach_meta(
    panel: pd.DataFrame,
    *,
    symbol: str,
    date: str,
    hour: str,
) -> pd.DataFrame:
    out = panel.copy()
    out.insert(0, "symbol", symbol)
    out.insert(1, "date", date)
    out.insert(2, "hour", hour)
    return out


def resolve_day_panel(
    *,
    symbol: str,
    date: str,
    dt_seconds: int = 1,
    top_k: int = 20,
    panels_root: str | Path | None = None,
) -> Path | None:
    """Return path to day ``panel.parquet`` if it exists, else None."""
    root = Path(panels_root) if panels_root else default_panels_root()
    path = panel_day_dir(root, symbol=symbol, date=date, dt_seconds=dt_seconds, top_k=top_k) / "panel.parquet"
    return path if path.is_file() else None
