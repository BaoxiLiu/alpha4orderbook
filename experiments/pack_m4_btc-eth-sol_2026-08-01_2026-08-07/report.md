# Factor pack eval

## Run meta

- **symbols**: `['BTCUSDC', 'ETHUSDC', 'SOLUSDC']`
- **start_date**: `2026-08-01`
- **end_date**: `2026-08-07`
- **train_dates**: `['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05']`
- **test_dates**: `['2026-08-06', '2026-08-07']`
- **factor_names**: `['imbalance', 'micro_combo']`
- **factor_specs**: `['/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/configs/factors/imbalance.yaml', '/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/configs/factors/micro_combo.yaml']`
- **dt_seconds**: `1`
- **top_k**: `20`
- **n_detail_rows**: `378`
- **n_failures**: `0`
- **elapsed_seconds**: `4.297`
- **panels_root**: `/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/panels`
- **built_at_utc**: `2026-11-03T01:40:00.719931+00:00`

## Rank IC matrix (mean across days) — factor × horizon × symbol

| spec | factor | horizon_s | symbol | rank_ic | n_days | n_obs_sum |
| --- | --- | --- | --- | --- | --- | --- |
| imbalance | imb_1 | 1 | BTCUSDC | 0.278567 | 7 | 141524 |
| imbalance | imb_1 | 1 | ETHUSDC | 0.266223 | 7 | 141524 |
| imbalance | imb_1 | 1 | SOLUSDC | 0.227793 | 7 | 141522 |
| imbalance | imb_1 | 5 | BTCUSDC | 0.232793 | 7 | 141496 |
| imbalance | imb_1 | 5 | ETHUSDC | 0.178782 | 7 | 141496 |
| imbalance | imb_1 | 5 | SOLUSDC | 0.261489 | 7 | 141494 |
| imbalance | imb_1 | 10 | BTCUSDC | 0.17617 | 7 | 141461 |
| imbalance | imb_1 | 10 | ETHUSDC | 0.122287 | 7 | 141461 |
| imbalance | imb_1 | 10 | SOLUSDC | 0.232372 | 7 | 141459 |
| imbalance | imb_1 | 30 | BTCUSDC | 0.094025 | 7 | 141321 |
| imbalance | imb_1 | 30 | ETHUSDC | 0.0563357 | 7 | 141321 |
| imbalance | imb_1 | 30 | SOLUSDC | 0.165783 | 7 | 141319 |
| imbalance | imb_1 | 60 | BTCUSDC | 0.0461301 | 7 | 141111 |
| imbalance | imb_1 | 60 | ETHUSDC | 0.0407322 | 7 | 141111 |
| imbalance | imb_1 | 60 | SOLUSDC | 0.114758 | 7 | 141109 |
| imbalance | imb_1 | 300 | BTCUSDC | 0.0199037 | 7 | 139431 |
| imbalance | imb_1 | 300 | ETHUSDC | 0.0165494 | 7 | 139431 |
| imbalance | imb_1 | 300 | SOLUSDC | 0.0678243 | 7 | 139429 |
| imbalance | imb_5 | 1 | BTCUSDC | 0.253233 | 7 | 141524 |
| imbalance | imb_5 | 1 | ETHUSDC | 0.22697 | 7 | 141524 |
| imbalance | imb_5 | 1 | SOLUSDC | 0.120598 | 7 | 141522 |
| imbalance | imb_5 | 5 | BTCUSDC | 0.211295 | 7 | 141496 |
| imbalance | imb_5 | 5 | ETHUSDC | 0.152598 | 7 | 141496 |
| imbalance | imb_5 | 5 | SOLUSDC | 0.145515 | 7 | 141494 |
| imbalance | imb_5 | 10 | BTCUSDC | 0.155677 | 7 | 141461 |
| imbalance | imb_5 | 10 | ETHUSDC | 0.105641 | 7 | 141461 |
| imbalance | imb_5 | 10 | SOLUSDC | 0.135493 | 7 | 141459 |
| imbalance | imb_5 | 30 | BTCUSDC | 0.0800008 | 7 | 141321 |
| imbalance | imb_5 | 30 | ETHUSDC | 0.0538643 | 7 | 141321 |
| imbalance | imb_5 | 30 | SOLUSDC | 0.0983193 | 7 | 141319 |
| imbalance | imb_5 | 60 | BTCUSDC | 0.0369953 | 7 | 141111 |
| imbalance | imb_5 | 60 | ETHUSDC | 0.0452937 | 7 | 141111 |
| imbalance | imb_5 | 60 | SOLUSDC | 0.0786191 | 7 | 141109 |
| imbalance | imb_5 | 300 | BTCUSDC | 0.0294526 | 7 | 139431 |
| imbalance | imb_5 | 300 | ETHUSDC | 0.0131052 | 7 | 139431 |
| imbalance | imb_5 | 300 | SOLUSDC | 0.0478067 | 7 | 139429 |
| micro_combo | micro_combo | 1 | BTCUSDC | 0.253252 | 7 | 141524 |
| micro_combo | micro_combo | 1 | ETHUSDC | 0.227059 | 7 | 141524 |
| micro_combo | micro_combo | 1 | SOLUSDC | 0.137589 | 7 | 141522 |
| micro_combo | micro_combo | 5 | BTCUSDC | 0.211311 | 7 | 141496 |
| micro_combo | micro_combo | 5 | ETHUSDC | 0.15266 | 7 | 141496 |
| micro_combo | micro_combo | 5 | SOLUSDC | 0.165075 | 7 | 141494 |
| micro_combo | micro_combo | 10 | BTCUSDC | 0.155691 | 7 | 141461 |
| micro_combo | micro_combo | 10 | ETHUSDC | 0.105679 | 7 | 141461 |
| micro_combo | micro_combo | 10 | SOLUSDC | 0.152753 | 7 | 141459 |
| micro_combo | micro_combo | 30 | BTCUSDC | 0.0800093 | 7 | 141321 |
| micro_combo | micro_combo | 30 | ETHUSDC | 0.0538771 | 7 | 141321 |
| micro_combo | micro_combo | 30 | SOLUSDC | 0.110599 | 7 | 141319 |
| micro_combo | micro_combo | 60 | BTCUSDC | 0.0370009 | 7 | 141111 |
| micro_combo | micro_combo | 60 | ETHUSDC | 0.0452958 | 7 | 141111 |
| micro_combo | micro_combo | 60 | SOLUSDC | 0.0866147 | 7 | 141109 |
| micro_combo | micro_combo | 300 | BTCUSDC | 0.02945 | 7 | 139431 |
| micro_combo | micro_combo | 300 | ETHUSDC | 0.0131143 | 7 | 139431 |
| micro_combo | micro_combo | 300 | SOLUSDC | 0.0527852 | 7 | 139429 |

