"""Built-in Factor Spec operators (panel transforms only)."""

from __future__ import annotations

import ast
import operator as op
from typing import Any

import numpy as np
import pandas as pd

from .baseline import imbalance as imbalance_series


# ---- safe expression eval (names → columns) ---------------------------------

_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
}
_UNARY = {ast.UAdd: op.pos, ast.USub: op.neg}
_FUNCS = {
    "abs": np.abs,
    "tanh": np.tanh,
    "sign": np.sign,
    "log": np.log,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "clip": np.clip,
}


def _eval_node(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, env)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise ValueError(f"unknown name in expr: {node.id}")
        return env[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_eval_node(node.left, env), _eval_node(node.right, env))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval_node(node.operand, env))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fn = _FUNCS.get(node.func.id)
        if fn is None:
            raise ValueError(f"disallowed function: {node.func.id}")
        args = [_eval_node(a, env) for a in node.args]
        return fn(*args)
    raise ValueError(f"unsupported expression node: {type(node).__name__}")


def eval_expr(expr: str, frame: pd.DataFrame, names: list[str] | None = None) -> pd.Series:
    """Evaluate a restricted arithmetic expression over DataFrame columns."""
    tree = ast.parse(expr, mode="eval")
    env: dict[str, Any] = {}
    wanted = names or []
    # Always expose referenced names found via AST walk if not provided
    if not wanted:
        wanted = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id not in _FUNCS]
    for name in wanted:
        if name in _FUNCS:
            continue
        if name not in frame.columns:
            raise KeyError(f"expr references missing column `{name}`")
        env[name] = frame[name].to_numpy(dtype=np.float64)
    # Also allow any column name that appears
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id not in env and n.id not in _FUNCS:
            if n.id not in frame.columns:
                raise KeyError(f"expr references missing column `{n.id}`")
            env[n.id] = frame[n.id].to_numpy(dtype=np.float64)
    result = _eval_node(tree, env)
    return pd.Series(np.asarray(result, dtype=np.float64), index=frame.index)


def op_imbalance(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    levels = int(params.get("levels", 1))
    out = str(params.get("out", f"imb_{levels}"))
    s = imbalance_series(panel, levels=levels, prefix="imb")
    s.name = out
    return {out: s}


def op_microprice_dev(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    """(microprice − mid) / mid; microprice = (ask*bid_sz + bid*ask_sz)/(bid_sz+ask_sz)."""
    out = str(params.get("out", "micro_dev"))
    bb = panel["best_bid"].to_numpy(dtype=np.float64)
    ba = panel["best_ask"].to_numpy(dtype=np.float64)
    bs = panel["best_bid_sz"].to_numpy(dtype=np.float64)
    as_ = panel["best_ask_sz"].to_numpy(dtype=np.float64)
    mid = panel["mid"].to_numpy(dtype=np.float64)
    denom = bs + as_
    micro = np.divide(ba * bs + bb * as_, denom, out=np.full_like(denom, np.nan), where=denom > 0)
    dev = np.divide(micro - mid, mid, out=np.full_like(mid, np.nan), where=np.isfinite(mid) & (mid != 0))
    return {out: pd.Series(dev, index=panel.index, name=out)}


def op_spread_bps(panel: pd.DataFrame, params: dict[str, Any]) -> dict[str, pd.Series]:
    out = str(params.get("out", "spread_bps"))
    mid = panel["mid"].to_numpy(dtype=np.float64)
    spread = panel["spread"].to_numpy(dtype=np.float64)
    bps = np.divide(spread, mid, out=np.full_like(mid, np.nan), where=np.isfinite(mid) & (mid != 0)) * 1e4
    return {out: pd.Series(bps, index=panel.index, name=out)}


def op_expr(panel: pd.DataFrame, params: dict[str, Any], *, expr: str, inputs: list[str]) -> dict[str, pd.Series]:
    out = str(params.get("out") or (inputs[-1] if inputs else "expr_out"))
    # Prefer explicit outputs naming via params.out; caller may override key
    s = eval_expr(expr, panel, names=inputs or None)
    s.name = out
    return {out: s}


OPS = {
    "imbalance": op_imbalance,
    "microprice_dev": op_microprice_dev,
    "spread_bps": op_spread_bps,
    "expr": op_expr,
}
