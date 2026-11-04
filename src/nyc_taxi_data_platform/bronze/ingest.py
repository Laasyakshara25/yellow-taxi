"""Bronze ingestion helpers (manifest identity, file resolution)."""

from __future__ import annotations

import hashlib
import re
from pathlib import PurePosixPath

SOURCE_MONTH_PATTERN = re.compile(r"(\d{4})-(\d{2})")


def source_file_identity(source_path: str, file_size_bytes: int | None = None) -> str:
    """Stable identity for deduplicating ingestion of the same source file."""
    normalized = PurePosixPath(source_path.replace("\\", "/")).as_posix()
    size_part = str(file_size_bytes) if file_size_bytes is not None else "unknown"
    payload = f"{normalized}|{size_part}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def infer_source_month(source_path: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    match = SOURCE_MONTH_PATTERN.search(source_path)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    raise ValueError(f"Cannot infer source month from path: {source_path}")


def resolve_trip_paths(
    volume_base: str,
    source_months: list[str],
    source_files: list[str],
) -> list[str]:
    """Build POSIX paths under volume_base for configured inputs."""
    paths: list[str] = []
    base = volume_base.rstrip("/")
    for month in source_months:
        paths.append(f"{base}/yellow/yellow_tripdata_{month}.parquet")
    paths.extend(source_files)
    return paths
