"""YAML config loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError(f"config root must be a mapping: {path}")
    return cfg


def default_config_path() -> Path:
    # repo_root/configs/sealed.yaml relative to this file: src/a4ob/config.py
    return Path(__file__).resolve().parents[2] / "configs" / "sealed.yaml"
