# Engineering decisions (ADR log)

## ADR-001: Catalog name `nyc_taxi`

**Status:** Accepted  
**Context:** Unity Catalog default in Free Edition workspace is `workspace`.  
**Decision:** Default catalog `nyc_taxi`, overridable via `NYC_TAXI_CATALOG`.  
**Verification (2026-10-28):** `databricks catalogs get nyc_taxi` → **does not exist**. Create in UI before Phase 2 DDL, or use `workspace` with dedicated schemas.

## ADR-002: Pre-2011 trips unsupported in v1

**Status:** Accepted  
**Decision:** Reject at ingest with `unsupported_schema`; document lat/lon era in [source_schemas.md](source_schemas.md).

## ADR-003: NYC wall-clock timestamps

**Status:** Accepted  
**Decision:** Store pickup/dropoff as timestamps with `local_timezone = America/New_York` on silver; no silent UTC conversion.

## ADR-004: Local testing without TLC downloads

**Status:** Accepted  
**Decision:** Synthetic Parquet in pytest via PyArrow; column validation tests run without Spark.

## ADR-005: Databricks bundle compute

**Status:** Accepted  
**Decision:** Job tasks use `environment_key: default` (serverless environment v2) for Free Edition compatibility.

---

## Phase 1 verification log (executed)

| Check | Command / action | Outcome |
|-------|------------------|---------|
| Unit tests | `pytest tests/unit -q` | **17 passed, 11 skipped** (Spark tests skipped: **no Java/JDK** on host; OpenJDK install cancelled at UAC) |
| Bundle validate | `databricks bundle validate -t dev` | **Validation OK** |
| Workspace report | `python scripts/workspace_compatibility.py DEFAULT` | `catalog_exists: true` |
| E2E pipeline | `databricks bundle run … --only backfill_silver_gold` | **SUCCESS** — see [validation_report.md](validation_report.md) |

## ADR-006: Silver partition writes

**Decision:** Use `DELETE` + `append` per `source_month` instead of `replaceWhere` overwrite (serverless/Delta compatibility).

## ADR-007: ML feature window column

**Decision:** Window `orderBy(forecast_hour)` after renaming `pickup_hour` → `forecast_hour` in `build_ml_features`.

**Assumption:** Install JDK 17+ locally to execute Spark integration tests, or run the same pytest suite on Databricks serverless.
