"""Source file / schema validation before ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from nyc_taxi_data_platform.sources.schema_registry import (
    MODERN_REQUIRED_COLUMNS,
    SchemaEra,
    detect_era,
    is_modern_era_supported,
    normalize_column_names,
)


class ValidationStatus(str, Enum):
    OK = "ok"
    MISSING_REQUIRED = "missing_required"
    EXTRA_COLUMNS = "extra_columns"
    ERA_MISMATCH = "era_mismatch"
    UNSUPPORTED_SCHEMA = "unsupported_schema"


@dataclass(frozen=True)
class SchemaValidationResult:
    status: ValidationStatus
    era: SchemaEra
    normalized_columns: tuple[str, ...]
    missing_required: tuple[str, ...]
    message: str


def validate_source_columns(columns: list[str]) -> SchemaValidationResult:
    normalized = normalize_column_names(columns)
    normalized_set = set(normalized)
    era = detect_era(normalized_set)

    if not is_modern_era_supported(era):
        return SchemaValidationResult(
            status=ValidationStatus.UNSUPPORTED_SCHEMA,
            era=era,
            normalized_columns=tuple(sorted(normalized_set)),
            missing_required=tuple(),
            message=(
                "Pre-2011 lat/lon schema is documented but not supported in pipeline v1. "
                "Upload post-2011 Yellow Taxi Parquet with zone IDs."
            ),
        )

    missing = sorted(MODERN_REQUIRED_COLUMNS - normalized_set)
    if missing:
        return SchemaValidationResult(
            status=ValidationStatus.MISSING_REQUIRED,
            era=era,
            normalized_columns=tuple(sorted(normalized_set)),
            missing_required=tuple(missing),
            message=f"Missing required columns: {', '.join(missing)}",
        )

    return SchemaValidationResult(
        status=ValidationStatus.OK,
        era=era,
        normalized_columns=tuple(sorted(normalized_set)),
        missing_required=tuple(),
        message="Schema validation passed.",
    )
