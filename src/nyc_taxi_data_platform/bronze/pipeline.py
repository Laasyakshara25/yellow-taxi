"""Bronze layer Spark transformations."""

from __future__ import annotations

from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from nyc_taxi_data_platform.bronze.ingest import infer_source_month, source_file_identity
from nyc_taxi_data_platform.sources.schema_registry import normalize_column_name
from nyc_taxi_data_platform.sources.validation import ValidationStatus, validate_source_columns


def read_parquet_with_validation(spark: SparkSession, path: str) -> tuple[DataFrame | None, dict]:
    """Read parquet and validate columns; returns (df, manifest_fields)."""
    try:
        df = spark.read.parquet(path)
    except Exception as exc:  # noqa: BLE001 — surface as manifest status
        return None, {
            "processing_status": "corrupted_file",
            "error_message": str(exc),
            "record_count": 0,
        }

    result = validate_source_columns(df.columns)
    if result.status != ValidationStatus.OK:
        status = (
            "unsupported_schema"
            if result.status == ValidationStatus.UNSUPPORTED_SCHEMA
            else "schema_mismatch"
        )
        return None, {
            "processing_status": status,
            "error_message": result.message,
            "record_count": 0,
        }

    renamed = df
    for col in df.columns:
        target = normalize_column_name(col)
        if target != col:
            renamed = renamed.withColumnRenamed(col, target)

    count = renamed.count()
    now = datetime.now(timezone.utc)
    month = infer_source_month(path)
    run_id = F.lit("local-run")

    enriched = (
        renamed.withColumn("source_file", F.lit(path))
        .withColumn("source_month", F.lit(month))
        .withColumn("ingestion_run_id", run_id)
        .withColumn("ingested_at", F.lit(now))
    )
    identity = source_file_identity(path, None)
    return enriched, {
        "source_file_identity": identity,
        "source_file": path,
        "source_month": month,
        "processing_status": "ingested",
        "error_message": None,
        "record_count": count,
    }
