# Final Architecture Overview

## Product Purpose

The application is a Cipla EMEU execution intelligence platform. Its purpose is to convert multiple disconnected Excel/XLSB files into one trusted, auditable dashboard for execution tracking, budget governance, doctor ROI, workflow bottlenecks, intervention mix, data quality, and AI-assisted summaries.

The product is designed as a deployable full-stack app, not a notebook or spreadsheet clone.

## High-Level System

```text
Local source workbooks
  -> ingestion CLI
  -> workbook profiler
  -> validation and normalization
  -> canonical database tables
  -> reconciliation records
  -> materialized KPI views
  -> FastAPI services
  -> React dashboard
  -> AI assistant grounded in API results
```

## Runtime Boundaries

### 1. Local Ingestion CLI

The ingestion layer is a Python CLI. It is the only MVP component that writes source-derived business facts.

It handles:

- file discovery,
- file hashing,
- workbook profiling,
- source type detection,
- sheet/header detection,
- row validation,
- column alias mapping,
- month normalization,
- Pcode normalization,
- currency normalization,
- RCPA aggregation,
- consolidation request loading,
- planner loading,
- execution snapshot loading,
- event reconciliation,
- materialized-view refresh,
- ingestion reports.

Main tools:

- Python 3.11,
- pandas,
- openpyxl for XLSX,
- python-calamine as primary XLSB reader,
- pyxlsb as fallback XLSB reader,
- Typer for CLI commands,
- SQLAlchemy for database writes,
- Alembic for migrations,
- pytest for ingestion and database tests.

### 2. Supabase PostgreSQL

Yes, Supabase is being used.

The app uses Supabase-hosted PostgreSQL as the main database for:

- canonical source-derived tables,
- ingestion run records,
- source file identity,
- validation errors,
- reconciliation records,
- materialized KPI views,
- AI query logs.

Important rule: the frontend must not connect directly to Supabase. Supabase is a database platform here, not the frontend data API. The Python ingestion CLI and FastAPI backend access Postgres server-side.

### 3. FastAPI Backend

FastAPI is the read API layer for the dashboard.

It handles:

- typed API schemas,
- filter validation,
- pagination,
- dashboard summary endpoints,
- event detail endpoints,
- budget endpoints,
- workflow governance endpoints,
- intervention mix endpoints,
- doctor ROI endpoints,
- data-quality endpoints,
- AI query endpoint,
- safe error handling,
- secret isolation.

The backend reads from materialized views and detail tables. It should keep route handlers thin and push business logic into services, repositories, SQL views, and typed schemas.

### 4. React Dashboard

The frontend is a React + TypeScript dashboard.

Main tools:

- React,
- Vite,
- TypeScript,
- Tailwind CSS,
- TanStack Query,
- Zustand,
- Recharts,
- Lucide React,
- Vitest and React Testing Library.

Frontend pages:

- Executive Overview,
- Execution Matrix,
- Budget Utilization,
- Doctor ROI,
- Data Quality,
- AI Assistant panel.

The frontend calls FastAPI only. It does not calculate core KPIs from raw rows.

### 5. Grounded AI Assistant

The AI assistant is the last layer, not the source of truth.

It uses backend-generated context from deterministic services. It can summarize execution risk, budget gaps, doctor ROI, intervention mix, workflow bottlenecks, and data quality. It must refuse unsupported questions instead of inventing metrics.

AI logs store only redacted questions. Pcodes, monetary values, and likely doctor names are masked before persistence.

## How Each Excel Workbook Family Is Used

### RCPA Workbooks

Files:

- Nepal/Myanmar historical RCPA,
- Nepal/Myanmar current RCPA,
- Sri Lanka current RCPA.

Used for:

- doctor master data,
- Pcodes,
- speciality/class/status,
- brand and SKU prescription behavior,
- own-vs-competitor split,
- prescription quantity,
- prescription value,
- doctor ROI,
- high-value unengaged doctor detection,
- Cipla share,
- prescription trends.

Special handling:

- XLSB parsing is required.
- Column names differ across files, so alias maps are required.
- Month values may be text or Excel serial numbers.
- Pcodes must be stored as text.
- RCPA rows are aggregated before database write.
- Local currency is preserved.

