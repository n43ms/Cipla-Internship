# Tasks: Cipla EMEU Execution Intelligence Platform

**Input**: Design documents from `specs/002-execution-intelligence-platform/` and product architecture from `finalplan.md`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `.specify/memory/constitution.md`, `finalplan.md`

**Tests**: Required. The constitution and specification require targeted tests for ingestion quirks, database constraints, reconciliation, materialized views, API contracts, frontend data states, AI grounding, deployment readiness, and confidentiality boundaries.

**Organization**: Tasks are grouped by dependency phase and user story. Each user story phase is independently testable after the shared foundation exists.

## Phase 1: Setup

**Purpose**: Establish the repository structure, toolchain, dependency manifests, environment contracts, and local-only data boundaries.

- [X] T001 Create backend, ingestion, frontend, database, docs, scripts, and data directory structure in `backend/`, `ingestion/`, `frontend/`, `database/`, `docs/`, `scripts/`, and `data/`
- [X] T002 Create Python backend dependency manifest with FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.0, Alembic, psycopg, pytest, httpx, and ruff in `backend/requirements.txt`
- [X] T003 Create Python ingestion dependency manifest with pandas, openpyxl, python-calamine, pyxlsb, Typer, SQLAlchemy 2.0, Alembic, pytest, and ruff in `ingestion/requirements.txt`
- [X] T004 Create frontend Vite React TypeScript dependency manifest with Tailwind CSS, TanStack Query, Zustand, Recharts, Lucide React, Vitest, and React Testing Library in `frontend/package.json`
- [X] T005 [P] Configure Python formatting, linting, import sorting, and pytest defaults for backend and ingestion in `pyproject.toml`
- [X] T006 [P] Configure TypeScript, Vite, Tailwind, path aliases, and Vitest setup in `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/tailwind.config.ts`, and `frontend/src/test/setup.ts`
- [X] T007 Create environment variable template for database, Supabase, data directory, backend URL, deployment mode, protected demo access, and AI provider configuration in `.env.example`
- [X] T008 Update git ignore rules for secrets, virtual environments, generated data, local raw workbooks, XLSX, XLSB, CSV extracts, reports, and local caches in `.gitignore`
- [X] T009 [P] Add backend application scaffolds in `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`, and `backend/app/database.py`
- [X] T010 [P] Add ingestion package scaffolds in `ingestion/__init__.py`, `ingestion/main.py`, `ingestion/config.py`, and `ingestion/report.py`
- [X] T011 [P] Add frontend shell files in `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/styles.css`, and `frontend/src/api/client.ts`
- [X] T012 Create local-only data folder scaffolding without real workbook content in `data/.gitkeep`, `data/raw/.gitkeep`, `data/processed/.gitkeep`, and `data/reports/.gitkeep`
- [X] T013 Create repository setup instructions with Windows PowerShell commands in `README.md`
- [X] T014 Create local validation command wrapper skeleton in `scripts/validate_quickstart.ps1`

**Checkpoint**: Repository structure, dependency manifests, environment contracts, and confidentiality boundaries exist.

---

## Phase 2: Foundational Architecture

**Purpose**: Build blocking infrastructure used by every user story: settings, database migrations, reference data, fixtures, common schemas, logging, API routing, and materialized-view refresh mechanics.

**Critical**: No user story implementation should start until this phase is complete.

- [ ] T015 Initialize Alembic migration environment and DATABASE_URL loading in `alembic.ini` and `database/migrations/env.py`
- [ ] T016 Create SQLAlchemy engine/session helpers, transaction utilities, and retry-safe connection handling in `backend/app/database.py` and `ingestion/database.py`
- [ ] T017 Create shared settings models with safe environment-variable handling and secret redaction in `backend/app/config.py` and `ingestion/config.py`
- [ ] T018 Create base database migration for schemas, UUID extension, audit timestamps, and enum types in `database/migrations/versions/0001_base_schema.py`
- [ ] T019 Create audit/source migration for `ingestion_runs`, reusable `source_files`, `ingestion_run_files`, and `validation_errors` in `database/migrations/versions/0002_audit_source_tables.py`
- [ ] T020 Create reference migration for `countries`, `calendar_months`, and `exchange_rates` including `rate_status` in `database/migrations/versions/0003_reference_tables.py`
- [ ] T021 Create canonical table migration for `plan_events`, `execution_snapshots`, `execution_requests`, `request_doctors`, `doctors`, and `rcpa_prescriptions` in `database/migrations/versions/0004_canonical_tables.py`
- [ ] T022 Create reconciliation and AI migration for `event_matches` and `ai_query_logs` in `database/migrations/versions/0005_reconciliation_ai_tables.py`
- [ ] T023 Create index and uniqueness migration for source file hash, run-file participation, country-scoped Pcodes, request identity, and RCPA aggregate conflict target in `database/migrations/versions/0006_indexes_constraints.py`
- [ ] T024 Create country seed SQL for Nepal, Sri Lanka, Myanmar, Oman, UAE, and Malaysia in `database/seeds/countries.sql`
- [ ] T025 Create FY26 and FY27 fiscal calendar seed generator with April fiscal-year start in `database/seeds/calendar_months.sql`
- [ ] T026 Create static exchange-rate seed with representative provisional rates for NPR, LKR, MMK, OMR, AED, and MYR in `database/seeds/exchange_rates_static.sql`
- [ ] T027 Create materialized-view refresh utility with dependency-ordered refresh behavior in `database/views/refresh_materialized_views.sql`
- [ ] T028 [P] Create backend pytest database fixture utilities and migration reset helper in `backend/tests/conftest.py`
- [ ] T029 [P] Create ingestion pytest database fixture utilities and temporary workbook helper in `ingestion/tests/conftest.py`
- [ ] T030 [P] Create frontend testing utility wrapper for router, query client, and mocked API responses in `frontend/tests/test-utils.tsx`
- [ ] T031 [P] Create synthetic fixture folder structure and README in `ingestion/tests/fixtures/xlsx/`, `ingestion/tests/fixtures/xlsb/`, `ingestion/tests/fixtures/expected/`, and `ingestion/tests/fixtures/README.md`
- [ ] T032 [P] Create synthetic fixture generation script for tiny planner, execution, consolidation, and RCPA workbook samples in `ingestion/tests/fixtures/build_fixtures.py`
- [ ] T033 [P] Create shared constants for source types, countries, fiscal years, status values, match statuses, ROI segments, workflow statuses, and snapshot sources in `ingestion/constants.py` and `backend/app/constants.py`
- [ ] T034 [P] Create shared normalizer package exports for months, Pcodes, event names, currencies, execution statuses, and workflow statuses in `ingestion/normalizers/__init__.py`
- [ ] T035 [P] Create backend typed error response schema and exception handlers in `backend/app/schemas/errors.py` and `backend/app/utils/errors.py`
- [ ] T036 [P] Create API router registration and health route skeleton in `backend/app/routers/__init__.py`, `backend/app/routers/health.py`, and `backend/app/main.py`
- [ ] T037 [P] Create OpenAPI-derived frontend API type definitions in `frontend/src/types/api.ts`
- [ ] T038 Create smoke test for Alembic migration and seed application in `backend/tests/database/test_migrations.py`
- [ ] T039 Create smoke test for settings validation, secret redaction, and missing secret handling in `backend/tests/unit/test_config.py` and `ingestion/tests/unit/test_config.py`
- [ ] T040 Create API error handling smoke tests for validation errors and unhandled exceptions in `backend/tests/api/test_error_handling.py`
- [ ] T041 Create frontend smoke test for app shell rendering and failed API fallback state in `frontend/tests/app-shell.test.tsx`
- [ ] T042 Create project-level architecture notes for runtime boundaries and data ownership in `docs/architecture.md`
- [ ] T043 Create source-file confidentiality and local workbook handling notes in `docs/source-data-policy.md`

