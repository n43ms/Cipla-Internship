# Cipla EMEU Doctor ROI and Execution Intelligence Platform

Full-stack analytics platform for Cipla's Emerging Markets and Europe branch (EMEU/PBP). The system turns fragmented planner, execution, consolidation, workflow, budget, and RCPA prescription workbooks into an auditable dashboard for doctor ROI, regional investment decisions, execution governance, budget utilization, and data-quality review.

## Business Objective

The platform is built around doctor ROI: identifying which doctors, interventions, markets, and workflow actions justify continued investment. It highlights high-value engaged doctors, low-effort/high-reward dark-horse opportunities, low-prescription high-spend cases, missed execution, budget gaps, approval bottlenecks, and data-quality limitations before stakeholders act on the numbers.

## Architecture

```text
Local Excel/XLSB workbooks
  -> Python ingestion and reconciliation CLI
  -> Supabase PostgreSQL canonical tables and materialized KPI views
  -> FastAPI read services
  -> React executive dashboard
  -> ExecAI structured RAG assistant
```

Runtime boundaries:

- `ingestion/`: local Python CLI for workbook profiling, validation, loading, reconciliation, materialized-view refresh, and reporting.
- `backend/`: FastAPI read API, service/repository layer, filter validation, response metadata, and ExecAI orchestration.
- `frontend/`: Vite React TypeScript dashboard with charts, tables, drilldowns, data-quality states, and ExecAI.
- `database/`: Alembic migrations, SQL views, materialized views, and seed scripts.
- `docs/`: architecture notes, source policies, ingestion runbooks, data dictionary, and deployment/demo guidance.
- `specs/002-execution-intelligence-platform/`: product specification, implementation plan, contracts, and task plans.

## Core Capabilities

- Doctor ROI views with ROI quadrants, dark-horse opportunity flags, engagement history, RCPA baseline context, spend allocation, and doctor detail drawers.
- Execution matrix comparing planner events, execution snapshots, consolidation requests, weak matches, unmatched records, and Sri Lanka May derived evidence.
- Budget utilization views separating planned budget, confirmed contracted value, direct HCP/BTU spend, overhead/BTC spend, total actual spend, unspent gaps, overruns, and FX quality.
- Workflow governance panels for request approval, request confirmation, post-event approval, post-event confirmation, current owner stage, pending requests, and pending reports.
- Intervention mix analytics grouped from source intervention type and subtype values rather than hard-coded categories.
- Data-quality layer for latest ingestion status, validation issues, match coverage, Pcode coverage, RCPA coverage, stale data, missing FX, provisional FX, BTU/BTC reconciliation issues, and unmatched records.
- Dashboard upload flow for business users to submit new Excel files, validate workbook type, reject duplicates or unknown files, and generate a reviewable batch manifest before any ingestion write occurs.
- ExecAI, an embedded structured RAG assistant that plans business questions, retrieves deterministic FastAPI/PostgreSQL context, asks Gemini to synthesize, validates evidence references, redacts sensitive query logs, and falls back to deterministic answers when provider calls fail.

## Data Trust and Confidentiality

Real Cipla source workbooks are confidential local inputs. Keep them under `data/raw/` or another gitignored local folder. Do not commit raw workbooks, generated extracts, reports, `.env`, database credentials, Supabase service-role keys, or AI provider keys.

The frontend never calls Supabase or the AI provider directly. Source-derived business facts are written only through controlled ingestion paths. The dashboard upload endpoint stores uploaded Excel batches locally for validation and profiling; it does not mutate KPI tables until a reviewed ingestion run is executed.

## Scale Signals

- The documented real-file dry run processed 8 workbooks with 1,179,273 rows seen and 423,693 rows loaded into compact online records.
- RCPA prescription data is aggregated before persistence so Supabase stores app-ready summaries while detailed SKU-level evidence remains in local generated extracts.
- The repository currently includes 100+ test definitions across ingestion, backend, database/view, API, frontend-state, and AI-grounding behavior.

## Local Setup

Run commands from the repository root in PowerShell.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install -r ingestion\requirements.txt

cd frontend
npm install
cd ..
```

Create local environment settings:

```powershell
Copy-Item .env.example .env
```

Fill in database, Supabase, deployment, and AI values in `.env`. Do not commit `.env`.

## Frontend Development

```powershell
npm run dev --prefix frontend
npm test --prefix frontend
npm run build --prefix frontend
```

## Full Validation

The full workflow is documented in `specs/002-execution-intelligence-platform/quickstart.md`.

Typical validation flow:

```powershell
python -m ingestion.main profile --data-dir data/raw --output data/reports/profile.json
python -m ingestion.main ingest --source all
python -m ingestion.main reconcile
python -m ingestion.main refresh-views
python -m ingestion.main report --output data/reports/latest-ingestion.md
pytest ingestion/tests backend/tests
npm test --prefix frontend
```

`scripts/validate_quickstart.ps1` exists as a project-level validation wrapper, but the current implementation plan still tracks later hardening work for a complete end-to-end validation script.
