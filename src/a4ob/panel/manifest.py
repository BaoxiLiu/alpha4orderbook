"""Panel build manifests (JSON beside panel.parquet)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def config_hash(cfg: dict[str, Any]) -> str:
    """Stable hash of panel-relevant config slices."""
    slice_ = {
        "universe": cfg.get("universe"),
        "window": cfg.get("window"),
        "panel": cfg.get("panel"),
        "labels": cfg.get("labels"),
        "data_root": (cfg.get("data") or {}).get("root"),
    }
    raw = json.dumps(slice_, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def file_sha256(path: Path, *, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            buf = f.read(chunk)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def write_manifest(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