**Checkpoint**: Database, migrations, seeds, fixtures, settings, test harness, and common application shells exist.

---

## Phase 3: User Story 1 - Trust the Ingested Data (Priority: P1) MVP

**Goal**: Profile, validate, normalize, and track all source workbook types with auditable ingestion runs and visible validation output.

**Independent Test**: Run profiling and ingestion over synthetic fixtures and real local workbooks; verify file classification, canonical sheet selection, row counts, validation errors, normalized months, normalized Pcodes, currency labels, and RCPA aggregation summaries.

### Tests for User Story 1

- [ ] T044 [P] [US1] Add tests for workbook discovery, file hashing, file identity reuse, and gitignored data path validation in `ingestion/tests/test_file_registry.py`
- [ ] T045 [P] [US1] Add tests for XLSX/XLSB reader behavior using openpyxl, python-calamine, and pyxlsb fallback in `ingestion/tests/test_workbook_reader.py`
- [ ] T046 [P] [US1] Add tests for workbook type detection, sheet profiling, used ranges, header detection, required-column coverage, and source classification in `ingestion/tests/test_profiler.py`
- [ ] T047 [P] [US1] Add tests for month normalization including `Apr-24`, `25-Apr`, `Oct-25`, `Apr'26`, `May-26`, date objects, and Excel serial `45772` in `ingestion/tests/test_month_normalizer.py`
- [ ] T048 [P] [US1] Add tests for Pcode normalization preserving text identifiers, blanks, decimal-looking numeric values, and duplicate raw values in `ingestion/tests/test_pcode_normalizer.py`
- [ ] T049 [P] [US1] Add tests for event-name, execution-status, workflow-status, and currency normalization in `ingestion/tests/test_normalizers.py`
- [ ] T050 [P] [US1] Add tests for Nepal and Sri Lanka planner canonical sheet selection and alternate-sheet profiling without double counting in `ingestion/tests/loaders/test_planner_loader.py`
- [ ] T051 [P] [US1] Add tests for April and May monthly execution status normalization, summary rows, country tabs, and missing Sri Lanka May tab detection in `ingestion/tests/loaders/test_execution_snapshot_loader.py`
- [ ] T052 [P] [US1] Add tests for consolidation `Working` sheet required fields, request IDs, approval chain capture, and raw doctor field preservation in `ingestion/tests/loaders/test_consolidation_loader.py`
- [ ] T053 [P] [US1] Add tests for RCPA column aliases, active-status aliases, own/competitor aliases, serial months, local currency preservation, and aggregate grain in `ingestion/tests/loaders/test_rcpa_loader.py`
- [ ] T054 [P] [US1] Add tests for expected and actual doctor participation splitting from multi-doctor consolidation fields in `ingestion/tests/loaders/test_request_doctors.py`
- [ ] T055 [P] [US1] Add tests for ingestion run, source file, run-file, validation error, and partial warning persistence in `ingestion/tests/test_ingestion_audit.py`
- [ ] T056 [P] [US1] Add tests for idempotent RCPA aggregate upsert and re-run behavior in `ingestion/tests/repositories/test_rcpa_repository.py`
- [ ] T057 [P] [US1] Add CLI contract tests for `profile`, `ingest --source all`, and `report` commands in `ingestion/tests/test_cli_contract.py`

### Implementation for User Story 1

