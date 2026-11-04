# NYC Taxi Data Platform

End-to-end NYC Yellow Taxi data engineering on Databricks: Bronze–Silver–Gold medallion layers, data quality, and ML-ready hourly demand features (no model training in this repo).

## Prerequisites

- Python 3.10+
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) v0.205+ (you have v1.22.x)
- Java 11+ (required for local PySpark tests)
- Git and optional [GitHub CLI](https://cli.github.com/) (`gh`)

## Git setup

```powershell
cd "c:\Users\user\Desktop\NYC Taxi Data Platform"
git status
```

Remote (install [GitHub CLI](https://cli.github.com/) then):

```powershell
winget install GitHub.cli
gh auth login
gh repo create nyc-taxi-data-platform --private --source=. --remote=origin --push
```

Or manually:

```powershell
git remote add origin https://github.com/<you>/nyc-taxi-data-platform.git
git push -u origin main
```

## Local development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest tests/unit -q
```

Or:

```powershell
.\scripts\run_local_tests.ps1
```

Tests use **synthetic Parquet** only; no TLC downloads.

## Configuration

Defaults: [config/defaults.yaml](config/defaults.yaml)

| Override | Purpose |
|----------|---------|
| `NYC_TAXI_CATALOG` | Unity Catalog name (default `nyc_taxi`) |
| `NYC_TAXI_VOLUME_BASE` | UC Volume path for raw Parquet |

Job parameters: `source_months`, `source_files`, `volume_base` (comma-separated months).

## Databricks authentication

```powershell
databricks auth login -p DEFAULT
databricks auth profiles
```

## Databricks Asset Bundle

Validate (no deploy required for local dev):

```powershell
databricks bundle validate -t dev
```

Deploy (may be restricted on Free Edition):

```powershell
databricks bundle deploy -t dev
databricks bundle run nyc_taxi_pipeline -t dev
```

If deploy fails, create a job manually in the workspace that runs:

`src/nyc_taxi_data_platform/pipeline/stages.py --stage init_catalog`

## Workspace compatibility

```powershell
python scripts/workspace_compatibility.py DEFAULT
```

## Raw data upload (Phase 2+)

When outbound download from the cluster is unavailable, upload to a UC Volume:

- `yellow/yellow_tripdata_YYYY-MM.parquet`
- `reference/taxi_zone_lookup.csv` (or Parquet)

Set `volume_base` in config or job parameters.

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/source_schemas.md](docs/source_schemas.md)
- [docs/data_dictionary.md](docs/data_dictionary.md)
- [docs/feature_contract.md](docs/feature_contract.md)
- [docs/data_quality.md](docs/data_quality.md)
- [docs/ml_handoff.md](docs/ml_handoff.md)
- [docs/decisions.md](docs/decisions.md)

## ML scope

This project delivers `gold.ml_training_features` and `gold.ml_inference_features` plus [docs/feature_contract.md](docs/feature_contract.md). Model training is out of scope.
