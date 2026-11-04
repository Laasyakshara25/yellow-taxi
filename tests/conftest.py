"""Pytest fixtures — local Spark and synthetic Parquet."""

from __future__ import annotations

import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

_SPARK_SESSION = None
_SPARK_UNAVAILABLE_REASON: str | None = None


def _java_available() -> bool:
    return shutil.which("java") is not None


def _get_spark():
    global _SPARK_SESSION, _SPARK_UNAVAILABLE_REASON
    if _SPARK_SESSION is not None:
        return _SPARK_SESSION
    if _SPARK_UNAVAILABLE_REASON is not None:
        pytest.skip(_SPARK_UNAVAILABLE_REASON)
    if not _java_available():
        _SPARK_UNAVAILABLE_REASON = (
            "Java (JDK 17+) is required for local PySpark tests. "
            "Install OpenJDK and re-run pytest."
        )
        pytest.skip(_SPARK_UNAVAILABLE_REASON)
    from pyspark.sql import SparkSession

    try:
        session = (
            SparkSession.builder.master("local[2]")
            .appName("nyc_taxi_data_platform_tests")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.ui.enabled", "false")
            .getOrCreate()
        )
        session.sparkContext.parallelize([1]).collect()
        _SPARK_SESSION = session
        return session
    except Exception as exc:  # noqa: BLE001
        _SPARK_UNAVAILABLE_REASON = f"Spark session failed: {exc}"
        pytest.skip(_SPARK_UNAVAILABLE_REASON)


@pytest.fixture(scope="session")
def spark():
    session = _get_spark()
    yield session
    # Session stopped at process exit only when created


def _write_parquet(path: Path, table: pa.Table) -> str:
    pq.write_table(table, path)
    return str(path)


@pytest.fixture
def modern_parquet_path(tmp_path: Path) -> str:
    table = pa.table(
        {
            "vendor_id": [1, 2],
            "tpep_pickup_datetime": [
                "2023-01-01 10:15:00",
                "2023-01-01 11:00:00",
            ],
            "tpep_dropoff_datetime": [
                "2023-01-01 10:45:00",
                "2023-01-01 11:30:00",
            ],
            "pickup_location_id": [161, 161],
            "dropoff_location_id": [162, 163],
            "trip_distance": [2.5, 3.0],
            "fare_amount": [12.5, 15.0],
            "passenger_count": [1, 2],
            "payment_type": [1, 1],
        }
    )
    return _write_parquet(tmp_path / "yellow_tripdata_2023-01.parquet", table)


@pytest.fixture
def missing_datetime_parquet(tmp_path: Path) -> str:
    table = pa.table(
        {
            "vendor_id": [1],
            "tpep_dropoff_datetime": ["2023-01-01 10:45:00"],
            "pickup_location_id": [161],
            "dropoff_location_id": [162],
            "trip_distance": [2.5],
            "fare_amount": [12.5],
        }
    )
    return _write_parquet(tmp_path / "bad.parquet", table)


@pytest.fixture
def pre2011_parquet(tmp_path: Path) -> str:
    table = pa.table(
        {
            "vendor_id": [1],
            "tpep_pickup_datetime": ["2010-06-01 10:00:00"],
            "tpep_dropoff_datetime": ["2010-06-01 10:30:00"],
            "pickup_longitude": [-73.98],
            "pickup_latitude": [40.75],
            "dropoff_longitude": [-73.99],
            "dropoff_latitude": [40.76],
            "trip_distance": [2.0],
            "fare_amount": [10.0],
        }
    )
    return _write_parquet(tmp_path / "yellow_tripdata_2010-06.parquet", table)
