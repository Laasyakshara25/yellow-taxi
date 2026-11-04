from nyc_taxi_data_platform.bronze.ingest import (
    infer_source_month,
    resolve_trip_paths,
    source_file_identity,
)


def test_source_file_identity_stable():
    a = source_file_identity("/vol/yellow_tripdata_2023-01.parquet", 100)
    b = source_file_identity("/vol/yellow_tripdata_2023-01.parquet", 100)
    c = source_file_identity("/vol/yellow_tripdata_2023-01.parquet", 101)
    assert a == b
    assert a != c


def test_infer_source_month():
    assert infer_source_month("/data/yellow_tripdata_2024-03.parquet") == "2024-03"


def test_resolve_paths():
    paths = resolve_trip_paths("/Volumes/cat/schema/raw", ["2023-01", "2023-02"], [])
    assert paths == [
        "/Volumes/cat/schema/raw/yellow/yellow_tripdata_2023-01.parquet",
        "/Volumes/cat/schema/raw/yellow/yellow_tripdata_2023-02.parquet",
    ]
