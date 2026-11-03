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

## Factor Spec + run-eval (M3)

Declare factors as YAML Specs under `configs/factors/`. The runner loads a day panel, applies Spec steps (panel ops / optional asof-join), scores Rank IC, and writes a report — **no full-depth tick replay**.

```bash
python -m a4ob.cli run-eval \
  --config configs/sealed.yaml \
  --factor configs/factors/imbalance.yaml \
  --symbol BTCUSDC --date 2026-08-01

python -m a4ob.cli run-eval \
  --factor configs/factors/micro_combo.yaml \
  --symbol BTCUSDC --date 2026-08-01
```

### Schema (implemented)

```yaml
factor:
  name: micro_combo
  version: "0.1.0"
  frequency: 1s
  description: optional prose
  output:
    - col: micro_combo
      dtype: float64
  requires:
    panel: [bid_sz_0, ask_sz_0, best_bid, best_ask, best_bid_sz, best_ask_sz, mid]
    # optional external series asof-joined onto panel.ts_ms
    # external:
    #   - name: toy_signal
    #     path: /path/to/signal.parquet
    #     ts_col: ts_ms
    #     value_col: signal
    #     direction: backward
  steps:
    - id: imb5
      op: imbalance          # built-ins: imbalance, microprice_dev, spread_bps, expr, external_asof
      params: { levels: 5, out: imb_5 }
      outputs: [imb_5]
    - id: mdev
      op: microprice_dev
      params: { out: micro_dev }
      outputs: [micro_dev]
    - id: combine
      op: expr
      expr: "0.7 * imb_5 + 0.3 * tanh(1000.0 * micro_dev)"
      inputs: [imb_5, micro_dev]
      outputs: [micro_combo]
  labels:
    price: mid
    horizons_seconds: [1, 5, 10, 30, 60, 300]
  eval:
    metrics: [rank_ic, coverage, ic_decay]
    primary_factor: micro_combo
    splits:
      method: time
      fractions: [0.6, 0.2, 0.2]
```

Shipped examples: `configs/factors/imbalance.yaml`, `configs/factors/micro_combo.yaml`.

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
