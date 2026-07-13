# Cipla EMEU Doctor ROI & Execution Intelligence Platform

Full-stack execution intelligence platform for Cipla's Emerging Markets and Europe Patient Benefits Program (EMEU/PBP). The system turns fragmented Excel/XLSB operational workbooks into auditable PostgreSQL facts, deterministic KPI views, typed FastAPI services, a polished React executive dashboard, and a grounded natural-language assistant called ExecAI.

## Business Objectives

The platform is designed to support recurring regional doctor investment and execution decisions across Cipla EMEU/PBP markets.

Primary objectives:

- Help business leaders orchestrate 50+ regional investment decisions per month across doctor sponsorships, paid engagements, no-fee activity, execution follow-up, budget governance, and territory coverage.
- Build one trustworthy decision layer from planner files, execution snapshots, consolidation reports, Smart Contract exports, doctor-wise intervention reports, MSL doctor master data, and RCPA prescription baselines.
- Identify high-value engaged doctors, dark-horse doctors, under-engaged high-prescription doctors, low-return spend patterns, territory gaps, and workflow bottlenecks.
- Separate planned budget, estimated/FMV reference values, confirmed contracted amounts, BTU direct HCP spend, BTC overhead spend, total actual expense, association amount, and FX quality instead of mixing finance concepts.
- Make data confidence visible before action: row counts, validation issues, match quality, P-code coverage, RCPA coverage, missing FX, provisional FX, stale ingestion, and unmatched records are surfaced in the dashboard.
- Use AI only as an explanatory layer over deterministic backend data. ExecAI answers natural-language business questions using bounded PostgreSQL/FastAPI context, evidence validation, redaction, and deterministic fallback.

## Business Impact Snapshot

| Signal | Detail |
|---|---|
| Decision cadence | Built to support 50+ recurring regional doctor investment and execution decisions per month. |
| Market scope | Covers the documented Cipla EMEU/PBP scope for Nepal, Sri Lanka, Myanmar, Oman, UAE, and Malaysia. |
| Data volume signal | Documented real-file dry run profiled 8 workbooks, saw 1,179,273 rows, and loaded 423,693 compact online records. |
| Architecture | Python/FastAPI backend, local ingestion CLI, Supabase/PostgreSQL, React/TypeScript dashboard, SQL materialized views, and ExecAI. |
| Reliability | Current repo scan shows 80 dedicated test modules/files and 205 test definitions across ingestion, backend, database, frontend, and AI behavior. |

## Table of Contents