- [ ] T058 [P] [US1] Implement source file discovery, hashing, metadata inference, duplicate hash handling, and gitignored path validation in `ingestion/file_registry.py`
- [ ] T059 [P] [US1] Implement workbook reader adapter using openpyxl for XLSX, python-calamine primary for XLSB, and pyxlsb fallback in `ingestion/workbook_reader.py`
- [ ] T060 [US1] Implement workbook profiler for sheet names, used ranges, header detection, row counts, sample rows, anomalies, and transcript-critical field detection in `ingestion/profiler.py`
- [ ] T061 [P] [US1] Implement month normalizer with fiscal-year mapping, date objects, Excel serial support, and parse diagnostics in `ingestion/normalizers/months.py`
- [ ] T062 [P] [US1] Implement Pcode normalizer preserving raw and normalized text values without numeric precision loss in `ingestion/normalizers/pcodes.py`
- [ ] T063 [P] [US1] Implement event-name, execution-status, workflow-status, and currency normalizers in `ingestion/normalizers/events.py`, `ingestion/normalizers/statuses.py`, `ingestion/normalizers/workflow_status.py`, and `ingestion/normalizers/currencies.py`
- [ ] T064 [P] [US1] Implement validation issue collector, severity model, and row-continuation policy in `ingestion/validators/errors.py`
- [ ] T065 [US1] Implement audit persistence for ingestion runs, source files, run-file records, and validation errors in `ingestion/repositories/audit_repository.py`
- [ ] T066 [US1] Implement planner loader with Nepal `Yearly Planner FY27 v2`, Sri Lanka `YP FY27`, source row references, and planner budget fields in `ingestion/loaders/planner.py`
- [ ] T067 [US1] Implement execution snapshot loader for April and May status values, country tabs, summary rows, source sheet references, and missing-tab limitations in `ingestion/loaders/execution_snapshot.py`
- [ ] T068 [US1] Implement consolidation loader for `Working` rows, request identity, dates, venues, interventions, status columns, approval chain, location, and raw doctor fields in `ingestion/loaders/consolidation.py`
- [ ] T069 [US1] Implement request doctor splitter for expected and actual names/classes/Pcodes with parse status and source positions in `ingestion/loaders/request_doctors.py`
- [ ] T070 [US1] Implement RCPA loader with alias maps, serial month parsing, local currency preservation, aggregation before persistence, and row-count summaries in `ingestion/loaders/rcpa.py`
- [ ] T071 [US1] Implement repositories for plan events, execution snapshots, execution requests, request doctors, doctors, and RCPA aggregates in `ingestion/repositories/canonical_repository.py`
- [ ] T072 [US1] Implement idempotent RCPA aggregate upsert against the explicit aggregate conflict target in `ingestion/repositories/rcpa_repository.py`
- [ ] T073 [US1] Implement ingestion orchestrator run order, transaction boundaries, partial warning behavior, fatal validation behavior, and terminal run status in `ingestion/orchestrator.py`
- [ ] T074 [US1] Implement Typer CLI commands `profile`, `ingest`, and `report` in `ingestion/main.py`
- [ ] T075 [US1] Implement markdown and JSON ingestion report generation with file participation, row counts, validation summaries, serial-month counts, Pcode coverage, and missing-FX warnings in `ingestion/report.py`
- [ ] T076 [US1] Add data dictionary entries for source workbooks, canonical sheets, source columns, normalized fields, and load rules in `docs/data-dictionary.md`
- [ ] T077 [US1] Add ingestion runbook section for local file placement, profiling, ingesting, rerunning, and interpreting validation output in `docs/ingestion-runbook.md`

**Checkpoint**: US1 is complete when all workbook families are profiled and ingested into auditable canonical records or explicit validation outputs.

---

## Phase 4: User Story 2 - Compare Planned vs Actual Execution (Priority: P2)

**Goal**: Reconcile planned events, monthly execution snapshots, consolidation requests, workflow statuses, and intervention mix so users can see executed, delayed, unmatched, weakly matched, pending, and reported activities.

**Independent Test**: Load planner, execution, and consolidation fixtures; run reconciliation; verify event matches, confidence, Sri Lanka May derived rows, workflow governance, intervention-type mix, and execution API/UI output.

### Tests for User Story 2

- [ ] T078 [P] [US2] Add unit tests for event name normalization, suffix removal, punctuation handling, harmless label removal, and conservative fuzzy thresholds in `ingestion/tests/reconciliation/test_event_name_matching.py`
- [ ] T079 [P] [US2] Add integration tests for event match creation across plan events, execution snapshots, and consolidation requests in `ingestion/tests/reconciliation/test_event_matcher.py`
- [ ] T080 [P] [US2] Add tests for Sri Lanka May consolidation-derived snapshot rows and source derivation notes in `ingestion/tests/reconciliation/test_sri_lanka_may_derivation.py`
- [ ] T081 [P] [US2] Add tests for workflow governance mapping from request approval, request confirmation, post approval, post confirmation, expense submitted, and expense confirmed columns in `ingestion/tests/loaders/test_consolidation_workflow_mapping.py`
- [ ] T082 [P] [US2] Add database tests for `mv_execution_kpis`, `mv_unmatched_events`, `mv_workflow_governance`, and `mv_intervention_mix` in `backend/tests/database/test_execution_governance_views.py`
- [ ] T083 [P] [US2] Add API contract tests for `/api/execution/summary`, `/api/execution/events`, `/api/workflow/summary`, `/api/workflow/requests`, and `/api/interventions/mix` in `backend/tests/api/test_execution_workflow_api.py`
- [ ] T084 [P] [US2] Add frontend tests for execution matrix loading, empty, error, weak-match, derived-source, workflow pending, and intervention mix states in `frontend/tests/execution-governance.test.tsx`

### Implementation for User Story 2

