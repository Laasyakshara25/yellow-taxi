"""Databricks job entry: locate bundle src/ and run pipeline stages."""

import sys
from pathlib import Path


def _bundle_src_path() -> Path:
    """Resolve src/ when Databricks runs this file via exec (no __file__)."""
    cwd = Path.cwd()
    candidates = [
        cwd / "src",
        cwd / "files" / "src",
        cwd.parent / "src",
    ]
    for parent in [cwd, *cwd.parents]:
        candidates.append(parent / "src")
        candidates.append(parent / "files" / "src")
    for path in candidates:
        if (path / "nyc_taxi_data_platform").is_dir():
            return path.resolve()
    raise RuntimeError(
        "Could not find nyc_taxi_data_platform under src/. cwd="
        f"{cwd}"
    )


_SRC = _bundle_src_path()
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from nyc_taxi_data_platform.pipeline.stages import main

if __name__ == "__main__":
    main()