- [Business Objectives](#business-objectives)
- [Business Impact Snapshot](#business-impact-snapshot)
- [Product Overview](#product-overview)
- [Key Capabilities](#key-capabilities)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Data Sources](#data-sources)
- [Data Pipeline](#data-pipeline)
- [Database Layer](#database-layer)
- [Backend API](#backend-api)
- [Frontend Dashboard](#frontend-dashboard)
- [ExecAI](#execai)
- [Testing and Reliability](#testing-and-reliability)
- [Security and Data Governance](#security-and-data-governance)
- [Local Setup](#local-setup)
- [Common Commands](#common-commands)
- [Environment Variables](#environment-variables)
- [Project Documentation](#project-documentation)

## Product Overview

Cipla EMEU/PBP decision data is spread across several source systems and workbook formats. The platform consolidates these inputs into an operating dashboard for regional leadership.

The product answers questions such as:

- Which doctors deserve continued investment?
- Which doctors have strong RCPA prescription signal but low engagement?
- Which events were planned but not executed?
- Which requests are stuck in approval or post-event reporting?
- Where did actual spend exceed planned budget?
- Which spend rows do not map cleanly to planner evidence?
- Which markets or territories are underserved or overserved?
- Which KPI caveats should be disclosed before an executive review?
- What does the structured data support, and what should not be claimed?

The result is a serious data-heavy decision intelligence system, not a generic spreadsheet viewer or CRUD dashboard.

## Key Capabilities

| Area | What It Does |
|---|---|
| Doctor ROI | Scores and segments doctors using engagement/spend evidence and RCPA prescription baselines. Includes ROI quadrants, dark-horse flags, no-RCPA states, brand mix, doctor details, and spend-per-prescription signals. |
| Execution Intelligence | Reconciles planner events, execution snapshots, and consolidation requests. Exposes matched, weak, unmatched, executed, missed, and action-due records. |
| Budget Governance | Separates planned budget, confirmed contracted amount, estimated value, BTU spend, BTC spend, total actual expense, association amount, unspent gaps, overruns, and FX quality. |
| Workflow Governance | Tracks request approval, request confirmation, post-event approval, post-event confirmation, current owner/stage, pending requests, pending reports, and correction states. |
| Intervention Mix | Groups observed intervention type/subtype values from source data instead of hard-coded categories. |
| Sponsorship and Engagement Evidence | Models National/International Conference sponsorship, ERS evidence, no-fee engagements, paid service engagements, contract economics, FMV, and contract savings. |
| Territory Intelligence | Uses RCPA location/patch, Smart Contract HQ, and MSL doctor master enrichment to flag underserved, overserved, balanced, and insufficient-data territories. |
| Data Quality | Shows ingestion freshness, validation warnings/errors, match coverage, P-code coverage, RCPA coverage, workflow coverage, FX issues, unmatched records, and source caveats. |
| Business Upload Intake | Accepts known Excel workbook batches, fingerprints files, rejects duplicates/unknown formats, creates a manifest, and only refreshes data after accepted ingestion. |
| ExecAI | Embedded RAG-style assistant with query planning, bounded backend context, provider abstraction, evidence validation, redaction, confidence, limitations, and fallback answers. |

## Architecture

```text
Confidential local source workbooks
  -> Python ingestion CLI / dashboard upload intake
  -> source fingerprinting, workbook profiling, schema checks
  -> deterministic loaders, normalizers, validators
  -> canonical PostgreSQL tables and audit records
  -> reconciliation records and compact RCPA summaries
  -> SQL materialized KPI views
  -> FastAPI service/repository layer
  -> React executive dashboard
  -> ExecAI grounded assistant over bounded backend context
```

Runtime boundaries:

- `ingestion/` owns source-derived writes, profiling, validation, normalization, reconciliation, and local reports.
- `database/` owns migrations, seeds, canonical tables, constraints, and materialized KPI views.
- `backend/` owns API contracts, filter validation, service/repository logic, upload state, and AI orchestration.
- `frontend/` owns the user experience and calls only FastAPI.
- `docs/` and `specs/` document architecture, contracts, source policy, runbooks, and implementation planning.

Important architectural decisions:

- Raw workbooks stay local and are not committed.
- The frontend never connects directly to Supabase/PostgreSQL or any AI provider.
- KPI math is deterministic SQL or backend service logic, not AI-generated.
- RCPA is stored as compact serving summaries online, while detailed extracts remain local.
- FX uses company-provided rates only. There is no live internet FX fallback.
- AI answers are evidence-backed summaries of structured dashboard context.

## Repository Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- routers/          # FastAPI route handlers
|   |   |-- schemas/          # Pydantic request/response contracts
|   |   |-- services/         # Business logic and orchestration
|   |   |-- repositories/     # SQL/data access layer
|   |   |-- services/ai/      # ExecAI planning, context, provider, validation, redaction
|   |   |-- config.py
|   |   |-- database.py
|   |   `-- main.py
|   `-- tests/
|
|-- ingestion/
|   |-- loaders/             # Source-specific workbook loaders
|   |-- normalizers/         # Months, P-codes, money, events, FX, status, territory
|   |-- validators/          # Data-quality validation helpers
|   |-- reconciliation/      # Event matching and derived execution logic
|   |-- repositories/        # Ingestion write repositories
|   |-- profiler.py
|   |-- orchestrator.py
|   |-- source_fingerprints.py
|   |-- source_manifest.py
|   `-- main.py             # Typer CLI
|
|-- database/
|   |-- migrations/versions/ # Alembic migrations
|   |-- views/               # Materialized KPI view SQL
|   `-- seeds/               # Country, calendar, and company FX seeds
|
|-- frontend/
|   |-- src/
|   |   |-- api/             # Typed API clients
|   |   |-- components/      # Reusable UI, dashboard, upload, AI components
|   |   |-- pages/           # Doctor ROI, Execution, Budget, Territory, Data Quality
|   |   |-- hooks/
|   |   |-- types/
|   |   `-- utils/
|   `-- tests/
|
|-- docs/                    # Runbooks, architecture, source policy, storage guidance
|-- specs/002-execution-intelligence-platform/
|   |-- contracts/           # API, CLI, dashboard contracts
|   |-- spec.md
|   |-- plan.md
|   |-- data-model.md
|   |-- quickstart.md
|   `-- tasks.md
|
|-- data/                    # Gitignored local raw/processed/report/upload zones
|-- files/                   # Local received source package, not test fixtures
|-- scripts/
|-- README.md
|-- pyproject.toml
|-- alembic.ini
`-- .env.example
```

## Data Sources

The system is designed around real operating source families.

| Source Family | Purpose |
|---|---|
| Yearly planner workbooks | Planned events, expected activity cadence, and planned budgets. |
| Monthly execution snapshots | Execution status and monthly planner evidence. |
| Consolidation reports | Request IDs, intervention dates, intervention types, workflow state, approval state, attendance, BTU/BTC/actual expense fields, and source-of-truth spend evidence. |
| Consolidated intervention reports | Event/intervention spine, expected/actual P-codes, HQ/territory fields, and expense evidence. |
| Doctor-wise intervention exports | Doctor-level intervention rows, FMV, contracted amount, contract ID, status, doctor/P-code linkage, and engagement economics. |
| Historical RCPA workbooks | Prescription baseline across historical periods. |
| Monthly cumulative RCPA workbook | Current all-BU prescription baseline and territory/patch data. |
| ERS conference file | Historical International Conference/ERS evidence. |
| MSL doctor master | Doctor, territory, patch, legacy-code, BU, representative, and location enrichment. |

The currently documented business scope includes six markets:

- Nepal
- Sri Lanka
- Myanmar
- Oman
- UAE
- Malaysia

## Data Pipeline

### 1. Source Fingerprinting and Profiling

The ingestion layer inspects workbooks before writing facts.

It supports:

- `.xlsx`
- `.xlsb`
- CRM HTML exports saved as `.xls`

Profiling captures:

- detected source type,
- file format,
- file hash,
- sheet/table shape,
- row counts,
- header evidence,
- canonical sheets,
- mapped and unknown columns,
- missing required fields,
- sample values,
- schema drift warnings.

### 2. Validation and Normalization

The pipeline normalizes messy operational data into stable business contracts.

Covered normalizers include:

- month strings and Excel serial dates,
- P-codes and text/numeric doctor IDs,
- country and currency fields,
- event names,
- workflow status,
- intervention status,
- sponsorship and engagement classification,
- territory and patch labels,
- expense fields,
- FX lookup,
- contract economics,
- RCPA mapping provenance.

Validation catches:

- duplicate file hashes,
- unsupported formats,
- unknown workbook types,
- missing required columns,
- rejected or blank P-codes,
- same-country doctor conflicts,
- cross-country P-code collisions,
- missing FX,
- BTU/BTC reconciliation issues,
- missing sponsorship amounts,
- insufficient pre/post RCPA windows,
- weak or unmatched event joins.

### 3. Canonical Persistence

Source-derived facts are written to PostgreSQL through ingestion repositories.

Key principles:

- Every run is auditable through ingestion run and file records.
- Source file reuse is separated from run participation.
- Doctors are scoped by `(country, normalized P-code)`.
- RCPA summary writes are idempotent.
- Detailed RCPA extracts are kept local to control storage.
- Invalid rows are reported instead of silently discarded.

### 4. Reconciliation

The reconciliation layer matches planned events, execution snapshots, and request evidence.

It uses:

- normalized event names,
- conservative match thresholds,
- explicit match status,
- confidence,
- source references,
- unmatched record visibility,
- Sri Lanka May derivation from consolidation where a monthly execution tab is missing.

### 5. Materialized View Refresh

After ingestion and reconciliation, materialized views are refreshed to serve dashboard APIs.

Current refresh target includes:

- execution KPIs,
- unmatched events,
- execution matrix,
- workflow governance,
- intervention mix,
- budget utilization,
- Doctor ROI,
- data quality,
- sponsorship outcomes,
- territory opportunity.

## Database Layer

The database is the shared contract between ingestion, backend, dashboard, and AI context.

Database assets:

- Alembic migrations under `database/migrations/versions/`
- SQL materialized views under `database/views/`
- reference seeds under `database/seeds/`

Important materialized views:

| View | Purpose |
|---|---|
| `mv_execution_kpis` | Executive execution summary KPIs. |
| `mv_execution_event_matrix` | Event-level planner/execution/request matrix. |
| `mv_workflow_governance` | Approval, confirmation, report, and owner-stage governance. |
| `mv_intervention_mix` | Intervention type/subtype analytics. |
| `mv_budget_utilization` | Planned, confirmed, BTU, BTC, actual, gap, overrun, and FX metrics. |
| `mv_doctor_roi` | Doctor ROI segments, quadrants, spend, RCPA, and opportunity flags. |
| `mv_sponsorship_outcomes` | Sponsorship/engagement economics and association-only outcome evidence. |
| `mv_territory_opportunity` | Underserved/overserved/balanced territory signals. |
| `mv_data_quality` | Coverage, validation, reconciliation, FX, and source-health signals. |
| `mv_unmatched_events` | Unmatched and weakly matched source records. |
| `mv_latest_file_ingestion_status` | Latest file ingestion status. |
| `mv_latest_validation_errors` | Latest validation issue summaries. |

Static seed data includes:

- countries,
- calendar months,
- company-provided FX rates.

Company FX rates are treated as official business inputs. The app does not fetch public exchange rates.

## Backend API

The backend is a FastAPI service with thin routers, typed schemas, service classes, repositories, and shared error handling.

### Main API Groups

| Group | Endpoints |
|---|---|
| Health | `GET /api/health` |
| Filters and ingestion metadata | `GET /api/filters`, `GET /api/ingestion/latest` |
| Upload intake | `POST /api/ingestion/upload-batch`, `GET /api/ingestion/upload-batches/{batch_id}`, `POST /api/ingestion/upload-batches/{batch_id}/ingest` |
| Execution | `GET /api/execution/summary`, `GET /api/execution/filter-options`, `GET /api/execution/events` |
| Workflow | `GET /api/workflow/summary`, `GET /api/workflow/requests` |
| Interventions | `GET /api/interventions/mix` |
| Budget | `GET /api/budget/summary` |
| Doctors | `GET /api/doctors/roi`, `GET /api/doctors/{country_code}/{pcode}` |
| Territory | `GET /api/territory/opportunities`, `GET /api/territory/doctors` |
| Data Quality | `GET /api/data-quality`, `GET /api/data-quality/unmatched` |
| AI | `POST /api/ai/query` |

### Backend Design Standards

- Pydantic schemas define request and response contracts.
- API responses serialize as camelCase for frontend use.
- Services own business orchestration.
- Repositories own SQL/data access.
- Filters are validated before repository calls.
- Errors use a consistent payload shape.
- CORS is configured for local Vite development.
- Secrets remain backend-only.

## Frontend Dashboard

The frontend is a Vite + React + TypeScript dashboard built for executive workflows.

Tech stack:

- React 19
- TypeScript
- Vite
- TanStack Query
- Zustand
- Recharts
- Tailwind CSS
- Lucide React
- React Markdown

### Main Pages

| Page | User Value |
|---|---|
| Doctor ROI | Identify doctor opportunities, dark horses, high-value engaged doctors, low-confidence rows, brand mix, engagement history, and RCPA context. |
| Execution | Review execution KPIs, event matrix, match quality, execution status, workflow state, and intervention mix. |
| Budget | Inspect budget utilization, BTU/BTC split, actual spend, confirmed amounts, gaps, overruns, FX status, and reconciliation warnings. |
| Territory Intelligence | Explore underserved, overserved, balanced, and insufficient-data territories with doctor drilldown. |
| Data Quality | Review ingestion freshness, validation, unmatched records, coverage, workflow quality, intervention quality, and FX caveats. |

### UX Features

- responsive dashboard shell,
- executive entry screen,
- global warning center,
- data freshness banner,
- loading, error, empty, and partial-data states,
- filter panels,
- sortable and paginated tables,
- doctor detail drawer,
- territory doctor drawer,
- upload side panel,
- ExecAI assistant drawer,
- evidence, limitation, and confidence display for AI answers.

## ExecAI

ExecAI is an embedded structured RAG assistant for natural-language querying across the dashboard.

It is intentionally constrained. It does not calculate KPI source-of-truth metrics and does not read raw Excel rows. It explains already-computed dashboard evidence.

### ExecAI Flow

```text
AiAssistantPanel.tsx
  -> frontend API client
  -> POST /api/ai/query
  -> FastAPI router
  -> AssistantService
  -> topic routing
  -> query planning
  -> compact context builder
  -> dashboard services and repositories
  -> PostgreSQL materialized views/tables
  -> provider abstraction
  -> structured response validation
  -> deterministic fallback if needed
  -> sanitized ai_query_logs row
  -> frontend evidence/confidence/limitations rendering
```

### ExecAI Guardrails

- Supports execution, workflow, intervention, budget, Doctor ROI, RCPA, territory, and data-quality questions.
- Refuses unsupported questions without calling the model.
- Retrieves bounded backend context through services, not raw workbook data.
- Enforces max context size and row limits.
- Optionally redacts P-codes, amounts, doctor-like names, and source snippets.
- Supports Gemini, test, null, and fallback provider modes.
- Handles retryable provider failures with configured fallback models.
- Requires model responses to be structured JSON.
- Validates evidence references against the supplied context.
- Removes invalid evidence references.
- Falls back to deterministic answers on provider failure or malformed model output.
- Returns dashboard pointers so users can verify answers in the UI.
- Logs sanitized query metadata, latency, provider, model, fallback status, and error state.

## Testing and Reliability

Current repo scan:

- 80 dedicated test modules/files.
- 205 test definitions.
- Coverage spans ingestion, backend API, database/view contracts, AI behavior, and frontend states.

Tested areas include:

- workbook reading,
- source fingerprinting,
- upload-batch validation,
- workbook profiling,
- schema drift reporting,
- RCPA alias mapping,
- RCPA provenance,
- month normalization including Excel serial dates,
- P-code normalization,
- planner canonical sheet selection,
- execution snapshot mapping,
- consolidation financial mapping,
- consolidation workflow mapping,
- BTU/BTC expense reconciliation,
- company FX and missing-FX handling,
- doctor identity constraints,
- event matching,
- Sri Lanka May execution derivation,
- RCPA summary idempotency,
- sponsorship classification,
- engagement classification,
- contract economics,
- territory labels,
- materialized view SQL contracts,
- FastAPI response contracts,
- filter validation,
- frontend loading/error/empty states,
- Doctor ROI UI,
- budget UI,
- execution governance UI,
- data-quality UI,
- ExecAI UI,
- AI redaction,
- AI query planning,
- AI provider failover,
- AI response validation,
- AI deterministic fallback.

## Security and Data Governance

Real source files are confidential and should remain local.

Do not commit:

- raw Cipla workbooks,
- generated extracts,
- ingestion reports containing sensitive values,
- `.env`,
- database credentials,
- Supabase service-role keys,
- AI provider keys.

Important boundaries:

- Raw workbooks belong under local ignored folders such as `data/raw/`, `data/processed/`, `data/reports/`, `data/uploads/`, or the local `files/` package.
- Synthetic fixtures must use fake rows only.
- Frontend does not receive database credentials.
- Frontend does not receive AI provider credentials.
- AI does not receive raw workbook rows.
- Source-derived writes are controlled by ingestion paths.
- Upload validation does not silently alter live KPIs.
- Business facts become dashboard-visible only after accepted ingestion writes canonical data and materialized views are refreshed.

## Local Setup

### Prerequisites

- Python 3.11
- Node.js 20+
- PostgreSQL or Supabase-hosted PostgreSQL
- PowerShell on Windows for the documented commands

### Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install -r ingestion\requirements.txt
npm install --prefix frontend
```

### Configure Environment

```powershell
Copy-Item .env.example .env
```

Fill in the database, Supabase, CORS, upload, and AI settings in `.env`.

## Common Commands

### Database

```powershell
alembic upgrade head
```

### Profile Workbooks

```powershell
python -m ingestion.main profile --data-dir data/raw
```

### Profile a Manifest Batch

```powershell
python -m ingestion.main batch-profile --manifest files/source-manifest.json
```

### Dry-Run a Manifest Batch

```powershell
python -m ingestion.main batch-ingest --manifest files/source-manifest.json --dry-run
```

### Ingest, Reconcile, and Refresh

```powershell
python -m ingestion.main ingest --source all
python -m ingestion.main reconcile
python -m ingestion.main refresh-views
python -m ingestion.main report
```

### Compare Raw and Cleaned Workbooks

```powershell
python -m ingestion.main compare --raw <raw-file> --cleaned <cleaned-file>
```

### Run Backend

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

### Run Frontend

```powershell
npm run dev --prefix frontend
```

### Build Frontend

```powershell
npm run build --prefix frontend
```

### Run Tests

```powershell
pytest ingestion/tests backend/tests
npm test --prefix frontend
```

## Environment Variables

`.env.example` documents the local configuration surface.

Important variables:

| Variable | Purpose |
|---|---|
| `APP_ENV` | Local/deployed runtime mode. |
| `DEPLOYMENT_MODE` | Deployment profile. |
| `DATABASE_URL` | SQLAlchemy PostgreSQL connection string. |
| `SUPABASE_URL` | Supabase project URL if using Supabase. |
| `SUPABASE_PROJECT_REF` | Supabase project reference. |
| `DATA_DIR` | Local raw workbook folder. |
| `PROCESSED_DATA_DIR` | Local generated extract folder. |
| `REPORTS_DIR` | Local generated report folder. |
| `BACKEND_HOST` | Backend bind host. |
| `BACKEND_PORT` | Backend port. |
| `CORS_ORIGINS` | Allowed frontend origins. |
| `VITE_API_BASE_URL` | Frontend API base URL. |
| `DEMO_ACCESS_MODE` | Demo access/protection mode. |
| `DEMO_SHARED_PASSWORD` | Optional protected-demo password. |
| `AI_PROVIDER` | `null`, `gemini`, or test provider mode. |
| `AI_API_KEY` | Server-side AI provider key. |
| `AI_MODEL` | Primary AI model. |
| `AI_MODEL_FALLBACKS` | Comma-separated fallback model list. |
| `AI_CONTEXT_MAX_CHARS` | Maximum AI context payload size. |
| `AI_CONTEXT_ROW_LIMIT` | Row limit for AI evidence context. |
| `AI_REDACTION_ENABLED` | Enables redaction before provider/logging paths. |
| `AI_TIMEOUT_SECONDS` | AI provider timeout. |

## Project Documentation

Useful docs:

- `specs/002-execution-intelligence-platform/plan.md`: architecture and implementation plan.
- `specs/002-execution-intelligence-platform/spec.md`: product specification.
- `specs/002-execution-intelligence-platform/data-model.md`: data model.
- `specs/002-execution-intelligence-platform/quickstart.md`: end-to-end validation guide.
- `specs/002-execution-intelligence-platform/contracts/openapi.yaml`: API contract.
- `specs/002-execution-intelligence-platform/contracts/cli.md`: ingestion CLI contract.
- `specs/002-execution-intelligence-platform/contracts/dashboard-data-contract.md`: dashboard data contract.
- `docs/architecture.md`: runtime boundaries and architecture notes.
- `docs/source-onboarding-playbook.md`: source-package onboarding rules.
- `docs/source-data-policy.md`: source handling policy.
- `docs/ingestion-runbook.md`: ingestion operations.
- `docs/data-dictionary.md`: data definitions.
- `docs/storage-budget.md`: storage budget and Supabase constraints.
- `backend/app/services/ai/AI_LAYER_WALKTHROUGH.md`: detailed ExecAI flow.

## Engineering Story

The strongest story in this repo is the full data product chain:

```text
messy confidential Excel sources
  -> deterministic ingestion
  -> auditable canonical facts
  -> reconciled event and doctor identity
  -> materialized KPI views
  -> typed API contracts
  -> polished executive dashboard
  -> grounded AI explanation layer
  -> tests across data, API, UI, and AI behavior
```

This is designed to be credible as an enterprise analytics demo, a recruiter-grade portfolio project, and a foundation for a production internal decision product.
