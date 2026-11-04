"""Silver standardization, fingerprint, and quarantine rules."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType

from nyc_taxi_data_platform.config import QualityConfig


def trip_fingerprint_expr() -> F.Column:
    """Deterministic fingerprint for deduplication."""
    return F.sha2(
        F.concat_ws(
            "|",
            F.col("vendor_id").cast("string"),
            F.col("tpep_pickup_datetime").cast("string"),
            F.col("tpep_dropoff_datetime").cast("string"),
            F.col("pickup_location_id").cast("string"),
            F.col("dropoff_location_id").cast("string"),
            F.col("trip_distance").cast("string"),
            F.col("fare_amount").cast("string"),
        ),
        256,
    )


def standardize_bronze_trips(df: DataFrame, local_timezone: str) -> DataFrame:
    """Map bronze columns to silver trip schema (NYC wall-clock as timestamp_ntz semantics)."""
    return df.select(
        trip_fingerprint_expr().alias("trip_fingerprint"),
        F.col("source_file"),
        F.col("source_month"),
        F.col("ingestion_run_id"),
        F.col("vendor_id"),
        F.col("tpep_pickup_datetime").cast(TimestampType()).alias("pickup_datetime"),
        F.col("tpep_dropoff_datetime").cast(TimestampType()).alias("dropoff_datetime"),
        F.col("pickup_location_id").alias("pickup_zone_id"),
        F.col("dropoff_location_id").alias("dropoff_zone_id"),
        F.col("trip_distance"),
        F.col("fare_amount"),
        F.col("passenger_count"),
        F.col("payment_type"),
        F.lit(local_timezone).alias("local_timezone"),
        F.current_timestamp().alias("processed_at"),
    )


def validation_flags(quality: QualityConfig) -> F.Column:
    return (
        F.col("pickup_datetime").isNull()
        | F.col("dropoff_datetime").isNull()
        | (F.col("dropoff_datetime") < F.col("pickup_datetime"))
        | F.col("pickup_zone_id").isNull()
        | F.col("dropoff_zone_id").isNull()
        | (F.col("pickup_zone_id") <= 0)
        | (F.col("dropoff_zone_id") <= 0)
        | F.col("trip_distance").isNull()
        | (F.col("trip_distance") < 0)
        | (F.col("trip_distance") > quality.max_trip_distance_miles)
        | F.col("fare_amount").isNull()
        | (F.col("fare_amount") < quality.min_fare_amount)
        | (F.col("fare_amount") > quality.max_fare_amount)
    )


def split_valid_and_quarantine(
    standardized: DataFrame, quality: QualityConfig
) -> tuple[DataFrame, DataFrame]:
    invalid = standardized.filter(validation_flags(quality))
    valid = standardized.filter(~validation_flags(quality))

    quarantined = invalid.select(
        F.col("source_file"),
        F.col("source_month"),
        F.col("ingestion_run_id"),
        F.lit("validation_failed").alias("rejection_reason"),
        F.to_json(
            F.struct(
                F.col("trip_fingerprint"),
                F.col("pickup_datetime"),
                F.col("dropoff_datetime"),
                F.col("pickup_zone_id"),
                F.col("dropoff_zone_id"),
            )
        ).alias("raw_payload"),
        F.current_timestamp().alias("processed_at"),
    )
    return valid, quarantined


def deduplicate_trips(df: DataFrame) -> DataFrame:
    """Keep earliest processed row per fingerprint within the batch."""
    from pyspark.sql.window import Window

    window = Window.partitionBy("trip_fingerprint").orderBy(F.col("processed_at").asc())
    return (
        df.withColumn("_row_num", F.row_number().over(window))
        .filter(F.col("_row_num") == 1)
        .drop("_row_num")
    )