- [ ] T085 [P] [US2] Implement event matching repository for plan, snapshot, request, and match records in `ingestion/repositories/event_match_repository.py`
- [ ] T086 [US2] Implement deterministic event matcher with exact, normalized, fuzzy, weak, unmatched-plan, unmatched-snapshot, unmatched-request, and ignored statuses in `ingestion/reconciliation/event_matcher.py`
- [ ] T087 [US2] Implement Sri Lanka May consolidation derivation service with grouped request evidence and `snapshot_source = derived_from_consolidation` in `ingestion/reconciliation/sri_lanka_may_derivation.py`
- [ ] T088 [US2] Update consolidation loader to persist request approval, request confirmation, post approval, post confirmation, expense submitted, expense confirmed, owner/stage, and Level 1-6 approval metadata in `ingestion/loaders/consolidation.py`
- [ ] T089 [US2] Implement workflow status parser for draft, approved, rejected, deleted, sent-for-correction, pending owner, pending confirmation, and report states in `ingestion/normalizers/workflow_status.py`
- [ ] T090 [US2] Implement `reconcile` and `refresh-views` CLI commands in `ingestion/main.py`
- [ ] T091 [US2] Implement SQL for `mv_execution_kpis` including planned events, matched events, weak/unmatched events, executed events, action-due events, HCP rates, match coverage, and snapshot source counts in `database/views/mv_execution_kpis.sql`
- [ ] T092 [US2] Implement SQL for `mv_unmatched_events` with source type, event name, event type, reason, candidate match, confidence, and source references in `database/views/mv_unmatched_events.sql`
- [ ] T093 [US2] Implement SQL for `mv_workflow_governance` with request lifecycle counts, post/report lifecycle counts, current owner/stage, pending counts, and report status coverage in `database/views/mv_workflow_governance.sql`
- [ ] T094 [US2] Implement SQL for `mv_intervention_mix` using source-driven intervention type/subtype values, request counts, executed counts, approved counts, report pending counts, and spend fields in `database/views/mv_intervention_mix.sql`
- [ ] T095 [US2] Create migration to install execution, unmatched, workflow governance, and intervention mix materialized views and indexes in `database/migrations/versions/0007_execution_governance_views.py`
- [ ] T096 [P] [US2] Implement backend execution schemas for summary, event rows, match status, source derivation notes, and pagination in `backend/app/schemas/execution.py`
- [ ] T097 [P] [US2] Implement backend workflow schemas for status counts, owner stages, request rows, and reporting coverage in `backend/app/schemas/workflow.py`
- [ ] T098 [P] [US2] Implement backend intervention schemas for type/subtype rows, spend fields, workflow counts, and FX status in `backend/app/schemas/interventions.py`
- [ ] T099 [US2] Implement execution repository querying execution materialized views and event detail rows in `backend/app/repositories/execution_repository.py`
- [ ] T100 [US2] Implement workflow repository querying workflow summary and request-level rows in `backend/app/repositories/workflow_repository.py`
- [ ] T101 [US2] Implement intervention repository querying intervention type/subtype mix rows in `backend/app/repositories/intervention_repository.py`
- [ ] T102 [US2] Implement execution service with filter validation, pagination, data-quality flags, and limitation assembly in `backend/app/services/execution_service.py`
- [ ] T103 [US2] Implement workflow service with lifecycle status normalization, owner-stage summaries, and pending-report limitations in `backend/app/services/workflow_service.py`
- [ ] T104 [US2] Implement intervention service with source-driven categories and no hard-coded seven-type assumptions in `backend/app/services/intervention_service.py`
- [ ] T105 [US2] Implement execution routes for `/api/execution/summary` and `/api/execution/events` in `backend/app/routers/execution.py`
- [ ] T106 [US2] Implement workflow routes for `/api/workflow/summary` and `/api/workflow/requests` in `backend/app/routers/workflow.py`
- [ ] T107 [US2] Implement intervention route `/api/interventions/mix` in `backend/app/routers/interventions.py`
- [ ] T108 [P] [US2] Implement frontend execution, workflow, and intervention API clients in `frontend/src/api/execution.ts`, `frontend/src/api/workflow.ts`, and `frontend/src/api/interventions.ts`
- [ ] T109 [P] [US2] Implement execution status badges, match confidence badges, source derivation badges, and workflow stage badges in `frontend/src/components/execution/ExecutionBadges.tsx`
- [ ] T110 [P] [US2] Implement workflow governance cards, stage table, report status table, and pending-owner components in `frontend/src/components/workflow/WorkflowComponents.tsx`
- [ ] T111 [P] [US2] Implement intervention mix chart and table components in `frontend/src/components/interventions/InterventionMixComponents.tsx`
- [ ] T112 [US2] Implement Execution Matrix page with filters, KPI cards, planned-vs-engaged chart, event table, workflow governance panel, intervention mix panel, and drilldown drawer in `frontend/src/pages/ExecutionMatrix.tsx`

**Checkpoint**: US2 is complete when plan-vs-actual execution, workflow bottlenecks, and intervention mix can be audited from source rows through dashboard UI.

---

## Phase 5: User Story 3 - Understand Budget Utilization (Priority: P3)

**Goal**: Show planned budget, estimated/FMV-like reference, confirmed/contracted amount, actual total spend, BTU direct spend, BTC overhead spend, unused budget, overruns, spend-without-plan, and safe currency status.

**Independent Test**: Select a country/month and verify budget summary and detail rows show local currency, USD only when FX exists, provisional-FX warnings, confirmed-vs-estimated variance, BTU/BTC split, reconciliation warnings, and unmatched spend.

### Tests for User Story 3

- [ ] T113 [P] [US3] Add tests for consolidation financial mapping from estimated, confirmed/contracted, BTU, BTC, total actual, association amount, and variance source columns in `ingestion/tests/loaders/test_consolidation_financial_mapping.py`
- [ ] T114 [P] [US3] Add tests for static FX seeds, provisional FX status, missing-FX flags, future official FX replacement, and local-vs-USD behavior in `backend/tests/database/test_exchange_rates.py`
- [ ] T115 [P] [US3] Add database tests for `mv_budget_utilization` including planned budget, estimated reference, confirmed amount, variance, BTU/BTC split, total actual spend, unspent gap, overrun, plan without spend, and spend without plan in `backend/tests/database/test_budget_view.py`
- [ ] T116 [P] [US3] Add tests for BTU plus BTC reconciliation warnings when populated values do not match total actual spend in `backend/tests/database/test_budget_reconciliation_quality.py`
- [ ] T117 [P] [US3] Add API contract tests for `/api/budget/summary` including confirmedContractedAmount, actualTotalSpend, fxRateStatus, and provisional-FX limitations in `backend/tests/api/test_budget_api.py`
- [ ] T118 [P] [US3] Add frontend tests for budget cards, confirmed-vs-estimated variance, BTU/BTC split, provisional-FX warning, unmatched spend table, and empty states in `frontend/tests/budget-utilization.test.tsx`

### Implementation for User Story 3

