from nyc_taxi_data_platform.bronze.pipeline import read_parquet_with_validation


def test_read_modern_parquet(spark, modern_parquet_path):
    df, manifest = read_parquet_with_validation(spark, modern_parquet_path)
    assert manifest["processing_status"] == "ingested"
    assert manifest["record_count"] == 2
    assert df is not None
    assert "pickup_location_id" in df.columns


def test_read_missing_columns(spark, missing_datetime_parquet):
    df, manifest = read_parquet_with_validation(spark, missing_datetime_parquet)
    assert df is None
    assert manifest["processing_status"] == "schema_mismatch"


def test_read_pre2011(spark, pre2011_parquet):
    df, manifest = read_parquet_with_validation(spark, pre2011_parquet)
    assert df is None
    assert manifest["processing_status"] == "unsupported_schema"