### Pivot (rows=spec/factor/horizon, cols=symbol)

| spec | factor | horizon_s | BTCUSDC | ETHUSDC | SOLUSDC |
| --- | --- | --- | --- | --- | --- |
| imbalance | imb_1 | 1 | 0.278567 | 0.266223 | 0.227793 |
| imbalance | imb_1 | 5 | 0.232793 | 0.178782 | 0.261489 |
| imbalance | imb_1 | 10 | 0.17617 | 0.122287 | 0.232372 |
| imbalance | imb_1 | 30 | 0.094025 | 0.0563357 | 0.165783 |
| imbalance | imb_1 | 60 | 0.0461301 | 0.0407322 | 0.114758 |
| imbalance | imb_1 | 300 | 0.0199037 | 0.0165494 | 0.0678243 |
| imbalance | imb_5 | 1 | 0.253233 | 0.22697 | 0.120598 |
| imbalance | imb_5 | 5 | 0.211295 | 0.152598 | 0.145515 |
| imbalance | imb_5 | 10 | 0.155677 | 0.105641 | 0.135493 |
| imbalance | imb_5 | 30 | 0.0800008 | 0.0538643 | 0.0983193 |
| imbalance | imb_5 | 60 | 0.0369953 | 0.0452937 | 0.0786191 |
| imbalance | imb_5 | 300 | 0.0294526 | 0.0131052 | 0.0478067 |
| micro_combo | micro_combo | 1 | 0.253252 | 0.227059 | 0.137589 |
| micro_combo | micro_combo | 5 | 0.211311 | 0.15266 | 0.165075 |
| micro_combo | micro_combo | 10 | 0.155691 | 0.105679 | 0.152753 |
| micro_combo | micro_combo | 30 | 0.0800093 | 0.0538771 | 0.110599 |
| micro_combo | micro_combo | 60 | 0.0370009 | 0.0452958 | 0.0866147 |
| micro_combo | micro_combo | 300 | 0.02945 | 0.0131143 | 0.0527852 |

