# GitHub survey: open-source HF orderbook factors

- Written: 2026-11-04
- Goal: formula-level LOB / crypto / futures / equity microstructure alphas portable to α4 L1 panels (`dt=1s`, `top_k=20` book + `trades_features` sidecars)
- Complements earlier framework survey: [`orderbook-framework-survey.md`](orderbook-framework-survey.md)
- Current library before this intake: Universe **165** / Core **74** (incl. NH 51)

## Fit legend (vs Seagate α4 panels)

| Tag | Meaning |
|---|---|
| **panel** | Computable from 1s top-20 book alone |
| **book+trades** | Needs `trades_features` / aggressor 1s bars |
| **event** | Needs true L2/L3 event diffs (cancel/add rates, exact multi-level OFI) — blocked for now |
| **exec** | Backtester / MM engine — borrow formulas only |
| **dup** | Already covered by Universe Spec (or near-duplicate) |

---

## Repos surveyed (factor-bearing)

| Repo | License | Stars (approx) | Factor formulas (high-signal) | Fit | Notes |
|---|---|---:|---|---|---|
| [twowaymind/orderflow-metrics](https://github.com/twowaymind/orderflow-metrics) | MIT | small | L1 OFI (CKS), depth imbalance, trade imbalance, **depth-weighted multi-level OFI**, weighted mid, relative spread bps | panel (snapshot OFI≈panel); **mlofi=event** | Cleanest formula reference; TS but trivial to port |
| [lobkit](https://pypi.org/project/lobkit/) / features | MIT (PyPI) | — | mid, spread, queue imbalance, microprice, single/multi-level OFI, Stoikov micro-price Markov | panel / **event** for exact OFI | Research kit; multi-level OFI needs event book |
| [gautierpetit/microalpha-engine](https://github.com/gautierpetit/microalpha-engine) | — | small | `queue_imbalance_best`, `microprice_deviation`, `ofi_best`, depth_imbalance_3/5/10, roll OFI, mid vol | panel / event | LOBSTER C++ features; names map to our imb/micro/OFI family (**dup**) |
| [bhardwaj-kunal/order-flow-imbalance](https://github.com/bhardwaj-kunal/order-flow-imbalance) | — | ~0 | Cont–Kukanov–Stoikov OFI + β regression | panel approx | Definition reference for `cont_ofi_panel_1s` (**dup**) |
| [tejeshvenkat/microstructure-alpha](https://github.com/tejeshvenkat/microstructure-alpha) | — | ~1 | CKS OFI, queue imbalance, microprice (unit-tested) | panel approx | Synthetic LOB; good tests |
| [NightCoderLJ/Order-Book-Microstructure-Research](https://github.com/NightCoderLJ/Order-Book-Microstructure-Research) | none listed | ~0 | OFI, QI, microprice, weighted microprice, **liquidity pressure**, arrival/cancel rate, trade imbalance | panel / **event** for rates | Pipeline template; pressure & weighted micro = Batch1 |
| [sajeev1003/Order-Flow-To-Execution](https://github.com/sajeev1003/Order-Flow-To-Execution) | MIT | ~1 | TOB imb, microprice, Cont OFI, aggressor trade imb, quote/trade intensity, depth ±1/2/5%, TOD | panel / book+trades | Binance USD-M research hygiene; features mostly **dup**/NH |
| [rwrrioe/l2](https://github.com/rwrrioe/l2) | — | small | OFI, microprice/weighted mid | event rebuild | Correctness-focused Binance L2 engine |
| [Aliipou/mm-live](https://github.com/Aliipou/mm-live) | — | — | Kalman FV, OFI EMA, Stoikov microprice, dual EWMA vol, composite edge | panel-ish / **exec** | MM system; borrow signal defs only |
| [ianfigueroa/Titan](https://github.com/ianfigueroa/Titan) | MIT | — | spread bps, imbalance, trade VWAP, buy/sell vol | book+trades | Futures analytics service |
| [zhd173/nanoARB](https://github.com/zhd173/nanoARB) | — | — | Microprice, OFI, VPIN, book imbalance | panel / **event** (VPIN) | CME futures Rust LOB |
| [Arshad-13/CryptoIntel-MCP](https://github.com/Arshad-13/CryptoIntel-MCP) | — | — | OFI, OBI, microprice, VPIN | panel / event | MCP wrapper; thin formula depth |
| [leionion/orderbook-imbalance-indicator-hft](https://github.com/leionion/orderbook-imbalance-indicator-hft) | — | ~18 | Weighted imbalance over snapshot+delta | panel | Small HFT indicator pattern |
| [nkaz001/hftbacktest](https://github.com/nkaz001/hftbacktest) | MIT | ~5k | Depth API inside strategies | **exec** | CryptoHFTData converter PR; not a factor catalog |
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | LGPL-3.0 | ~31k | OrderBookImbalance demo | **exec** | Too heavy for IC host |
| [study-holic/q1-lob-alpha](https://github.com/study-holic/q1-lob-alpha) | MIT | ~0 | OFI, QI, microprice, spread + **IC protocol** | methods | Borrow eval gates, not new formulas |
| [Evintkoo/orderflow-rs](https://github.com/Evintkoo/orderflow-rs) | MIT | ~1 | Multi-level OFI + 87 indicators | event / FX | IC batch ideas |

---

## Prioritized shortlist for α4

### Batch 1 — admit now (panel or book+trades; not already Spec’d)

| ID | Formula (brief) | Source inspiration | Inputs | Status |
|---|---|---|---|---|
| `gh_weighted_depth_imb_l{5,10}` | Σdecayⁱ·sz imbalance | orderflow-metrics / lobkit | panel | **Spec’d** |
| `gh_liquidity_pressure_l5` | depth_imb / rel_spread | NightCoderLJ | panel | **Spec’d** |
| `gh_ofi_over_depth` | Cont panel OFI / avg touch qty | Cont 2014 + orderflow-metrics | panel | **Spec’d** |
| `gh_book_vwap_offset_bp_l5` | both-side top-5 VWAP − mid (bp) | weighted microprice family | panel | **Spec’d** |
| `gh_relative_spread_depth` | spread / (mid·touch_depth) | orderflow-metrics relative spread × depth | panel | **Spec’d** |
| `gh_trade_vs_depth` | `nh_ti_1s` / log1p(touch) | sajeev intensity × depth | book+trades | **Spec’d** |
| `gh_kyle_lambda_30s` | roll Σ\|Δmid_bp\| / Σ\|signed_vol\| | classic Kyle proxy + NH signed vol | book+trades | **Spec’d** |

### Batch 2 — later (need event LOB or careful design)

| Idea | Why blocked / deferred |
|---|---|
| Exact multi-level OFI / depthWeightedOFI | Needs per-level event transitions, not 1s snapshots |
| Arrival / cancel rates | Event message types absent on panel |
| Stoikov Markov micro-price | Needs fitted transition matrix on (spread, imbalance) states |
| VPIN / equal-volume buckets | Needs volume-clock trades bucketing Spec |
| Cross-venue lead-lag (lobkit) | Multi-symbol / multi-venue |
| Funding / mark_price factors | `mark_price` parquet not joined |

### Already covered (do not re-port)

L1/L3/L5/L10 imbalance, microprice offset / spread frac / mom, `cont_ofi_panel_1s`, NH 23+28 trades/value features, depth_imb ticks/bp, HHI / outer share / uniformity / touch ratios, RV / jump / hour cycle.

---

## License / hygiene notes

- Prefer **MIT / Apache** formula ports (reimplement; do not vendor GPL book engines like lob.py).
- Cite paper defs (Cont–Kukanov–Stoikov 2014, Stoikov microprice, Gould–Bonart QI) in Spec `description` / Sources headers.
- Execution-only repos (hftbacktest, Nautilus, mm-live) → **formula borrow only**, no dependency.

---

## Admission log

| Batch | Specs added | Eval window | Universe after | Core after | Notes |
|---|---:|---|---:|---:|---|
| 1 | 8 `gh_*` | BTC/ETH/SOL × 2026-08-01..07 | **173** | **75** | weighted_depth_imb #6–7 (clustered w/ L1 imb → not Core rep); `gh_book_vwap_offset_bp_l5` **new Core rep**; kyle/spread-depth weak |
