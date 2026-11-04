# Run local unit tests for NYC Taxi Data Platform
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest tests/unit -q
