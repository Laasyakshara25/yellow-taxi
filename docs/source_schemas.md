# NYC TLC Yellow Taxi — source schemas

Reference: [TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), Yellow Taxi data dictionary (2025).

Parquet files often use **snake_case**; TLC PDFs use **PascalCase**. The pipeline normalizes via `CANONICAL_RENAME_MAP` in `schema_registry.py`.

## Eras

| Era | Approx. years | Distinguishing columns | Pipeline support |
|-----|---------------|------------------------|------------------|
| `pre_2011` | &lt; 2011 | `pickup_longitude`, `pickup_latitude`, … | Documented; **rejected** (`unsupported_schema`) in v1 |
| `post_2011` | 2011+ | `pickup_location_id`, `dropoff_location_id` | **Supported** |
| `post_congestion` | ~2019+ | `congestion_surcharge`, `airport_fee` | Supported (optional columns) |
| `post_2025` | 2025+ | `cbd_congestion_fee` | Supported (optional) |

## Required columns (modern)

| Canonical column | Description |
|------------------|-------------|
| `vendor_id` | TPEP vendor |
| `tpep_pickup_datetime` | Meter engaged |
| `tpep_dropoff_datetime` | Meter disengaged |
| `pickup_location_id` | TLC zone ID |
| `dropoff_location_id` | TLC zone ID |
| `trip_distance` | Miles |
| `fare_amount` | Meter fare |

## Taxi zone lookup

Expected columns (case-insensitive): `LocationID`, `Borough`, `Zone`, `service_zone`.

## Filename convention

`yellow_tripdata_YYYY-MM.parquet` — month inferred for partitioning when not passed explicitly.