## Calendar-day time split

> Train = first 5 calendar days `['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05']`; test = last 2 days `['2026-08-06', '2026-08-07']`. IC values are means of per-day Rank ICs (not pooled ticks).

| spec | factor | horizon_s | split | n_days | mean_rank_ic | mean_n |
| --- | --- | --- | --- | --- | --- | --- |
| imbalance | imb_1 | 1 | train | 5 | 0.25584 | 13358.7 |
| imbalance | imb_1 | 1 | test | 2 | 0.261747 | 37364.8 |
| imbalance | imb_1 | 5 | train | 5 | 0.221645 | 13354.7 |
| imbalance | imb_1 | 5 | test | 2 | 0.23113 | 37360.8 |
| imbalance | imb_1 | 10 | train | 5 | 0.172541 | 13349.7 |
| imbalance | imb_1 | 10 | test | 2 | 0.187949 | 37355.8 |
| imbalance | imb_1 | 30 | train | 5 | 0.101172 | 13329.7 |
| imbalance | imb_1 | 30 | test | 2 | 0.115904 | 37335.8 |
| imbalance | imb_1 | 60 | train | 5 | 0.0668196 | 13299.7 |
| imbalance | imb_1 | 60 | test | 2 | 0.0681749 | 37305.8 |
| imbalance | imb_1 | 300 | train | 5 | 0.036963 | 13059.7 |
| imbalance | imb_1 | 300 | test | 2 | 0.0292494 | 37065.8 |
| imbalance | imb_5 | 1 | train | 5 | 0.196892 | 13358.7 |
| imbalance | imb_5 | 1 | test | 2 | 0.208705 | 37364.8 |
| imbalance | imb_5 | 5 | train | 5 | 0.163489 | 13354.7 |
| imbalance | imb_5 | 5 | test | 2 | 0.185586 | 37360.8 |
| imbalance | imb_5 | 10 | train | 5 | 0.124297 | 13349.7 |
| imbalance | imb_5 | 10 | test | 2 | 0.152203 | 37355.8 |
| imbalance | imb_5 | 30 | train | 5 | 0.0689993 | 13329.7 |
| imbalance | imb_5 | 30 | test | 2 | 0.0983836 | 37335.8 |
| imbalance | imb_5 | 60 | train | 5 | 0.0502767 | 13299.7 |
| imbalance | imb_5 | 60 | test | 2 | 0.0620344 | 37305.8 |
| imbalance | imb_5 | 300 | train | 5 | 0.0322053 | 13059.7 |
| imbalance | imb_5 | 300 | test | 2 | 0.024912 | 37065.8 |
| micro_combo | micro_combo | 1 | train | 5 | 0.202527 | 13358.7 |
| micro_combo | micro_combo | 1 | test | 2 | 0.214567 | 37364.8 |
| micro_combo | micro_combo | 5 | train | 5 | 0.170058 | 13354.7 |
| micro_combo | micro_combo | 5 | test | 2 | 0.192074 | 37360.8 |
| micro_combo | micro_combo | 10 | train | 5 | 0.130126 | 13349.7 |
| micro_combo | micro_combo | 10 | test | 2 | 0.157828 | 37355.8 |
| micro_combo | micro_combo | 30 | train | 5 | 0.0733175 | 13329.7 |
| micro_combo | micro_combo | 30 | test | 2 | 0.101939 | 37335.8 |
| micro_combo | micro_combo | 60 | train | 5 | 0.0531602 | 13299.7 |
| micro_combo | micro_combo | 60 | test | 2 | 0.0641627 | 37305.8 |
| micro_combo | micro_combo | 300 | train | 5 | 0.0339099 | 13059.7 |
| micro_combo | micro_combo | 300 | test | 2 | 0.0264663 | 37065.8 |

## Panel load coverage

- **loaded ok**: `21`
- **missing / unusable**: `0`

## Notes

- Built on precomputed L1 day panels; no LOB tick replay per factor.
- Single-week / 3-symbol slice — expand universe in later M4 runs.
- Rank IC ≠ tradable edge.

---
Generated by `python -m a4ob.cli run-eval-pack`.