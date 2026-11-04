"""Local and runtime dependency checks."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def check_python_version(min_minor: int = 10) -> CheckResult:
    version = sys.version_info
    ok = version.major == 3 and version.minor >= min_minor
    return CheckResult(
        name="python_version",
        passed=ok,
        detail=f"{version.major}.{version.minor}.{version.micro}",
    )


def _import_check(module: str) -> CheckResult:
    try:
        __import__(module)
        return CheckResult(name=f"import_{module}", passed=True, detail="ok")
    except ImportError as exc:
        return CheckResult(
            name=f"import_{module}",
            passed=False,
            detail=str(exc),
        )


def run_local_checks() -> list[CheckResult]:
    checks: list[Callable[[], CheckResult]] = [
        check_python_version,
        lambda: _import_check("yaml"),
        lambda: _import_check("pyarrow"),
        lambda: _import_check("pyspark"),
    ]
    return [fn() for fn in checks]
