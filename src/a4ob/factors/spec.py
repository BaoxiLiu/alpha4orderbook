"""Factor Spec YAML loader + validation (M3)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ExternalSeriesSpec:
    name: str
    path: str
    ts_col: str = "ts_ms"
    value_col: str = "value"
    direction: str = "backward"  # merge_asof


@dataclass
class FactorStep:
    id: str
    op: str
    outputs: list[str]
    params: dict[str, Any] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)
    expr: str | None = None


@dataclass
class FactorSpec:
    name: str
    version: str
    frequency: str
    output_cols: list[str]
    requires_panel: list[str]
    steps: list[FactorStep]
    horizons_seconds: list[int]
    price_col: str = "mid"
    primary_factor: str | None = None
    metrics: list[str] = field(default_factory=lambda: ["rank_ic", "coverage"])
    splits: dict[str, Any] = field(default_factory=dict)
    external: list[ExternalSeriesSpec] = field(default_factory=list)
    description: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    path: str | None = None

    @property
    def factor_cols(self) -> list[str]:
        """Columns treated as evaluable factors (declared outputs)."""
        return list(self.output_cols)


def _require(d: dict[str, Any], key: str, ctx: str) -> Any:
    if key not in d:
        raise ValueError(f"Factor Spec missing `{key}` under {ctx}")
    return d[key]


def load_factor_spec(path: str | Path) -> FactorSpec:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, dict) or "factor" not in doc:
        raise ValueError(f"{path}: root must contain a `factor:` mapping")
    fac = doc["factor"]
    if not isinstance(fac, dict):
        raise ValueError(f"{path}: `factor` must be a mapping")

    name = str(_require(fac, "name", "factor"))
    version = str(fac.get("version", "0.0.0"))
    frequency = str(fac.get("frequency", "1s"))
    description = str(fac.get("description", ""))

    output = _require(fac, "output", "factor")
    if isinstance(output, list):
        output_cols = [str(x["col"] if isinstance(x, dict) else x) for x in output]
    else:
        raise ValueError("factor.output must be a list")

    requires = fac.get("requires") or {}
    requires_panel = [str(c) for c in (requires.get("panel") or [])]
    external: list[ExternalSeriesSpec] = []
    for ext in requires.get("external") or []:
        external.append(
            ExternalSeriesSpec(
                name=str(ext["name"]),
                path=str(ext["path"]),
                ts_col=str(ext.get("ts_col", "ts_ms")),
                value_col=str(ext.get("value_col", "value")),
                direction=str(ext.get("direction", "backward")),
            )
        )

    steps_raw = _require(fac, "steps", "factor")
    steps: list[FactorStep] = []
    for s in steps_raw:
        steps.append(
            FactorStep(
                id=str(s.get("id", s.get("op", "step"))),
                op=str(_require(s, "op", f"step {s}")),
                outputs=[str(x) for x in (s.get("outputs") or [])],
                params=dict(s.get("params") or {}),
                inputs=[str(x) for x in (s.get("inputs") or [])]
                if isinstance(s.get("inputs"), list)
                else [],
                expr=s.get("expr"),
            )
        )

    labels = fac.get("labels") or {}
    horizons = list(labels.get("horizons_seconds") or [1, 5, 10, 30, 60, 300])
    price_col = str(labels.get("price", "mid"))

    ev = fac.get("eval") or {}
    metrics = list(ev.get("metrics") or ["rank_ic", "coverage"])
    primary = ev.get("primary_factor") or (output_cols[0] if output_cols else None)
    splits = dict(ev.get("splits") or {})

    return FactorSpec(
        name=name,
        version=version,
        frequency=frequency,
        output_cols=output_cols,
        requires_panel=requires_panel,
        steps=steps,
        horizons_seconds=[int(h) for h in horizons],
        price_col=price_col,
        primary_factor=str(primary) if primary else None,
        metrics=metrics,
        splits=splits,
        external=external,
        description=description,
        raw=doc,
        path=str(path.resolve()),
    )
