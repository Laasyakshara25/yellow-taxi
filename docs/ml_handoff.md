# ML developer handoff

## Deliverables

1. `nyc_taxi.gold.ml_training_features` — includes `target_pickup_count`
2. `nyc_taxi.gold.ml_inference_features` — same schema minus target
3. [feature_contract.md](feature_contract.md) — definitions and leakage rules
4. `nyc_taxi.gold.fact_pickups_hourly` — source of truth for targets and lags

## Recommended workflow

1. Read feature contract and confirm warm-up (168h) handling for your model.
2. Filter training rows where required lags are non-null, or use your imputation policy.
3. Train on `forecast_hour` ranges documented in your experiment config.
4. For inference, read `ml_inference_features` at the latest `processed_at` for each zone/hour.

## Retrain triggers

- Corrected TLC month reprocessed (manifest + silver partition for `source_month`)
- Zone lookup updates
- Changes to `config/defaults.yaml` quality thresholds or coverage dates

## Out of scope in this repo

Model training, hyperparameter search, serving, MLflow registration, dashboards.

## Contact / lineage

Trace `source_month` and `ingestion_run_id` on `silver.trips` back to `bronze.ingestion_manifest`.
