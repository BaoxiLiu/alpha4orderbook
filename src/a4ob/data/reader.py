"""CryptoHFTData hour reader (orderbook parquet)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from .paths import HourKey, list_hours, orderbook_path


REQUIRED_COLS = [
    "received_time",
    "event_time",
    "transaction_time",
    "symbol",
    "event_type",
    "first_update_id",
    "final_update_id",
    "prev_final_update_id",
    "last_update_id",
    "side",
    "price",
    "quantity",
    "order_count",
]


def read_orderbook_hour(path: str | Path) -> pd.DataFrame:
    """
    Read one CryptoHFTData ``*_orderbook.parquet`` hour file.

    - Ignores AppleDouble paths (caller should not pass ``._*``).
    - Casts ``price`` / ``quantity`` strings to float64.
    - Keeps update-id columns as nullable Int64.
    """
    path = Path(path)
    if path.name.startswith("._"):
        raise ValueError(f"refusing AppleDouble sidecar: {path}")
    if not path.is_file():
        raise FileNotFoundError(path)

    table = pq.read_table(path)
    df = table.to_pandas()
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")

    df = df.copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    for col in (
        "first_update_id",
        "final_update_id",
        "prev_final_update_id",
        "last_update_id",
        "order_count",
        "transaction_time",
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df["event_type"] = df["event_type"].astype(str)
    df["side"] = df["side"].astype(str)
    return df


def hour_has_snapshot(path: Path, *, min_snap_rows: int = 100) -> bool:
    """Cheap scan: does this hour file contain enough snapshot rows?"""
    if not path.is_file() or path.name.startswith("._"):
        return False
    pf = pq.ParquetFile(path)
    n_snap = 0
    for i in range(pf.num_row_groups):
        et = pf.read_row_group(i, columns=["event_type"]).column(0).to_pylist()
        n_snap += sum(1 for x in et if x == "snapshot")
        if n_snap >= min_snap_rows:
            return True
    return False


def find_hour_with_snapshot(
    root: Path,
    symbol: str,
    *,
    prefer: HourKey | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    min_snap_rows: int = 100,
) -> tuple[HourKey, Path]:
    """
    Resolve an hour that has a usable snapshot for ``symbol``.

    Preference order: ``prefer`` if it has a snapshot; else first hour in
    ``[start_date, end_date]`` with a snapshot; else raise.
    """
    if prefer is not None:
        path = orderbook_path(root, symbol, prefer)
        if hour_has_snapshot(path, min_snap_rows=min_snap_rows):
            return prefer, path

    for key in list_hours(root, start_date=start_date, end_date=end_date):
        path = orderbook_path(root, symbol, key)
        if hour_has_snapshot(path, min_snap_rows=min_snap_rows):
            return key, path

    raise FileNotFoundError(
        f"no orderbook hour with snapshot for {symbol} under {root} "
        f"(window {start_date}..{end_date}, prefer={prefer})"
    )
