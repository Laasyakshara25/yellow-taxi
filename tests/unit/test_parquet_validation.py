"""Parquet column validation without Spark (runs when Java is unavailable)."""

import pyarrow.parquet as pq

from nyc_taxi_data_platform.sources.validation import ValidationStatus, validate_source_columns


def test_modern_parquet_columns(modern_parquet_path):
    columns = pq.read_schema(modern_parquet_path).names
    result = validate_source_columns(columns)
    assert result.status == ValidationStatus.OK


def test_missing_datetime_parquet_columns(missing_datetime_parquet):
    columns = pq.read_schema(missing_datetime_parquet).names
    result = validate_source_columns(columns)
    assert result.status == ValidationStatus.MISSING_REQUIRED


def test_pre2011_parquet_columns(pre2011_parquet):
    columns = pq.read_schema(pre2011_parquet).names
    result = validate_source_columns(columns)
    assert result.status == ValidationStatus.UNSUPPORTED_SCHEMA
