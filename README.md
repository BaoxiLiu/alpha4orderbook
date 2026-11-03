# alpha4orderbook (`a4ob`)

Long-lived **orderbook factor evaluation** framework for CryptoHFTData Binance USDC perps.

**Product goal:** declare a multi-field orderbook factor (possibly multi-step) → run a fast backtest on a precomputed research panel → emit a complete report.

Layers (do **not** tick-replay every factor on full depth for all coins):

| Layer | Role |
|---|---|
| **L0** | Book rebuild from snapshot + incremental updates (per symbol-hour) |
| **L1** | Research panel: fixed clock (default 1s), top-K depth + mid/spread cores |
| **L2** | Factor eval on the panel (Rank IC × horizons × symbol, …) |
| **L3** | Optional execution realism later (not required for predictive IC) |

Sealed research window: **2026-08-01 → 2026-10-10**, 13 symbols — see `configs/sealed.yaml`.

## Install

```bash
# from repo root; use an env with pyarrow/pandas/numpy/pyyaml
pip install -e .
```

Light hard deps only: `numpy`, `pandas`, `pyarrow`, `pyyaml`.  
`hftbacktest` / Nautilus are **not** required (see `third_party/NOTES.md`).

## Quick smoke

```bash
python -m a4ob.cli smoke --config configs/sealed.yaml
python -m a4ob.cli eval --config configs/sealed.yaml   # smoke-backed stub
```

Smoke prefers an existing day panel under `panels/` when present; otherwise it rebuilds one hour (config `smoke.date/hour`, with fallback to the first hour that has a snapshot).

## Build a day panel (M2)

```bash
python -m a4ob.cli build-panel --symbol BTCUSDC --date 2026-08-01
# debug one hour:
python -m a4ob.cli build-panel --symbol BTCUSDC --date 2026-08-01 --hour 21
python -m a4ob.cli eval --symbol BTCUSDC --date 2026-08-01
```

Output (gitignored under `panels/`):

```
panels/dt=1s/K=20/symbol=BTCUSDC/date=2026-08-01/panel.parquet
panels/dt=1s/K=20/symbol=BTCUSDC/date=2026-08-01/manifest.json
```

**Cross-hour policy (`CARRY_FORWARD_AFTER_SNAPSHOT`):** skip missing hours and update-only hours before the first snapshot; after the book is ready, carry the in-memory L2 book into later hours (including update-only); a later snapshot resyncs.

## Factor Spec (YAML contract — target shape)

Factors are declared as specs the Runner will resolve (M3). Multi-field / multi-step deps are first-class:

```yaml
factor:
  name: weighted_imbalance_ofi
  version: "0.1.0"
  frequency: 1s          # must align to panel clock (or asof-join)
  output:
    - col: wimb_ofi
      dtype: float64

  # Fields required from the L1 panel (no full-depth replay)
  requires:
    panel:
      - bid_sz_0..bid_sz_19
      - ask_sz_0..ask_sz_19
      - mid
      - best_bid
      - best_ask
    # Optional side inputs joined by (ts, symbol)
    services:
      - name: trades_1s
        fields: [buy_qty, sell_qty]

  # Multi-step compute graph (cached, idempotent — M5)
  steps:
    - id: depth_imb
      op: imbalance
      params: { levels: 20, weights: linear }
      inputs: { panel: [bid_sz_*, ask_sz_*] }
      outputs: [imb20]
    - id: ofi_core
      op: cont_ofi
      inputs: { panel: [bid_sz_0, ask_sz_0, best_bid, best_ask] }
      outputs: [ofi]
    - id: combine
      op: expr
      expr: "0.7 * imb20 + 0.3 * tanh(ofi)"
      inputs: [imb20, ofi]
      outputs: [wimb_ofi]

  labels:
    price: mid
    horizons_seconds: [1, 5, 10, 30, 60, 300]

  eval:
    metrics: [rank_ic, ic_decay]
    splits: { method: time, fractions: [0.6, 0.2, 0.2] }
```

Today only baseline `imbalance` is implemented as a panel transform (`a4ob.factors.baseline`). The Spec runner lands in M3.

## Layout

```
src/a4ob/
  data/     # CryptoHFTData paths + hour reader
  book/     # L0 L2 rebuild
  panel/    # L1 schema / helpers
  factors/  # panel factor adapters
  labels/   # forward returns
  eval/     # Rank IC suite
  report/   # Markdown reports
  cli.py
configs/sealed.yaml
third_party/NOTES.md
experiments/          # run outputs (panel parquet gitignored)
```

## Roadmap

Project-store docs (strategy, survey, inventory) live beside this repo’s planning notes. Milestones: M0 scaffold → M1 smoke → M2 daily panels → M3 Factor Spec runner → M4 full-universe panels → M5 multi-service orchestration → M6 optional L3 → M7 mining on the same runner.
