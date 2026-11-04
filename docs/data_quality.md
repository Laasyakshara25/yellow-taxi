# Data quality

## Silver validation rules

Records are **quarantined** (`rejection_reason = validation_failed`) when any of:

- Null pickup or dropoff timestamp
- Dropoff before pickup
- Null or non-positive zone IDs
- Null `trip_distance` or distance &gt; `quality.max_trip_distance_miles`
- Null `fare_amount` or outside `[min_fare_amount, max_fare_amount]`

Thresholds: [config/defaults.yaml](../config/defaults.yaml).

## Ingestion statuses (`ingestion_manifest.processing_status`)

| Status | Meaning |
|--------|---------|
| `ingested` | Success |
| `schema_mismatch` | Missing required columns |
| `unsupported_schema` | Pre-2011 era |
| `corrupted_file` | Unreadable Parquet |
| `duplicate` | Same `source_file_identity` already ingested |

## Reconciliation

Gold `pickup_count` sums must equal silver trip row counts for the same scope (see `reconcile_counts` in tests).

## DQ results table

`silver.data_quality_results` stores check name, expected/actual, and run ID (populated during orchestrated runs).
