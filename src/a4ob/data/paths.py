"""Path helpers for CryptoHFTData hourly parquet layout."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


@dataclass(frozen=True, order=True)
class HourKey:
    date: str  # YYYY-MM-DD
    hour: str  # HH (00-23)

    def __str__(self) -> str:
        return f"{self.date}/{self.hour}"


def resolve_data_root(root: str | Path) -> Path:
    p = Path(root)
    if not p.is_dir():
        raise FileNotFoundError(f"data root not found or not a directory: {p}")
    return p


def _is_apple_double(name: str) -> bool:
    return name.startswith("._")


def orderbook_path(root: Path, symbol: str, key: HourKey) -> Path:
    return root / key.date / key.hour / f"{symbol}_orderbook.parquet"


def trades_path(root: Path, symbol: str, key: HourKey) -> Path:
    """CryptoHFTData ``{SYMBOL}_trades.parquet`` beside the orderbook hour file."""
    return root / key.date / key.hour / f"{symbol}_trades.parquet"


def list_hours(
    root: Path,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[HourKey]:
    """List available UTC hours under root, ignoring AppleDouble sidecars."""
    keys: list[HourKey] = []
    for day_dir in sorted(root.iterdir()):
        if not day_dir.is_dir() or _is_apple_double(day_dir.name):
            continue
        date = day_dir.name
        if start_date and date < start_date:
            continue
        if end_date and date > end_date:
            continue
        for hour_dir in sorted(day_dir.iterdir()):
            if not hour_dir.is_dir() or _is_apple_double(hour_dir.name):
                continue
            if len(hour_dir.name) == 2 and hour_dir.name.isdigit():
                keys.append(HourKey(date=date, hour=hour_dir.name))
    return keys


def iter_symbol_orderbook_files(
    root: Path, symbol: str, hours: Iterable[HourKey]
) -> Iterator[tuple[HourKey, Path]]:
    for key in hours:
        path = orderbook_path(root, symbol, key)
        if path.exists() and not _is_apple_double(path.name):
            yield key, path
