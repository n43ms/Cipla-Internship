# Cipla EMEU Doctor ROI & Execution Intelligence Platform

Full-stack enterprise decision intelligence platform engineered for Cipla's Emerging Markets and Europe Patient Benefits Program (EMEU/PBP). The system transforms fragmented, un-reconciled Excel/XLSB operating workbooks into auditable PostgreSQL facts, deterministic SQL materialized views, typed FastAPI REST endpoints, a high-performance React executive dashboard, and a grounded structured-RAG natural language copilot called **ExecAI**.

---

## Business Objectives

The platform provides a single, trustworthy decision layer for regional Cipla leadership across 6 EMEU/PBP markets: **Nepal, Sri Lanka, Myanmar, Oman, UAE, and Malaysia**.

### Primary Business Goals:
- **Orchestrate 50+ Regional Investment Decisions / Month**: Standardizes decision-making across doctor sponsorships, paid engagements, no-fee activities, workflow follow-ups, budget control, and territory coverage.
- **Unified Operating Layer**: Unifies yearly planner workbooks, monthly execution snapshots, smart-contract consolidation reports, doctor-wise intervention exports, MSL doctor master files, and RCPA prescription baselines.
- **Identify High-Value Opportunities**: Automatically surfaces **High-Value Engaged Doctors**, **Dark-Horse Doctors** (low effort / high reward), under-engaged high-prescription doctors, low-return spend patterns, territory gaps, and workflow bottlenecks.
- **Financial Rigor**: Rigorously separates planned budget, estimated FMV values, confirmed contracted amounts, direct HCP spend (BTU), overhead spend (BTC), total actual expense, and company-provided FX rates without mixing financial concepts.
- **Data Confidence First**: Discloses data-quality limitations before action: surfaces row counts, validation issues, match quality, P-code coverage, RCPA coverage, missing FX, and unmatched records directly in executive views.
- **Grounded AI Explanation Layer**: ExecAI answers natural-language business queries using strictly bounded PostgreSQL evidence, Pydantic contract validation, automated PII redaction, and deterministic fallback behavior.

---

## Business & Engineering Impact Snapshot

| Metric / Dimension | Enterprise Detail |
|---|---|
| **Decision Cadence** | Engineered to support 50+ recurring regional doctor investment & execution decisions per month. |
| **Market Scope** | 6 EMEU/PBP countries: Nepal, Sri Lanka, Myanmar, Oman, UAE, and Malaysia. |
| **Data Scale** | Documented real-file dry run profiled 8 workbooks, processed 1,179,273 raw rows, and loaded 423,693 canonical records into PostgreSQL. |
| **Authentication & Access Control** | Dual-tier credential access, `@cipla.com` email domain gate, Master Admin immutability lock, and Admin Passcode Management. |
| **Architecture** | Python 3.12 / FastAPI, Typer Ingestion CLI, Supabase PostgreSQL, React 19 / TypeScript / Tailwind CSS, and ExecAI. |
| **Test Reliability** | 98 passing backend pytest contract tests + 18 passing frontend Vitest component tests. |

---

## Table of Contents

