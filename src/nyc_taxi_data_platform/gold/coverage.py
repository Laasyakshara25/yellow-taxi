"""Zero-fill grid for known zones within an explicit date range."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def build_hourly_grid(
    spark: SparkSession,
    zone_ids: list[int],
    start_ts: str,
    end_ts: str,
) -> DataFrame:
    """Dense hourly grid for zones between start and end (inclusive hours)."""
    zones_df = spark.createDataFrame([(int(z),) for z in zone_ids], "pickup_zone_id int")
    hours_df = spark.sql(
        f"""
        SELECT explode(sequence(
            date_trunc('hour', timestamp '{start_ts}'),
            date_trunc('hour', timestamp '{end_ts}'),
            interval 1 hour
        )) AS pickup_hour
        """
    )
    return hours_df.crossJoin(zones_df)


def apply_zero_fill(observed: DataFrame, grid: DataFrame) -> DataFrame:
    """Left join observed counts onto coverage grid; missing -> 0."""
    return (
        grid.join(observed, on=["pickup_hour", "pickup_zone_id"], how="left")
        .select(
            F.col("pickup_hour"),
            F.col("pickup_zone_id"),
            F.coalesce(F.col("pickup_count"), F.lit(0)).alias("pickup_count"),
            F.coalesce(F.col("processed_at"), F.current_timestamp()).alias("processed_at"),
        )
    )
