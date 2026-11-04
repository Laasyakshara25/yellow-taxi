from nyc_taxi_data_platform.sources.validation import ValidationStatus, validate_source_columns


def test_modern_schema_ok():
    cols = [
        "vendor_id",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "pickup_location_id",
        "dropoff_location_id",
        "trip_distance",
        "fare_amount",
    ]
    result = validate_source_columns(cols)
    assert result.status == ValidationStatus.OK


def test_missing_pickup_datetime():
    cols = [
        "vendor_id",
        "tpep_dropoff_datetime",
        "pickup_location_id",
        "dropoff_location_id",
        "trip_distance",
        "fare_amount",
    ]
    result = validate_source_columns(cols)
    assert result.status == ValidationStatus.MISSING_REQUIRED
    assert "tpep_pickup_datetime" in result.missing_required


def test_pre_2011_unsupported():
    cols = [
        "vendor_id",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
        "trip_distance",
        "fare_amount",
    ]
    result = validate_source_columns(cols)
    assert result.status == ValidationStatus.UNSUPPORTED_SCHEMA
