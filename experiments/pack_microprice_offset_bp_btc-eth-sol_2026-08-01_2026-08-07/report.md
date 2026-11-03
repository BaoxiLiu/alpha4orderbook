# Factor pack eval

## Run meta

- **symbols**: `['BTCUSDC', 'ETHUSDC', 'SOLUSDC']`
- **start_date**: `2026-08-01`
- **end_date**: `2026-08-07`
- **train_dates**: `['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05']`
- **test_dates**: `['2026-08-06', '2026-08-07']`
- **factor_names**: `['microprice_offset_bp']`
- **factor_specs**: `['/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/configs/factors/microprice_offset_bp.yaml']`
- **dt_seconds**: `1`
- **top_k**: `20`
- **n_detail_rows**: `126`
- **n_layering_rows**: `756`
- **n_quantiles**: `5`
- **layering_method**: `ts_within_day`
- **n_failures**: `0`
- **elapsed_seconds**: `5.113`
- **panels_root**: `/Volumes/Seagate Bas/科研项目/quant_project/alpha4orderbook/panels`
- **built_at_utc**: `2026-11-03T13:12:15.347614+00:00`

- Companion HTML charts: `report.html` (Plotly CDN).

## Rank IC matrix (mean across days) — factor × horizon × symbol

| spec | factor | horizon_s | symbol | rank_ic | n_days | n_obs_sum |
| --- | --- | --- | --- | --- | --- | --- |
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

### Pivot (rows=spec/factor/horizon, cols=symbol)

| spec | factor | horizon_s | BTCUSDC | ETHUSDC | SOLUSDC |
| --- | --- | --- | --- | --- | --- |
| microprice_offset_bp | microprice_offset_bp | 1 | 0.278499 | 0.266092 | 0.227759 |
| microprice_offset_bp | microprice_offset_bp | 5 | 0.23268 | 0.178738 | 0.261516 |
| microprice_offset_bp | microprice_offset_bp | 10 | 0.176106 | 0.122194 | 0.232417 |
| microprice_offset_bp | microprice_offset_bp | 30 | 0.0940389 | 0.0562444 | 0.165833 |
| microprice_offset_bp | microprice_offset_bp | 60 | 0.0462044 | 0.0407301 | 0.114785 |
| microprice_offset_bp | microprice_offset_bp | 300 | 0.0199186 | 0.016714 | 0.0677865 |

## Calendar-day time split

> Train = first 5 calendar days `['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05']`; test = last 2 days `['2026-08-06', '2026-08-07']`. IC values are means of per-day Rank ICs (not pooled ticks).

| spec | factor | horizon_s | split | n_days | mean_rank_ic | mean_n |
| --- | --- | --- | --- | --- | --- | --- |
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

## Panel load coverage

- **loaded ok**: `21`
- **missing / unusable**: `0`

## Quantile layering (分层收益)

> 分层 = time-series quantiles within each symbol-day (method=`ts_within_day`, Q=5). Equal-day mean of per-day bucket mean forward mid returns; LS = Q_high − Q_low. Order-book depth tags (L3/L5) are unrelated to these quintiles.

### Long-short Q_high − Q_low (equal-day mean)

| spec | factor | horizon_s | symbol | quantile | mean_ret | n_obs_sum | n_days |
| --- | --- | --- | --- | --- | --- | --- | --- |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | LS | 2.19179e-05 | 56614 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | LS | 2.8936e-05 | 56615 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | LS | 3.27144e-05 | 56611 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | LS | 4.20556e-05 | 56607 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | LS | 4.63133e-05 | 56599 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | LS | 7.87536e-05 | 56595 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | LS | 4.67232e-05 | 56595 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | LS | 4.75652e-05 | 56585 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | LS | 9.40674e-05 | 56568 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | LS | 4.77081e-05 | 56564 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | LS | 4.44892e-05 | 56550 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | LS | 0.000115106 | 56491 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | LS | 4.02247e-05 | 56501 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | LS | 4.16322e-05 | 56456 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | LS | 0.000124016 | 56379 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | LS | 2.86227e-05 | 55898 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | LS | 8.90689e-07 | 55850 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | LS | 0.000176075 | 55507 | 7 |

### Full quantile means