- [Business Objectives](#business-objectives)
- [Business & Engineering Impact Snapshot](#business--engineering-impact-snapshot)
- [Product Overview](#product-overview)
- [Comprehensive Feature Highlights](#comprehensive-feature-highlights)
- [Dual-Tier Authentication & Security Model](#dual-tier-authentication--security-model)
- [System Architecture](#system-architecture)
- [Repository Structure](#repository-structure)
- [Data Sources & Ingestion Pipeline](#data-sources--ingestion-pipeline)
- [Database Layer & Materialized Views](#database-layer--materialized-views)
- [Backend API Specification](#backend-api-specification)
- [Frontend Executive Dashboard](#frontend-executive-dashboard)
- [ExecAI Structured RAG Architecture](#execai-structured-rag-architecture)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Security & Data Governance](#security--data-governance)
- [Local Setup & Deployment](#local-setup--deployment)
- [Common CLI Commands](#common-cli-commands)
- [Environment Variables](#environment-variables)
- [Project Documentation](#project-documentation)

---

## Product Overview

Cipla EMEU/PBP operating data originates from fragmented spreadsheet workbooks maintained by regional representatives, finance leads, and compliance teams. The platform ingests, cleans, reconciles, and models these inputs into an executive dashboard.

The system answers critical operational questions:
- *Which doctors deliver the highest ROI on Cipla sponsorships and contract investments?*
- *Which doctors demonstrate strong RCPA prescription signals but zero recent engagement?*
- *Which planned events lack execution evidence or post-event proof submissions?*
- *Which requests are delayed in multi-stage approval or confirmation workflows?*
- *Where did actual spend exceed planned budget allocations across territories?*
- *Which spend rows cannot be matched cleanly to planner evidence?*
- *Which territories are underserved, overserved, or lacking data confidence?*

---

## Comprehensive Feature Highlights

### 1. Doctor ROI Matrix & Intelligence
- **Deterministic ROI Classification**: Classifies doctors into 4 quadrants: *Low Effort / High Reward* (Dark-Horse), *High Effort / High Reward* (Key Accounts), *Low Effort / Low Reward*, and *High Effort / Low Reward*.
- **Dark-Horse Flags**: Highlights under-engaged doctors generating high RCPA prescription volume.
- **No-RCPA Disclosures**: Discloses doctors with active sponsorships but missing RCPA prescription baseline coverage.
- **Doctor Detail Drawer**: Slide-over drawer detailing historical sponsorships, brand prescription breakdown, contract economics, FMV savings, and attendance records.

### 2. Execution Governance Matrix
- **3-Way Reconciliation**: Matches planned events, monthly execution snapshots, and smart-contract consolidation requests.
- **Match Confidence & Disclosures**: Surfaces exact matches, weak matches (date/name tolerance), and unmatched events.
- **Proof & Evidence Tracking**: Flags missing post-event proof, pending reports, and delayed execution owners.

### 3. Budget Utilization & Financial Governance
- **Multi-Category Financial Breakdown**: Separates Planned Budget, Estimated Value, Confirmed Contracted Amount, BTU Direct Spend, BTC Overhead Spend, Total Actual Expense, and Association Amounts.
- **Burn Rate & Gap Analysis**: Calculates budget burn rates, unspent budget gaps, and budget overruns per country and activity type.
- **Company FX Rate Engine**: Applies official company exchange rates with explicit missing-FX warnings.

### 4. Territory Intelligence
- **Geographic Coverage Mapping**: Maps doctor reach, prescription volume, and investment allocation across regions.
- **Territory Classification**: Flags territories as *Underserved*, *Overserved*, *Balanced*, or *Insufficient Data*.
- **Specialty & Patch Density**: Analyzes doctor concentration by medical specialty and patch location.

### 5. Data Quality & Audit Engine
- **Freshness Banner**: Surfaces latest ingestion timestamps and dataset status across dashboard headers.
- **Skipped Row & Error Audits**: Discloses file hash tracking, missing required columns, rejected P-codes, cross-country collisions, and weak-match warnings.
- **Compact Warning Disclosures**: Replaces loud alert banners with elegant, expandable disclosure panels (`WarningDisclosure.tsx`).

### 6. ExecAI Decision Copilot
- **Structured RAG Querying**: Bounded natural-language assistant answering queries on ROI, execution risk, budget gaps, territory reach, and data quality.
- **Quick Prompt Pills**: Pre-populated business prompts for instant execution.
- **Evidence & Citation Rendering**: Displays supporting SQL view evidence, confidence scores, and platform limitations alongside answers.

### 7. Dual-Tier Authentication & Single-Node Entry
- **Inline Entrance Screen**: Glassmorphic Email + Passcode login form replacing the static entrance button without modifying top navbar layout.
- **Domain Gate Enforcement**: Only `@cipla.com` email addresses and the Master Admin are permitted (`403 Forbidden` for all other domains).
- **Master Admin Immortality**: Master Admin `adityaxnema@gmail.com` password (`Guddan@1205`) is hardcoded and immutable.

### 8. Admin Passcode Management Modal
- **Reset Admin Passcode Modal**: Slide-over modal accessible via `UtilityMenu` allowing whitelisted administrators to update the shared `@cipla.com` passcode (`POST /api/auth/change-password`).
- **Strict Role Authorization**: Non-admin users do not see the option; non-whitelisted attempts return `403 Forbidden`.

---

## Dual-Tier Authentication & Security Model

The system enforces strict credential access and role-based privilege management:

```text
                                [ User Login Request ]
                                          │
                                ┌─────────┴─────────┐
                                ▼                   ▼
                   [ adityaxnema@gmail.com ]    [ *@cipla.com ]
                                │                   │
                                ▼                   ▼
                      Requires "Guddan@1205"   Requires Shared Passcode
                                │              ("AdityaIntern@2026")
                                ▼                   │
                         Master Admin               ▼
                       (isAdmin = True)     Check Admin Whitelist
                                                    │
                                         ┌──────────┴──────────┐
                                         ▼                     ▼
                                  [ Whitelisted ]       [ Standard User ]
                                  (isAdmin = True)      (isAdmin = False)
                                         │                     │
                                         ▼                     ▼
                                  Can Reset Shared     Standard Access
                                  Admin Passcode       No Reset Privilege
```

### Whitelisted Administrators:
- `pralhad.gujar@cipla.com`
- `abhijeet.mudila@cipla.com`
- `aditya.emmanual@cipla.com`
- `adityaxnema@gmail.com` (Master Admin)

### Security Safeguards:
- **Master Admin Password Immutability**: `POST /api/auth/change-password` explicitly blocks any attempt targeting or modifying `adityaxnema@gmail.com`'s credentials.
- **Domain Gate Enforcement**: Non-@cipla.com email domains (e.g. `user@gmail.com`) return `403 Forbidden`.
- **Zero Frontend Menu Alteration**: The top navbar header, Cipla logo badge (`CiplaLogoPlaceholder`), primary pages dropdown, and governance dropdown remain 100% invariant.

---

## System Architecture

```text
Confidential Local Workbooks (.xlsx, .xlsb)
   │
   ▼
Python Ingestion Engine (Typer CLI / Upload Intake)
   ├── Source Fingerprinting & Schema Mapping
   ├── Deterministic Loaders, Normalizers & Validators
   └── 3-Way Fuzzy Event Reconciliation
   │
   ▼
Supabase PostgreSQL Database
   ├── Canonical Fact & Dimension Tables
   └── Materialized KPI Views (12 Views)
   │
   ▼
FastAPI Backend Service Layer
   ├── Typed Pydantic v2 Schemas & Repositories
   ├── Dual-Tier Auth & Domain Gate Router
   └── ExecAI Structured RAG Engine
   │
   ▼
React 19 / TypeScript Executive Dashboard
   ├── Tailwind CSS Glassmorphic Aesthetics
   ├── Interactive Recharts Analytics & Slide-Over Drawers
   └── ExecAI Natural Language Assistant Panel
```

---

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── routers/          # FastAPI route handlers (auth, doctors, budget, execution, territory, workflow, data_quality, ai)
│   │   ├── schemas/          # Pydantic v2 request/response contracts
│   │   ├── services/         # Business logic and orchestration
│   │   ├── repositories/     # SQL data access repositories
│   │   ├── services/ai/      # ExecAI query planning, context, provider, validation, redaction
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   └── tests/                # 98 passing pytest unit and contract tests
│
├── ingestion/
│   ├── loaders/              # Source-specific workbook loaders (consolidation, planner, rcpa, doctor_wise, etc.)
│   ├── normalizers/          # Months, P-codes, currencies, events, FX, statuses, territories
│   ├── validators/           # Schema drift and quality validation helpers
│   ├── reconciliation/       # Fuzzy event matcher and derived execution logic
│   ├── repositories/         # Ingestion database write repositories
│   ├── orchestrator.py
│   └── main.py               # Typer CLI CLI entry point
│
├── database/
│   ├── migrations/versions/  # Alembic database migrations
│   ├── views/                # Materialized KPI View SQL definitions
│   └── seeds/                # Country, calendar, and official FX seeds
│
├── frontend/
│   ├── src/
│   │   ├── api/              # Typed API clients (apiGet, apiPost, apiPostForm)
│   │   ├── components/       # Reusable UI, dashboard, upload, modal, and ExecAI components
│   │   ├── pages/            # Doctor ROI, Execution, Budget, Territory, Data Quality
│   │   ├── hooks/            # Custom React hooks
│   │   └── types/            # TypeScript interface definitions
│   └── tests/                # 18 passing Vitest component tests
│
├── scripts/                  # Automated validation scripts (validate_auth.ps1)
├── specs/                    # Spec Kit artifacts (spec.md, plan.md, tasks.md, data-model.md)
├── README.md
└── pyproject.toml
```

---

## Data Sources & Ingestion Pipeline

### Supported Source Families:
1. **Yearly Planner Workbooks**: Planned events, expected activity cadence, and allocated budgets.
2. **Monthly Execution Snapshots**: Monthly execution statuses and planner evidence.
3. **Consolidation Reports**: Request IDs, intervention dates, workflow states, approval stages, attendance, BTU/BTC actual expenses.
4. **Doctor-Wise Intervention Exports**: Doctor-level intervention rows, FMV, contracted amounts, contract IDs, and P-code linkages.
5. **Cumulative & Historical RCPA Workbooks**: Prescription baselines across brand portfolios and territory patches.
6. **MSL Doctor Master**: Doctor demographic, specialty, patch, legacy-code, and territory enrichment.

### Ingestion Pipeline Stages:
- **Fingerprinting & Profiling**: SHA-256 hash checking, format detection (`.xlsx`, `.xlsb`, CRM HTML), row counts, and schema drift reports.
- **Deterministic Normalization**: P-code formatting, Excel serial date parsing, currency conversion via official FX table, and status mapping.
- **Fuzzy Event Matching**: Reconciles planned vs executed events using normalized event names, P-codes, date tolerances, and amount proximity.
- **Materialized View Refresh**: Refreshes all 12 SQL materialized views upon ingestion completion.

---

## Database Layer & Materialized Views

The database layer serves as the single source of truth across ingestion, backend API endpoints, and ExecAI context.

| Materialized View | Purpose |
|---|---|
| `mv_doctor_roi` | Doctor ROI quadrant scoring, spend, RCPA prescriptions, and dark-horse flags. |
| `mv_execution_event_matrix` | 3-way event matrix comparing planner, execution, and consolidation records. |
| `mv_budget_utilization` | Planned, confirmed, BTU, BTC, actual, gap, overrun, and FX metrics. |
| `mv_workflow_governance` | Approval stage, confirmation state, delayed owners, and workflow bottlenecks. |
| `mv_territory_opportunity` | Underserved, overserved, balanced, and insufficient-data territory classifications. |
| `mv_data_quality` | Data freshness, coverage rates, validation errors, and reconciliation caveats. |
| `mv_sponsorship_outcomes` | Sponsorship economics, FMV contract savings, and attendance records. |

---

## Backend API Specification

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login` | `POST` | Dual-tier login authentication with domain gate enforcement. |
| `/api/auth/change-password` | `POST` | Admin passcode update endpoint with Master Admin immutability lock. |
| `/api/doctors/roi` | `GET` | Doctor ROI metrics, quadrant counts, and paginated doctor table. |
| `/api/doctors/{country_code}/{pcode}` | `GET` | Comprehensive doctor detail payload (sponsorships, RCPA, attendance). |
| `/api/execution/summary` | `GET` | Executive execution KPIs and gap analytics. |
| `/api/execution/events` | `GET` | Event matrix table with match quality and proof status filters. |
| `/api/budget/summary` | `GET` | Budget utilization, BTU/BTC split, overruns, and FX status. |
| `/api/territory/opportunities` | `GET` | Territory classifications, doctor reach, and specialty density. |
| `/api/workflow/requests` | `GET` | Workflow request drilldown with approval stage tracking. |
| `/api/data-quality` | `GET` | Dataset freshness, file manifests, skipped rows, and validation warnings. |
| `/api/ai/query` | `POST` | ExecAI grounded natural language query processing. |

---

## Frontend Executive Dashboard

Built using React 19, TypeScript, and Tailwind CSS with a curated Dark Mode palette (`#07090a`), cyan/emerald/amber/rose HSL accents, and glassmorphic blur cards:

- **Doctor ROI View**: Interactive ROI quadrant scatterplot, dark-horse badges, brand mix indicators, and slide-over doctor profile drawer.
- **Execution Governance View**: Event progress tracking, missing evidence alerts, and match-quality indicators.
- **Budget Utilization View**: BTU vs BTC burn rates, currency conversion disclosures, and gap analysis charts.
- **Territory Intelligence View**: Interactive geographic breakdown and specialty concentration tables.
- **Data Quality Audit View**: Dataset freshness status, file ingestion manifest, and validation error disclosures.
- **ExecAI Copilot Panel**: Slide-over AI chat assistant with pre-populated prompt pills and supporting SQL evidence citations.
- **Admin Passcode Modal**: Glassmorphic modal for whitelisted administrators to update shared passcodes securely.

---

## ExecAI Structured RAG Architecture

ExecAI is an embedded structured RAG assistant designed for high-precision decision support:

```text
User Question (Frontend)
   │
   ▼
POST /api/ai/query
   │
   ▼
AssistantService (Topic Routing & Intent Analysis)
   │
   ▼
Context Builder (Fetches bounded evidence from SQL Materialized Views)
   │
   ▼
PII Redaction Engine (Masks sensitive P-codes / Names if configured)
   │
   ▼
Gemini 1.5 Provider (Generates structured JSON response)
   │
   ▼
Response Validator (Verifies evidence references & handles failover)
   │
   ▼
Frontend Render (Displays Answer, Evidence Pointers, Confidence & Limitations)
```

---

## Testing & Quality Assurance

The codebase undergoes rigorous automated test verification:

### Backend Test Suite (Pytest):
- **98 Passing Tests** covering FastAPI API routes, Pydantic schemas, database repository queries, ingestion normalizers, fuzzy event matchers, dual-tier auth domain gates, and ExecAI fallback mechanics.

### Frontend Test Suite (Vitest & React Testing Library):
- **18 Passing Tests** covering dashboard page rendering, warning disclosure toggles, table refetch stability, modal submission states, and ExecAI assistant interactions.

---

## Security & Data Governance

1. **Confidential Raw Data**: Raw Cipla Excel workbooks remain strictly local and gitignored (`data/raw/`, `data/processed/`).
2. **Backend-Only Secrets**: Database connection strings, Supabase service keys, and Gemini API keys remain strictly backend-side and are never exposed to the frontend.
3. **No Direct Frontend DB Access**: The React frontend communicates exclusively through typed FastAPI REST endpoints.
4. **Master Admin Protection**: Hardcoded Master Admin credentials (`adityaxnema@gmail.com` $\rightarrow$ `"Guddan@1205"`) cannot be altered or reset by API requests.
5. **Domain Access Control**: Non-@cipla.com email domains return `403 Forbidden`.

---

## Local Setup & Deployment

### Prerequisites:
- Python 3.11+
- Node.js 20+
- PostgreSQL or Supabase-hosted PostgreSQL

### 1. Backend Setup:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r ingestion\requirements.txt
```

### 2. Frontend Setup:
```powershell
npm install --prefix frontend
```

### 3. Environment Configuration:
```powershell
Copy-Item .env.example .env
```

### 4. Run Development Servers:
```powershell
# Start Backend FastAPI Server (Port 8000)
uvicorn backend.app.main:app --reload --port 8000

# Start Frontend Vite Dev Server (Port 5173)
npm run dev --prefix frontend
```

---

## Common CLI Commands

```powershell
# Run Backend Test Suite
.venv\Scripts\python -m pytest backend/tests/api/test_auth.py

# Run Full Pytest Suite
.venv\Scripts\python -m pytest backend/tests

# Run Frontend Vitest Suite
npm test --prefix frontend

# Build Frontend Production Bundle
npm run build --prefix frontend

# Execute Automated Auth Script
powershell -ExecutionPolicy Bypass -File scripts/validate_auth.ps1
```

---

## Environment Variables

| Variable | Purpose | Default / Fallback |
|---|---|---|
| `DATABASE_URL` | PostgreSQL SQLAlchemy connection string. | Local PostgreSQL |
| `CIPLA_SHARED_PASSCODE` | Shared passcode for `@cipla.com` users. | `AdityaIntern@2026` |
| `AI_PROVIDER` | ExecAI provider (`gemini`, `test`, `null`). | `gemini` |
| `AI_API_KEY` | Server-side Gemini API key. | — |
| `VITE_API_BASE_URL` | Frontend API base URL. | `http://localhost:8000` |

---

## Project Documentation

- **Specs & Architecture**: [plan.md](file:///C:/Users/adity/OneDrive/Desktop/Apps/CS/Cipla-Internship/specs/002-execution-intelligence-platform/plan.md), [spec.md](file:///C:/Users/adity/OneDrive/Desktop/Apps/CS/Cipla-Internship/specs/002-execution-intelligence-platform/spec.md), [data-model.md](file:///C:/Users/adity/OneDrive/Desktop/Apps/CS/Cipla-Internship/specs/002-execution-intelligence-platform/data-model.md)
- **API & Task Contracts**: [tasks.md](file:///C:/Users/adity/OneDrive/Desktop/Apps/CS/Cipla-Internship/specs/002-execution-intelligence-platform/tasks.md), [frontend-cleanup-tasks.md](file:///C:/Users/adity/OneDrive/Desktop/Apps/CS/Cipla-Internship/specs/002-execution-intelligence-platform/frontend-cleanup-tasks.md)
- **ExecAI Deep Dive**: [AI_LAYER_WALKTHROUGH.md](file:///C:/Users/adity/OneDrive/Desktop/Apps/CS/Cipla-Internship/backend/app/services/ai/AI_LAYER_WALKTHROUGH.md)

---

## Engineering Story

This repository represents an end-to-end data product built with enterprise-grade software engineering principles:

```text
Messy Confidential Excel Source Workbooks
  └── Deterministic Python Ingestion & 3-Way Event Matching
      └── Supabase PostgreSQL Canonical Tables & Materialized Views
          └── Typed FastAPI REST Endpoints & Dual-Tier Security Gate
              └── React 19 Executive Dashboard & ExecAI Copilot
                  └── Comprehensive Pytest & Vitest Suite Verification
```

Engineered for **Cipla EMEU/PBP** by **Aditya Nema**.
