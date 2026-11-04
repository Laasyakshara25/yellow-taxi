"""ML feature engineering from hourly pickup fact."""

from __future__ import annotations

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

TRAINING_FEATURE_COLUMNS = [
    "pickup_zone_id",
    "forecast_hour",
    "hour_of_day",
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",
    "lag_1h",
    "lag_24h",
    "lag_168h",
    "rolling_mean_24h",
    "rolling_mean_168h",
    "rolling_std_24h",
    "target_pickup_count",
]

INFERENCE_FEATURE_COLUMNS = [c for c in TRAINING_FEATURE_COLUMNS if c != "target_pickup_count"]


def _partition_window() -> Window:
    return Window.partitionBy("pickup_zone_id").orderBy("forecast_hour")


def build_ml_features(hourly: DataFrame) -> DataFrame:
    """
    Build training features per (zone, hour).

    Lags and rolling stats use only strictly prior hours (excludes forecast hour).
    """
    base = (
        hourly.withColumnRenamed("pickup_hour", "forecast_hour")
        .withColumn("pickup_zone_id", F.col("pickup_zone_id").cast("int"))
        .withColumn("pickup_count", F.col("pickup_count").cast("double"))
    )

    w = _partition_window()
    prior = base.withColumn("prior_pickup_count", F.col("pickup_count"))

    featured = (
        prior.withColumn("hour_of_day", F.hour("forecast_hour"))
        .withColumn("day_of_week", F.dayofweek("forecast_hour"))
        .withColumn("day_of_month", F.dayofmonth("forecast_hour"))
        .withColumn("month", F.month("forecast_hour"))
        .withColumn(
            "is_weekend",
            F.dayofweek("forecast_hour").isin([1, 7]),
        )
        .withColumn(
            "lag_1h",
            F.lag("prior_pickup_count", 1).over(w),
        )
        .withColumn(
            "lag_24h",
            F.lag("prior_pickup_count", 24).over(w),
        )
        .withColumn(
            "lag_168h",
            F.lag("prior_pickup_count", 168).over(w),
        )
        .withColumn(
            "rolling_mean_24h",
            F.avg("prior_pickup_count").over(w.rowsBetween(-24, -1)),
        )
        .withColumn(
            "rolling_mean_168h",
            F.avg("prior_pickup_count").over(w.rowsBetween(-168, -1)),
        )
        .withColumn(
            "rolling_std_24h",
            F.stddev_samp("prior_pickup_count").over(w.rowsBetween(-24, -1)),
        )
        .withColumn("target_pickup_count", F.col("pickup_count").cast("long"))
        .withColumn("processed_at", F.current_timestamp())
        .drop("prior_pickup_count", "pickup_count")
    )
    return featured


def to_inference_features(training: DataFrame) -> DataFrame:
    return training.select(
        *[c for c in INFERENCE_FEATURE_COLUMNS],
        F.col("processed_at"),
    )