- [ ] T119 [US3] Update consolidation loader financial mapping for `ESTIMATED INTERVENTION`, `APPROVE/CONFIRMED TOTAL INTERVENTION`, `ACTUAL EXPENSE AGAINST BTU`, `TOTAL ACTUAL BTC EXPENSE`, `TOTAL ACTUAL EXPENSES FOR INTERVENTION`, and `Association Amount` in `ingestion/loaders/consolidation.py`
- [ ] T120 [US3] Update execution request repository upserts for estimated, confirmed, variance, BTU, BTC, total actual, association, FX, and USD fields in `ingestion/repositories/execution_request_repository.py`
- [ ] T121 [US3] Implement FX lookup and monetary normalization helper with local amount preservation and nullable USD fields in `ingestion/normalizers/money.py`
- [ ] T122 [US3] Implement budget utilization SQL view using plan events, event matches, execution requests, local values, USD values, provisional-FX flags, and missing-FX flags in `database/views/mv_budget_utilization.sql`
- [ ] T123 [US3] Create migration to install budget materialized view, monetary indexes, and financial mapping constraints in `database/migrations/versions/0008_budget_finance_view.py`
- [ ] T124 [P] [US3] Implement backend budget schemas for summary cards, event budget gaps, confirmed-vs-estimated variance, BTU/BTC split, currency labels, and FX metadata in `backend/app/schemas/budget.py`
- [ ] T125 [US3] Implement budget repository querying `mv_budget_utilization`, unmatched spend detail rows, and FX metadata in `backend/app/repositories/budget_repository.py`
- [ ] T126 [US3] Implement budget service with local/normalized currency separation, provisional-FX limitations, reconciliation warnings, and pagination in `backend/app/services/budget_service.py`
- [ ] T127 [US3] Implement budget route `/api/budget/summary` in `backend/app/routers/budget.py`
- [ ] T128 [P] [US3] Implement frontend budget API client in `frontend/src/api/budget.ts`
- [ ] T129 [P] [US3] Implement currency label, FX warning, budget KPI card, BTU/BTC split, and variance components in `frontend/src/components/budget/BudgetComponents.tsx`
- [ ] T130 [US3] Implement Budget Utilization page with summary cards, planned-vs-confirmed-vs-actual chart, BTU/BTC split, event gap table, unmatched spend view, and FX warnings in `frontend/src/pages/BudgetUtilization.tsx`
- [ ] T131 [US3] Update data dictionary with exact consolidation financial source-column mapping and association amount rules in `docs/data-dictionary.md`

**Checkpoint**: US3 is complete when budget usage is explainable without mixing currencies, using estimated values as spend, or hiding BTU/BTC reconciliation problems.

---

## Phase 6: User Story 4 - Evaluate Doctor ROI and Missed Opportunities (Priority: P4)

**Goal**: Connect doctor attendance, total ROI spend, BTU/BTC spend, and RCPA prescription behavior to show engaged high-value doctors, high-prescribing unengaged doctors, low-prescription high-spend doctors, ROI quadrants, and dark-horse opportunities.

**Independent Test**: Load consolidation doctor attendance and RCPA aggregates; verify country-scoped Pcode joins, doctor segments, prescription splits, spend allocation, ROI quadrant labels, dark-horse flags, and no-RCPA states.

### Tests for User Story 4

- [ ] T132 [P] [US4] Add database tests for country-scoped doctor uniqueness and cross-country Pcode collision reporting in `backend/tests/database/test_doctor_constraints.py`
- [ ] T133 [P] [US4] Add tests for request doctor parsing into expected and actual participation records with missing, duplicate, and malformed Pcodes in `ingestion/tests/loaders/test_request_doctors.py`
- [ ] T134 [P] [US4] Add database tests for `mv_doctor_roi` including engagement count, last engagement, direct spend, overhead spend, total ROI spend, no-RCPA, divide-by-zero, and segment assignment in `backend/tests/database/test_doctor_roi_view.py`
- [ ] T135 [P] [US4] Add tests for ROI quadrant labels, deterministic median thresholds, low-effort/high-reward dark-horse flags, and insufficient-data handling in `backend/tests/database/test_roi_quadrant.py`
- [ ] T136 [P] [US4] Add API contract tests for `/api/doctors/roi` and `/api/doctors/{countryCode}/{pcode}` in `backend/tests/api/test_doctor_api.py`
- [ ] T137 [P] [US4] Add frontend tests for Doctor ROI table, quadrant matrix, scatter chart, no-RCPA state, segment filters, dark-horse list, and doctor detail drawer in `frontend/tests/doctor-roi.test.tsx`

### Implementation for User Story 4

- [ ] T138 [US4] Implement doctor master upsert from RCPA aggregates using country-scoped Pcode uniqueness in `ingestion/repositories/doctor_repository.py`
- [ ] T139 [US4] Implement cross-country Pcode collision detection, same-country conflict warnings, and doctor coverage summaries in `ingestion/validators/doctor_quality.py`
- [ ] T140 [US4] Update request doctor loader to link expected and actual attendance to execution requests and preserve unparseable raw fields in `ingestion/loaders/request_doctors.py`
- [ ] T141 [US4] Implement doctor ROI SQL view with engagement count, last engagement, direct HCP/BTU spend, overhead/BTC spend, total ROI spend, Cipla prescriptions, competitor prescriptions, Cipla share, spend per Cipla prescription, ROI segment, quadrant x/y, quadrant label, and dark-horse flag in `database/views/mv_doctor_roi.sql`
- [ ] T142 [US4] Create migration to install doctor ROI materialized view, doctor indexes, and quadrant indexes in `database/migrations/versions/0009_doctor_roi_quadrant_view.py`
- [ ] T143 [P] [US4] Implement backend doctor schemas for ROI rows, ROI quadrant fields, dark-horse flag, doctor profile, engagement history, prescription trend, brand mix, and coverage flags in `backend/app/schemas/doctors.py`
- [ ] T144 [US4] Implement doctor repository querying ROI view, doctor detail, engagement history, prescription trend, quadrant groups, and top opportunity rows in `backend/app/repositories/doctor_repository.py`
- [ ] T145 [US4] Implement doctor service with segment filters, quadrant filters, no-RCPA handling, pagination, detail assembly, and limitation propagation in `backend/app/services/doctor_service.py`
- [ ] T146 [US4] Implement doctor routes `/api/doctors/roi` and `/api/doctors/{countryCode}/{pcode}` in `backend/app/routers/doctors.py`
- [ ] T147 [P] [US4] Implement frontend doctor API client in `frontend/src/api/doctors.ts`
- [ ] T148 [P] [US4] Implement Doctor ROI chart, quadrant matrix, dark-horse card, segment badges, and coverage flag components in `frontend/src/components/doctors/DoctorRoiComponents.tsx`
- [ ] T149 [US4] Implement Doctor ROI page with scatter plot, quadrant matrix, segment tables, top opportunities, high-spend low-Rx list, filters, and detail drawer in `frontend/src/pages/DoctorRoi.tsx`
- [ ] T150 [US4] Update data dictionary with doctor ROI segment definitions, quadrant logic, and Pcode uniqueness rules in `docs/data-dictionary.md`

