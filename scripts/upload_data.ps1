# Upload TLC reference + trip Parquet to UC Volume (run after volume exists)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Data = Join-Path $Root "data\raw"

databricks fs mkdir "dbfs:/Volumes/nyc_taxi/bronze/raw/reference" -p DEFAULT
databricks fs mkdir "dbfs:/Volumes/nyc_taxi/bronze/raw/yellow" -p DEFAULT

databricks fs cp (Join-Path $Data "reference\taxi_zone_lookup.csv") `
  "dbfs:/Volumes/nyc_taxi/bronze/raw/reference/taxi_zone_lookup.csv" -p DEFAULT --overwrite

databricks fs cp (Join-Path $Data "yellow\yellow_tripdata_2023-01.parquet") `
  "dbfs:/Volumes/nyc_taxi/bronze/raw/yellow/yellow_tripdata_2023-01.parquet" -p DEFAULT --overwrite

Write-Host "Upload complete."
