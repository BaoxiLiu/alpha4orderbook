# Factor pack eval

## Run meta

- **symbols**: `['BTCUSDC', 'ETHUSDC', 'SOLUSDC']`
- **start_date**: `2026-08-01`
- **end_date**: `2026-08-07`
- **train_dates**: `['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05']`
- **test_dates**: `['2026-08-06', '2026-08-07']`
- **factor_names**: `['spread_bp', 'microprice_offset_bp', 'cont_ofi_panel_1s']`
- **factor_specs**: `['/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/configs/factors/spread_bp.yaml', '/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/configs/factors/microprice_offset_bp.yaml', '/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/configs/factors/cont_ofi_panel_1s.yaml']`
- **dt_seconds**: `1`
- **top_k**: `20`
- **n_detail_rows**: `378`
- **n_failures**: `0`
- **elapsed_seconds**: `4.822`
- **panels_root**: `/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/panels`
- **built_at_utc**: `2026-11-03T05:09:37.906718+00:00`

## Rank IC matrix (mean across days) — factor × horizon × symbol

| spec | factor | horizon_s | symbol | rank_ic | n_days | n_obs_sum |
| --- | --- | --- | --- | --- | --- | --- |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | 0.170226 | 7 | 141517 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | 0.168937 | 7 | 141517 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | 0.119352 | 7 | 141515 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | 0.122282 | 7 | 141489 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | 0.0964916 | 7 | 141489 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | 0.103753 | 7 | 141487 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | 0.0893792 | 7 | 141454 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | 0.064001 | 7 | 141454 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | 0.0803975 | 7 | 141452 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | 0.0489055 | 7 | 141314 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | 0.0366896 | 7 | 141314 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | 0.0470963 | 7 | 141312 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | 0.0325649 | 7 | 141104 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | 0.0206428 | 7 | 141104 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | 0.034294 | 7 | 141102 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | 0.0115531 | 7 | 139424 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | 0.0097441 | 7 | 139424 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | 0.0137249 | 7 | 139422 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 0.278499 | 7 | 141524 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 0.266092 | 7 | 141524 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 0.227759 | 7 | 141522 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 0.23268 | 7 | 141496 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 0.178738 | 7 | 141496 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 0.261516 | 7 | 141494 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 0.176106 | 7 | 141461 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 0.122194 | 7 | 141461 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 0.232417 | 7 | 141459 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 0.0940389 | 7 | 141321 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 0.0562444 | 7 | 141321 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 0.165833 | 7 | 141319 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 0.0462044 | 7 | 141111 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 0.0407301 | 7 | 141111 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 0.114785 | 7 | 141109 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 0.0199186 | 7 | 139431 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 0.016714 | 7 | 139431 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 0.0677865 | 7 | 139429 |
| spread_bp | spread_bp | 1 | BTCUSDC | 0.016763 | 7 | 141524 |
| spread_bp | spread_bp | 1 | ETHUSDC | 0.0217858 | 7 | 141524 |
| spread_bp | spread_bp | 1 | SOLUSDC | 0.0219309 | 7 | 141522 |
| spread_bp | spread_bp | 5 | BTCUSDC | 0.044533 | 7 | 141496 |
| spread_bp | spread_bp | 5 | ETHUSDC | 0.053178 | 7 | 141496 |
| spread_bp | spread_bp | 5 | SOLUSDC | 0.0513373 | 7 | 141494 |
| spread_bp | spread_bp | 10 | BTCUSDC | 0.0649135 | 7 | 141461 |
| spread_bp | spread_bp | 10 | ETHUSDC | 0.0744984 | 7 | 141461 |
| spread_bp | spread_bp | 10 | SOLUSDC | 0.0695604 | 7 | 141459 |
| spread_bp | spread_bp | 30 | BTCUSDC | 0.108553 | 7 | 141321 |
| spread_bp | spread_bp | 30 | ETHUSDC | 0.123076 | 7 | 141321 |
| spread_bp | spread_bp | 30 | SOLUSDC | 0.121372 | 7 | 141319 |
| spread_bp | spread_bp | 60 | BTCUSDC | 0.156365 | 7 | 141111 |
| spread_bp | spread_bp | 60 | ETHUSDC | 0.174563 | 7 | 141111 |
| spread_bp | spread_bp | 60 | SOLUSDC | 0.164962 | 7 | 141109 |
| spread_bp | spread_bp | 300 | BTCUSDC | 0.296396 | 7 | 139431 |
| spread_bp | spread_bp | 300 | ETHUSDC | 0.342075 | 7 | 139431 |
| spread_bp | spread_bp | 300 | SOLUSDC | 0.315029 | 7 | 139429 |

### Pivot (rows=spec/factor/horizon, cols=symbol)

