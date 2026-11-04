"""Structured logging helpers for pipeline runs."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("nyc_taxi_data_platform")


def new_run_id() -> str:
    return str(uuid.uuid4())


@dataclass
class AuditEvent:
    run_id: str
    stage: str
    status: str
    message: str
    record_count: int | None = None
    duration_ms: int | None = None
    extra: dict[str, Any] | None = None

    def to_json(self) -> str:
        payload = asdict(self)
        payload["logged_at"] = datetime.now(timezone.utc).isoformat()
        return json.dumps(payload, default=str)


def log_audit(event: AuditEvent) -> None:
    logger.info(event.to_json())
