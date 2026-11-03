"""L1 research panel schema (fixed clock, top-K)."""

from __future__ import annotations

PANEL_META_COLS = [
    "ts_ms",
    "event_time_ms",
    "symbol",
    "date",
    "hour",
    "mid",
    "spread",
    "best_bid",
    "best_ask",
    "best_bid_sz",
    "best_ask_sz",
]


def panel_level_cols(k: int) -> list[str]:
    cols: list[str] = []
    for i in range(k):
        cols.extend([f"bid_px_{i}", f"bid_sz_{i}", f"ask_px_{i}", f"ask_sz_{i}"])
    return cols