| spec | factor | horizon_s | BTCUSDC | ETHUSDC | SOLUSDC |
| --- | --- | --- | --- | --- | --- |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | 0.170226 | 0.168937 | 0.119352 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | 0.122282 | 0.0964916 | 0.103753 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | 0.0893792 | 0.064001 | 0.0803975 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | 0.0489055 | 0.0366896 | 0.0470963 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | 0.0325649 | 0.0206428 | 0.034294 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | 0.0115531 | 0.0097441 | 0.0137249 |
| microprice_offset_bp | microprice_offset_bp | 1 | 0.278499 | 0.266092 | 0.227759 |
| microprice_offset_bp | microprice_offset_bp | 5 | 0.23268 | 0.178738 | 0.261516 |
| microprice_offset_bp | microprice_offset_bp | 10 | 0.176106 | 0.122194 | 0.232417 |
| microprice_offset_bp | microprice_offset_bp | 30 | 0.0940389 | 0.0562444 | 0.165833 |
| microprice_offset_bp | microprice_offset_bp | 60 | 0.0462044 | 0.0407301 | 0.114785 |
| microprice_offset_bp | microprice_offset_bp | 300 | 0.0199186 | 0.016714 | 0.0677865 |
| spread_bp | spread_bp | 1 | 0.016763 | 0.0217858 | 0.0219309 |
| spread_bp | spread_bp | 5 | 0.044533 | 0.053178 | 0.0513373 |
| spread_bp | spread_bp | 10 | 0.0649135 | 0.0744984 | 0.0695604 |
| spread_bp | spread_bp | 30 | 0.108553 | 0.123076 | 0.121372 |
| spread_bp | spread_bp | 60 | 0.156365 | 0.174563 | 0.164962 |
| spread_bp | spread_bp | 300 | 0.296396 | 0.342075 | 0.315029 |

## Calendar-day time split

> Train = first 5 calendar days `['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05']`; test = last 2 days `['2026-08-06', '2026-08-07']`. IC values are means of per-day Rank ICs (not pooled ticks).

| spec | factor | horizon_s | split | n_days | mean_rank_ic | mean_n |
| --- | --- | --- | --- | --- | --- | --- |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | train | 5 | 0.150728 | 13357.7 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | test | 2 | 0.158113 | 37363.8 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | train | 5 | 0.105757 | 13353.7 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | test | 2 | 0.11189 | 37359.8 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | train | 5 | 0.0759506 | 13348.7 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | test | 2 | 0.0828642 | 37354.8 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | train | 5 | 0.0429144 | 13328.7 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | test | 2 | 0.0475205 | 37334.8 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | train | 5 | 0.0276901 | 13298.7 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | test | 2 | 0.0328603 | 37304.8 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | train | 5 | 0.0112884 | 13058.7 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | test | 2 | 0.0126382 | 37064.8 |
| microprice_offset_bp | microprice_offset_bp | 1 | train | 5 | 0.255766 | 13358.7 |
| microprice_offset_bp | microprice_offset_bp | 1 | test | 2 | 0.261659 | 37364.8 |
| microprice_offset_bp | microprice_offset_bp | 5 | train | 5 | 0.22157 | 13354.7 |
| microprice_offset_bp | microprice_offset_bp | 5 | test | 2 | 0.231164 | 37360.8 |
| microprice_offset_bp | microprice_offset_bp | 10 | train | 5 | 0.172477 | 13349.7 |
| microprice_offset_bp | microprice_offset_bp | 10 | test | 2 | 0.187978 | 37355.8 |
| microprice_offset_bp | microprice_offset_bp | 30 | train | 5 | 0.101153 | 13329.7 |
| microprice_offset_bp | microprice_offset_bp | 30 | test | 2 | 0.115919 | 37335.8 |
| microprice_offset_bp | microprice_offset_bp | 60 | train | 5 | 0.0668335 | 13299.7 |
| microprice_offset_bp | microprice_offset_bp | 60 | test | 2 | 0.0682552 | 37305.8 |
| microprice_offset_bp | microprice_offset_bp | 300 | train | 5 | 0.0369773 | 13059.7 |
| microprice_offset_bp | microprice_offset_bp | 300 | test | 2 | 0.0293791 | 37065.8 |
| spread_bp | spread_bp | 1 | train | 5 | 0.0236628 | 13358.7 |
| spread_bp | spread_bp | 1 | test | 2 | 0.0114027 | 37364.8 |
| spread_bp | spread_bp | 5 | train | 5 | 0.0582785 | 13354.7 |
| spread_bp | spread_bp | 5 | test | 2 | 0.0281935 | 37360.8 |
| spread_bp | spread_bp | 10 | train | 5 | 0.0808741 | 13349.7 |
| spread_bp | spread_bp | 10 | test | 2 | 0.0416157 | 37355.8 |
| spread_bp | spread_bp | 30 | train | 5 | 0.135645 | 13329.7 |
| spread_bp | spread_bp | 30 | test | 2 | 0.0727218 | 37335.8 |
| spread_bp | spread_bp | 60 | train | 5 | 0.190101 | 13299.7 |
| spread_bp | spread_bp | 60 | test | 2 | 0.103285 | 37305.8 |
| spread_bp | spread_bp | 300 | train | 5 | 0.359101 | 13059.7 |
| spread_bp | spread_bp | 300 | test | 2 | 0.214663 | 37065.8 |

## Panel load coverage

- **loaded ok**: `21`
- **missing / unusable**: `0`

## Notes

- Built on precomputed L1 day panels; no LOB tick replay per factor.
- Single-week / 3-symbol slice — expand universe in later M4 runs.
- Rank IC ≠ tradable edge.

---
Generated by `python -m a4ob.cli run-eval-pack`.