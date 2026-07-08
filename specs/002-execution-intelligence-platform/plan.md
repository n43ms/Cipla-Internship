# Implementation Plan: Cipla EMEU Execution Intelligence Platform

**Branch**: `002-execution-intelligence-platform` | **Date**: 2026-06-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-execution-intelligence-platform/spec.md`, product architecture from `finalplan.md`, and project constitution from `.specify/memory/constitution.md`.

## Summary

Build a protected, deployment-ready execution intelligence platform that converts Cipla EMEU planner, execution, consolidation, and RCPA workbooks into audited canonical tables, explicit reconciliation records, materialized KPI views, typed FastAPI services, and a polished React dashboard. Ingestion remains a local controlled CLI for MVP; the deployed app is read-only except for ExecAI query logging.

The core design decision is to treat the source workbooks as complementary evidence, not interchangeable sources of truth:

- yearly planner files define planned events and planned budget,
- monthly execution planner files provide execution snapshots,
- the consolidation `Working` sheet provides actual request, spend, approval, and attendance evidence,
- RCPA files provide aggregated prescription behavior and doctor coverage.

AI provider choice is intentionally deferred. The architecture defines a backend-only `AIProvider` interface and requires all AI answers to summarize deterministic service results.

Transcript 2026-06-15 adds confirmed financial governance scope: budget and ROI must use confirmed/contracted amounts and actual BTU/BTC spend splits from consolidation, not estimated/FMV-like values. Execution must include workflow governance for request approval, request confirmation, post-event report approval, and post-event report confirmation. ROI must include a leadership quadrant matrix and intervention-type mix analytics.

## Technical Context

**Language/Version**: Python 3.11 for backend and ingestion; TypeScript 5.x for frontend; SQL for migrations and views.

**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.0, Alembic, psycopg, pandas, openpyxl, python-calamine as the primary XLSB reader with pyxlsb fallback, Typer, pytest, ruff; React, Vite, Tailwind CSS, TanStack Query, Zustand, Recharts, Lucide React.

**Storage**: Supabase PostgreSQL for canonical data, compact RCPA summary tables, reconciliation records, validation records, materialized KPI views, and AI query logs. Local filesystem for confidential raw workbooks, generated ingestion reports, and detailed RCPA aggregate extracts.

**Testing**: pytest for ingestion, normalization, reconciliation, database/view, and API tests; React Testing Library/Vitest for frontend states and query behavior; contract tests against OpenAPI schemas.

**Target Platform**: Local Windows development and ingestion; deployed React frontend on Vercel or equivalent; deployed Python backend on Render/Railway/Fly.io or equivalent; Supabase-hosted PostgreSQL.

**Project Type**: Data-heavy full-stack web application with local ingestion CLI, read-only web API, React dashboard, and backend-mediated ExecAI assistant.

**Performance Goals**: Profile all eight supplied workbooks without manual inspection; aggregate RCPA prescription rows before persistence; keep Supabase under the free-tier storage limit by persisting compact RCPA summaries online and detailed RCPA extracts locally; keep dashboard summary API responses under 1s against materialized views for MVP data volume; keep event/doctor detail tables paginated.

**Constraints**: Real workbooks and generated extracts must not enter git; service-role database credentials and AI keys remain server-side; no browser upload in MVP; no AI calculation of KPIs; cross-country money comparisons require normalized currency or explicit warning; protected demo access is required for deployment.

**Transcript-Verified Data Constraints**: `APPROVE/CONFIRMED TOTAL INTERVENTION` is the contracted/confirmed amount; `ESTIMATED INTERVENTION` is estimated/FMV-like reference only; `ACTUAL EXPENSE AGAINST BTU` is direct HCP/BTU spend; `TOTAL ACTUAL BTC EXPENSE` is overhead/BTC spend; `TOTAL ACTUAL EXPENSES FOR INTERVENTION` is total actual spend; `Association Amount` is preserved separately; LKR must use the official company rate `1 USD = 310 LKR` (`rate_to_usd = 1/310`) with `fx_rate_status = official`; other currencies may remain provisional or missing until company rates are supplied.

**Scale/Scope**: MVP supports Nepal and Sri Lanka as primary markets, Myanmar as modeled/ingested source coverage where present, FY27 planner analysis, execution data from November 2025 onward, historical Nepal/Myanmar RCPA baseline from April 2024 through March 2025, and current RCPA through March 2026.

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked after Phase 1 design.*

- Data provenance: PASS. The design includes `ingestion_runs`, `source_files`, `ingestion_run_files`, workbook profiling output, row counts, validation issues, canonical sheet selection, and source row references.
- Reconciliation: PASS. Event reconciliation is modeled through explicit `event_matches` with match method, confidence, status, source references, and unmatched/weak-match visibility.
- Deterministic logic: PASS. KPI, budget, ROI, matching, coverage, and segmentation rules are computed by SQL/services. AI is limited to summarizing structured service results.
- Testing: PASS. The plan requires tests for XLSB aliases, month formats, Pcode text handling, April/May execution status differences, missing Sri Lanka May tab, multi-doctor fields, currency handling, views, APIs, and UI states.
- Security/deployment: PASS. Raw files are local-only, secrets are backend-only, deployed app is protected, ingestion is not browser-triggered, and frontend never talks directly to Supabase or the AI provider.
- UX reliability: PASS. Dashboard pages must implement loading, empty, error, stale-ingestion, weak-match, missing-FX, no-RCPA, and partial-data states.

## Architecture Decisions and Corrections

### Corrections to `finalplan.md`

1. `source_files.file_hash` cannot also model run participation. Use reusable `source_files` plus `ingestion_run_files` so the same workbook can be included in multiple ingestion runs without losing run history.
2. `doctors.pcode_normalized` must not be globally unique until validated. Use `(country_id, pcode_normalized)` as the safe unique boundary and separately report cross-country Pcode collisions.
3. `execution_requests.req_id` must not be assumed globally unique. Use a stable `request_uid` and unique `(source_system, req_id)` with a duplicate-detection validation path.
4. Nepal planner must use `Yearly Planner FY27 v2` as canonical when present. Other planner sheets are profiled but not loaded as duplicate canonical plan events.
5. RCPA local currency values must remain visible. USD fields are nullable and only populated when trusted FX is available.
6. AI query logs must store compact structured context summaries, not raw prompts containing sensitive workbook data.
7. Manual match editing is deferred. Therefore unmatched and weak matches must be sufficiently visible for operational review from day one.
8. Excel serial-number dates are real source data in current RCPA files. The month normalizer must parse serials such as `45772` into canonical calendar months and test them explicitly.
9. FX conversion is static-seeded for MVP. Seed LKR using the official company rate `1 USD = 310 LKR`; seed other currencies only when a documented company/provisional rate exists, and expose missing-FX flags rather than adding a live exchange-rate integration.
10. `question_redacted` in AI logs requires concrete masking rules for Pcodes, monetary values, and likely doctor-name spans before storage.
11. Sri Lanka May execution must be derived from consolidation requests in a deterministic, labeled path because no monthly execution country tab exists.
12. RCPA aggregation must be idempotent through explicit unique conflict targets on compact online summary grains. Detailed SKU-level aggregate evidence belongs in local generated extracts, not in Supabase.
13. Transcript-verified financial mapping must be modeled directly from consolidation columns: confirmed/contracted amount, estimated/FMV-like reference, BTU direct spend, BTC overhead spend, and total actual spend.
14. Workflow governance must be modeled from request approval/confirmation and post-event report approval/confirmation fields, not inferred from execution status alone.
15. Intervention type analytics must be data-driven from observed `INTERVENTION TYPE` and `INTERVENTION SUB TYPE` values; current files contain eight observed types.
16. ROI quadrant must be deterministic and leadership-facing, with low-effort/high-reward doctors highlighted as dark-horse opportunities.

### Selected Architecture

```text
data/raw local workbooks
  -> ingestion CLI
  -> workbook profiler
  -> validation + normalization
  -> canonical PostgreSQL tables
  -> explicit reconciliation tables
  -> materialized KPI/data-quality views
  -> FastAPI read services
  -> React dashboard
  -> backend-mediated ExecAI service
