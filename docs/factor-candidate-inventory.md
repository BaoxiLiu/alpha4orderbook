# L0 Factor Candidate Inventory (HF orderbook → a4ob)

- Generated: `2026-11-03T05:51:06.365768+00:00`
- Track: factor library quality-gate → orthogonality (see `factor-library-roadmap.md`)
- Scope: **inventory only** — no full-window panel rebuild
- a4ob panel today: `dt=1s`, `top_k=20`, BBO + level px/sz, mid/spread; **no trades**, **no event-diff fields**, single-symbol day panels

## Sources scanned

| Source | Path | Role |
|---|---|---|
| FACTOR_CATALOG (early9) | `cryptocurrency_quant/app/backtesting/research/FACTOR_CATALOG.md` | Canonical early nine + author extras |
| feature_cache | `cryptocurrency_quant/app/backtesting/feature_cache.py` | Early9 implementation |
| prediction v3 | `cryptocurrency_quant/app/prediction/factors.py` + `schema.py` | Frozen 50-factor machine |
| factor_library registry | `cryptocurrency_quant/app/factor_library/registry.json` | Flow S01–S27 |
| factor_library code | `cryptocurrency_quant/app/factor_library/{flow,microstructure,market_states,paper173}.py` | Flow / micro / states / paper173 |
| unified catalog | `cryptocurrency_quant/doc/factors/unified-v1/catalog.json` | 602 metadata rows |
| crypto_factor_research | `quant_project/crypto_factor_research/` | Daily/hourly CS OHLCV — **no HF LOB factors** |
| a4ob ports | `alpha4orderbook/src/a4ob/factors/catalog_nine.py` + `configs/factors/*.yaml` | Already Spec-evaled subset |

## Portability legend (a4ob **today**)

| Tag | Meaning |
|---|---|
| `ready` | Computable from existing top-K 1s panel (+ rolling lags on mid/depth) |
| `needs_work` | Approx possible, but needs Spec design / cross-symbol join / subsecond or event-OFI caveat |
| `blocked` | Requires trade tape and/or true event LOB diffs (cancel/add rates, message rates, VPIN buckets, …) not on panel |
| `out_of_scope` | Minute bars / cicc formula candidates — not HF orderbook primary track |

### Already ported in a4ob

| a4ob id | Status |
|---|---|
| `spread_bp` | a4ob configs/factors/spread_bp.yaml + catalog_nine |
| `microprice_offset_bp` | a4ob configs/factors/microprice_offset_bp.yaml + catalog_nine |
| `cont_ofi_panel_1s` | a4ob configs/factors/cont_ofi_panel_1s.yaml (panel approx of early9 ofi / Cont) |
| `l1_imbalance` | ops imbalance / baseline; demo imbalance.yaml (not pack-eval Spec of early9 name) |
| `imbalance_l3` | catalog_nine.imbalance_l3 code; no dedicated Spec yaml yet |
| `mid_return_1s` | catalog_nine.mid_return_1s code; no dedicated Spec yaml yet |

Pack-eval Specs with yaml today: `spread_bp`, `microprice_offset_bp`, `cont_ofi_panel_1s` (+ demo `imbalance`, `micro_combo`).

## Counts

### Unified catalog (`catalog.json`)

| Collection | n | ready | needs_work | blocked | out_of_scope |
|---|---:|---:|---:|---:|---:|
| `cicc` | 79 | 0 | 0 | 0 | 79 |
| `flow` | 27 | 2 | 0 | 25 | 0 |
| `micro` | 202 | 74 | 26 | 102 | 0 |
| `minute` | 18 | 0 | 0 | 0 | 18 |
| `paper` | 173 | 0 | 45 | 128 | 0 |
| `states` | 53 | 13 | 6 | 34 | 0 |
| `v3` | 50 | 22 | 9 | 19 | 0 |
| **TOTAL** | **602** | **111** | **86** | **308** | **97** |

Plus **early9** (9) outside unified catalog IDs (overlap with micro/v3 names). Author extras (~9) mostly trades/cross — see below.

### crypto_factor_research

**0 HF orderbook factors.** Repo is cross-sectional OHLCV; LOB marked missing. Tape proxies (`taker_imbalance_24h`, `roll_spread_proxy_7d`, …) are daily bars — out of a4ob HF scope.

## 1. Early nine + author extras (`FACTOR_CATALOG` / `feature_cache`)

| id | source | formula/role | required inputs | portability | already-ported? |
|---|---|---|---|---|---|
| `spread_bp` | `feature_cache / FACTOR_CATALOG` | (a-b)/m*1e4 | `panel_topk` | `ready` | yes |
| `l1_imbalance` | `feature_cache / FACTOR_CATALOG` | (B-A)/(B+A) | `panel_topk` | `ready` | code:imbalance (demo Spec) |
| `microprice_offset_bp` | `feature_cache / FACTOR_CATALOG` | microprice offset bp | `panel_topk` | `ready` | yes |
| `ofi` | `feature_cache.add_ofi` | Cont L1 OFI window prefix diff | `event_lob (exact) / panel approx` | `needs_work` | yes:cont_ofi_panel_1s approx |
| `buy_qty` | `feature_cache` | aggressor buy qty 1s | `trades` | `blocked` | no |
| `sell_qty` | `feature_cache` | aggressor sell qty 1s | `trades` | `blocked` | no |
| `signed_notional` | `feature_cache` | buy-sell notional 1s | `trades` | `blocked` | no |
| `mid_return` | `feature_cache` | m(t)/m(t-L)-1 | `panel_topk` | `ready` | code:mid_return_1s (no Spec) |
| `book_age_ms` | `feature_cache` | t-last depth receipt | `event_lob` | `blocked` | no |

### Author extras / increments

| id | source | formula/role | required inputs | portability | already-ported? |
|---|---|---|---|---|---|
| `active_flow_ratio / flow_imbalance_1s` | `flow_increment.py` | (buy-sell)/(buy+sell) 1s | `trades` | `blocked` | no |
| `btc_mid_return / btc_mid_ret_1s` | `btc_increment / cross_coin_features` | BTC 1s mid return | `panel_topk+cross_symbol` | `needs_work` | no |
| `btc_ofi / btc_ofi_1s` | `btc_increment.py` | BTC 1s Cont OFI | `event_lob+cross_symbol` | `needs_work` | related:cont_ofi_panel_1s |
| `volume_intensity_1s` | `author archive` | aggressor qty sum 1s | `trades` | `blocked` | no |
| `notional_intensity_1s` | `author archive` | aggressor notional sum 1s | `trades` | `blocked` | no |
| `rv_60s_bp2` | `author archive` | sum sq bp mid Δ 60s | `panel_topk` | `ready` | no (related v3:D7) |
| `btc_mid_ret_5s` | `author candidate` | BTC 5s mid ret | `panel_topk+cross_symbol` | `needs_work` | no |
| `btc_ofi_5s` | `author candidate` | BTC 5s OFI | `event_lob+cross_symbol` | `needs_work` | no |
| `btc_flow_imb_1s` | `author candidate` | BTC 1s taker imb | `trades+cross_symbol` | `blocked` | no |

## 2. Prediction v3 — 50 factors (`v3:*`)

n=50. Primary impl under `cryptocurrency_quant/app/…` (see Sources).

