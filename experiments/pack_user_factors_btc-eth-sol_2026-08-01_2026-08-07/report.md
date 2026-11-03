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
- **n_layering_rows**: `2268`
- **n_quantiles**: `5`
- **layering_method**: `ts_within_day`
- **n_failures**: `0`
- **elapsed_seconds**: `5.787`
- **panels_root**: `/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/panels`
- **built_at_utc**: `2026-11-03T12:13:47.615057+00:00`

- Companion HTML charts: `report.html` (Plotly CDN).

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

## Quantile layering (分层收益)

> 分层 = time-series quantiles within each symbol-day (method=`ts_within_day`, Q=5). Equal-day mean of per-day bucket mean forward mid returns; LS = Q_high − Q_low. Order-book depth tags (L3/L5) are unrelated to these quintiles.

### Long-short Q_high − Q_low (equal-day mean)

| spec | factor | horizon_s | symbol | quantile | mean_ret | n_days | n_obs_sum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | LS | 1.39215e-05 | 7 | 56611 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | LS | 2.00079e-05 | 7 | 56612 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | LS | 1.852e-05 | 7 | 56610 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | LS | 2.39099e-05 | 7 | 56603 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | LS | 2.81322e-05 | 7 | 56602 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | LS | 3.46284e-05 | 7 | 56594 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | LS | 2.62249e-05 | 7 | 56588 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | LS | 2.83369e-05 | 7 | 56591 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | LS | 3.71634e-05 | 7 | 56581 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | LS | 2.69352e-05 | 7 | 56556 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | LS | 3.14201e-05 | 7 | 56549 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | LS | 4.14441e-05 | 7 | 56544 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | LS | 2.83996e-05 | 7 | 56509 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | LS | 2.68391e-05 | 7 | 56479 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | LS | 4.3914e-05 | 7 | 56481 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | LS | 2.13757e-05 | 7 | 56055 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | LS | 2.45793e-05 | 7 | 55957 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | LS | 4.10531e-05 | 7 | 56023 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | LS | 2.19179e-05 | 7 | 56614 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | LS | 2.8936e-05 | 7 | 56615 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | LS | 3.27144e-05 | 7 | 56611 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | LS | 4.20556e-05 | 7 | 56607 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | LS | 4.63133e-05 | 7 | 56599 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | LS | 7.87536e-05 | 7 | 56595 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | LS | 4.67232e-05 | 7 | 56595 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | LS | 4.75652e-05 | 7 | 56585 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | LS | 9.40674e-05 | 7 | 56568 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | LS | 4.77081e-05 | 7 | 56564 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | LS | 4.44892e-05 | 7 | 56550 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | LS | 0.000115106 | 7 | 56491 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | LS | 4.02247e-05 | 7 | 56501 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | LS | 4.16322e-05 | 7 | 56456 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | LS | 0.000124016 | 7 | 56379 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | LS | 2.86227e-05 | 7 | 55898 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | LS | 8.90689e-07 | 7 | 55850 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | LS | 0.000176075 | 7 | 55507 |
| spread_bp | spread_bp | 1 | BTCUSDC | LS | 2.29713e-06 | 7 | 56596 |
| spread_bp | spread_bp | 1 | ETHUSDC | LS | 3.27908e-06 | 7 | 56632 |
| spread_bp | spread_bp | 1 | SOLUSDC | LS | 2.89937e-06 | 7 | 56436 |
| spread_bp | spread_bp | 5 | BTCUSDC | LS | 1.13636e-05 | 7 | 56584 |
| spread_bp | spread_bp | 5 | ETHUSDC | LS | 1.72847e-05 | 7 | 56617 |
| spread_bp | spread_bp | 5 | SOLUSDC | LS | 1.57861e-05 | 7 | 56428 |
| spread_bp | spread_bp | 10 | BTCUSDC | LS | 2.28777e-05 | 7 | 56569 |
| spread_bp | spread_bp | 10 | ETHUSDC | LS | 3.45873e-05 | 7 | 56597 |
| spread_bp | spread_bp | 10 | SOLUSDC | LS | 3.19389e-05 | 7 | 56418 |
| spread_bp | spread_bp | 30 | BTCUSDC | LS | 7.27837e-05 | 7 | 56509 |
| spread_bp | spread_bp | 30 | ETHUSDC | LS | 9.96972e-05 | 7 | 56517 |
| spread_bp | spread_bp | 30 | SOLUSDC | LS | 9.8431e-05 | 7 | 56378 |
| spread_bp | spread_bp | 60 | BTCUSDC | LS | 0.000148011 | 7 | 56419 |
| spread_bp | spread_bp | 60 | ETHUSDC | LS | 0.000202903 | 7 | 56418 |
| spread_bp | spread_bp | 60 | SOLUSDC | LS | 0.000193176 | 7 | 56315 |
| spread_bp | spread_bp | 300 | BTCUSDC | LS | 0.000617229 | 7 | 55633 |
| spread_bp | spread_bp | 300 | ETHUSDC | LS | 0.000918496 | 7 | 55623 |
| spread_bp | spread_bp | 300 | SOLUSDC | LS | 0.000819897 | 7 | 55394 |

