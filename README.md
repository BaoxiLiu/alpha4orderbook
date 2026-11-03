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
# or: python -m a4ob smoke ...
python -m a4ob.cli eval --config configs/sealed.yaml   # smoke-backed stub
```

Smoke will prefer `smoke.date/hour` in the config (default BTCUSDC `2026-08-01/00`). If that hour has no snapshot rows, it auto-selects the first sealed-window hour that does, rebuilds L2, samples a 1s top-20 panel, computes baseline imbalance + mid forward returns, and writes:

`experiments/smoke_<symbol>_<date>_<hour>_<utc>/report.md`

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
