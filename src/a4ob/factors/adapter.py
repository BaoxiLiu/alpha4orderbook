"""Apply a Factor Spec onto an L1 research panel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .ops import OPS, eval_expr
from .spec import FactorSpec, load_factor_spec


def _expand_required(cols: list[str]) -> list[str]:
    """Expand simple ``bid_sz_0..bid_sz_4`` ranges if ever used; pass-through otherwise."""
    out: list[str] = []
    for c in cols:
        if ".." in c:
            left, right = c.split("..", 1)
            # e.g. bid_sz_0..bid_sz_4
            import re

            m1 = re.match(r"^(.*_)(\d+)$", left.strip())
            m2 = re.match(r"^(.*_)(\d+)$", right.strip())
            if not m1 or not m2 or m1.group(1) != m2.group(1):
                raise ValueError(f"cannot expand range `{c}`")
            prefix = m1.group(1)
            for i in range(int(m1.group(2)), int(m2.group(2)) + 1):
                out.append(f"{prefix}{i}")
        else:
            out.append(c)
    return out


def _asof_join_external(
    panel: pd.DataFrame,
    *,
    path: str | Path,
    ts_col: str,
    value_col: str,
    out_col: str,
    direction: str = "backward",
) -> pd.Series:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"external series not found: {path}")
    if path.suffix.lower() in {".parquet", ".pq"}:
        ext = pd.read_parquet(path)
    else:
        ext = pd.read_csv(path)
    if ts_col not in ext.columns or value_col not in ext.columns:
        raise KeyError(f"{path}: need columns {ts_col!r} and {value_col!r}")
    left = panel[["ts_ms"]].copy().reset_index(drop=True)
    left["_i"] = left.index
    right = ext[[ts_col, value_col]].rename(columns={ts_col: "ts_ms", value_col: out_col})
    right = right.sort_values("ts_ms")
    left = left.sort_values("ts_ms")
    merged = pd.merge_asof(left, right, on="ts_ms", direction=direction)
    merged = merged.sort_values("_i")
    return pd.Series(merged[out_col].to_numpy(), index=panel.index, name=out_col)


def apply_factor_spec(
    panel: pd.DataFrame,
    spec: FactorSpec | str | Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Resolve Spec steps onto a copy of ``panel``.

    Returns ``(augmented_panel, meta)`` where meta records produced columns and
    any external joins.
    """
    if not isinstance(spec, FactorSpec):
        spec = load_factor_spec(spec)

    out = panel.copy()
    required = _expand_required(spec.requires_panel)
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise KeyError(
            f"Factor Spec `{spec.name}` missing panel columns: {missing}. "
            "Rebuild panel with sufficient top-K or adjust requires.panel."
        )

    meta: dict[str, Any] = {
        "factor": spec.name,
        "version": spec.version,
        "produced": [],
        "external_joined": [],
        "steps": [],
    }

    # Optional external asof joins declared under requires.external
    for ext in spec.external:
        col = ext.name
        series = _asof_join_external(
            out,
            path=ext.path,
            ts_col=ext.ts_col,
            value_col=ext.value_col,
            out_col=col,
            direction=ext.direction,
        )
        out[col] = series
        meta["external_joined"].append({"name": col, "path": ext.path})

    for step in spec.steps:
        if step.op not in OPS and step.op != "external_asof":
            raise ValueError(f"unknown op `{step.op}` in step `{step.id}`")

        if step.op == "external_asof":
            # Inline external join as a step (alternative to requires.external)
            path = step.params.get("path")
            if not path:
                raise ValueError(f"step `{step.id}` external_asof needs params.path")
            col = step.outputs[0] if step.outputs else str(step.params.get("out", step.id))
            series = _asof_join_external(
                out,
                path=path,
                ts_col=str(step.params.get("ts_col", "ts_ms")),
                value_col=str(step.params.get("value_col", "value")),
                out_col=col,
                direction=str(step.params.get("direction", "backward")),
            )
            produced = {col: series}
        elif step.op == "expr":
            if not step.expr:
                raise ValueError(f"step `{step.id}` expr op requires `expr:`")
            out_name = step.outputs[0] if step.outputs else step.params.get("out", step.id)
            params = dict(step.params)
            params.setdefault("out", out_name)
            s = eval_expr(step.expr, out, names=step.inputs or None)
            s.name = str(out_name)
            produced = {str(out_name): s}
        else:
            fn = OPS[step.op]
            if step.op == "expr":
                produced = fn(out, step.params, expr=step.expr or "", inputs=step.inputs)
            else:
                produced = fn(out, step.params)
            # Honor step.outputs naming when single-output and mismatch
            if step.outputs and len(step.outputs) == 1 and len(produced) == 1:
                old_k = next(iter(produced))
                new_k = step.outputs[0]
                if old_k != new_k:
                    produced = {new_k: produced[old_k].rename(new_k)}

        for col, series in produced.items():
            out[col] = series
            meta["produced"].append(col)
        meta["steps"].append({"id": step.id, "op": step.op, "outputs": list(produced)})

    for col in spec.output_cols:
        if col not in out.columns:
            raise RuntimeError(
                f"Spec `{spec.name}` declared output `{col}` was not produced by steps"
            )

    return out, meta