### Full quantile means

| spec | factor | horizon_s | symbol | quantile | mean_ret | n_days | n_obs_sum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | 1 | -6.89785e-06 | 7 | 28311 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | 2 | -2.12708e-06 | 7 | 28450 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | 3 | 3.39339e-07 | 7 | 28253 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | 4 | 1.34579e-06 | 7 | 28203 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | 5 | 7.02365e-06 | 7 | 28300 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | BTCUSDC | LS | 1.39215e-05 | 7 | 56611 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | 1 | -1.03161e-05 | 7 | 28308 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | 2 | -1.62773e-06 | 7 | 28301 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | 3 | -2.0411e-07 | 7 | 28301 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | 4 | 1.46951e-06 | 7 | 28303 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | 5 | 9.69179e-06 | 7 | 28304 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | ETHUSDC | LS | 2.00079e-05 | 7 | 56612 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | 1 | -9.8142e-06 | 7 | 28306 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | 2 | -1.76995e-06 | 7 | 28309 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | 3 | 1.38434e-08 | 7 | 28298 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | 4 | 1.9124e-06 | 7 | 28298 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | 5 | 8.70578e-06 | 7 | 28304 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 1 | SOLUSDC | LS | 1.852e-05 | 7 | 56610 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | 1 | -1.19181e-05 | 7 | 28308 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | 2 | -5.10361e-06 | 7 | 28447 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | 3 | -1.31177e-07 | 7 | 28245 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | 4 | 3.5277e-06 | 7 | 28194 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | 5 | 1.19918e-05 | 7 | 28295 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | BTCUSDC | LS | 2.39099e-05 | 7 | 56603 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | 1 | -1.50587e-05 | 7 | 28301 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | 2 | -4.35983e-06 | 7 | 28295 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | 3 | -8.10783e-07 | 7 | 28296 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | 4 | 2.24105e-06 | 7 | 28296 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | 5 | 1.30735e-05 | 7 | 28301 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | ETHUSDC | LS | 2.81322e-05 | 7 | 56602 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | 1 | -1.92459e-05 | 7 | 28296 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | 2 | -6.32953e-06 | 7 | 28304 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | 3 | -1.67286e-07 | 7 | 28294 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | 4 | 5.6184e-06 | 7 | 28295 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | 5 | 1.53825e-05 | 7 | 28298 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 5 | SOLUSDC | LS | 3.46284e-05 | 7 | 56594 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | 1 | -1.33379e-05 | 7 | 28303 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | 2 | -6.19647e-06 | 7 | 28444 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | 3 | -1.09391e-06 | 7 | 28236 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | 4 | 4.31237e-06 | 7 | 28186 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | 5 | 1.2887e-05 | 7 | 28285 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | BTCUSDC | LS | 2.62249e-05 | 7 | 56588 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | 1 | -1.60687e-05 | 7 | 28296 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | 2 | -5.74047e-06 | 7 | 28287 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | 3 | -2.02499e-06 | 7 | 28287 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | 4 | 1.59844e-06 | 7 | 28289 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | 5 | 1.22682e-05 | 7 | 28295 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | ETHUSDC | LS | 2.83369e-05 | 7 | 56591 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | 1 | -2.16934e-05 | 7 | 28293 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | 2 | -9.38994e-06 | 7 | 28294 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | 3 | 5.89441e-07 | 7 | 28286 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | 4 | 5.50757e-06 | 7 | 28291 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | 5 | 1.547e-05 | 7 | 28288 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 10 | SOLUSDC | LS | 3.71634e-05 | 7 | 56581 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | 1 | -1.5058e-05 | 7 | 28284 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | 2 | -7.30511e-06 | 7 | 28404 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | 3 | -2.75361e-06 | 7 | 28206 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | 4 | 2.82102e-06 | 7 | 28148 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | 5 | 1.18772e-05 | 7 | 28272 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | BTCUSDC | LS | 2.69352e-05 | 7 | 56556 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | 1 | -2.23836e-05 | 7 | 28272 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | 2 | -8.74165e-06 | 7 | 28259 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | 3 | -7.54617e-06 | 7 | 28255 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | 4 | 1.4761e-07 | 7 | 28251 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | 5 | 9.03649e-06 | 7 | 28277 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | ETHUSDC | LS | 3.14201e-05 | 7 | 56549 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | 1 | -2.70408e-05 | 7 | 28278 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | 2 | -1.25797e-05 | 7 | 28262 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | 3 | -2.83366e-06 | 7 | 28248 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | 4 | -6.01269e-07 | 7 | 28258 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | 5 | 1.44033e-05 | 7 | 28266 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 30 | SOLUSDC | LS | 4.14441e-05 | 7 | 56544 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | 1 | -1.5022e-05 | 7 | 28262 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | 2 | -1.15936e-05 | 7 | 28354 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | 3 | -8.40384e-06 | 7 | 28147 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | 4 | 4.56156e-07 | 7 | 28094 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | 5 | 1.33776e-05 | 7 | 28247 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | BTCUSDC | LS | 2.83996e-05 | 7 | 56509 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | 1 | -2.16574e-05 | 7 | 28234 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | 2 | -1.57648e-05 | 7 | 28203 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | 3 | -1.70684e-05 | 7 | 28210 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | 4 | -8.67835e-06 | 7 | 28212 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | 5 | 5.18172e-06 | 7 | 28245 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | ETHUSDC | LS | 2.68391e-05 | 7 | 56479 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | 1 | -3.13274e-05 | 7 | 28246 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | 2 | -2.20144e-05 | 7 | 28211 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | 3 | -8.42131e-06 | 7 | 28205 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | 4 | -8.29913e-06 | 7 | 28205 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | 5 | 1.25866e-05 | 7 | 28235 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 60 | SOLUSDC | LS | 4.3914e-05 | 7 | 56481 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | 1 | -2.55151e-05 | 7 | 28035 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | 2 | -2.11082e-05 | 7 | 27979 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | 3 | -3.85829e-05 | 7 | 27670 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | 4 | -2.21105e-05 | 7 | 27720 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | 5 | -4.13945e-06 | 7 | 28020 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | BTCUSDC | LS | 2.13757e-05 | 7 | 56055 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | 1 | -6.49718e-05 | 7 | 27974 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | 2 | -6.09577e-05 | 7 | 27824 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | 3 | -6.87957e-05 | 7 | 27759 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | 4 | -6.05901e-05 | 7 | 27884 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | 5 | -4.03925e-05 | 7 | 27983 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | ETHUSDC | LS | 2.45793e-05 | 7 | 55957 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | 1 | -7.94419e-05 | 7 | 28046 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | 2 | -7.43894e-05 | 7 | 27875 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | 3 | -7.78499e-05 | 7 | 27649 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | 4 | -5.77322e-05 | 7 | 27875 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | 5 | -3.83888e-05 | 7 | 27977 |
| cont_ofi_panel_1s | cont_ofi_panel_1s | 300 | SOLUSDC | LS | 4.10531e-05 | 7 | 56023 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 1 | -1.09173e-05 | 7 | 28309 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 2 | -3.88572e-06 | 7 | 28304 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 3 | -1.3946e-08 | 7 | 28302 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 4 | 3.4908e-06 | 7 | 28304 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 5 | 1.10006e-05 | 7 | 28305 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | LS | 2.19179e-05 | 7 | 56614 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 1 | -1.43882e-05 | 7 | 28310 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 2 | -5.81512e-06 | 7 | 28302 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 3 | 1.87878e-07 | 7 | 28302 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 4 | 4.47605e-06 | 7 | 28305 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 5 | 1.45478e-05 | 7 | 28305 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | LS | 2.8936e-05 | 7 | 56615 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 1 | -1.65653e-05 | 7 | 28308 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 2 | -4.53769e-06 | 7 | 28303 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 3 | -2.5657e-07 | 7 | 28305 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 4 | 4.26132e-06 | 7 | 28303 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 5 | 1.61491e-05 | 7 | 28303 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | LS | 3.27144e-05 | 7 | 56611 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 1 | -2.1239e-05 | 7 | 28306 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 2 | -8.39165e-06 | 7 | 28301 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 3 | 1.5309e-07 | 7 | 28289 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 4 | 7.03175e-06 | 7 | 28299 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 5 | 2.08165e-05 | 7 | 28301 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | LS | 4.20556e-05 | 7 | 56607 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 1 | -2.3562e-05 | 7 | 28303 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 2 | -1.00134e-05 | 7 | 28298 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 3 | -6.57027e-07 | 7 | 28296 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 4 | 6.55125e-06 | 7 | 28303 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 5 | 2.27513e-05 | 7 | 28296 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | LS | 4.63133e-05 | 7 | 56599 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 1 | -4.02808e-05 | 7 | 28303 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 2 | -1.33525e-05 | 7 | 28296 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 3 | -9.66899e-07 | 7 | 28301 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 4 | 1.14113e-05 | 7 | 28302 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 5 | 3.84728e-05 | 7 | 28292 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | LS | 7.87536e-05 | 7 | 56595 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 1 | -2.35501e-05 | 7 | 28300 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 2 | -1.00133e-05 | 7 | 28296 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 3 | -1.74688e-08 | 7 | 28277 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 4 | 6.97317e-06 | 7 | 28293 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 5 | 2.31732e-05 | 7 | 28295 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | LS | 4.67232e-05 | 7 | 56595 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 1 | -2.58937e-05 | 7 | 28293 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 2 | -1.11926e-05 | 7 | 28291 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 3 | -1.44048e-06 | 7 | 28287 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 4 | 6.87136e-06 | 7 | 28298 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 5 | 2.16715e-05 | 7 | 28292 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | LS | 4.75652e-05 | 7 | 56585 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 1 | -4.88471e-05 | 7 | 28294 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 2 | -1.80703e-05 | 7 | 28295 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 3 | -4.39809e-06 | 7 | 28296 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 4 | 1.66331e-05 | 7 | 28300 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 5 | 4.52203e-05 | 7 | 28274 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | LS | 9.40674e-05 | 7 | 56568 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 1 | -2.60408e-05 | 7 | 28290 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 2 | -1.18549e-05 | 7 | 28266 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 3 | 9.39639e-07 | 7 | 28220 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 4 | 4.89377e-06 | 7 | 28271 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 5 | 2.16674e-05 | 7 | 28274 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | LS | 4.77081e-05 | 7 | 56564 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 1 | -2.67047e-05 | 7 | 28267 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 2 | -1.21499e-05 | 7 | 28235 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 3 | -8.15964e-06 | 7 | 28250 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 4 | -3.14423e-07 | 7 | 28286 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 5 | 1.77844e-05 | 7 | 28283 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | LS | 4.44892e-05 | 7 | 56550 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 1 | -6.3108e-05 | 7 | 28288 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 2 | -2.76797e-05 | 7 | 28283 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 3 | -8.83415e-06 | 7 | 28273 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 4 | 1.924e-05 | 7 | 28272 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 5 | 5.19984e-05 | 7 | 28203 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | LS | 0.000115106 | 7 | 56491 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 1 | -2.16713e-05 | 7 | 28256 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 2 | -1.34368e-05 | 7 | 28233 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 3 | -4.27803e-06 | 7 | 28159 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 4 | -4.21147e-07 | 7 | 28218 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 5 | 1.85535e-05 | 7 | 28245 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | LS | 4.02247e-05 | 7 | 56501 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 1 | -3.0626e-05 | 7 | 28232 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 2 | -2.14044e-05 | 7 | 28187 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 3 | -1.01358e-05 | 7 | 28206 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 4 | -6.92574e-06 | 7 | 28262 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 5 | 1.10062e-05 | 7 | 28224 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | LS | 4.16322e-05 | 7 | 56456 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 1 | -6.93204e-05 | 7 | 28276 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 2 | -3.27752e-05 | 7 | 28262 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 3 | -1.84824e-05 | 7 | 28231 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 4 | 8.75796e-06 | 7 | 28237 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 5 | 5.4696e-05 | 7 | 28103 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | LS | 0.000124016 | 7 | 56379 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 1 | -3.19089e-05 | 7 | 27984 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 2 | -3.03207e-05 | 7 | 27961 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 3 | -2.62642e-05 | 7 | 27776 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 4 | -1.95216e-05 | 7 | 27796 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 5 | -3.28615e-06 | 7 | 27914 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | LS | 2.86227e-05 | 7 | 55898 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 1 | -4.16496e-05 | 7 | 27971 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 2 | -8.43458e-05 | 7 | 27849 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 3 | -7.72771e-05 | 7 | 27822 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 4 | -5.24113e-05 | 7 | 27910 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 5 | -4.07589e-05 | 7 | 27879 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | LS | 8.90689e-07 | 7 | 55850 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 1 | -0.000150712 | 7 | 28047 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 2 | -8.57573e-05 | 7 | 28032 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 3 | -7.53512e-05 | 7 | 27966 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 4 | -4.18419e-05 | 7 | 27924 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 5 | 2.53637e-05 | 7 | 27460 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | LS | 0.000176075 | 7 | 55507 |
| spread_bp | spread_bp | 1 | BTCUSDC | 1 | -1.07843e-06 | 7 | 28367 |
| spread_bp | spread_bp | 1 | BTCUSDC | 2 | -3.36364e-07 | 7 | 28374 |
| spread_bp | spread_bp | 1 | BTCUSDC | 3 | -7.54558e-08 | 7 | 28307 |
| spread_bp | spread_bp | 1 | BTCUSDC | 4 | -4.71564e-08 | 7 | 28247 |
| spread_bp | spread_bp | 1 | BTCUSDC | 5 | 1.2187e-06 | 7 | 28229 |
| spread_bp | spread_bp | 1 | BTCUSDC | LS | 2.29713e-06 | 7 | 56596 |
| spread_bp | spread_bp | 1 | ETHUSDC | 1 | -1.65854e-06 | 7 | 28422 |
| spread_bp | spread_bp | 1 | ETHUSDC | 2 | -7.34565e-07 | 7 | 28322 |
| spread_bp | spread_bp | 1 | ETHUSDC | 3 | -4.46468e-07 | 7 | 28379 |
| spread_bp | spread_bp | 1 | ETHUSDC | 4 | 2.72007e-07 | 7 | 28191 |
| spread_bp | spread_bp | 1 | ETHUSDC | 5 | 1.62055e-06 | 7 | 28210 |
| spread_bp | spread_bp | 1 | ETHUSDC | LS | 3.27908e-06 | 7 | 56632 |
| spread_bp | spread_bp | 1 | SOLUSDC | 1 | -1.37836e-06 | 7 | 29797 |
| spread_bp | spread_bp | 1 | SOLUSDC | 2 | -6.53846e-07 | 7 | 28445 |
| spread_bp | spread_bp | 1 | SOLUSDC | 3 | -4.33147e-07 | 7 | 27891 |
| spread_bp | spread_bp | 1 | SOLUSDC | 4 | 2.19978e-07 | 7 | 28750 |
| spread_bp | spread_bp | 1 | SOLUSDC | 5 | 1.52102e-06 | 7 | 26639 |
| spread_bp | spread_bp | 1 | SOLUSDC | LS | 2.89937e-06 | 7 | 56436 |
| spread_bp | spread_bp | 5 | BTCUSDC | 1 | -5.56655e-06 | 7 | 28367 |
| spread_bp | spread_bp | 5 | BTCUSDC | 2 | -2.11356e-06 | 7 | 28370 |
| spread_bp | spread_bp | 5 | BTCUSDC | 3 | 4.03109e-07 | 7 | 28303 |
| spread_bp | spread_bp | 5 | BTCUSDC | 4 | -1.35479e-07 | 7 | 28239 |
| spread_bp | spread_bp | 5 | BTCUSDC | 5 | 5.79704e-06 | 7 | 28217 |
| spread_bp | spread_bp | 5 | BTCUSDC | LS | 1.13636e-05 | 7 | 56584 |
| spread_bp | spread_bp | 5 | ETHUSDC | 1 | -8.59403e-06 | 7 | 28422 |
| spread_bp | spread_bp | 5 | ETHUSDC | 2 | -3.91532e-06 | 7 | 28314 |
| spread_bp | spread_bp | 5 | ETHUSDC | 3 | -2.43966e-06 | 7 | 28379 |
| spread_bp | spread_bp | 5 | ETHUSDC | 4 | 1.55292e-06 | 7 | 28186 |
| spread_bp | spread_bp | 5 | ETHUSDC | 5 | 8.69066e-06 | 7 | 28195 |
| spread_bp | spread_bp | 5 | ETHUSDC | LS | 1.72847e-05 | 7 | 56617 |
| spread_bp | spread_bp | 5 | SOLUSDC | 1 | -7.66229e-06 | 7 | 29797 |
| spread_bp | spread_bp | 5 | SOLUSDC | 2 | -3.11766e-06 | 7 | 28437 |
| spread_bp | spread_bp | 5 | SOLUSDC | 3 | -2.65033e-06 | 7 | 27883 |
| spread_bp | spread_bp | 5 | SOLUSDC | 4 | 1.68614e-06 | 7 | 28746 |
| spread_bp | spread_bp | 5 | SOLUSDC | 5 | 8.12378e-06 | 7 | 26631 |
| spread_bp | spread_bp | 5 | SOLUSDC | LS | 1.57861e-05 | 7 | 56428 |
| spread_bp | spread_bp | 10 | BTCUSDC | 1 | -1.15044e-05 | 7 | 28367 |
| spread_bp | spread_bp | 10 | BTCUSDC | 2 | -4.24323e-06 | 7 | 28365 |
| spread_bp | spread_bp | 10 | BTCUSDC | 3 | 6.68319e-07 | 7 | 28298 |
| spread_bp | spread_bp | 10 | BTCUSDC | 4 | 3.19285e-07 | 7 | 28229 |
| spread_bp | spread_bp | 10 | BTCUSDC | 5 | 1.13733e-05 | 7 | 28202 |
| spread_bp | spread_bp | 10 | BTCUSDC | LS | 2.28777e-05 | 7 | 56569 |
| spread_bp | spread_bp | 10 | ETHUSDC | 1 | -1.68162e-05 | 7 | 28422 |
| spread_bp | spread_bp | 10 | ETHUSDC | 2 | -7.7726e-06 | 7 | 28304 |
| spread_bp | spread_bp | 10 | ETHUSDC | 3 | -5.77825e-06 | 7 | 28379 |
| spread_bp | spread_bp | 10 | ETHUSDC | 4 | 3.04621e-06 | 7 | 28181 |
| spread_bp | spread_bp | 10 | ETHUSDC | 5 | 1.77711e-05 | 7 | 28175 |
| spread_bp | spread_bp | 10 | ETHUSDC | LS | 3.45873e-05 | 7 | 56597 |
| spread_bp | spread_bp | 10 | SOLUSDC | 1 | -1.53949e-05 | 7 | 29797 |
| spread_bp | spread_bp | 10 | SOLUSDC | 2 | -5.7623e-06 | 7 | 28427 |
| spread_bp | spread_bp | 10 | SOLUSDC | 3 | -5.61096e-06 | 7 | 27873 |
| spread_bp | spread_bp | 10 | SOLUSDC | 4 | 3.05857e-06 | 7 | 28741 |
| spread_bp | spread_bp | 10 | SOLUSDC | 5 | 1.65441e-05 | 7 | 26621 |
| spread_bp | spread_bp | 10 | SOLUSDC | LS | 3.19389e-05 | 7 | 56418 |
| spread_bp | spread_bp | 30 | BTCUSDC | 1 | -3.71844e-05 | 7 | 28367 |
| spread_bp | spread_bp | 30 | BTCUSDC | 2 | -7.1398e-06 | 7 | 28345 |
| spread_bp | spread_bp | 30 | BTCUSDC | 3 | 7.1815e-07 | 7 | 28278 |
| spread_bp | spread_bp | 30 | BTCUSDC | 4 | -2.1906e-06 | 7 | 28189 |
| spread_bp | spread_bp | 30 | BTCUSDC | 5 | 3.55993e-05 | 7 | 28142 |
| spread_bp | spread_bp | 30 | BTCUSDC | LS | 7.27837e-05 | 7 | 56509 |
| spread_bp | spread_bp | 30 | ETHUSDC | 1 | -5.23906e-05 | 7 | 28422 |
| spread_bp | spread_bp | 30 | ETHUSDC | 2 | -2.18567e-05 | 7 | 28265 |
| spread_bp | spread_bp | 30 | ETHUSDC | 3 | -1.36126e-05 | 7 | 28378 |
| spread_bp | spread_bp | 30 | ETHUSDC | 4 | 1.22145e-05 | 7 | 28161 |
| spread_bp | spread_bp | 30 | ETHUSDC | 5 | 4.73066e-05 | 7 | 28095 |
| spread_bp | spread_bp | 30 | ETHUSDC | LS | 9.96972e-05 | 7 | 56517 |
| spread_bp | spread_bp | 30 | SOLUSDC | 1 | -4.76232e-05 | 7 | 29797 |
| spread_bp | spread_bp | 30 | SOLUSDC | 2 | -1.58439e-05 | 7 | 28387 |
| spread_bp | spread_bp | 30 | SOLUSDC | 3 | -1.31382e-05 | 7 | 27833 |
| spread_bp | spread_bp | 30 | SOLUSDC | 4 | 5.8294e-06 | 7 | 28721 |
| spread_bp | spread_bp | 30 | SOLUSDC | 5 | 5.08078e-05 | 7 | 26581 |
| spread_bp | spread_bp | 30 | SOLUSDC | LS | 9.8431e-05 | 7 | 56378 |
| spread_bp | spread_bp | 60 | BTCUSDC | 1 | -7.80321e-05 | 7 | 28367 |
| spread_bp | spread_bp | 60 | BTCUSDC | 2 | -1.11881e-05 | 7 | 28315 |
| spread_bp | spread_bp | 60 | BTCUSDC | 3 | 1.87139e-06 | 7 | 28248 |
| spread_bp | spread_bp | 60 | BTCUSDC | 4 | -3.50034e-06 | 7 | 28129 |
| spread_bp | spread_bp | 60 | BTCUSDC | 5 | 6.99784e-05 | 7 | 28052 |
| spread_bp | spread_bp | 60 | BTCUSDC | LS | 0.000148011 | 7 | 56419 |
| spread_bp | spread_bp | 60 | ETHUSDC | 1 | -0.000107747 | 7 | 28422 |
| spread_bp | spread_bp | 60 | ETHUSDC | 2 | -4.46947e-05 | 7 | 28220 |
| spread_bp | spread_bp | 60 | ETHUSDC | 3 | -2.10387e-05 | 7 | 28363 |
| spread_bp | spread_bp | 60 | ETHUSDC | 4 | 2.22791e-05 | 7 | 28110 |
| spread_bp | spread_bp | 60 | ETHUSDC | 5 | 9.51565e-05 | 7 | 27996 |
| spread_bp | spread_bp | 60 | ETHUSDC | LS | 0.000202903 | 7 | 56418 |
| spread_bp | spread_bp | 60 | SOLUSDC | 1 | -9.7948e-05 | 7 | 29797 |
| spread_bp | spread_bp | 60 | SOLUSDC | 2 | -3.15985e-05 | 7 | 28327 |
| spread_bp | spread_bp | 60 | SOLUSDC | 3 | -2.14443e-05 | 7 | 27778 |
| spread_bp | spread_bp | 60 | SOLUSDC | 4 | 1.52992e-05 | 7 | 28689 |
| spread_bp | spread_bp | 60 | SOLUSDC | 5 | 9.52276e-05 | 7 | 26518 |
| spread_bp | spread_bp | 60 | SOLUSDC | LS | 0.000193176 | 7 | 56315 |
| spread_bp | spread_bp | 300 | BTCUSDC | 1 | -0.000319794 | 7 | 28367 |
| spread_bp | spread_bp | 300 | BTCUSDC | 2 | -9.6312e-05 | 7 | 28290 |
| spread_bp | spread_bp | 300 | BTCUSDC | 3 | 7.87966e-06 | 7 | 27752 |
| spread_bp | spread_bp | 300 | BTCUSDC | 4 | 1.32417e-05 | 7 | 27756 |
| spread_bp | spread_bp | 300 | BTCUSDC | 5 | 0.000297434 | 7 | 27266 |
| spread_bp | spread_bp | 300 | BTCUSDC | LS | 0.000617229 | 7 | 55633 |
| spread_bp | spread_bp | 300 | ETHUSDC | 1 | -0.000550237 | 7 | 28422 |
| spread_bp | spread_bp | 300 | ETHUSDC | 2 | -0.000161508 | 7 | 28024 |
| spread_bp | spread_bp | 300 | ETHUSDC | 3 | -3.02042e-05 | 7 | 28146 |
| spread_bp | spread_bp | 300 | ETHUSDC | 4 | 9.22742e-05 | 7 | 27638 |
| spread_bp | spread_bp | 300 | ETHUSDC | 5 | 0.000368259 | 7 | 27201 |
| spread_bp | spread_bp | 300 | ETHUSDC | LS | 0.000918496 | 7 | 55623 |
| spread_bp | spread_bp | 300 | SOLUSDC | 1 | -0.000494955 | 7 | 29797 |
| spread_bp | spread_bp | 300 | SOLUSDC | 2 | -0.000116708 | 7 | 28095 |
| spread_bp | spread_bp | 300 | SOLUSDC | 3 | -9.13503e-05 | 7 | 27290 |
| spread_bp | spread_bp | 300 | SOLUSDC | 4 | 0.000117214 | 7 | 28650 |
| spread_bp | spread_bp | 300 | SOLUSDC | 5 | 0.000324942 | 7 | 25597 |
| spread_bp | spread_bp | 300 | SOLUSDC | LS | 0.000819897 | 7 | 55394 |

## Notes

- Built on precomputed L1 day panels; no LOB tick replay per factor.
- Single-week / 3-symbol slice — expand universe in later M4 runs.
- Rank IC ≠ tradable edge.
- **分层** = factor-value TS quantiles within day; depth `L3`/`L5` = book levels.

---
Generated by `python -m a4ob.cli run-eval-pack`.