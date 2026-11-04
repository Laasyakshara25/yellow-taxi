"""Ingestion manifest helpers for idempotent loads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import types as T

MANIFEST_SCHEMA = T.StructType(
    [
        T.StructField("source_file_identity", T.StringType(), False),
        T.StructField("source_file", T.StringType(), False),
        T.StructField("source_month", T.StringType(), False),
        T.StructField("ingestion_run_id", T.StringType(), False),
        T.StructField("ingested_at", T.TimestampType(), False),
        T.StructField("record_count", T.LongType(), True),
        T.StructField("processing_status", T.StringType(), False),
        T.StructField("error_message", T.StringType(), True),
    ]
)


@dataclass(frozen=True)
class ManifestRecord:
    source_file_identity: str
    source_file: str
    source_month: str
    ingestion_run_id: str
    ingested_at: datetime
    record_count: int
    processing_status: str
    error_message: str | None = None


def manifest_to_spark_df(spark: SparkSession, manifest: ManifestRecord):
    row = (
        manifest.source_file_identity,
        manifest.source_file,
        manifest.source_month,
        manifest.ingestion_run_id,
        manifest.ingested_at,
        int(manifest.record_count),
        manifest.processing_status,
        manifest.error_message,
    )
    return spark.createDataFrame([row], schema=MANIFEST_SCHEMA)


def is_duplicate(identity: str, known_identities: set[str]) -> bool:
    return identity in known_identities


def apply_duplicate_policy(
    manifest: ManifestRecord, known_identities: set[str]
) -> ManifestRecord:
    if is_duplicate(manifest.source_file_identity, known_identities):
        return ManifestRecord(
            source_file_identity=manifest.source_file_identity,
            source_file=manifest.source_file,
            source_month=manifest.source_month,
            ingestion_run_id=manifest.ingestion_run_id,
            ingested_at=manifest.ingested_at,
            record_count=0,
            processing_status="duplicate",
            error_message="Source file identity already ingested.",
        )
    return manifest
