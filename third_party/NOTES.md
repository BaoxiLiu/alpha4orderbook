# Third-party protocols (attribution only — no vendored engines)

We **do not** hard-depend on hftbacktest / Nautilus / GPL lob.py. Ideas below are
reimplemented under MIT-friendly APIs in `src/a4ob/`.

| Source | What we borrow | Where it lands |
|---|---|---|
| [hftbacktest](https://github.com/nkaz001/hftbacktest) (+ open PR #307 CryptoHFTData converter) | Snapshot-then-update L2 rebuild; event ordering; string price/qty casting; optional L3 later | `book/`, docs |
| [binance-LOB](https://github.com/pfei-sa/binance-LOB) | Binance futures `pu`/`u` continuity / gap → resync rules | `book/rebuild.py` |
| [lob.py](https://github.com/mattermat/lob.py) (GPL) | API *shape* only (`snapshot` + `updates` + top-N) — **not** vendored | `book/l2.py` |
| [q1-lob-alpha](https://github.com/study-holic/q1-lob-alpha) | Rank IC × horizons, decay, IC ≠ PnL separation | `eval/` |
| [Order-Flow-To-Execution](https://github.com/sajeev1003/Order-Flow-To-Execution) | 1s causal panel hygiene, reporting style | `panel/`, `report/` |
| [NightCoderLJ OB research](https://github.com/NightCoderLJ/Order-Book-Microstructure-Research) | Module layout: ingest → book → features → labels → evaluate | package layout |
| Cont–Kukanov–Stoikov OFI notebooks | Baseline formula reference for validation | `factors/` |

CryptoHFTData schema notes also live in the sibling project docs under
`cryptocurrency_quant/doc/data/` (orderbook = one row per price level; group by
event before clearing the book).
