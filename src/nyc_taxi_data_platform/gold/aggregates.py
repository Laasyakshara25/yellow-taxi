"""Gold hourly pickup aggregates."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def hourly_pickups_from_silver(trips: DataFrame) -> DataFrame:
    """Aggregate accepted silver trips to (pickup_hour, pickup_zone_id) counts."""
    return (
        trips.withColumn("pickup_hour", F.date_trunc("hour", F.col("pickup_datetime")))
        .withColumn("pickup_zone_id", F.col("pickup_zone_id").cast("int"))
        .groupBy("pickup_hour", F.col("pickup_zone_id"))
        .agg(F.count(F.lit(1)).alias("pickup_count"))
        .withColumn("processed_at", F.current_timestamp())
    )


def reconcile_counts(silver_trips: DataFrame, gold_hourly: DataFrame) -> dict[str, int]:
    """Driver-side reconciliation for tests and DQ (small fixtures only)."""
    silver_count = silver_trips.count()
    gold_sum = gold_hourly.agg(F.sum("pickup_count")).collect()[0][0] or 0
    return {"silver_trip_count": silver_count, "gold_pickup_sum": int(gold_sum)}