```

The ingestion CLI is the only component that writes source-derived business facts. Backend routes are read-only for dashboard data, except `POST /api/ai/query`, which stores sanitized AI query logs.

## Project Structure

### Documentation

```text
specs/002-execution-intelligence-platform/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- openapi.yaml
|   |-- cli.md
|   `-- dashboard-data-contract.md
`-- tasks.md                 # dependency-ordered implementation tasks
```

### Source Code

```text
backend/
|-- app/
|   |-- main.py
|   |-- config.py
|   |-- database.py
|   |-- routers/
|   |-- schemas/
|   |-- services/
|   |-- repositories/
|   `-- utils/
`-- tests/

ingestion/
|-- main.py
|-- config.py
|-- profiler.py
|-- report.py
|-- loaders/
|-- normalizers/
|-- validators/
|-- reconciliation/
`-- tests/

frontend/
|-- src/
|   |-- api/
|   |-- components/
|   |-- charts/
|   |-- pages/
|   |-- hooks/
|   |-- store/
|   |-- types/
|   `-- utils/
`-- tests/

database/
|-- migrations/
|-- views/
`-- seeds/

docs/
|-- data-dictionary.md
|-- ingestion-runbook.md
|-- deployment.md
`-- demo-validation.md

data/
|-- raw/                     # gitignored real workbooks
|-- processed/               # gitignored generated extracts
`-- reports/                 # gitignored ingestion reports

ingestion/tests/fixtures/
|-- xlsx/
|-- xlsb/
`-- expected/
```

**Structure Decision**: Use one repository with three runtime boundaries: `ingestion` for local writes, `backend` for deployed read services and AI orchestration, and `frontend` for the dashboard. Keep SQL migrations/views in `database` because the database is the shared contract between ingestion and API layers.