**Checkpoint**: US4 is complete when doctor opportunity analysis is traceable to attendance, spend, RCPA coverage, and deterministic quadrant rules.

---

## Phase 7: User Story 5 - See Data Quality Before Acting (Priority: P5)

**Goal**: Make freshness, validation errors, match coverage, Pcode coverage, RCPA coverage, missing FX, provisional FX, BTU/BTC reconciliation, workflow coverage, intervention coverage, and unmatched records visible before users act on KPIs.

**Independent Test**: Load a dataset with warnings and weak coverage; verify every dashboard API and page exposes data-quality flags and the Data Quality page drills into issue categories.

### Tests for User Story 5

- [ ] T151 [P] [US5] Add database tests for `mv_data_quality` including rows seen/skipped, validation counts, match coverage, Pcode coverage, RCPA coverage, missing FX, provisional FX, serial-month counts, BTU/BTC reconciliation issues, workflow coverage, and intervention-type coverage in `backend/tests/database/test_data_quality_view.py`
- [ ] T152 [P] [US5] Add API contract tests for `/api/data-quality`, `/api/filters`, and `/api/ingestion/latest` in `backend/tests/api/test_data_quality_api.py`
- [ ] T153 [P] [US5] Add frontend tests for data freshness banner, weak-match warning, missing-FX warning, provisional-FX warning, no-RCPA warning, stale-ingestion state, and partial-data state in `frontend/tests/data-quality-states.test.tsx`
- [ ] T154 [P] [US5] Add frontend tests for Data Quality page validation error drilldowns, unmatched records table, workflow coverage, and intervention coverage sections in `frontend/tests/data-quality-page.test.tsx`

### Implementation for User Story 5

- [ ] T155 [US5] Implement data quality SQL view with ingestion freshness, file counts, row counts, validation errors, match coverage, Pcode coverage, RCPA coverage, missing FX, provisional FX, stale run state, serial-month parse counts, BTU/BTC reconciliation issues, missing confirmed amounts, workflow status coverage, intervention type coverage, unmatched counts, and Sri Lanka May derivation notes in `database/views/mv_data_quality.sql`
- [ ] T156 [US5] Create migration to install data quality materialized view and indexes in `database/migrations/versions/0010_data_quality_view.py`
- [ ] T157 [P] [US5] Implement backend data quality schemas, filter option schemas, shared response metadata schemas, and limitation schemas in `backend/app/schemas/data_quality.py`, `backend/app/schemas/filters.py`, and `backend/app/schemas/meta.py`
- [ ] T158 [US5] Implement data quality repository querying latest ingestion, validation errors, unmatched records, source derivation notes, and coverage metrics in `backend/app/repositories/data_quality_repository.py`
- [ ] T159 [US5] Implement data quality service for shared `ResponseMeta`, limitations, quality flags, filter options, stale-run detection, and warning severity in `backend/app/services/data_quality_service.py`
- [ ] T160 [US5] Implement routes `/api/data-quality`, `/api/filters`, and `/api/ingestion/latest` in `backend/app/routers/data_quality.py`
- [ ] T161 [P] [US5] Implement frontend shared response metadata handling and query hooks in `frontend/src/hooks/useDashboardMeta.ts` and `frontend/src/api/filters.ts`
- [ ] T162 [P] [US5] Implement Data Freshness Banner, Quality Warning, Empty State, Error State, Partial Data State, Limitation List, and Stale Ingestion components in `frontend/src/components/common/DataStateComponents.tsx`
- [ ] T163 [US5] Implement Data Quality page with ingestion status, file row counts, validation errors, match coverage, Pcode coverage, RCPA coverage, unmatched records, missing FX, provisional FX, serial-month counts, workflow coverage, intervention coverage, and derivation notes in `frontend/src/pages/DataQuality.tsx`
- [ ] T164 [US5] Integrate shared quality banners into Executive Overview, Execution Matrix, Budget Utilization, and Doctor ROI pages in `frontend/src/App.tsx`
- [ ] T165 [US5] Update quickstart validation expectations for all data-quality flags in `specs/002-execution-intelligence-platform/quickstart.md`

**Checkpoint**: US5 is complete when uncertainty is visible at summary level, drilldown level, and AI context level.

---

## Phase 8: User Story 6 - Ask Grounded Business Questions (Priority: P6)

**Goal**: Add a backend-mediated AI assistant that summarizes deterministic dashboard facts, cites supporting metrics, includes limitations, redacts stored questions, and refuses unsupported questions.

**Independent Test**: Ask questions about execution risk, workflow bottlenecks, budget gaps, BTU/BTC spend, doctor ROI, intervention mix, data quality, and unsupported facts; verify answers are grounded in structured service context and logs store only redacted questions.

### Tests for User Story 6

