#!/usr/bin/env python3
"""Generate configs/factors/universe/*.yaml for all panel-ready inventory factors.

Dedupes aliases that share the same a4ob compute (e.g. micro:spread_bp → spread_bp).
Writes pending_blocked.md listing blocked inventory IDs skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "configs" / "factors" / "universe"
STORE_DOCS = Path(
    "/Users/baoxiliu/Library/Application Support/Cursor/AgentStores/"
    "cursor_agent_stores/bc-a9b81689-5c61-47c9-a1c9-634511458f09/files/docs"
)
INVENTORY = STORE_DOCS / "factor-candidate-inventory.md"

HORIZONS = [1, 5, 10, 30, 60, 300]

# (a4ob_id, source_ids, description, op, params, requires)
# requires: short | depth | bbo | mid | ts
FACTORS: list[tuple] = []


def add(fid: str, sources: list[str], desc: str, op: str, params: dict, req: str = "depth") -> None:
    FACTORS.append((fid, sources, desc, op, params, req))


# ---- early9 / already ported ----
add("spread_bp", ["spread_bp", "micro:spread_bp"], "Catalog spread_bp", "spread_bp", {"out": "spread_bp"}, "bbo")
add("l1_imbalance", ["l1_imbalance", "flow:touch_qty_imbalance", "micro:bid_signed_imbalance_l1"], "L1 size imbalance", "imbalance_levels", {"levels": 1, "out": "l1_imbalance"}, "depth")
add("microprice_offset_bp", ["microprice_offset_bp"], "Microprice offset bp", "microprice_offset_bp", {"out": "microprice_offset_bp"}, "bbo")
add("mid_return_1s", ["mid_return", "micro:w1000ms_bid_signed_return_bp"], "1s mid return", "mid_return_1s", {"lag": 1, "out": "mid_return_1s"}, "mid")
add("cont_ofi_panel_1s", ["cont_ofi_panel_1s"], "Panel Cont OFI approx", "cont_ofi_panel_1s", {"out": "cont_ofi_panel_1s"}, "bbo")
add("rv_60s_bp2", ["rv_60s_bp2"], "Sum-sq bp mid Δ RV 60s", "sum_sq_rv_bp", {"window": 60, "out": "rv_60s_bp2"}, "mid")

# ---- v3 ready ----
add("depth_imb_3t", ["v3:A1"], "Depth imb ≤3 ticks", "depth_imb_ticks", {"n_ticks": 3, "tick_size": 0.01, "out": "depth_imb_3t"}, "depth")
add("depth_imb_10t", ["v3:A2"], "Depth imb ≤10 ticks", "depth_imb_ticks", {"n_ticks": 10, "tick_size": 0.01, "out": "depth_imb_10t"}, "depth")
add("depth_imb_5bp", ["v3:A3"], "Depth imb ±5bp", "depth_imb_bp", {"n_bp": 5, "out": "depth_imb_5bp"}, "depth")
add("depth_imb_10bp", ["v3:A4"], "Depth imb ±10bp", "depth_imb_bp", {"n_bp": 10, "out": "depth_imb_10bp"}, "depth")
add("depth_slope_imb", ["v3:A5"], "Tick-band slope imbalance", "depth_slope_imb", {"tick_size": 0.01, "out": "depth_slope_imb"}, "depth")
add(
    "depth_imb_3t_d5s",
    ["v3:A6"],
    "A1(t)−A1(t−5s)",
    "factor_delta",
    {"base_op": "depth_imb_ticks", "n_ticks": 3, "tick_size": 0.01, "lag": 5, "out": "depth_imb_3t_d5s"},
    "depth",
)
add("spread_dev_1h", ["v3:A8"], "spread_bp − rolling median 1h", "spread_dev", {"window": 3600, "out": "spread_dev_1h"}, "bbo")
add("ret_5s_bp", ["v3:D1"], "5s mid return bp", "ret_bp", {"lag": 5, "out": "ret_5s_bp"}, "mid")
add("ret_30s_bp", ["v3:D2"], "30s mid return bp", "ret_bp", {"lag": 30, "out": "ret_30s_bp"}, "mid")
add("ret_60s_bp", ["v3:D3"], "60s mid return bp", "ret_bp", {"lag": 60, "out": "ret_60s_bp"}, "mid")
add("rv_30s", ["v3:D6"], "30s realized vol bp", "realized_vol_bp", {"window": 30, "out": "rv_30s"}, "mid")
add("rv_60s", ["v3:D7"], "60s realized vol bp", "realized_vol_bp", {"window": 60, "out": "rv_60s"}, "mid")
add("rv_300s", ["v3:D8"], "300s realized vol bp", "realized_vol_bp", {"window": 300, "out": "rv_300s"}, "mid")
add("rv_ratio_30_300", ["v3:D9"], "rv30/rv300", "rv_ratio", {"short": 30, "long": 300, "out": "rv_ratio_30_300"}, "mid")
add("up_rv_30s", ["v3:D10"], "Upside semi-vol 30s", "half_rv_bp", {"window": 30, "direction": "up", "out": "up_rv_30s"}, "mid")
add("down_rv_30s", ["v3:D11"], "Downside semi-vol 30s", "half_rv_bp", {"window": 30, "direction": "down", "out": "down_rv_30s"}, "mid")
add("signed_semivar_30s", ["v3:D12"], "Signed semi-variance 30s", "signed_semivar", {"window": 30, "out": "signed_semivar_30s"}, "mid")
add("microprice_mom_10s", ["v3:D13"], "Microprice spread-frac Δ10s", "microprice_mom", {"lag": 10, "out": "microprice_mom_10s"}, "bbo")
add("range_position_60s", ["v3:D14"], "Range position 60s", "range_position", {"window": 60, "out": "range_position_60s"}, "mid")
add("jump_count_60s", ["v3:D15"], "Jump count vs 4× med |ret|", "jump_count", {"window": 60, "mult": 4.0, "out": "jump_count_60s"}, "mid")
add("hour_sin", ["v3:E10"], "UTC hour sin", "hour_cycle", {"component": "sin", "out": "hour_sin"}, "ts")
add("hour_cos", ["v3:E11"], "UTC hour cos", "hour_cycle", {"component": "cos", "out": "hour_cos"}, "ts")

# ---- flow ----
add("near_depth_imbalance", ["flow:near_depth_imbalance"], "Near-depth notional imb", "near_depth_imbalance", {"near_ticks": 2, "tick_size": 0.01, "out": "near_depth_imbalance"}, "depth")

# ---- micro static book ----
add("spread_ticks", ["micro:spread_ticks"], "Spread in ticks", "spread_ticks", {"tick_size": 0.01, "out": "spread_ticks"}, "bbo")
add("microprice_spread_frac", ["micro:microprice_bid_signed_bp"], "(micro−mid)/spread", "microprice_spread_frac", {"out": "microprice_spread_frac"}, "bbo")
add("log_touch_total_notional", ["micro:log_touch_total_notional"], "log1p touch notional", "log_touch_total_notional", {"out": "log_touch_total_notional"}, "bbo")

for lvl in (1, 3, 5, 10):
    add(f"log_bid_notional_l{lvl}", [f"micro:log_bid_notional_l{lvl}"], f"log1p bid notional L{lvl}", "side_log_notional", {"side": "bid", "levels": lvl, "out": f"log_bid_notional_l{lvl}"}, "depth")
    add(f"log_ask_notional_l{lvl}", [f"micro:log_ask_notional_l{lvl}"], f"log1p ask notional L{lvl}", "side_log_notional", {"side": "ask", "levels": lvl, "out": f"log_ask_notional_l{lvl}"}, "depth")

for lvl in (5, 10):
    # l1 covered by l1_imbalance; micro:bid_signed_imbalance_l5/l10
    add(f"imbalance_l{lvl}", [f"micro:bid_signed_imbalance_l{lvl}"], f"Signed imbalance L{lvl}", "imbalance_levels", {"levels": lvl, "out": f"imbalance_l{lvl}"}, "depth")

add("imbalance_l3", ["micro:imbalance_l3", "imbalance_l3"], "Imbalance L3", "imbalance_levels", {"levels": 3, "out": "imbalance_l3"}, "depth")

add("bid_touch_share_l10", ["micro:bid_touch_share_l10"], "Bid touch share L10", "side_touch_share", {"side": "bid", "levels": 10, "out": "bid_touch_share_l10"}, "depth")
add("ask_touch_share_l10", ["micro:ask_touch_share_l10"], "Ask touch share L10", "side_touch_share", {"side": "ask", "levels": 10, "out": "ask_touch_share_l10"}, "depth")
add("bid_l10_width_ticks", ["micro:bid_l10_width_ticks"], "Bid L10 width ticks", "side_width_ticks", {"side": "bid", "levels": 10, "tick_size": 0.01, "out": "bid_l10_width_ticks"}, "depth")
add("ask_l10_width_ticks", ["micro:ask_l10_width_ticks"], "Ask L10 width ticks", "side_width_ticks", {"side": "ask", "levels": 10, "tick_size": 0.01, "out": "ask_l10_width_ticks"}, "depth")

for w_ms, lag in ((1000, 1), (5000, 5), (30000, 30)):
    add(f"w{w_ms}ms_realized_vol_bp", [f"micro:w{w_ms}ms_realized_vol_bp"], f"RV over {lag}s", "realized_vol_bp", {"window": lag, "out": f"w{w_ms}ms_realized_vol_bp"}, "mid")
    add(f"w{w_ms}ms_bid_signed_return_bp", [f"micro:w{w_ms}ms_bid_signed_return_bp"], f"Mid return {lag}s bp", "ret_bp", {"lag": lag, "out": f"w{w_ms}ms_bid_signed_return_bp"}, "mid")

for lvl in (3, 5, 10):
    add(f"log_bid_touch_back_ratio_l{lvl}", [f"micro:log_bid_touch_back_ratio_l{lvl}"], f"Bid touch/back L{lvl}", "side_log_touch_back_ratio", {"side": "bid", "levels": lvl, "out": f"log_bid_touch_back_ratio_l{lvl}"}, "depth")
    add(f"log_ask_touch_back_ratio_l{lvl}", [f"micro:log_ask_touch_back_ratio_l{lvl}"], f"Ask touch/back L{lvl}", "side_log_touch_back_ratio", {"side": "ask", "levels": lvl, "out": f"log_ask_touch_back_ratio_l{lvl}"}, "depth")
    add(f"bid_uniformity_l{lvl}", [f"micro:bid_uniformity_l{lvl}"], f"Bid uniformity L{lvl}", "side_uniformity", {"side": "bid", "levels": lvl, "out": f"bid_uniformity_l{lvl}"}, "depth")
    add(f"ask_uniformity_l{lvl}", [f"micro:ask_uniformity_l{lvl}"], f"Ask uniformity L{lvl}", "side_uniformity", {"side": "ask", "levels": lvl, "out": f"ask_uniformity_l{lvl}"}, "depth")
    add(f"bid_hhi_l{lvl}", [f"micro:bid_hhi_l{lvl}"], f"Bid HHI L{lvl}", "side_hhi", {"side": "bid", "levels": lvl, "out": f"bid_hhi_l{lvl}"}, "depth")
    add(f"ask_hhi_l{lvl}", [f"micro:ask_hhi_l{lvl}"], f"Ask HHI L{lvl}", "side_hhi", {"side": "ask", "levels": lvl, "out": f"ask_hhi_l{lvl}"}, "depth")
    add(f"bid_outer_share_l{lvl}", [f"micro:bid_outer_share_l{lvl}"], f"Bid outer share L{lvl}", "side_outer_share", {"side": "bid", "levels": lvl, "outer_from": 2, "out": f"bid_outer_share_l{lvl}"}, "depth")
    add(f"ask_outer_share_l{lvl}", [f"micro:ask_outer_share_l{lvl}"], f"Ask outer share L{lvl}", "side_outer_share", {"side": "ask", "levels": lvl, "outer_from": 2, "out": f"ask_outer_share_l{lvl}"}, "depth")

for lvl in (1, 3, 5, 10):
    add(f"depth_symmetry_l{lvl}", [f"micro:depth_symmetry_l{lvl}"], f"1−|imb| L{lvl}", "depth_symmetry", {"levels": lvl, "out": f"depth_symmetry_l{lvl}"}, "depth")

# micro deltas (1s / 5s) on shape features
DELTA_BASES = [
    ("bid_uniformity_l5", "side_uniformity", {"side": "bid", "levels": 5}),
    ("ask_uniformity_l5", "side_uniformity", {"side": "ask", "levels": 5}),
    ("bid_hhi_l5", "side_hhi", {"side": "bid", "levels": 5}),
    ("ask_hhi_l5", "side_hhi", {"side": "ask", "levels": 5}),
    ("bid_outer_share_l5", "side_outer_share", {"side": "bid", "levels": 5, "outer_from": 2}),
    ("ask_outer_share_l5", "side_outer_share", {"side": "ask", "levels": 5, "outer_from": 2}),
    ("log_bid_notional_l3", "side_log_notional", {"side": "bid", "levels": 3}),
    ("log_ask_notional_l3", "side_log_notional", {"side": "ask", "levels": 3}),
    ("imbalance_l3", "imbalance_levels", {"levels": 3}),
    ("depth_symmetry_l10", "depth_symmetry", {"levels": 10}),
]
for w_ms, lag in ((1000, 1), (5000, 5)):
    for base_name, base_op, base_params in DELTA_BASES:
        fid = f"w{w_ms}ms_delta_{base_name}"
        src = f"micro:w{w_ms}ms_delta_{base_name}"
        params = {"base_op": base_op, "lag": lag, "out": fid, **base_params}
        add(fid, [src], f"Δ{lag}s of {base_name}", "factor_delta", params, "depth")

# ---- states ----
for lag_s, w_ms in ((1, 1000), (2, 2000), (3, 3000)):
    add(
        f"w{w_ms}ms_spread_change_ticks",
        [f"states:w{w_ms}ms_spread_change_ticks"],
        f"Spread ticks Δ{lag_s}s",
        "spread_change_ticks",
        {"lag": lag_s, "tick_size": 0.01, "out": f"w{w_ms}ms_spread_change_ticks"},
        "bbo",
    )
    add(
        f"w{w_ms}ms_bid_l5_change_fraction",
        [f"states:w{w_ms}ms_bid_l5_change_fraction"],
        f"Bid L5 notional frac Δ{lag_s}s",
        "notional_change_frac",
        {"side": "bid", "levels": 5, "lag": lag_s, "out": f"w{w_ms}ms_bid_l5_change_fraction"},
        "depth",
    )
    add(
        f"w{w_ms}ms_ask_l5_change_fraction",
        [f"states:w{w_ms}ms_ask_l5_change_fraction"],
        f"Ask L5 notional frac Δ{lag_s}s",
        "notional_change_frac",
        {"side": "ask", "levels": 5, "lag": lag_s, "out": f"w{w_ms}ms_ask_l5_change_fraction"},
        "depth",
    )

for lag_s, w_ms in ((2, 2000), (3, 3000)):
    add(
        f"w{w_ms}ms_return_bp",
        [f"states:w{w_ms}ms_return_bp"],
        f"Log mid return {lag_s}s bp",
        "log_ret_bp",
        {"lag": lag_s, "out": f"w{w_ms}ms_return_bp"},
        "mid",
    )
    add(
        f"w{w_ms}ms_realized_vol_bp",
        [f"states:w{w_ms}ms_realized_vol_bp"],
        f"RV {lag_s}s",
        "realized_vol_bp",
        {"window": lag_s, "out": f"w{w_ms}ms_realized_vol_bp"},
        "mid",
    )


def _requires(kind: str) -> list[str]:
    if kind == "mid":
        return ["mid"]
    if kind == "ts":
        return ["ts_ms"]
    if kind == "bbo":
        return ["mid", "spread", "best_bid", "best_ask", "best_bid_sz", "best_ask_sz"]
    # depth
    cols = ["mid", "best_bid", "best_ask", "best_bid_sz", "best_ask_sz"]
    for i in range(20):
        cols += [f"bid_px_{i}", f"ask_px_{i}", f"bid_sz_{i}", f"ask_sz_{i}"]
    return cols


def _fmt_params(params: dict) -> str:
    parts = []
    for k, v in params.items():
        if isinstance(v, str):
            parts.append(f"{k}: {v}")
        elif isinstance(v, bool):
            parts.append(f"{k}: {str(v).lower()}")
        else:
            parts.append(f"{k}: {v}")
    return "{ " + ", ".join(parts) + " }"


def write_spec(fid: str, sources: list[str], desc: str, op: str, params: dict, req: str) -> Path:
    panel_cols = ", ".join(_requires(req))
    src = ", ".join(sources)
    text = f"""# Universe Spec — {fid}