| spec | factor | horizon_s | symbol | quantile | mean_ret | n_obs_sum | n_days |
| --- | --- | --- | --- | --- | --- | --- | --- |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 1 | -1.09173e-05 | 28309 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 2 | -3.88572e-06 | 28304 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 3 | -1.3946e-08 | 28302 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 4 | 3.4908e-06 | 28304 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | 5 | 1.10006e-05 | 28305 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | BTCUSDC | LS | 2.19179e-05 | 56614 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 1 | -1.43882e-05 | 28310 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 2 | -5.81512e-06 | 28302 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 3 | 1.87878e-07 | 28302 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 4 | 4.47605e-06 | 28305 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | 5 | 1.45478e-05 | 28305 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | ETHUSDC | LS | 2.8936e-05 | 56615 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 1 | -1.65653e-05 | 28308 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 2 | -4.53769e-06 | 28303 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 3 | -2.5657e-07 | 28305 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 4 | 4.26132e-06 | 28303 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | 5 | 1.61491e-05 | 28303 | 7 |
| microprice_offset_bp | microprice_offset_bp | 1 | SOLUSDC | LS | 3.27144e-05 | 56611 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 1 | -2.1239e-05 | 28306 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 2 | -8.39165e-06 | 28301 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 3 | 1.5309e-07 | 28289 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 4 | 7.03175e-06 | 28299 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | 5 | 2.08165e-05 | 28301 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | BTCUSDC | LS | 4.20556e-05 | 56607 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 1 | -2.3562e-05 | 28303 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 2 | -1.00134e-05 | 28298 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 3 | -6.57027e-07 | 28296 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 4 | 6.55125e-06 | 28303 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | 5 | 2.27513e-05 | 28296 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | ETHUSDC | LS | 4.63133e-05 | 56599 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 1 | -4.02808e-05 | 28303 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 2 | -1.33525e-05 | 28296 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 3 | -9.66899e-07 | 28301 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 4 | 1.14113e-05 | 28302 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | 5 | 3.84728e-05 | 28292 | 7 |
| microprice_offset_bp | microprice_offset_bp | 5 | SOLUSDC | LS | 7.87536e-05 | 56595 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 1 | -2.35501e-05 | 28300 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 2 | -1.00133e-05 | 28296 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 3 | -1.74688e-08 | 28277 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 4 | 6.97317e-06 | 28293 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | 5 | 2.31732e-05 | 28295 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | BTCUSDC | LS | 4.67232e-05 | 56595 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 1 | -2.58937e-05 | 28293 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 2 | -1.11926e-05 | 28291 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 3 | -1.44048e-06 | 28287 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 4 | 6.87136e-06 | 28298 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | 5 | 2.16715e-05 | 28292 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | ETHUSDC | LS | 4.75652e-05 | 56585 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 1 | -4.88471e-05 | 28294 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 2 | -1.80703e-05 | 28295 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 3 | -4.39809e-06 | 28296 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 4 | 1.66331e-05 | 28300 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | 5 | 4.52203e-05 | 28274 | 7 |
| microprice_offset_bp | microprice_offset_bp | 10 | SOLUSDC | LS | 9.40674e-05 | 56568 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 1 | -2.60408e-05 | 28290 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 2 | -1.18549e-05 | 28266 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 3 | 9.39639e-07 | 28220 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 4 | 4.89377e-06 | 28271 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | 5 | 2.16674e-05 | 28274 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | BTCUSDC | LS | 4.77081e-05 | 56564 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 1 | -2.67047e-05 | 28267 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 2 | -1.21499e-05 | 28235 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 3 | -8.15964e-06 | 28250 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 4 | -3.14423e-07 | 28286 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | 5 | 1.77844e-05 | 28283 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | ETHUSDC | LS | 4.44892e-05 | 56550 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 1 | -6.3108e-05 | 28288 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 2 | -2.76797e-05 | 28283 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 3 | -8.83415e-06 | 28273 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 4 | 1.924e-05 | 28272 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | 5 | 5.19984e-05 | 28203 | 7 |
| microprice_offset_bp | microprice_offset_bp | 30 | SOLUSDC | LS | 0.000115106 | 56491 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 1 | -2.16713e-05 | 28256 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 2 | -1.34368e-05 | 28233 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 3 | -4.27803e-06 | 28159 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 4 | -4.21147e-07 | 28218 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | 5 | 1.85535e-05 | 28245 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | BTCUSDC | LS | 4.02247e-05 | 56501 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 1 | -3.0626e-05 | 28232 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 2 | -2.14044e-05 | 28187 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 3 | -1.01358e-05 | 28206 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 4 | -6.92574e-06 | 28262 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | 5 | 1.10062e-05 | 28224 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | ETHUSDC | LS | 4.16322e-05 | 56456 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 1 | -6.93204e-05 | 28276 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 2 | -3.27752e-05 | 28262 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 3 | -1.84824e-05 | 28231 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 4 | 8.75796e-06 | 28237 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | 5 | 5.4696e-05 | 28103 | 7 |
| microprice_offset_bp | microprice_offset_bp | 60 | SOLUSDC | LS | 0.000124016 | 56379 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 1 | -3.19089e-05 | 27984 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 2 | -3.03207e-05 | 27961 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 3 | -2.62642e-05 | 27776 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 4 | -1.95216e-05 | 27796 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | 5 | -3.28615e-06 | 27914 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | BTCUSDC | LS | 2.86227e-05 | 55898 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 1 | -4.16496e-05 | 27971 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 2 | -8.43458e-05 | 27849 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 3 | -7.72771e-05 | 27822 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 4 | -5.24113e-05 | 27910 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | 5 | -4.07589e-05 | 27879 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | ETHUSDC | LS | 8.90689e-07 | 55850 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 1 | -0.000150712 | 28047 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 2 | -8.57573e-05 | 28032 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 3 | -7.53512e-05 | 27966 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 4 | -4.18419e-05 | 27924 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | 5 | 2.53637e-05 | 27460 | 7 |
| microprice_offset_bp | microprice_offset_bp | 300 | SOLUSDC | LS | 0.000176075 | 55507 | 7 |

## Notes

- Built on precomputed L1 day panels; no LOB tick replay per factor.
- Single-week / 3-symbol slice — expand universe in later M4 runs.
- Rank IC ≠ tradable edge.
- **分层** = factor-value TS quantiles within day; depth `L3`/`L5` = book levels.

---
Generated by `python -m a4ob.cli run-eval-pack`.