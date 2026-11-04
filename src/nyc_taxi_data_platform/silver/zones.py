"""Taxi zone lookup standardization."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def standardize_zone_lookup(df: DataFrame) -> DataFrame:
    """Normalize TLC taxi zone lookup CSV/parquet to silver.taxi_zones."""
    cols = {c.lower(): c for c in df.columns}
    loc = cols.get("locationid") or cols.get("location_id")
    borough = cols.get("borough")
    zone = cols.get("zone")
    service = cols.get("service_zone") or cols.get("servicezone")

    return df.select(
        F.col(loc).cast("int").alias("zone_id"),
        F.col(borough).alias("borough"),
        F.col(zone).alias("zone_name"),
        F.col(service).alias("service_zone"),
        F.current_timestamp().alias("processed_at"),
    )
