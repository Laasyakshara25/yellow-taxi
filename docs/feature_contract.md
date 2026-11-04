# Feature contract (ML handoff)

## Grain

One row per (`pickup_zone_id`, `forecast_hour`) in NYC local time.

## Target (training only)

| Column | Definition |
|--------|------------|
| `target_pickup_count` | Trip count in `forecast_hour` from `fact_pickups_hourly` |

## Features

| Column | Definition |
|--------|------------|
| `hour_of_day`, `day_of_week`, `day_of_month`, `month`, `is_weekend` | Calendar attributes of `forecast_hour` |
| `lag_1h`, `lag_24h`, `lag_168h` | Pickup count at `forecast_hour - n hours` (same zone) |
| `rolling_mean_24h`, `rolling_std_24h` | Stats over **prior** 24 hours (excludes `forecast_hour`) |
| `rolling_mean_168h` | Mean over prior 168 hours (excludes `forecast_hour`) |

## Leakage policy

No feature may use pickup counts at or after `forecast_hour`. Implemented with `lag` and `rowsBetween(-N, -1)` window frames.

## Warm-up

`lag_168h` and `rolling_mean_168h` require **168 prior observed hours** per zone; values are null until history exists. Do not impute with zero unless coverage grid explicitly marks the hour as observed-empty.

## Inference table

Same columns as training **except** `target_pickup_count`. Types must match.

## Time zone

`forecast_hour` is NYC wall-clock (`America/New_York`), documented on silver `local_timezone`.

## Null handling

- Lags/rollings: null during warm-up; ML developer chooses imputation or row filtering.
- Unknown history: do not fabricate zero demand.
