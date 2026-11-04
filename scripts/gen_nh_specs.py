#!/usr/bin/env python3
"""Generate Universe Specs for NH 23 alpha + 28 value factors (from_column ops)."""

from __future__ import annotations

from pathlib import Path

from a4ob.factors.nh_features import NH_ALPHA_NAMES, NH_VALUE_NAMES

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "configs" / "factors" / "universe"
HORIZONS = [1, 5, 10, 30, 60, 300]


def write_spec(fid: str, source: str) -> None:
    text = f"""# Universe Spec — {fid}
# Sources: {source}
factor:
  name: {fid}
  version: "0.3.0"
  frequency: 1s
  description: >
    NH port via trades_features.parquet ({source})

  output:
    - col: {fid}
      dtype: float64

  requires:
    panel: [ts_ms, mid, best_bid, best_ask, best_bid_sz, best_ask_sz, {fid}]

  steps:
    - id: {fid}
      op: from_column
      params: {{ col: {fid}, out: {fid} }}
      outputs: [{fid}]

  labels:
    price: mid
    horizons_seconds: {HORIZONS}

  eval:
    metrics: [rank_ic, coverage, ic_decay]
    primary_factor: {fid}
"""
    (OUT / f"{fid}.yaml").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for name in NH_ALPHA_NAMES:
        write_spec(name, f"nh_alpha:{name.removeprefix('nh_')}")
        n += 1
    for name in NH_VALUE_NAMES:
        write_spec(name, f"nh_value:{name.removeprefix('nh_')}")
        n += 1
    print(f"wrote {n} NH Specs → {OUT}")


if __name__ == "__main__":
    main()
