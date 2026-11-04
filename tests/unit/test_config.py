import os

from nyc_taxi_data_platform.config import load_config


def test_load_config_defaults():
    config = load_config()
    assert config.catalog == "nyc_taxi"
    assert config.bronze_schema == "bronze"
    assert config.table_fqn("gold", "fact_pickups_hourly") == "nyc_taxi.gold.fact_pickups_hourly"


def test_catalog_env_override(monkeypatch):
    monkeypatch.setenv("NYC_TAXI_CATALOG", "workspace")
    config = load_config()
    assert config.catalog == "workspace"
