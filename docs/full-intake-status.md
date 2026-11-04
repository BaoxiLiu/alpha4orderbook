# Full intake status (book + trades)

- Written: 2026-11-04T00:56:27Z
- Repo: 
- Window: BTCUSDC / ETHUSDC / SOLUSDC × 2026-08-01..07
- Data: CryptoHFTData  +  (+  present on disk, not joined)
- Run: 

## Counts (headline)

| metric | n |
|---|---:|
| **Evaluated (Universe Specs ranked)** | **165** |
| · book-panel Specs | 114 |
| · NH trades-augmented Specs (23 alpha + 28 value) | 51 |
| Rank failures | 0 |
| **Core representatives** | **74** (was 59) |
| · NH factors in Core | 17 |
| **Still blocked / needs_more for Spec+eval** | **~330** inventory rows (event LOB, subsecond tape, cross-symbol, mark_price funding, …) |
| Inventory rows computable now as book+trades 1s (not all Spec'd) | 77 |
| · of which near-covered by NH Spec family | ~13 named overlaps + full NH 51 |
| Out of scope (minute/cicc track) | 97 (official catalog) |

### Unified catalog (legacy L0 tags)

| bucket | n |
|---|---:|
| TOTAL | 602 |
| ready | 111 |
| needs_work | 86 |
| blocked | 308 |
| out_of_scope | 97 |

### Recompute with available CryptoHFTData (this pass)

| computability now | parsed inventory rows | meaning |
|---|---:|---|
|  | 117 | top-K 1s panel only |
|  | 77 | 1s aggressor bars from trades parquet |
|  | 330 | event LOB, <1s windows, VPIN/buckets, cross-symbol, … |
|  | 0 | minute/cicc if parsed |

Parsed markdown rows: **524** (legacy port={'ready': 117, 'needs_work': 91, 'blocked': 316}).

## Trades panel enrich

- Sidecar: 
- Completed: **21/21** (BTC/ETH/SOL × Aug 1–7)
- Features: 51  columns; bid-touch probe for NH value action features

## NH coverage after ingest

| set | before | after |
|---|---|---|
| Alpha 23 in Universe | ~2 approx | **23/23 Spec'd + ranked** |
| Value 28 in Universe | ~7 approx | **28/28 Spec'd + ranked** |
| NH in Core | ~4 approx-only | **17** NH-named representatives |
| NH Spec rank failures | n/a | **0** |

Universe NH count in ranking CSV: **51**.

Top NH ranks:  /  (#3–4),  /  (#6–7),  /  (#17–18),  cluster (#49–56).

## What remains blocked

- True event LOB (cancel/add rates, Cont OFI exact, book_age_ms)
- Subsecond trade windows (100–500ms multilevel print rates)
- Volume-time / VPIN buckets, trailing quota durations
- Cross-symbol BTC features on alt panels
-  stream joins (e.g. funding ) — files exist, not on research panel
- Other inventory  IDs without dedicated Specs (paper:* lag stacks, some flow/micro) — computable, Spec pending; NH covers primary 1s taker space

## Artifacts

-  (165)
-  (static, no CDN)
-  / 
- Store: , , ,

---

## GitHub Batch1 intake (2026-11-04)

- Survey: [`github-orderbook-factor-survey.md`](github-orderbook-factor-survey.md)
- Admitted Specs: **8** `gh_*` (panel + book×trades)
- Universe after: **173** (was 165)
- Core after: **75** (was 74); new Core rep: `gh_book_vwap_offset_bp_l5`
- Strongest new IC: `gh_weighted_depth_imb_l5/l10` ranks **#6–#7** but collinear with `l1_imbalance` cluster
- Weak / low priority: `gh_kyle_lambda_30s`, `gh_relative_spread_depth`
- Still blocked (Batch2): event multi-level OFI, cancel/add rates, VPIN, Stoikov Markov micro-price, mark_price joins
