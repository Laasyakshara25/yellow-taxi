"""Load pipeline configuration from YAML and environment overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "defaults.yaml"


@dataclass(frozen=True)
class QualityConfig:
    max_trip_distance_miles: float = 500.0
    min_fare_amount: float = -500.0
    max_fare_amount: float = 10000.0


@dataclass(frozen=True)
class FeatureConfig:
    warmup_hours: int = 168


@dataclass(frozen=True)
class PipelineConfig:
    catalog: str
    bronze_schema: str
    silver_schema: str
    gold_schema: str
    volume_base: str
    source_months: list[str]
    source_files: list[str]
    local_timezone: str
    coverage_start_date: str | None
    coverage_end_date: str | None
    quality: QualityConfig
    features: FeatureConfig

    def table_fqn(self, schema: str, table: str) -> str:
        return f"{self.catalog}.{schema}.{table}"

    @property
    def bronze(self) -> str:
        return self.bronze_schema

    @property
    def silver(self) -> str:
        return self.silver_schema

    @property
    def gold(self) -> str:
        return self.gold_schema


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def load_config(path: Path | None = None) -> PipelineConfig:
    config_path = path or DEFAULT_CONFIG_PATH
    with config_path.open(encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle) or {}

    schemas = raw.get("schemas") or {}
    quality_raw = raw.get("quality") or {}
    features_raw = raw.get("features") or {}

    catalog = os.environ.get("NYC_TAXI_CATALOG", raw.get("catalog", "nyc_taxi"))

    return PipelineConfig(
        catalog=catalog,
        bronze_schema=schemas.get("bronze", "bronze"),
        silver_schema=schemas.get("silver", "silver"),
        gold_schema=schemas.get("gold", "gold"),
        volume_base=os.environ.get("NYC_TAXI_VOLUME_BASE", raw.get("volume_base") or ""),
        source_months=_coerce_list(raw.get("source_months")),
        source_files=_coerce_list(raw.get("source_files")),
        local_timezone=raw.get("local_timezone", "America/New_York"),
        coverage_start_date=raw.get("coverage_start_date"),
        coverage_end_date=raw.get("coverage_end_date"),
        quality=QualityConfig(
            max_trip_distance_miles=float(
                quality_raw.get("max_trip_distance_miles", 500.0)
            ),
            min_fare_amount=float(quality_raw.get("min_fare_amount", -500.0)),
            max_fare_amount=float(quality_raw.get("max_fare_amount", 10000.0)),
        ),
        features=FeatureConfig(warmup_hours=int(features_raw.get("warmup_hours", 168))),
    )