| id | name | formula/role (brief) | required inputs | portability | already-ported? |
|---|---|---|---|---|---|
| `v3:A1` | `A1` | (BidQty@≤3tick − AskQty@≤3tick)/(sum) | `panel_topk` | `ready` | no |
| `v3:A2` | `A2` | 同上 @≤10tick | `panel_topk` | `ready` | no |
| `v3:A3` | `A3` | (±5bp 内买深度 − 卖深度)/(sum) | `panel_topk` | `ready` | no |
| `v3:A4` | `A4` | 同上 @±10bp | `panel_topk` | `ready` | no |
| `v3:A5` | `A5` | slope_s = (Qty@10t − Qty@3t)/7；因子 = (slope_bid − slope_ask)/(\\|slope_bid\\|+\\|slope_ask\\|+ε) | `panel_topk` | `ready` | no |
| `v3:A6` | `A6` | A1(t) − A1(t−5s) | `panel_topk` | `ready` | no |
| `v3:A7` | `A7` | depth 事件数/秒 | `event_lob` | `blocked` | no |
| `v3:A8` | `A8` | spread_bp(t) − rolling_median_1h(spread_bp) | `panel_topk` | `ready` | no |
| `v3:B1` | `B1` | 买/卖侧撤单量（名义额）/秒 | `event_lob` | `blocked` | no |
| `v3:B2` | `B2` | 买/卖侧撤单量（名义额）/秒 | `event_lob` | `blocked` | no |
| `v3:B3` | `B3` | 撤单名义额 / 新增名义额（量上升求和） | `event_lob` | `blocked` | no |
| `v3:B4` | `B4` | ≤1 tick 内撤单名义额 / 总撤单名义额；触价距离取 **1s 网格状态**（与总则行网格一致） | `event_lob` | `blocked` | no |
| `v3:B5` | `B5` | (B1 − B2)/(B1 + B2) | `event_lob` | `blocked` | no |
| `v3:B6` | `B6` | 单笔撤量名义额 > 滚动 p90（**名义额口径**，p90 从训练段估计冻结；另设最小撤量地板 = 该币 0.1×中位单笔撤量，防微幅抖动左偏基准）的撤单名义额/秒 | `event_lob` | `blocked` | no |
| `v3:C1` | `C1` | (主动买名义额 − 主动卖名义额)/(sum) | `trades` | `blocked` | no |
| `v3:C2` | `C2` | (主动买名义额 − 主动卖名义额)/(sum) | `trades` | `blocked` | no |
| `v3:C3` | `C3` | (主动买名义额 − 主动卖名义额)/(sum) | `trades` | `blocked` | no |
| `v3:C4` | `C4` | 成交笔数/秒 | `trades` | `blocked` | no |
| `v3:C5` | `C5` | 单笔均量 / rolling_median_1h(单笔均量) | `trades` | `blocked` | no |
| `v3:C6` | `C6` | 大单（>滚动 p90）名义额 / 总名义额（p90 训练段冻结） | `trades` | `blocked` | no |
| `v3:C7` | `C7` | 近窗内 taker_imb_1s>0 的秒数占比 | `trades` | `blocked` | no |
| `v3:C8` | `C8` | taker_imb_5s(t) − taker_imb_5s(t−5s) | `trades` | `blocked` | no |
| `v3:C9` | `C9` | Σ\\|买−卖\\|名义额 / Σ(买+卖) 名义额（VPIN 时间分桶近似） | `trades` | `blocked` | no |
| `v3:C10` | `C10` | 滚动回归 slope：Δmid ~ signed_taker_notional（充分统计量 O(1) 更新） | `trades` | `blocked` | no |
| `v3:D1` | `D1` | (mid(t)/mid(t−Δ)−1)×1e4 | `panel_topk` | `ready` | no |
| `v3:D2` | `D2` | (mid(t)/mid(t−Δ)−1)×1e4 | `panel_topk` | `ready` | no |
| `v3:D3` | `D3` | (mid(t)/mid(t−Δ)−1)×1e4 | `panel_topk` | `ready` | no |
| `v3:D4` | `D4` | 触价档量变化构造的 OFI（冻结口径同族），Δ 窗口 | `panel_topk (approx; subsecond/event design)` | `needs_work` | related:cont_ofi_panel_1s (panel approx) |
| `v3:D5` | `D5` | 触价档量变化构造的 OFI（冻结口径同族），Δ 窗口 | `panel_topk (approx; subsecond/event design)` | `needs_work` | related:cont_ofi_panel_1s (panel approx) |
| `v3:D6` | `D6` | std(Δlog mid 1s 收益)×1e4 | `panel_topk` | `ready` | no |
| `v3:D7` | `D7` | std(Δlog mid 1s 收益)×1e4 | `panel_topk` | `ready` | no |
| `v3:D8` | `D8` | std(Δlog mid 1s 收益)×1e4 | `panel_topk` | `ready` | no |
| `v3:D9` | `D9` | rv_30s / (rv_300s+ε) | `panel_topk` | `ready` | no |
| `v3:D10` | `D10` | 正/负 1s 收益的平方和开根（有符号半方差） | `panel_topk` | `ready` | no |
| `v3:D11` | `D11` | 正/负 1s 收益的平方和开根（有符号半方差） | `panel_topk` | `ready` | no |
| `v3:D12` | `D12` | (up_rv − down_rv)/(up_rv + down_rv + ε) | `panel_topk` | `ready` | no |
| `v3:D13` | `D13` | (microprice − mid)/spread 的 10s 变化 | `panel_topk` | `ready` | no |
| `v3:D14` | `D14` | (mid − min_60s)/(max_60s − min_60s + ε) | `panel_topk` | `ready` | no |
| `v3:D15` | `D15` | \\|1s 收益\\| > 4×滚动中位(\\|1s 收益\\|) 的次数 | `panel_topk` | `ready` | no |
| `v3:E1` | `E1` | BTC mid 收益（冻结链已含部分 BTC 特征，此处按本文件统一口径重算） | `panel_topk+cross_symbol` | `needs_work` | no |
| `v3:E2` | `E2` | BTC mid 收益（冻结链已含部分 BTC 特征，此处按本文件统一口径重算） | `panel_topk+cross_symbol` | `needs_work` | no |
| `v3:E3` | `E3` | BTC rv_60s | `panel_topk+cross_symbol` | `needs_work` | no |
| `v3:E4` | `E4` | BTC taker_imb_30s | `panel_topk+cross_symbol` | `needs_work` | no |
| `v3:E5` | `E5` | 13 币等权 mid 收益 / 其 rv | `panel_topk+cross_symbol` | `needs_work` | no |
| `v3:E6` | `E6` | 13 币等权 mid 收益 / 其 rv | `panel_topk+cross_symbol` | `needs_work` | no |
| `v3:E7` | `E7` | 13 币等权 mid 收益 / 其 rv | `panel_topk+cross_symbol` | `needs_work` | no |
| `v3:E8` | `E8` | 当前资金费率（mark_price 流最近值） | `other:mark_funding` | `blocked` | no |
| `v3:E9` | `E9` | 距下一结算点分钟数 | `other:mark_funding` | `blocked` | no |
| `v3:E10` | `E10` | UTC 小时周期编码 | `panel_topk` | `ready` | no |
| `v3:E11` | `E11` | UTC 小时周期编码 | `panel_topk` | `ready` | no |

## 3. Flow library S01–S27 (`flow:*`)

n=27. Primary impl under `cryptocurrency_quant/app/…` (see Sources).