# Sources: {src}
factor:
  name: {fid}
  version: "0.2.0"
  frequency: 1s
  description: >
    {desc}

  output:
    - col: {fid}
      dtype: float64

  requires:
    panel: [{panel_cols}]

  steps:
    - id: {fid}
      op: {op}
      params: {_fmt_params(params)}
      outputs: [{fid}]

  labels:
    price: mid
    horizons_seconds: {HORIZONS}

  eval:
    metrics: [rank_ic, coverage, ic_decay]
    primary_factor: {fid}
"""
    path = OUT / f"{fid}.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def parse_inventory_portability() -> dict[str, list[str]]:
    text = INVENTORY.read_text(encoding="utf-8") if INVENTORY.is_file() else ""
    buckets: dict[str, list[str]] = {"ready": [], "blocked": [], "needs_work": [], "out_of_scope": []}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = [x.strip() for x in line.strip("|").split("|")]
        ports = [c.strip("`") for c in parts if c.strip("`") in buckets]
        if not ports:
            continue
        fid = parts[0].strip("`")
        if fid in ("id", "Tag", "a4ob id", "Collection") or fid.startswith("---"):
            continue
        buckets[ports[0]].append(fid)
    return buckets


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # remove prior universe specs (keep directory)
    for old in OUT.glob("*.yaml"):
        if not old.name.startswith("._"):
            old.unlink()
    for old in OUT.glob("._*"):
        old.unlink()

    seen_ids: set[str] = set()
    covered_sources: set[str] = set()
    written = []
    for fid, sources, desc, op, params, req in FACTORS:
        if fid in seen_ids:
            raise SystemExit(f"duplicate a4ob id: {fid}")
        seen_ids.add(fid)
        covered_sources.update(sources)
        written.append(write_spec(fid, sources, desc, op, params, req))

    buckets = parse_inventory_portability()
    ready = [r for r in buckets["ready"] if r not in ("Collection",)]
    blocked = buckets["blocked"]
    needs = buckets["needs_work"]

    # which ready inventory ids remain uncovered (after alias map)
    uncovered = [r for r in ready if r not in covered_sources and r.replace(":", "_") not in seen_ids]

    pending = REPO / "library" / "pending_blocked_factors.md"
    pending.parent.mkdir(parents=True, exist_ok=True)
    pending.write_text(
        "\n".join(
            [
                "# Pending / blocked HF factors (not in Universe v0.2)",
                "",
                f"- Generated Specs: **{len(written)}**",
                f"- Inventory ready listed: **{len(ready)}**",
                f"- Ready sources mapped into Specs: **{len(covered_sources & set(ready))}**",
                f"- Ready still uncovered (name mismatch / skip): **{len(uncovered)}**",
                f"- Blocked (trades/event): **{len(blocked)}**",
                f"- needs_work: **{len(needs)}**",
                "",
                "## Uncovered ready (manual follow-up)",
                "",
                *[f"- `{x}`" for x in uncovered[:80]],
                "",
                "## Blocked sample (first 40)",
                "",
                *[f"- `{x}`" for x in blocked[:40]],
                "",
                f"... and {max(0, len(blocked)-40)} more blocked.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"wrote {len(written)} specs → {OUT}")
    print(f"pending → {pending}")
    print(f"uncovered ready: {len(uncovered)}")
    if uncovered:
        print("  " + ", ".join(uncovered[:20]))


if __name__ == "__main__":
    main()
