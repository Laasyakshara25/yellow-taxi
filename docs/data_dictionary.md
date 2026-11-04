# Data dictionary

Catalog default: `nyc_taxi` (configurable).

## Bronze

### `bronze.yellow_taxi_trips`

| Column | Type | Notes |
|--------|------|-------|
| `source_file`, `source_month`, `ingestion_run_id`, `ingested_at` | lineage | Partition: `source_month` |
| Trip fields | various | Normalized snake_case where possible |

**Grain:** one row per source trip record. **Refresh:** append/replace per reprocessed source month.

### `bronze.taxi_zone_lookup`

**Grain:** one row per TLC zone from reference file.

### `bronze.ingestion_manifest`

**Key:** `source_file_identity` (hash of path + size). **Purpose:** idempotent ingest, duplicate prevention.

### `bronze.pipeline_audit_log`

**Grain:** one row per stage event per run.

## Silver

### `silver.trips`

**Key:** `trip_fingerprint` (SHA-256 of core fields). **Grain:** one row per deduplicated trip.

### `silver.quarantined_trips`

**Grain:** one row per rejected trip with `rejection_reason`.

### `silver.taxi_zones`

**Key:** `zone_id`.

### `silver.data_quality_results`

**Grain:** one row per check per pipeline run.

## Gold

### `gold.fact_pickups_hourly`

**Key:** (`pickup_hour`, `pickup_zone_id`). **Measures:** `pickup_count`.

### `gold.dim_taxi_zone`

**Key:** `pickup_zone_id`.

### `gold.ml_training_features` / `gold.ml_inference_features`

See [feature_contract.md](feature_contract.md).