## Implementation Phases

### Phase 1: Data Profiling and Fixtures

Deliver workbook profiler, source classification, header detection, row counts, sheet selection rules, and synthetic fixtures for all workbook classes. Real files stay in `data/raw/`. Synthetic fixtures live under `ingestion/tests/fixtures/` and contain three to five rows per edge case, including Excel serial dates, RCPA alias columns, text/numeric Pcodes, April/May execution statuses, multi-doctor consolidation fields, and missing Sri Lanka May execution tab coverage.

Exit criteria:

- all eight supplied files are classified,
- canonical sheets are identified,
- known schema differences are reported,
- no real workbook is committed.

### Phase 2: Database Foundation

Deliver Alembic migrations for audit, reference, canonical, reconciliation, KPI, and AI tables; seed countries and fiscal months; add indexes and constraints.

Exit criteria:

- database can be rebuilt from migrations,
- uniqueness rules reflect country-scoped Pcodes and run/file separation,
- static exchange-rate seeds include official LKR at `1 USD = 310 LKR` with documented `rate_date`, `source = company`, and `rate_status = official`; other supported currencies have documented provisional or missing status,
- materialized views compile on empty or seeded data.

### Phase 3: Ingestion MVP

Deliver loaders for planners, consolidation, monthly execution snapshots, and aggregated RCPA facts. Add validation errors, ingestion summaries, and deterministic normalizers for months, Pcodes, event names, status values, and currencies. Month normalization must cover string months and Excel serial numbers. Use SQLAlchemy transactions and Alembic-owned schema objects; do not use the Supabase client as the primary write/read abstraction. RCPA writes compact online summaries to Supabase and detailed SKU-level aggregate extracts to local `data/processed/` files.

Exit criteria:

- supplied files load or produce explicit validation errors,
- RCPA is aggregated before persistence, compact summaries are written to Supabase, and detailed SKU-level aggregate evidence is written locally,
- consolidation doctor fields split into traceable participation rows,
- Sri Lanka missing May tab is handled by deterministic consolidation-derived rows labeled `derived_from_consolidation`,
- repeated RCPA ingestion of the same file is idempotent through the summary unique keys.

### Phase 4: Reconciliation and KPI Views

Deliver event matching, match coverage metrics, unmatched records, budget utilization views, workflow governance views, intervention mix views, doctor ROI views, ROI quadrant outputs, and data-quality views.

Exit criteria:

- weak and unmatched records are queryable,
- KPI views include freshness and coverage flags,
- budget views expose estimated, confirmed, BTU, BTC, actual total, variance, and FX status,
- workflow views expose request approval, request confirmation, post/report approval, post/report confirmation, and owner/stage,
- intervention mix views are driven by source values rather than hard-coded categories,
- no KPI requires frontend-side business calculations.

### Phase 5: Backend API

Deliver FastAPI routes, schemas, service/repository layers, pagination, filter validation, error handling, and contract tests.

Exit criteria:

- frontend can retrieve all dashboard data through typed APIs,
- secrets remain backend-only,
- invalid filters return clear client errors,
- APIs read from views/detail tables instead of duplicating calculations.

### Phase 6: Frontend MVP

Deliver executive overview, execution matrix, global filters, data freshness banner, drilldowns, and robust loading/error/empty/partial states.

Exit criteria:

- deployed frontend can demo execution risk and data quality,
- no blank screens when ingestion has warnings,
- tables are paginated and filters update query keys.

### Phase 7: Advanced Analytics

Deliver budget utilization, workflow governance drilldowns, intervention-type mix, doctor ROI, ROI quadrant matrix, doctor detail drawer, unmatched records/data-quality pages, and demo-ready business narratives.

Exit criteria:

- user can identify missed/action-due events, budget gaps, and doctor opportunities in under two minutes,
- user can identify pending approval/reporting bottlenecks and intervention-type mix by country/month,
- user can distinguish low-effort/high-reward dark-horse doctors from high-effort/high-return established voices,
- local currency warnings and no-RCPA states are visible where applicable.

### Phase 8: AI Assistant

Deliver backend provider abstraction, structured context builder, grounded answer endpoint, sanitized query logging, suggested prompts, and frontend AI panel.

Exit criteria:

- AI answers include supporting metrics or refuse unsupported facts,
- model provider can be selected later through environment configuration,
- raw workbook rows and secrets are never sent to or logged from AI flows,
- `question_redacted` masks Pcode-like identifiers, monetary values, and likely doctor-name spans before persistence.

### Phase 9: Deployment and Runbooks

Deliver protected frontend deployment, hosted backend, Supabase database, `.env.example`, ingestion runbook, deployment guide, and demo validation script.

Exit criteria:

- deployed dashboard is protected from public access,
- ingestion remains locally runnable,
- demo can be repeated from a clean database.

## Complexity Tracking

No constitution violations are introduced.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