| id | name | formula/role (brief) | required inputs | portability | already-ported? |
|---|---|---|---|---|---|
| `flow:depth_message_rate_1s` | `depth_message_rate_1s` | 完整增量消息数/1s | `event_lob` | `blocked` | no |
| `flow:near_bid_net_add_rate_1s` | `near_bid_net_add_rate_1s` | Σp max(Δq,0)，买侧、距消息前最优价≤2ticks | `event_lob` | `blocked` | no |
| `flow:near_ask_net_add_rate_1s` | `near_ask_net_add_rate_1s` | 同S02，卖侧 | `event_lob` | `blocked` | no |
| `flow:near_bid_net_decrease_rate_1s` | `near_bid_net_decrease_rate_1s` | Σp max(-Δq,0)，买侧、距消息前最优价≤2ticks | `event_lob` | `blocked` | no |
| `flow:near_ask_net_decrease_rate_1s` | `near_ask_net_decrease_rate_1s` | 同S04，卖侧 | `event_lob` | `blocked` | no |
| `flow:buy_notional_rate_1s` | `buy_notional_rate_1s` | Σ主动买成交名义额/1s | `trades` | `blocked` | no |
| `flow:sell_notional_rate_1s` | `sell_notional_rate_1s` | Σ主动卖成交名义额/1s | `trades` | `blocked` | no |
| `flow:notional_acceleration_0p5s_5s` | `notional_acceleration_0p5s_5s` | (0.5s成交额/0.5)/(5s成交额/5) | `event_lob` | `blocked` | no |
| `flow:last_valid_trade_age_ms` | `last_valid_trade_age_ms` | 决策时间减最近有效成交接收时间 | `trades` | `blocked` | no |
| `flow:trade_interval_cv_5s` | `trade_interval_cv_5s` | 5s内有效成交接收间隔总体标准差/均值 | `trades` | `blocked` | no |
| `flow:trailing_quota_duration_all_ms` | `trailing_quota_duration_all_ms` | 向后累计成交额首次达到Q，决策时间减边界成交接收时间 | `trades` | `blocked` | no |
| `flow:trailing_quota_duration_buy_ms` | `trailing_quota_duration_buy_ms` | 同S11，仅主动买 | `trades` | `blocked` | no |
| `flow:trailing_quota_duration_sell_ms` | `trailing_quota_duration_sell_ms` | 同S11，仅主动卖 | `trades` | `blocked` | no |
| `flow:equal_notional_bucket_abs_imbalance` | `equal_notional_bucket_abs_imbalance` | 最近20个完成的Q桶平均\|buy-sell\|/Q | `trades` | `blocked` | no |
| `flow:last_completed_volume_bucket_duration_ms` | `last_completed_volume_bucket_duration_ms` | 最后完成Q桶的末笔时间减上一桶结束时间；首桶从首筆时间开始 | `trades` | `blocked` | no |
| `flow:near_depth_depletion_asymmetry_1s` | `near_depth_depletion_asymmetry_1s` | S04/当前近端买深度名义额-S05/当前近端卖深度名义额 | `event_lob` | `blocked` | no |
| `flow:near_depth_imbalance` | `near_depth_imbalance` | (近端买深度名义额-近端卖深度名义额)/(两者和) | `panel_topk` | `ready` | no |
| `flow:touch_qty_imbalance` | `touch_qty_imbalance` | (最优买档名义额-最优卖档名义额)/(两者和) | `panel_topk` | `ready` | related:imbalance/l1 |
| `flow:bid_replenish_share` | `bid_replenish_share` | S02/(S02+S04) 买侧近端补充/(补充+消耗) | `event_lob` | `blocked` | no |
| `flow:ask_replenish_share` | `ask_replenish_share` | S03/(S03+S05) 卖侧近端补充/(补充+消耗) | `event_lob` | `blocked` | no |
| `flow:near_net_flow_share` | `near_net_flow_share` | ((S02-S04)-(S03-S05))/(S02+S03+S04+S05) 净流量占总近端流量份额 | `event_lob` | `blocked` | no |
| `flow:taker_imbalance_1s` | `taker_imbalance_1s` | (S06-S07)/(S06+S07) 主动买卖金额失衡 | `trades` | `blocked` | no |
| `flow:taker_vwap_basis_bp_5s` | `taker_vwap_basis_bp_5s` | ((买主动VWAP-卖主动VWAP)/mid)*1e4，mid取簿内最优 | `trades` | `blocked` | no |
| `flow:trade_value_concentration_5s` | `trade_value_concentration_5s` | 5s内最大单笔成交额/5s总成交额 | `trades` | `blocked` | no |
| `flow:bucket_imbalance_streak` | `bucket_imbalance_streak` | 最近连续同号带符号桶失衡计数（0号桶打断） | `trades` | `blocked` | no |
| `flow:bucket_duration_cv` | `bucket_duration_cv` | 保留窗口内闭合桶时长CV(pstdev/mean，同S10算法) | `trades` | `blocked` | no |
| `flow:bucket_imbalance_momentum` | `bucket_imbalance_momentum` | 最近半数带符号桶失衡均值-前一半均值 | `trades` | `blocked` | no |

## 4. Microstructure library (`micro:*`, 202)

Impl: `app/factor_library/microstructure.py` (+ markout legacy). Full list:

| id | name | formula/role (brief) | required inputs | portability | already-ported? |
|---|---|---|---|---|---|
| `micro:spread_bp` | `spread_bp` | market_feature | `panel_topk` | `ready` | yes:spread_bp |
| `micro:spread_ticks` | `spread_ticks` | market_feature | `panel_topk` | `ready` | no |
| `micro:microprice_bid_signed_bp` | `microprice_bid_signed_bp` | market_feature | `panel_topk` | `ready` | related:microprice_offset_bp (scale/denom differ) |
| `micro:log_touch_total_notional` | `log_touch_total_notional` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_bid_notional_l1` | `log_bid_notional_l1` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_ask_notional_l1` | `log_ask_notional_l1` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_bid_notional_l5` | `log_bid_notional_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_ask_notional_l5` | `log_ask_notional_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_bid_notional_l10` | `log_bid_notional_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_ask_notional_l10` | `log_ask_notional_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_signed_imbalance_l1` | `bid_signed_imbalance_l1` | market_feature | `panel_topk` | `ready` | related:imbalance/l1 |
| `micro:bid_signed_imbalance_l5` | `bid_signed_imbalance_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_signed_imbalance_l10` | `bid_signed_imbalance_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_touch_share_l10` | `bid_touch_share_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_touch_share_l10` | `ask_touch_share_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_l10_width_ticks` | `bid_l10_width_ticks` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_l10_width_ticks` | `ask_l10_width_ticks` | market_feature | `panel_topk` | `ready` | no |
| `micro:w100ms_log_trade_count_rate` | `w100ms_log_trade_count_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w100ms_log_trade_notional_rate` | `w100ms_log_trade_notional_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w100ms_bid_signed_trade_notional_imbalance` | `w100ms_bid_signed_trade_notional_imbalance` | market_feature | `trades` | `blocked` | no |
| `micro:w100ms_log_bid_aggressor_rate` | `w100ms_log_bid_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w100ms_log_ask_aggressor_rate` | `w100ms_log_ask_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w100ms_log_depth_batch_rate` | `w100ms_log_depth_batch_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_depth_row_rate` | `w100ms_log_depth_row_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_bid_signed_ofi_scaled` | `w100ms_bid_signed_ofi_scaled` | market_feature | `panel_topk (approx) / event_lob (exact)` | `needs_work` | related:cont_ofi_panel_1s (panel approx) |
| `micro:w100ms_realized_vol_bp` | `w100ms_realized_vol_bp` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w100ms_bid_signed_return_bp` | `w100ms_bid_signed_return_bp` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w100ms_log_bid_add_ticks0_1_rate` | `w100ms_log_bid_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_ask_add_ticks0_1_rate` | `w100ms_log_ask_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_bid_decrease_ticks0_1_rate` | `w100ms_log_bid_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_ask_decrease_ticks0_1_rate` | `w100ms_log_ask_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_bid_add_ticks2_4_rate` | `w100ms_log_bid_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_ask_add_ticks2_4_rate` | `w100ms_log_ask_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_bid_decrease_ticks2_4_rate` | `w100ms_log_bid_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_ask_decrease_ticks2_4_rate` | `w100ms_log_ask_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_bid_add_ticks5_9_rate` | `w100ms_log_bid_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_ask_add_ticks5_9_rate` | `w100ms_log_ask_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_bid_decrease_ticks5_9_rate` | `w100ms_log_bid_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_ask_decrease_ticks5_9_rate` | `w100ms_log_ask_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_bid_refill_proxy_rate` | `w100ms_log_bid_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_ask_refill_proxy_rate` | `w100ms_log_ask_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_bid_refill_proxy_mean_ms` | `w100ms_bid_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_ask_refill_proxy_mean_ms` | `w100ms_ask_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w100ms_log_bid_refill_proxy_notional_rate` | `w100ms_log_bid_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w100ms_log_ask_refill_proxy_notional_rate` | `w100ms_log_ask_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w100ms_bid_signed_touch_qty_change` | `w100ms_bid_signed_touch_qty_change` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w1000ms_log_trade_count_rate` | `w1000ms_log_trade_count_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w1000ms_log_trade_notional_rate` | `w1000ms_log_trade_notional_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w1000ms_bid_signed_trade_notional_imbalance` | `w1000ms_bid_signed_trade_notional_imbalance` | market_feature | `trades` | `blocked` | no |
| `micro:w1000ms_log_bid_aggressor_rate` | `w1000ms_log_bid_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w1000ms_log_ask_aggressor_rate` | `w1000ms_log_ask_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w1000ms_log_depth_batch_rate` | `w1000ms_log_depth_batch_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_depth_row_rate` | `w1000ms_log_depth_row_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_bid_signed_ofi_scaled` | `w1000ms_bid_signed_ofi_scaled` | market_feature | `panel_topk (approx) / event_lob (exact)` | `needs_work` | related:cont_ofi_panel_1s (panel approx) |
| `micro:w1000ms_realized_vol_bp` | `w1000ms_realized_vol_bp` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_bid_signed_return_bp` | `w1000ms_bid_signed_return_bp` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_log_bid_add_ticks0_1_rate` | `w1000ms_log_bid_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_ask_add_ticks0_1_rate` | `w1000ms_log_ask_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_bid_decrease_ticks0_1_rate` | `w1000ms_log_bid_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_ask_decrease_ticks0_1_rate` | `w1000ms_log_ask_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_bid_add_ticks2_4_rate` | `w1000ms_log_bid_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_ask_add_ticks2_4_rate` | `w1000ms_log_ask_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_bid_decrease_ticks2_4_rate` | `w1000ms_log_bid_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_ask_decrease_ticks2_4_rate` | `w1000ms_log_ask_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_bid_add_ticks5_9_rate` | `w1000ms_log_bid_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_ask_add_ticks5_9_rate` | `w1000ms_log_ask_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_bid_decrease_ticks5_9_rate` | `w1000ms_log_bid_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_ask_decrease_ticks5_9_rate` | `w1000ms_log_ask_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_bid_refill_proxy_rate` | `w1000ms_log_bid_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_ask_refill_proxy_rate` | `w1000ms_log_ask_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_bid_refill_proxy_mean_ms` | `w1000ms_bid_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_ask_refill_proxy_mean_ms` | `w1000ms_ask_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w1000ms_log_bid_refill_proxy_notional_rate` | `w1000ms_log_bid_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w1000ms_log_ask_refill_proxy_notional_rate` | `w1000ms_log_ask_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w1000ms_bid_signed_touch_qty_change` | `w1000ms_bid_signed_touch_qty_change` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w5000ms_log_trade_count_rate` | `w5000ms_log_trade_count_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w5000ms_log_trade_notional_rate` | `w5000ms_log_trade_notional_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w5000ms_bid_signed_trade_notional_imbalance` | `w5000ms_bid_signed_trade_notional_imbalance` | market_feature | `trades` | `blocked` | no |
| `micro:w5000ms_log_bid_aggressor_rate` | `w5000ms_log_bid_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w5000ms_log_ask_aggressor_rate` | `w5000ms_log_ask_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w5000ms_log_depth_batch_rate` | `w5000ms_log_depth_batch_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_depth_row_rate` | `w5000ms_log_depth_row_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_bid_signed_ofi_scaled` | `w5000ms_bid_signed_ofi_scaled` | market_feature | `panel_topk (approx) / event_lob (exact)` | `needs_work` | related:cont_ofi_panel_1s (panel approx) |
| `micro:w5000ms_realized_vol_bp` | `w5000ms_realized_vol_bp` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_bid_signed_return_bp` | `w5000ms_bid_signed_return_bp` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_log_bid_add_ticks0_1_rate` | `w5000ms_log_bid_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_ask_add_ticks0_1_rate` | `w5000ms_log_ask_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_bid_decrease_ticks0_1_rate` | `w5000ms_log_bid_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_ask_decrease_ticks0_1_rate` | `w5000ms_log_ask_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_bid_add_ticks2_4_rate` | `w5000ms_log_bid_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_ask_add_ticks2_4_rate` | `w5000ms_log_ask_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_bid_decrease_ticks2_4_rate` | `w5000ms_log_bid_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_ask_decrease_ticks2_4_rate` | `w5000ms_log_ask_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_bid_add_ticks5_9_rate` | `w5000ms_log_bid_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_ask_add_ticks5_9_rate` | `w5000ms_log_ask_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_bid_decrease_ticks5_9_rate` | `w5000ms_log_bid_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_ask_decrease_ticks5_9_rate` | `w5000ms_log_ask_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_bid_refill_proxy_rate` | `w5000ms_log_bid_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_ask_refill_proxy_rate` | `w5000ms_log_ask_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_bid_refill_proxy_mean_ms` | `w5000ms_bid_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_ask_refill_proxy_mean_ms` | `w5000ms_ask_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w5000ms_log_bid_refill_proxy_notional_rate` | `w5000ms_log_bid_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w5000ms_log_ask_refill_proxy_notional_rate` | `w5000ms_log_ask_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w5000ms_bid_signed_touch_qty_change` | `w5000ms_bid_signed_touch_qty_change` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w30000ms_log_trade_count_rate` | `w30000ms_log_trade_count_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w30000ms_log_trade_notional_rate` | `w30000ms_log_trade_notional_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w30000ms_bid_signed_trade_notional_imbalance` | `w30000ms_bid_signed_trade_notional_imbalance` | market_feature | `trades` | `blocked` | no |
| `micro:w30000ms_log_bid_aggressor_rate` | `w30000ms_log_bid_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w30000ms_log_ask_aggressor_rate` | `w30000ms_log_ask_aggressor_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w30000ms_log_depth_batch_rate` | `w30000ms_log_depth_batch_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_depth_row_rate` | `w30000ms_log_depth_row_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_bid_signed_ofi_scaled` | `w30000ms_bid_signed_ofi_scaled` | market_feature | `panel_topk (approx) / event_lob (exact)` | `needs_work` | related:cont_ofi_panel_1s (panel approx) |
| `micro:w30000ms_realized_vol_bp` | `w30000ms_realized_vol_bp` | market_feature | `panel_topk` | `ready` | no |
| `micro:w30000ms_bid_signed_return_bp` | `w30000ms_bid_signed_return_bp` | market_feature | `panel_topk` | `ready` | no |
| `micro:w30000ms_log_bid_add_ticks0_1_rate` | `w30000ms_log_bid_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_ask_add_ticks0_1_rate` | `w30000ms_log_ask_add_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_bid_decrease_ticks0_1_rate` | `w30000ms_log_bid_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_ask_decrease_ticks0_1_rate` | `w30000ms_log_ask_decrease_ticks0_1_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_bid_add_ticks2_4_rate` | `w30000ms_log_bid_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_ask_add_ticks2_4_rate` | `w30000ms_log_ask_add_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_bid_decrease_ticks2_4_rate` | `w30000ms_log_bid_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_ask_decrease_ticks2_4_rate` | `w30000ms_log_ask_decrease_ticks2_4_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_bid_add_ticks5_9_rate` | `w30000ms_log_bid_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_ask_add_ticks5_9_rate` | `w30000ms_log_ask_add_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_bid_decrease_ticks5_9_rate` | `w30000ms_log_bid_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_ask_decrease_ticks5_9_rate` | `w30000ms_log_ask_decrease_ticks5_9_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_bid_refill_proxy_rate` | `w30000ms_log_bid_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_ask_refill_proxy_rate` | `w30000ms_log_ask_refill_proxy_rate` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_bid_refill_proxy_mean_ms` | `w30000ms_bid_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_ask_refill_proxy_mean_ms` | `w30000ms_ask_refill_proxy_mean_ms` | market_feature | `event_lob` | `blocked` | no |
| `micro:w30000ms_log_bid_refill_proxy_notional_rate` | `w30000ms_log_bid_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w30000ms_log_ask_refill_proxy_notional_rate` | `w30000ms_log_ask_refill_proxy_notional_rate` | market_feature | `event_lob+trades` | `blocked` | no |
| `micro:w30000ms_bid_signed_touch_qty_change` | `w30000ms_bid_signed_touch_qty_change` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:log_bid_touch_back_ratio_l3` | `log_bid_touch_back_ratio_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_ask_touch_back_ratio_l3` | `log_ask_touch_back_ratio_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_uniformity_l3` | `bid_uniformity_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_uniformity_l3` | `ask_uniformity_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_hhi_l3` | `bid_hhi_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_hhi_l3` | `ask_hhi_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_outer_share_l3` | `bid_outer_share_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_outer_share_l3` | `ask_outer_share_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_bid_touch_back_ratio_l5` | `log_bid_touch_back_ratio_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_ask_touch_back_ratio_l5` | `log_ask_touch_back_ratio_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_uniformity_l5` | `bid_uniformity_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_uniformity_l5` | `ask_uniformity_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_hhi_l5` | `bid_hhi_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_hhi_l5` | `ask_hhi_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_outer_share_l5` | `bid_outer_share_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_outer_share_l5` | `ask_outer_share_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_bid_touch_back_ratio_l10` | `log_bid_touch_back_ratio_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_ask_touch_back_ratio_l10` | `log_ask_touch_back_ratio_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_uniformity_l10` | `bid_uniformity_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_uniformity_l10` | `ask_uniformity_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_hhi_l10` | `bid_hhi_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_hhi_l10` | `ask_hhi_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:bid_outer_share_l10` | `bid_outer_share_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:ask_outer_share_l10` | `ask_outer_share_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_bid_notional_l3` | `log_bid_notional_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:log_ask_notional_l3` | `log_ask_notional_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:imbalance_l3` | `imbalance_l3` | market_feature | `panel_topk` | `ready` | code:imbalance_l3 (no Spec yaml) |
| `micro:depth_symmetry_l1` | `depth_symmetry_l1` | market_feature | `panel_topk` | `ready` | no |
| `micro:depth_symmetry_l3` | `depth_symmetry_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:depth_symmetry_l5` | `depth_symmetry_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:depth_symmetry_l10` | `depth_symmetry_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:w500ms_delta_bid_uniformity_l5` | `w500ms_delta_bid_uniformity_l5` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_ask_uniformity_l5` | `w500ms_delta_ask_uniformity_l5` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_bid_hhi_l5` | `w500ms_delta_bid_hhi_l5` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_ask_hhi_l5` | `w500ms_delta_ask_hhi_l5` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_bid_outer_share_l5` | `w500ms_delta_bid_outer_share_l5` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_ask_outer_share_l5` | `w500ms_delta_ask_outer_share_l5` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_log_bid_notional_l3` | `w500ms_delta_log_bid_notional_l3` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_log_ask_notional_l3` | `w500ms_delta_log_ask_notional_l3` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_imbalance_l3` | `w500ms_delta_imbalance_l3` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_delta_depth_symmetry_l10` | `w500ms_delta_depth_symmetry_l10` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w1000ms_delta_bid_uniformity_l5` | `w1000ms_delta_bid_uniformity_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_ask_uniformity_l5` | `w1000ms_delta_ask_uniformity_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_bid_hhi_l5` | `w1000ms_delta_bid_hhi_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_ask_hhi_l5` | `w1000ms_delta_ask_hhi_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_bid_outer_share_l5` | `w1000ms_delta_bid_outer_share_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_ask_outer_share_l5` | `w1000ms_delta_ask_outer_share_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_log_bid_notional_l3` | `w1000ms_delta_log_bid_notional_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_log_ask_notional_l3` | `w1000ms_delta_log_ask_notional_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_imbalance_l3` | `w1000ms_delta_imbalance_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:w1000ms_delta_depth_symmetry_l10` | `w1000ms_delta_depth_symmetry_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_bid_uniformity_l5` | `w5000ms_delta_bid_uniformity_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_ask_uniformity_l5` | `w5000ms_delta_ask_uniformity_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_bid_hhi_l5` | `w5000ms_delta_bid_hhi_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_ask_hhi_l5` | `w5000ms_delta_ask_hhi_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_bid_outer_share_l5` | `w5000ms_delta_bid_outer_share_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_ask_outer_share_l5` | `w5000ms_delta_ask_outer_share_l5` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_log_bid_notional_l3` | `w5000ms_delta_log_bid_notional_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_log_ask_notional_l3` | `w5000ms_delta_log_ask_notional_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_imbalance_l3` | `w5000ms_delta_imbalance_l3` | market_feature | `panel_topk` | `ready` | no |
| `micro:w5000ms_delta_depth_symmetry_l10` | `w5000ms_delta_depth_symmetry_l10` | market_feature | `panel_topk` | `ready` | no |
| `micro:w500ms_return_bp` | `w500ms_return_bp` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:w500ms_log_trade_notional_rate` | `w500ms_log_trade_notional_rate` | market_feature | `trades` | `blocked` | no |
| `micro:w500ms_trade_imbalance` | `w500ms_trade_imbalance` | market_feature | `trades` | `blocked` | no |
| `micro:w500ms_ofi_scaled` | `w500ms_ofi_scaled` | market_feature | `panel_topk (approx) / event_lob (exact)` | `needs_work` | related:cont_ofi_panel_1s (panel approx) |
| `micro:w500ms_realized_vol_bp` | `w500ms_realized_vol_bp` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:volatility_rate_ratio_100ms_5s` | `volatility_rate_ratio_100ms_5s` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:bid_fragility_interaction` | `bid_fragility_interaction` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `micro:ask_fragility_interaction` | `ask_fragility_interaction` | market_feature | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |

## 5. Market states supplements (`states:*`, 53 new)

n=53. Primary impl under `cryptocurrency_quant/app/…` (see Sources).

| id | name | formula/role (brief) | required inputs | portability | already-ported? |
|---|---|---|---|---|---|
| `states:w100ms_spread_change_ticks` | `w100ms_spread_change_ticks` | spread_ticks(t)-spread_ticks(t-w) | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `states:w100ms_bid_l5_change_fraction` | `w100ms_bid_l5_change_fraction` | bid_L5_notional(t)/bid_L5_notional(asof(t-w))-1 | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `states:w100ms_ask_l5_change_fraction` | `w100ms_ask_l5_change_fraction` | ask_L5_notional(t)/ask_L5_notional(asof(t-w))-1 | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `states:w100ms_bbo_change_rate` | `w100ms_bbo_change_rate` | number of complete LOCAL batches whose BBO changed / window seconds | `event_lob` | `blocked` | no |
| `states:w100ms_both_decrease_batch_rate` | `w100ms_both_decrease_batch_rate` | number of LOCAL timestamp batches with positive net decreases on both sides, within 2 ticks of pre-b | `event_lob` | `blocked` | no |
| `states:w100ms_both_add_batch_rate` | `w100ms_both_add_batch_rate` | number of LOCAL timestamp batches with positive net adds on both sides, within 2 ticks of pre-batch  | `event_lob` | `blocked` | no |
| `states:w100ms_buy_multilevel_print_rate` | `w100ms_buy_multilevel_print_rate` | number of public buy prints priced at/above the second pre-batch visible ask / seconds | `trades` | `blocked` | no |
| `states:w100ms_sell_multilevel_print_rate` | `w100ms_sell_multilevel_print_rate` | number of public sell prints priced at/below the second pre-batch visible bid / seconds | `trades` | `blocked` | no |
| `states:w500ms_spread_change_ticks` | `w500ms_spread_change_ticks` | spread_ticks(t)-spread_ticks(t-w) | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `states:w500ms_bid_l5_change_fraction` | `w500ms_bid_l5_change_fraction` | bid_L5_notional(t)/bid_L5_notional(asof(t-w))-1 | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `states:w500ms_ask_l5_change_fraction` | `w500ms_ask_l5_change_fraction` | ask_L5_notional(t)/ask_L5_notional(asof(t-w))-1 | `panel_topk (approx; subsecond/event design)` | `needs_work` | no |
| `states:w500ms_bbo_change_rate` | `w500ms_bbo_change_rate` | number of complete LOCAL batches whose BBO changed / window seconds | `event_lob` | `blocked` | no |
| `states:w500ms_both_decrease_batch_rate` | `w500ms_both_decrease_batch_rate` | number of LOCAL timestamp batches with positive net decreases on both sides, within 2 ticks of pre-b | `event_lob` | `blocked` | no |
| `states:w500ms_both_add_batch_rate` | `w500ms_both_add_batch_rate` | number of LOCAL timestamp batches with positive net adds on both sides, within 2 ticks of pre-batch  | `event_lob` | `blocked` | no |
| `states:w500ms_buy_multilevel_print_rate` | `w500ms_buy_multilevel_print_rate` | number of public buy prints priced at/above the second pre-batch visible ask / seconds | `trades` | `blocked` | no |
| `states:w500ms_sell_multilevel_print_rate` | `w500ms_sell_multilevel_print_rate` | number of public sell prints priced at/below the second pre-batch visible bid / seconds | `trades` | `blocked` | no |
| `states:w1000ms_spread_change_ticks` | `w1000ms_spread_change_ticks` | spread_ticks(t)-spread_ticks(t-w) | `panel_topk` | `ready` | no |
| `states:w1000ms_bid_l5_change_fraction` | `w1000ms_bid_l5_change_fraction` | bid_L5_notional(t)/bid_L5_notional(asof(t-w))-1 | `panel_topk` | `ready` | no |
| `states:w1000ms_ask_l5_change_fraction` | `w1000ms_ask_l5_change_fraction` | ask_L5_notional(t)/ask_L5_notional(asof(t-w))-1 | `panel_topk` | `ready` | no |
| `states:w1000ms_bbo_change_rate` | `w1000ms_bbo_change_rate` | number of complete LOCAL batches whose BBO changed / window seconds | `event_lob` | `blocked` | no |
| `states:w1000ms_both_decrease_batch_rate` | `w1000ms_both_decrease_batch_rate` | number of LOCAL timestamp batches with positive net decreases on both sides, within 2 ticks of pre-b | `event_lob` | `blocked` | no |
| `states:w1000ms_both_add_batch_rate` | `w1000ms_both_add_batch_rate` | number of LOCAL timestamp batches with positive net adds on both sides, within 2 ticks of pre-batch  | `event_lob` | `blocked` | no |
| `states:w1000ms_buy_multilevel_print_rate` | `w1000ms_buy_multilevel_print_rate` | number of public buy prints priced at/above the second pre-batch visible ask / seconds | `trades` | `blocked` | no |
| `states:w1000ms_sell_multilevel_print_rate` | `w1000ms_sell_multilevel_print_rate` | number of public sell prints priced at/below the second pre-batch visible bid / seconds | `trades` | `blocked` | no |
| `states:w2000ms_spread_change_ticks` | `w2000ms_spread_change_ticks` | spread_ticks(t)-spread_ticks(t-w) | `panel_topk` | `ready` | no |
| `states:w2000ms_bid_l5_change_fraction` | `w2000ms_bid_l5_change_fraction` | bid_L5_notional(t)/bid_L5_notional(asof(t-w))-1 | `panel_topk` | `ready` | no |
| `states:w2000ms_ask_l5_change_fraction` | `w2000ms_ask_l5_change_fraction` | ask_L5_notional(t)/ask_L5_notional(asof(t-w))-1 | `panel_topk` | `ready` | no |
| `states:w2000ms_bbo_change_rate` | `w2000ms_bbo_change_rate` | number of complete LOCAL batches whose BBO changed / window seconds | `event_lob` | `blocked` | no |
| `states:w2000ms_both_decrease_batch_rate` | `w2000ms_both_decrease_batch_rate` | number of LOCAL timestamp batches with positive net decreases on both sides, within 2 ticks of pre-b | `event_lob` | `blocked` | no |
| `states:w2000ms_both_add_batch_rate` | `w2000ms_both_add_batch_rate` | number of LOCAL timestamp batches with positive net adds on both sides, within 2 ticks of pre-batch  | `event_lob` | `blocked` | no |
| `states:w2000ms_buy_multilevel_print_rate` | `w2000ms_buy_multilevel_print_rate` | number of public buy prints priced at/above the second pre-batch visible ask / seconds | `trades` | `blocked` | no |
| `states:w2000ms_sell_multilevel_print_rate` | `w2000ms_sell_multilevel_print_rate` | number of public sell prints priced at/below the second pre-batch visible bid / seconds | `trades` | `blocked` | no |
| `states:w3000ms_spread_change_ticks` | `w3000ms_spread_change_ticks` | spread_ticks(t)-spread_ticks(t-w) | `panel_topk` | `ready` | no |
| `states:w3000ms_bid_l5_change_fraction` | `w3000ms_bid_l5_change_fraction` | bid_L5_notional(t)/bid_L5_notional(asof(t-w))-1 | `panel_topk` | `ready` | no |
| `states:w3000ms_ask_l5_change_fraction` | `w3000ms_ask_l5_change_fraction` | ask_L5_notional(t)/ask_L5_notional(asof(t-w))-1 | `panel_topk` | `ready` | no |
| `states:w3000ms_bbo_change_rate` | `w3000ms_bbo_change_rate` | number of complete LOCAL batches whose BBO changed / window seconds | `event_lob` | `blocked` | no |
| `states:w3000ms_both_decrease_batch_rate` | `w3000ms_both_decrease_batch_rate` | number of LOCAL timestamp batches with positive net decreases on both sides, within 2 ticks of pre-b | `event_lob` | `blocked` | no |
| `states:w3000ms_both_add_batch_rate` | `w3000ms_both_add_batch_rate` | number of LOCAL timestamp batches with positive net adds on both sides, within 2 ticks of pre-batch  | `event_lob` | `blocked` | no |
| `states:w3000ms_buy_multilevel_print_rate` | `w3000ms_buy_multilevel_print_rate` | number of public buy prints priced at/above the second pre-batch visible ask / seconds | `trades` | `blocked` | no |
| `states:w3000ms_sell_multilevel_print_rate` | `w3000ms_sell_multilevel_print_rate` | number of public sell prints priced at/below the second pre-batch visible bid / seconds | `trades` | `blocked` | no |
| `states:last_trade_age_ms` | `last_trade_age_ms` | (now-last observed valid public trade receipt)/1e6 | `trades` | `blocked` | no |
| `states:bid_touch_depletion_seconds` | `bid_touch_depletion_seconds` | current bid touch notional / prior 1s aggressive sell notional rate | `event_lob` | `blocked` | no |
| `states:ask_touch_depletion_seconds` | `ask_touch_depletion_seconds` | current ask touch notional / prior 1s aggressive buy notional rate | `event_lob` | `blocked` | no |
| `states:bid_trade_adjusted_net_decrease_rate` | `bid_trade_adjusted_net_decrease_rate` | max(0, prior1s bid net decrease within1tick - prior1s aggressive sell notional); spatial/timing mism | `event_lob+trades` | `blocked` | no |
| `states:ask_trade_adjusted_net_decrease_rate` | `ask_trade_adjusted_net_decrease_rate` | max(0, prior1s ask net decrease within1tick - prior1s aggressive buy notional); spatial/timing misma | `event_lob+trades` | `blocked` | no |
| `states:w2000ms_return_bp` | `w2000ms_return_bp` | ln(mid(t)/mid(asof(t-w)))*10000 | `panel_topk` | `ready` | no |
| `states:w2000ms_realized_vol_bp` | `w2000ms_realized_vol_bp` | sqrt(sum of squared successive observed log-mid changes in bp over (t-w,t]) | `panel_topk` | `ready` | no |
| `states:w2000ms_trade_imbalance` | `w2000ms_trade_imbalance` | (buy_notional-sell_notional)/(buy_notional+sell_notional); valid complete empty window =>0 | `trades` | `blocked` | no |
| `states:w2000ms_trade_notional_rate` | `w2000ms_trade_notional_rate` | (buy_notional+sell_notional)/window_seconds | `trades` | `blocked` | no |
| `states:w3000ms_return_bp` | `w3000ms_return_bp` | ln(mid(t)/mid(asof(t-w)))*10000 | `panel_topk` | `ready` | no |
| `states:w3000ms_realized_vol_bp` | `w3000ms_realized_vol_bp` | sqrt(sum of squared successive observed log-mid changes in bp over (t-w,t]) | `panel_topk` | `ready` | no |
| `states:w3000ms_trade_imbalance` | `w3000ms_trade_imbalance` | (buy_notional-sell_notional)/(buy_notional+sell_notional); valid complete empty window =>0 | `trades` | `blocked` | no |
| `states:w3000ms_trade_notional_rate` | `w3000ms_trade_notional_rate` | (buy_notional+sell_notional)/window_seconds | `trades` | `blocked` | no |

## 6. Paper173 (`paper:*`, 173)

Impl: `app/factor_library/paper173.py` / `research/paper_reversal_20261027/features.py`.
Most need 100ms event/trade windows → `blocked` or `needs_work` (return/autocov only).

| id | name | formula/role (brief) | required inputs | portability | already-ported? |
|---|---|---|---|---|---|
| `paper:ret_autocov_100ms_w0` | `ret_autocov_100ms_w0` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_100ms_w1` | `ret_autocov_100ms_w1` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_100ms_w2` | `ret_autocov_100ms_w2` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_100ms_w0` | `ret_sum_100ms_w0` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_100ms_w1` | `ret_sum_100ms_w1` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_100ms_w2` | `ret_sum_100ms_w2` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:trade_intensity_100ms_w0` | `trade_intensity_100ms_w0` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_100ms_w1` | `trade_intensity_100ms_w1` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_100ms_w2` | `trade_intensity_100ms_w2` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:ret_autocov_1s_w0` | `ret_autocov_1s_w0` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_1s_w1` | `ret_autocov_1s_w1` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_1s_w2` | `ret_autocov_1s_w2` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_1s_w0` | `ret_sum_1s_w0` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_1s_w1` | `ret_sum_1s_w1` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_1s_w2` | `ret_sum_1s_w2` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:trade_intensity_1s_w0` | `trade_intensity_1s_w0` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_1s_w1` | `trade_intensity_1s_w1` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_1s_w2` | `trade_intensity_1s_w2` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:ret_autocov_5s_w0` | `ret_autocov_5s_w0` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_5s_w1` | `ret_autocov_5s_w1` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_5s_w2` | `ret_autocov_5s_w2` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_5s_w0` | `ret_sum_5s_w0` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_5s_w1` | `ret_sum_5s_w1` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_5s_w2` | `ret_sum_5s_w2` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:trade_intensity_5s_w0` | `trade_intensity_5s_w0` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_5s_w1` | `trade_intensity_5s_w1` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_5s_w2` | `trade_intensity_5s_w2` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:ret_autocov_30s_w0` | `ret_autocov_30s_w0` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_30s_w1` | `ret_autocov_30s_w1` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_30s_w2` | `ret_autocov_30s_w2` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_30s_w0` | `ret_sum_30s_w0` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_30s_w1` | `ret_sum_30s_w1` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_30s_w2` | `ret_sum_30s_w2` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:trade_intensity_30s_w0` | `trade_intensity_30s_w0` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_30s_w1` | `trade_intensity_30s_w1` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_30s_w2` | `trade_intensity_30s_w2` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:ret_autocov_300s_w0` | `ret_autocov_300s_w0` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_300s_w1` | `ret_autocov_300s_w1` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_autocov_300s_w2` | `ret_autocov_300s_w2` | mean((r[:-1]-mean(r))*(r[1:]-mean(r))); r=side*diff(log(trade_price)) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_300s_w0` | `ret_sum_300s_w0` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_300s_w1` | `ret_sum_300s_w1` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:ret_sum_300s_w2` | `ret_sum_300s_w2` | sum(side*diff(log(trade_price))) | `event_lob` | `needs_work` | no |
| `paper:trade_intensity_300s_w0` | `trade_intensity_300s_w0` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_300s_w1` | `trade_intensity_300s_w1` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:trade_intensity_300s_w2` | `trade_intensity_300s_w2` | mean(diff(trade_receipt_ns))/1e9; an interval, NOT trades/second | `trades` | `blocked` | no |
| `paper:age` | `age` | (now-last_actual_BBO_price_change_ns)/1e9 | `event_lob` | `blocked` | no |
| `paper:ob_ask_liq` | `ob_ask_liq` | opposite-order-side touch base_qty | `event_lob` | `blocked` | no |
| `paper:ob_bid_liq` | `ob_bid_liq` | same-order-side touch base_qty | `event_lob` | `blocked` | no |
| `paper:ob_half` | `ob_half` | same-side VWAP impact for 500000 quote notional, bp; insufficient book ->NaN | `event_lob` | `blocked` | no |
| `paper:ob_other_half` | `ob_other_half` | opposite-side VWAP impact for 500000 quote notional, bp; insufficient book ->NaN | `event_lob` | `blocked` | no |
| `paper:totb_mean` | `totb_mean` | mean(BBO price change intervals ending within trailing 600s) | `event_lob` | `blocked` | no |
| `paper:amplitude_100ms_w0` | `amplitude_100ms_w0` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_100ms_w1` | `amplitude_100ms_w1` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_100ms_w2` | `amplitude_100ms_w2` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:ret_vwap_100ms_w0` | `ret_vwap_100ms_w0` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_100ms_w1` | `ret_vwap_100ms_w1` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_100ms_w2` | `ret_vwap_100ms_w2` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:amplitude_1s_w0` | `amplitude_1s_w0` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_1s_w1` | `amplitude_1s_w1` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_1s_w2` | `amplitude_1s_w2` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:ret_vwap_1s_w0` | `ret_vwap_1s_w0` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_1s_w1` | `ret_vwap_1s_w1` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_1s_w2` | `ret_vwap_1s_w2` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:amplitude_5s_w0` | `amplitude_5s_w0` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_5s_w1` | `amplitude_5s_w1` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_5s_w2` | `amplitude_5s_w2` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:ret_vwap_5s_w0` | `ret_vwap_5s_w0` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_5s_w1` | `ret_vwap_5s_w1` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_5s_w2` | `ret_vwap_5s_w2` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:amplitude_30s_w0` | `amplitude_30s_w0` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_30s_w1` | `amplitude_30s_w1` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_30s_w2` | `amplitude_30s_w2` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:ret_vwap_30s_w0` | `ret_vwap_30s_w0` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_30s_w1` | `ret_vwap_30s_w1` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_30s_w2` | `ret_vwap_30s_w2` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:amplitude_300s_w0` | `amplitude_300s_w0` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_300s_w1` | `amplitude_300s_w1` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:amplitude_300s_w2` | `amplitude_300s_w2` | max(trade_price)-min(trade_price) | `event_lob` | `blocked` | no |
| `paper:ret_vwap_300s_w0` | `ret_vwap_300s_w0` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_300s_w1` | `ret_vwap_300s_w1` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:ret_vwap_300s_w2` | `ret_vwap_300s_w2` | side*log(sum(price*qty)/sum(qty)/current_side_touch_price) | `event_lob` | `needs_work` | no |
| `paper:stdev_100` | `stdev_100` | std(100 log returns of trailing 10s last-trade grid,ddof=1) | `event_lob` | `blocked` | no |
| `paper:stdev_500` | `stdev_500` | std(500 log returns of trailing 10s last-trade grid,ddof=1) | `event_lob` | `blocked` | no |
| `paper:max_size_100ms_w0` | `max_size_100ms_w0` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_100ms_w1` | `max_size_100ms_w1` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_100ms_w2` | `max_size_100ms_w2` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_100ms_w0` | `avg_size_100ms_w0` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_100ms_w1` | `avg_size_100ms_w1` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_100ms_w2` | `avg_size_100ms_w2` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:buy_count_100ms_w0` | `buy_count_100ms_w0` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_100ms_w1` | `buy_count_100ms_w1` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_100ms_w2` | `buy_count_100ms_w2` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_100ms_w0` | `sell_count_100ms_w0` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_100ms_w1` | `sell_count_100ms_w1` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_100ms_w2` | `sell_count_100ms_w2` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:total_buy_100ms_w0` | `total_buy_100ms_w0` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_100ms_w1` | `total_buy_100ms_w1` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_100ms_w2` | `total_buy_100ms_w2` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_100ms_w0` | `total_sell_100ms_w0` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_100ms_w1` | `total_sell_100ms_w1` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_100ms_w2` | `total_sell_100ms_w2` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_1s_w0` | `max_size_1s_w0` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_1s_w1` | `max_size_1s_w1` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_1s_w2` | `max_size_1s_w2` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_1s_w0` | `avg_size_1s_w0` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_1s_w1` | `avg_size_1s_w1` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_1s_w2` | `avg_size_1s_w2` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:buy_count_1s_w0` | `buy_count_1s_w0` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_1s_w1` | `buy_count_1s_w1` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_1s_w2` | `buy_count_1s_w2` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_1s_w0` | `sell_count_1s_w0` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_1s_w1` | `sell_count_1s_w1` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_1s_w2` | `sell_count_1s_w2` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:total_buy_1s_w0` | `total_buy_1s_w0` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_1s_w1` | `total_buy_1s_w1` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_1s_w2` | `total_buy_1s_w2` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_1s_w0` | `total_sell_1s_w0` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_1s_w1` | `total_sell_1s_w1` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_1s_w2` | `total_sell_1s_w2` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_5s_w0` | `max_size_5s_w0` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_5s_w1` | `max_size_5s_w1` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_5s_w2` | `max_size_5s_w2` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_5s_w0` | `avg_size_5s_w0` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_5s_w1` | `avg_size_5s_w1` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_5s_w2` | `avg_size_5s_w2` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:buy_count_5s_w0` | `buy_count_5s_w0` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_5s_w1` | `buy_count_5s_w1` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_5s_w2` | `buy_count_5s_w2` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_5s_w0` | `sell_count_5s_w0` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_5s_w1` | `sell_count_5s_w1` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_5s_w2` | `sell_count_5s_w2` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:total_buy_5s_w0` | `total_buy_5s_w0` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_5s_w1` | `total_buy_5s_w1` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_5s_w2` | `total_buy_5s_w2` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_5s_w0` | `total_sell_5s_w0` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_5s_w1` | `total_sell_5s_w1` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_5s_w2` | `total_sell_5s_w2` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_30s_w0` | `max_size_30s_w0` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_30s_w1` | `max_size_30s_w1` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_30s_w2` | `max_size_30s_w2` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_30s_w0` | `avg_size_30s_w0` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_30s_w1` | `avg_size_30s_w1` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_30s_w2` | `avg_size_30s_w2` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:buy_count_30s_w0` | `buy_count_30s_w0` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_30s_w1` | `buy_count_30s_w1` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_30s_w2` | `buy_count_30s_w2` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_30s_w0` | `sell_count_30s_w0` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_30s_w1` | `sell_count_30s_w1` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_30s_w2` | `sell_count_30s_w2` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:total_buy_30s_w0` | `total_buy_30s_w0` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_30s_w1` | `total_buy_30s_w1` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_30s_w2` | `total_buy_30s_w2` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_30s_w0` | `total_sell_30s_w0` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_30s_w1` | `total_sell_30s_w1` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_30s_w2` | `total_sell_30s_w2` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_300s_w0` | `max_size_300s_w0` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_300s_w1` | `max_size_300s_w1` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:max_size_300s_w2` | `max_size_300s_w2` | max(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_300s_w0` | `avg_size_300s_w0` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_300s_w1` | `avg_size_300s_w1` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:avg_size_300s_w2` | `avg_size_300s_w2` | mean(trade_base_qty) | `event_lob` | `blocked` | no |
| `paper:buy_count_300s_w0` | `buy_count_300s_w0` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_300s_w1` | `buy_count_300s_w1` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:buy_count_300s_w2` | `buy_count_300s_w2` | count(order-same-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_300s_w0` | `sell_count_300s_w0` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_300s_w1` | `sell_count_300s_w1` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:sell_count_300s_w2` | `sell_count_300s_w2` | count(order-opposite-side aggressor trades) | `event_lob` | `blocked` | no |
| `paper:total_buy_300s_w0` | `total_buy_300s_w0` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_300s_w1` | `total_buy_300s_w1` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_buy_300s_w2` | `total_buy_300s_w2` | sum(order-same-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_300s_w0` | `total_sell_300s_w0` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_300s_w1` | `total_sell_300s_w1` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |
| `paper:total_sell_300s_w2` | `total_sell_300s_w2` | sum(order-opposite-side aggressor base_qty) | `event_lob` | `blocked` | no |

## 7. Out of scope for HF OB library (still catalogued)

### minute (18) + cicc (79)

Listed in unified catalog as technical / 中金 formula candidates. **Not** panel-LOB first-class. IDs:

- **minute** (18): `minute:side_rsi14_centered`, `minute:side_rsi7_centered`, `minute:side_rsi14_change`, `minute:rsi14_reversal_extreme`, `minute:side_return1_bp`, `minute:side_return5_bp`, `minute:side_return15_bp`, `minute:absolute_return1_bp`, `minute:range1_bp`, `minute:side_body1_bp`, `minute:side_close_minus_vwap1_bp`, `minute:side_close_minus_sma20_bp`, `minute:realized_volatility20_bp`, `minute:range_relative20`, `minute:log_volume1`, `minute:volume_relative20`, `minute:log_trade_count1`, `minute:side_aggressor_imbalance1`
- **cicc** (79): `cicc:mmt_pm`, `cicc:mmt_last30`, `cicc:mmt_paratio`, `cicc:mmt_am`, `cicc:mmt_between`, `cicc:mmt_ols_qrs`, `cicc:mmt_ols_corr_square_mean`, `cicc:mmt_ols_corr_mean`, `cicc:mmt_ols_beta_mean`, `cicc:mmt_ols_beta_zscore_last`, `cicc:mmt_top50VolumeRet`, `cicc:mmt_bottom50VolumeRet`, `cicc:mmt_top20VolumeRet`, `cicc:mmt_bottom20VolumeRet`, `cicc:vol_volume1min`, `cicc:vol_range1min`, `cicc:vol_return1min`, `cicc:vol_upVol`, `cicc:vol_upRatio`, `cicc:vol_downVol`, `cicc:vol_downRatio`, `cicc:shape_skew`, `cicc:shape_kurt`, `cicc:shape_skratio`, `cicc:shape_skewVol`, `cicc:shape_kurtVol`, `cicc:shape_skratioVol`, `cicc:liq_amihud_1min`, `cicc:liq_askDepthCct`, `cicc:liq_avgDepthCct`, `cicc:liq_bidDepthCct`, `cicc:liq_closeprevol`, `cicc:liq_closevol`, `cicc:liq_effDepthCct`, `cicc:liq_firstCallR`, `cicc:liq_lastCallR`, `cicc:liq_openvol`, `cicc:liq_spread_std`, `cicc:corr_prv`, `cicc:corr_prvr`, `cicc:corr_pv`, `cicc:corr_pvd`, `cicc:corr_pvl`, `cicc:corr_pvr`, `cicc:doc_kurt`, `cicc:doc_skew`, `cicc:doc_std`, `cicc:doc_vol_pdf60`, `cicc:doc_vol_pdf70`, `cicc:doc_vol_pdf80`, `cicc:doc_vol_pdf90`, `cicc:doc_vol_pdf90bi`, `cicc:doc_vol_pdf95`, `cicc:doc_vol10_ratio`, `cicc:doc_vol5_ratio`, `cicc:doc_vol50_ratio`, `cicc:crowd_fftv10`, `cicc:crowd_fftv20_30s_no0`, `cicc:crowd_fftv20_30s_w0`, `cicc:crowd_fftv20_3s_w0`, `cicc:crowd_fftv20_high`, `cicc:crowd_fftv20_low`, `cicc:crowd_fftv5`, `cicc:crowd_origin_v50`, `cicc:crowd_fftv50m10`, `cicc:crowd_fftv50m5`, `cicc:trade_bidAskRatio`, `cicc:trade_bottom20retRatio`, `cicc:trade_bottom50retRatio`, `cicc:trade_CBuyRatio`, `cicc:trade_Cratio`, `cicc:trade_CSellRatio`, `cicc:trade_headRatio`, `cicc:trade_netBuyRatio`, `cicc:trade_tailRatio`, `cicc:trade_top20retRatio`, `cicc:trade_top50retRatio`, `cicc:trade_topNeg20retRatio`, `cicc:trade_topPos20retRatio`

## Recommended first Spec+pack batch (≤20, panel-ready)

Prefer diversity across families; skip already-evaled Specs; favor static book + short mid-path that L1 Spec can express now.

| # | proposed a4ob Spec id | source id | why |
|---:|---|---|---|
| 1 | `l1_imbalance` | `early9 / flow:touch_qty_imbalance / micro:bid_signed_imbalance_l1` | code exists; close Spec gap vs early9 |
| 2 | `imbalance_l3` | `micro:imbalance_l3` | code exists; multi-level shape |
| 3 | `imbalance_l5` | `micro:bid_signed_imbalance_l5` | depth shape beyond L1/L3 |
| 4 | `imbalance_l10` | `micro:bid_signed_imbalance_l10` | depth shape |
| 5 | `mid_return_1s` | `early9 mid_return / micro:w1000ms_bid_signed_return_bp` | code exists; path baseline |
| 6 | `ret_5s_bp` | `v3:D1` | panel lag mid return |
| 7 | `ret_30s_bp` | `v3:D2` | slower path |
| 8 | `rv_30s` | `v3:D6` | vol state |
| 9 | `rv_60s` | `v3:D7` | vol state |
| 10 | `rv_ratio_30_300` | `v3:D9` | vol regime |
| 11 | `range_position_60s` | `v3:D14` | path location |
| 12 | `microprice_mom_10s` | `v3:D13` | microprice dynamics on panel |
| 13 | `spread_dev_1h` | `v3:A8` | liquidity regime vs own history |
| 14 | `depth_imb_3t` | `v3:A1` | tick-band depth imb (approx with top-K) |
| 15 | `depth_imb_10t` | `v3:A2` | wider band |
| 16 | `depth_slope_imb` | `v3:A5` | shape slope |
| 17 | `near_depth_imbalance` | `flow:near_depth_imbalance` | near static; complements L1 |
| 18 | `depth_symmetry_l5` | `micro:depth_symmetry_l5` | 1−|imb| liquidity balance |
| 19 | `bid_hhi_l5` | `micro:bid_hhi_l5` | concentration / fragility proxy |
| 20 | `bid_outer_share_l5` | `micro:bid_outer_share_l5` | shape back-book share |

**Deferred (high value but not panel-ready):** flow S02–S05/S16–S21 event near-add/decrease; v3 B*/C* cancel & taker; event OFI exact (keep `cont_ofi_panel_1s` as approx); cross-coin E1–E7; paper173 100ms set.

## Notes / caveats

1. `ready` ≠ certified Rank-IC; only means Spec+panel compute is feasible on current L1.
2. Tick-band factors (A1–A5) approximate with top-K levels; tick size must come from config/symbol meta.
3. `microprice_bid_signed_bp` uses spread denom — related but not identical to ported `microprice_offset_bp`.
4. 80 `states→micro` aliases exist in unified `known_reuse` — do not double-count for orthogonality.
5. Next L1 step: Spec-ize the batch above; then expand pack universe (L2) before quality gate (L3).

---
L0 inventory for alpha4orderbook factor-library track.
