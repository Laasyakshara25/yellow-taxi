# Pipeline validation report

**Executed:** 2026-10-28 (Databricks workspace `<workspace-host>`)

## Data loaded

| Asset | Location |
|-------|----------|
| Yellow trips 2023-01 | `/Volumes/nyc_taxi/bronze/raw/yellow/yellow_tripdata_2023-01.parquet` (~3.07M rows) |
| Taxi zone lookup | `/Volumes/nyc_taxi/bronze/raw/reference/taxi_zone_lookup.csv` |

Local copies (gitignored): `data/raw/` via TLC CloudFront URLs.

## Job run

| Item | Value |
|------|-------|
| Job | `nyc_taxi_pipeline_dev` (dev bundle target) |
| Final backfill run | **SUCCESS** (run id `1103078925623792` in workspace) |
| Bundle | `databricks bundle deploy -t dev` |

## Table row counts (SQL warehouse)

| Table | Rows |
|-------|------|
| `nyc_taxi.bronze.yellow_taxi_trips` | 3,066,766 |
| `nyc_taxi.silver.trips` | 3,066,526 |
| `nyc_taxi.gold.fact_pickups_hourly` | 197,160 |
| `nyc_taxi.gold.ml_training_features` | 197,160 |
| `nyc_taxi.bronze.ingestion_manifest` | 1 |

**Silver vs bronze delta:** 240 trips quarantined or deduplicated (expected).

**Gold hourly rows:** January 2023 coverage grid (zones × hours with zero-fill per config).

## Local tests

`pytest tests/unit -q` → **17 passed, 11 skipped** (Spark tests require local JDK).

## Re-run / new month

1. Upload Parquet to volume under `yellow/`.
2. `databricks bundle run nyc_taxi_pipeline -t dev`  
   Or `--only backfill_silver_gold` after bronze load.