### Yearly Planner Workbooks

Files:

- Nepal FY27 yearly planner,
- Sri Lanka FY27 yearly planner.

Used for:

- planned events,
- planned country/month/therapy,
- event type,
- event name,
- central/local classification,
- planned brands,
- planned HCP counts,
- planned patients/pharmacies,
- planned costs,
- country comments and planning notes.

Special handling:

- Nepal has multiple candidate sheets; `Yearly Planner FY27 v2` is canonical when present.
- Sri Lanka uses `YP FY27` as canonical.
- Alternate sheets are profiled but not loaded as duplicate canonical events.

### Consolidation Report

File:

- Consolidation report from Nov 2025 to June 2026.

Used for:

- actual smart-contract requests,
- request ID,
- country/division,
- intervention dates,
- venue,
- intervention name/type/subtype,
- estimated intervention value,
- confirmed/contracted amount,
- actual total spend,
- direct HCP/BTU spend,
- overhead/BTC spend,
- association amount and contract details,
- expected and actual doctors,
- expected and actual Pcodes,
- approval chain,
- request approval status,
- request confirmation status,
- post-event approval status,
- post-event confirmation status,
- expense submitted and confirmed dates,
- cancellation reason,
- city/state.

Special handling:

- `APPROVE/CONFIRMED TOTAL INTERVENTION` is the confirmed/contracted amount.
- `ESTIMATED INTERVENTION` is reference only and must not drive ROI spend.
- `ACTUAL EXPENSE AGAINST BTU` is direct HCP/BTU spend.
- `TOTAL ACTUAL BTC EXPENSE` is overhead/BTC spend.
- `TOTAL ACTUAL EXPENSES FOR INTERVENTION` is total actual spend.
- `Association Amount` is preserved separately and is not used as default contracted HCP spend.
- Doctor fields can contain multiple doctors/Pcodes and must be split into normalized participation rows.
- Workflow governance comes from request and post-event approval/confirmation fields.

### Monthly Execution Planner Workbooks

Files:

- April execution planner,
- May execution planner.

Used for:

- monthly execution snapshots,
- executed/action-due status,
- raised request totals,
- approved doctor totals,
- YP totals,
- country-tab execution evidence,
- event-created counts.

Special handling:

- April status uses `1` or blank.
- May status uses `Executed` or `Action due`.
- May has no Sri Lanka country tab, so Sri Lanka May execution evidence is derived from consolidation requests and clearly labeled as `derived_from_consolidation`.

## Database Model

Core tables:

- `ingestion_runs`
- `source_files`
- `ingestion_run_files`
- `validation_errors`
- `countries`
- `calendar_months`
- `exchange_rates`
- `plan_events`
- `execution_snapshots`
- `execution_requests`
- `request_doctors`
- `doctors`
- `rcpa_prescriptions`
- `event_matches`
- `ai_query_logs`

Core materialized views:

- `mv_execution_kpis`
- `mv_budget_utilization`
- `mv_workflow_governance`
- `mv_intervention_mix`
- `mv_doctor_roi`
- `mv_data_quality`
- `mv_unmatched_events`

## Dashboard Outputs

The final dashboard should show:

- planned vs actual execution,
- weak and unmatched events,
- Sri Lanka May derived execution note,
- request approval and confirmation bottlenecks,
- post-event report status,
- intervention type/subtype mix,
- planned vs confirmed vs actual budget,
- confirmed-vs-estimated variance,
- BTU/BTC spend split,
- official LKR FX at `1 USD = 310 LKR`, plus provisional/missing FX warnings for other currencies,
- doctor engagement and RCPA prescription behavior,
- ROI segments,
- ROI quadrant,
- dark-horse doctors,
- data-quality warnings,
- grounded AI summaries.

## Why This Architecture Is Practical

This architecture separates the hard parts cleanly:

- ingestion handles messy Excel,
- Postgres stores trusted canonical data,
- materialized views compute deterministic KPIs,
- FastAPI exposes typed read contracts,
- React focuses on dashboard UX,
- AI only summarizes trusted backend results.

That keeps the app credible, testable, deployable, and easier to debug when the source files are messy.