- [ ] T166 [P] [US6] Add unit tests for AI question redaction of Pcodes, monetary values, and likely doctor names in `backend/tests/ai/test_redaction.py`
- [ ] T167 [P] [US6] Add unit tests for AI context builder using execution, workflow, intervention, budget, doctor, and data-quality service outputs in `backend/tests/ai/test_context_builder.py`
- [ ] T168 [P] [US6] Add tests for unsupported-question refusal, stale-data limitation propagation, and missing-data confidence downgrades in `backend/tests/ai/test_answer_policy.py`
- [ ] T169 [P] [US6] Add API contract tests for `/api/ai/query` grounded answers, unsupported questions, limitations, confidence, and `redactionApplied` in `backend/tests/api/test_ai_api.py`
- [ ] T170 [P] [US6] Add frontend tests for AI panel loading, grounded answer, unsupported answer, limitation display, confidence display, and error states in `frontend/tests/ai-assistant.test.tsx`

### Implementation for User Story 6

- [ ] T171 [P] [US6] Implement AI provider protocol, null provider, test provider, and environment-based provider selection in `backend/app/services/ai/provider.py`
- [ ] T172 [P] [US6] Implement AI redaction utility for `question_redacted` with Pcode, amount, and likely doctor-name masking in `backend/app/services/ai/redaction.py`
- [ ] T173 [US6] Implement deterministic AI context builder using execution, workflow, intervention, budget, doctor, and data-quality services in `backend/app/services/ai/context_builder.py`
- [ ] T174 [US6] Implement AI answer policy for supported topics, unsupported-topic refusal, source limitation propagation, and confidence assignment in `backend/app/services/ai/answer_policy.py`
- [ ] T175 [US6] Implement AI answer orchestration with provider-neutral model selection, compact structured context, timeout handling, and no raw workbook rows in `backend/app/services/ai/assistant_service.py`
- [ ] T176 [US6] Implement AI query log repository with sanitized payload persistence and error metadata in `backend/app/repositories/ai_repository.py`
- [ ] T177 [P] [US6] Implement AI request and response schemas in `backend/app/schemas/ai.py`
- [ ] T178 [US6] Implement `/api/ai/query` route in `backend/app/routers/ai.py`
- [ ] T179 [P] [US6] Implement frontend AI API client in `frontend/src/api/ai.ts`
- [ ] T180 [P] [US6] Implement AI Assistant panel, suggested prompts, supporting metrics display, limitation display, confidence badge, and grounded answer layout in `frontend/src/components/ai/AiAssistantPanel.tsx`
- [ ] T181 [US6] Integrate AI Assistant panel into dashboard layout with current page context and active filters in `frontend/src/App.tsx`

**Checkpoint**: US6 is complete when the assistant cannot invent metrics and every answer is tied to deterministic backend context.

---

## Phase 9: Product Shell, Deployment, Documentation, and Operational Hardening

**Purpose**: Complete cross-cutting app shell, protected deployment, runbooks, validation scripts, performance checks, and demo readiness after the selected user stories are complete.

- [ ] T182 [P] Implement Executive Overview page with KPI summary cards, execution risk highlights, budget highlights, ROI highlights, data-quality summary, and AI entry point in `frontend/src/pages/ExecutiveOverview.tsx`
- [ ] T183 Implement frontend route layout, navigation, responsive shell, global filters, protected-demo note, and page registration in `frontend/src/App.tsx`
- [ ] T184 [P] Implement shared filter bar, date range control, country selector, therapy/event/intervention filters, and persisted filter state in `frontend/src/components/common/FilterBar.tsx` and `frontend/src/store/filterStore.ts`
- [ ] T185 [P] Implement reusable table, pagination, sort, drawer, card, chart container, and tooltip components in `frontend/src/components/common/`
- [ ] T186 Add backend CORS, request logging, structured error logging, response timing, and safe exception handling in `backend/app/main.py`
- [ ] T187 Add backend repository pagination helpers, filter validation helpers, and common query parameter parsing in `backend/app/utils/query.py`
- [ ] T188 Add performance indexes and materialized-view refresh timing checks in `database/migrations/versions/0011_performance_indexes.py`
- [ ] T189 Add contract consistency check comparing backend schemas to OpenAPI response shapes in `backend/tests/contracts/test_openapi_schema_contract.py`
- [ ] T190 Add end-to-end quickstart validation script for migration, fixture generation, profiling, ingest, reconcile, refresh, backend tests, frontend tests, and git hygiene in `scripts/validate_quickstart.ps1`
- [ ] T191 [P] Update data dictionary with final tables, fields, source mappings, views, APIs, status semantics, financial mappings, and ROI quadrant rules in `docs/data-dictionary.md`
- [ ] T192 [P] Write ingestion runbook with local file placement, profiling, ingestion, reconciliation, refresh, reporting, rerun, failure recovery, and real-workbook confidentiality instructions in `docs/ingestion-runbook.md`
- [ ] T193 [P] Write deployment guide for protected frontend, hosted backend, Supabase PostgreSQL, environment variables, local ingestion, CORS, and secret handling in `docs/deployment.md`
- [ ] T194 [P] Write demo validation script covering executive overview, execution matrix, workflow governance, intervention mix, budget split, doctor ROI, data quality, and AI limitations in `docs/demo-validation.md`
- [ ] T195 Update README with project overview, architecture, setup commands, source-file confidentiality warning, local ingestion flow, deployment flow, and validation commands in `README.md`
- [ ] T196 Run backend and ingestion test command from quickstart and record the exact command and outcome in `docs/demo-validation.md`
- [ ] T197 Run frontend test command from quickstart and record the exact command and outcome in `docs/demo-validation.md`
- [ ] T198 Run OpenAPI YAML parse and contract validation and record the outcome in `docs/demo-validation.md`
- [ ] T199 Verify git status excludes real workbooks, generated data, reports, and secrets and document the result in `docs/deployment.md`
- [ ] T200 Review OpenAPI, CLI, and dashboard contracts against implemented schemas and update `specs/002-execution-intelligence-platform/contracts/openapi.yaml`, `specs/002-execution-intelligence-platform/contracts/cli.md`, and `specs/002-execution-intelligence-platform/contracts/dashboard-data-contract.md`

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational Architecture (Phase 2)**: Depends on Setup and blocks all user stories.
- **US1 Data Trust (Phase 3)**: Depends on Foundational Architecture and is the strict MVP.
- **US2 Execution Governance (Phase 4)**: Depends on US1 because reconciliation, workflow, and intervention mix need loaded planner, execution, and consolidation data.
- **US3 Budget Utilization (Phase 5)**: Depends on US1 and benefits from US2 event matches for event-level budget gaps.
- **US4 Doctor ROI (Phase 6)**: Depends on US1 and US3 spend fields; can proceed alongside US2 after canonical tables exist, but final ROI spend outputs require US3 financial mapping.
- **US5 Data Quality (Phase 7)**: Depends on US1 and integrates quality metrics from US2, US3, and US4.
- **US6 Grounded AI (Phase 8)**: Depends on US2, US3, US4, and US5 service outputs because AI must summarize deterministic context only.
- **Product Shell and Deployment (Phase 9)**: Depends on the selected demo scope; full demo readiness depends on all user stories.

### User Story Completion Order

1. US1 Trust the Ingested Data
2. US2 Compare Planned vs Actual Execution
3. US3 Understand Budget Utilization
4. US4 Evaluate Doctor ROI and Missed Opportunities
5. US5 See Data Quality Before Acting
6. US6 Ask Grounded Business Questions

### MVP Scope

The strict MVP is Phase 1, Phase 2, and US1. The first business-demo MVP is Phase 1, Phase 2, US1, US2, US3 budget summary, and the US5 data-quality banner subset. The recruiter-grade advanced demo is all phases through Phase 9.

---

## Parallel Execution Examples

### Setup Parallel Work

```text
T005, T006, T009, T010, and T011 can run in parallel after T001 creates folders.
```

### Foundational Parallel Work

```text
T028, T029, T030, T031, T032, T033, T034, T035, T036, and T037 can run in parallel while migrations T018-T023 are developed carefully in order.
```

### US1 Parallel Work

```text
T044-T057 can be written in parallel before implementation.
T061-T064 can be implemented in parallel.
T066-T070 can be implemented in parallel after T058-T065 are understood.
```

### US2 Parallel Work

```text
T078-T084 can be written in parallel.
T096-T098 and T108-T111 can run in parallel with repository/service work after view contracts are stable.
```

### US3 Parallel Work

```text
T113-T118 can be written in parallel.
T124, T128, and T129 can run in parallel while T119-T123 are implemented.
```

### US4 Parallel Work

```text
T132-T137 can be written in parallel.
T143, T147, and T148 can run in parallel while T138-T142 are implemented.
```

### US5 Parallel Work

```text
T151-T154 can be written in parallel.
T157, T161, and T162 can run in parallel while T155-T160 are implemented.
```

### US6 Parallel Work

```text
T166-T170 can be written in parallel.
T171, T172, T177, T179, and T180 can run in parallel before final AI orchestration.
```

### Cross-Cutting Parallel Work

```text
T182, T184, T185, T191, T192, T193, and T194 can run in parallel after the relevant story contracts exist.
```

---

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational Architecture.
2. Complete US1 tests and implementation.
3. Run profiling and ingestion against synthetic fixtures.
4. Run profiling against the real local workbooks without committing them.
5. Stop and validate row counts, validation errors, canonical sheet choices, serial dates, Pcodes, static/provisional FX, and RCPA aggregation.

### Business Demo Increment

1. Add US2 execution reconciliation, workflow governance, intervention mix, and event matrix.
2. Add US3 budget utilization with confirmed-vs-estimated mapping and BTU/BTC split.
3. Add minimal US5 data freshness and data-quality warnings.
4. Demo planned vs actual execution, pending workflow bottlenecks, budget gaps, and visible unmatched/weak-match records.

### Analytics Increment

1. Add US4 doctor ROI with RCPA joins, spend allocation, ROI segments, quadrant labels, and dark-horse flags.
2. Add full US5 data-quality drilldowns.
3. Validate no-RCPA, missing-Pcode, missing-FX, provisional-FX, and partial-data states.

### AI Increment

1. Add US6 only after deterministic APIs are stable.
2. Keep provider choice behind `AIProvider`.
3. Validate unsupported-question refusal, limitation propagation, and redacted logging before enabling real provider calls.

### Deployment Increment

1. Add product shell, responsive navigation, global filters, and executive overview.
2. Add protected frontend deployment, hosted backend, Supabase configuration, and local ingestion runbook.
3. Run full quickstart validation and document results before demo.

---

## Independent Test Criteria

- **US1**: Profiling and ingestion over synthetic and real local files reports source identities, canonical sheets, row counts, validation errors, normalized months, normalized Pcodes, and RCPA aggregates.
- **US2**: Reconciliation produces explicit match records, weak/unmatched records, Sri Lanka May derived execution rows, workflow status summaries, intervention mix, and execution dashboard outputs.
- **US3**: Budget APIs and UI expose planned budget, estimated reference, confirmed/contracted amount, variance, BTU/BTC split, total actual spend, local/USD handling, and FX warnings.
- **US4**: Doctor ROI APIs and UI expose country-scoped Pcode joins, engagement history, prescription behavior, ROI segments, quadrant labels, dark-horse flags, and no-RCPA limitations.
- **US5**: Data-quality APIs and UI expose freshness, validation errors, match coverage, Pcode coverage, RCPA coverage, FX quality, reconciliation quality, workflow coverage, and unmatched records.
- **US6**: AI answers cite deterministic metrics, include limitations, refuse unsupported facts, and persist only redacted questions.

---

## Notes

- Every task marked `[P]` touches separate files or can be performed without depending on incomplete tasks.
- Tests should be written before the matching implementation task and should fail before implementation.
- Real Cipla workbooks must remain under `data/raw/` and must not be committed.
- Frontend must never call Supabase or the AI provider directly.
- KPI math belongs in SQL/materialized views or typed backend services, never in AI or ad hoc frontend code.
- Browser ingestion, manual match editing, scheduled ingestion, full RBAC, and Power BI embedding remain out of MVP scope.
