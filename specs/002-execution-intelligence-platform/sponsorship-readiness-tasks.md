# Tasks: Sponsorship Readiness MVP

**Input**: `tasks.md`, `ingestion_sponsorship.md`, current repository architecture, and `sponsorship-readiness-plan.md`

**Goal**: Build the smallest sustainable pre-data pipeline that is useful even if the requested business data arrives late, incomplete, or not at all.

**Scope Boundary**: This is not a sponsorship/territory implementation task list. It is a readiness MVP. Do not create sponsorship, territory, accommodation, or doctor-contract database tables, loaders, routers, frontend pages, or AI contexts until real source files have been profiled and a new post-data task file is created.

**Tests**: Required for profiler behavior, workbook comparison behavior, CLI/report behavior, and storage-report parsing where practical. Documentation-only work must include review checklists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches separate files or independent tests.
- **[Story]**: User-story traceability label.
- Every task names the exact target file.

---

## Phase 1: MVP Guardrails And Data Request

**Purpose**: Make the business ask realistic and prevent the team from waiting for a perfect data package.

- [X] T001 [US1] Create the source intake contract in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T002 [P] [US1] Create the minimum viable and full desired data request in `docs/sponsorship-data-request.md`
- [X] T003 [P] [US1] Add a short Teams message, email outline, and priority order to `docs/sponsorship-data-request.md`
- [X] T004 [P] [US1] Add a received-data checklist covering raw file, cleaned file, RCPA sample, doctor/territory sample, and validation examples to `docs/sponsorship-data-request.md`
- [X] T005 [US1] Update source data handling rules for raw recurring extracts, cleaned presentation files, and no-real-data-in-git policy in `docs/source-data-policy.md`
- [X] T006 [US1] Cross-link the data request and source intake contract from `docs/ingestion-runbook.md`

**Checkpoint**: Abhijeet can send even one imperfect file, and the team still has a clear next step.

---

## Phase 2: Generic Profiler Schema-Drift Foundation

**Purpose**: Upgrade the existing profiler so any future file can be inspected before loaders or migrations are touched.

- [X] T007 [P] [US2] Add synthetic workbook fixture builders for schema-drift cases in `ingestion/tests/fixtures/build_fixtures.py`
- [X] T008 [P] [US2] Document synthetic fixture rules and the ban on real Cipla data in `ingestion/tests/fixtures/README.md`
- [X] T009 [P] [US2] Add profiler tests for mapped canonical fields and unknown columns in `ingestion/tests/test_profile_schema_drift.py`
- [X] T010 [P] [US2] Add profiler tests for missing required fields and empty columns in `ingestion/tests/test_profile_schema_drift.py`
- [X] T011 [P] [US2] Add profiler tests for bounded representative sample values in `ingestion/tests/test_profile_schema_drift.py`
- [X] T012 [US2] Extend profile models with mapped fields, unknown columns, missing required fields, empty columns, and sample values in `ingestion/models.py`
- [X] T013 [US2] Populate the new schema-drift metadata in `ingestion/profiler.py`
- [X] T014 [US2] Render schema-drift sections in profile markdown reports in `ingestion/report.py`
- [X] T015 [US2] Confirm existing profile CLI behavior still works after model changes in `ingestion/main.py`

**Checkpoint**: A single unknown workbook can produce a useful profile report without any source-specific code.

---

## Phase 3: Raw-Vs-Cleaned Workbook Comparison MVP

**Purpose**: Detect differences between recurring raw extracts and manually cleaned/presentable files before coding against the wrong shape.

- [X] T016 [P] [US3] Add comparison tests for shared, raw-only, cleaned-only, and normalized-header columns in `ingestion/tests/test_workbook_compare.py`
- [X] T017 [P] [US3] Add comparison tests for rename candidates and action-required columns in `ingestion/tests/test_workbook_compare.py`
- [X] T018 [P] [US3] Add CLI/report tests for markdown and JSON comparison outputs in `ingestion/tests/test_cli_schema_readiness.py`
- [X] T019 [US3] Implement source-neutral workbook comparison models and logic in `ingestion/workbook_compare.py`
- [X] T020 [US3] Add JSON serialization for comparison output in `ingestion/workbook_compare.py`
- [X] T021 [US3] Add markdown rendering for comparison reports in `ingestion/report.py`
- [X] T022 [US3] Wire a compare command into the ingestion CLI without changing existing ingest behavior in `ingestion/main.py`
- [X] T023 [US3] Document profile and compare commands with expected outputs in `docs/ingestion-runbook.md`

**Checkpoint**: If the business sends one raw and one cleaned file, the system can show exactly what changed before implementation starts.

---

## Phase 4: Storage Budget Guard

**Purpose**: Keep Supabase as the compact serving database and prevent accidental free-tier exhaustion.

- [X] T024 [P] [US4] Add storage report output contract tests in `backend/tests/database/test_storage_budget_report.py`
- [X] T025 [P] [US4] Create the storage budget runbook with pre-load and post-load checklist in `docs/storage-budget.md`
- [X] T026 [US4] Add a PowerShell database size report script that reads `DATABASE_URL` without printing secrets in `scripts/db_size_report.ps1`
- [X] T027 [US4] Add SQL snippets for total database size, largest relations, RCPA summaries, materialized views, and AI logs in `docs/storage-budget.md`
- [X] T028 [US4] Document compact-mode rules and no-raw-RCPA-online rules in `docs/storage-budget.md`
- [X] T029 [US4] Link the storage budget runbook from `docs/ingestion-runbook.md`

**Checkpoint**: Before any large future load, the engineer can measure database size and decide whether data belongs in Supabase or local processed storage.

---

## Phase 5: Feature Gates And Source Onboarding

**Purpose**: Make blocked work explicit and define what to do when partial data arrives.

- [X] T030 [P] [US5] Create the feature gate policy in `docs/feature-gate-policy.md`
- [X] T031 [P] [US5] Add planned, data-gated terms to `docs/data-dictionary.md`
- [X] T032 [US5] Document forbidden pre-data work in `docs/feature-gate-policy.md`
- [X] T033 [US5] Document minimum gates for raw consolidation, cleaned-only files, RCPA-only files, doctor/territory-only files, and no-data scenarios in `docs/feature-gate-policy.md`
- [X] T034 [US5] Create the source onboarding playbook in `docs/source-onboarding-playbook.md`
- [X] T035 [US5] Add the one-file-arrived workflow to `docs/source-onboarding-playbook.md`
- [X] T036 [US5] Add the post-data task-file creation rule to `docs/source-onboarding-playbook.md`
- [X] T037 [US5] Cross-link `sponsorship-readiness-plan.md`, `sponsorship-readiness-tasks.md`, `ingestion_sponsorship.md`, and the onboarding playbook from `docs/architecture.md`

**Checkpoint**: Anyone continuing the project can tell what is safe now, what is blocked, and what evidence is required to unblock each future slice.

---

## Phase 6: MVP Validation And Cleanup

**Purpose**: Verify the readiness MVP is coherent, test-covered where appropriate, and free of speculative product code.

- [X] T038 [P] Run profiler and comparison tests and record commands in `docs/ingestion-runbook.md`
- [X] T039 [P] Run or dry-run the storage report script and record a sanitized example in `docs/storage-budget.md`
- [X] T040 Review `git status --short` and document that no real workbooks, generated extracts, or secrets were added in `docs/source-data-policy.md`
- [X] T041 Review `sponsorship-readiness-tasks.md` and confirm no task creates speculative sponsorship/territory/accommodation migrations, loaders, routers, pages, or AI contexts in `specs/002-execution-intelligence-platform/sponsorship-readiness-tasks.md`
- [X] T042 Add a short pointer to the readiness MVP docs in `README.md`

**Checkpoint**: The MVP is ready to receive incomplete data and convert it into evidence-backed implementation tasks.

---

## MVP Completion Definition

The readiness MVP is complete when:

```text
minimum viable data request exists
source intake contract exists
profiler reports schema drift
raw-vs-cleaned comparison works on synthetic fixtures
storage budget check exists
feature gates are documented
source onboarding playbook exists
no source-specific sponsorship/territory implementation has been added
```

---

## Explicitly Blocked Future Work

Do not start these from this task file:

```text
sponsorship_events table
sponsorship_doctors table
doctor_contract_observations table
doctor_territory_assignments table
accommodation_records table
sponsorship normalizer with final business labels
doctor contract loader
territory loader
accommodation loader
sponsorship materialized views
territory materialized views
sponsorship FastAPI router
territory FastAPI router
SponsorshipIntelligence page
TerritoryIntelligence page
AI sponsorship context
AI territory context
AI suggested prompts for unavailable data
```

Create a separate post-data task file only after real files are profiled and the gate policy says a slice is unblocked.

Checklist review: this task file contains only readiness infrastructure, documentation, generic profiling/comparison behavior, and storage guard work. It does not create speculative sponsorship/territory/accommodation migrations, loaders, routers, pages, or AI contexts.

---

## Post-Data Slice Rule

When any data arrives, use this sequence:

```text
1. Save real source outside git.
2. Fill source intake contract.
3. Run profile.
4. Run raw-vs-cleaned compare if two variants exist.
5. Identify confirmed columns, labels, joins, and gaps.
6. Create tiny synthetic fixture from observed shape.
7. Write failing tests.
8. Update schema maps/loaders only for proven fields.
9. Estimate storage impact.
10. Create a new source-specific task file for database/backend/frontend/AI work only if gates pass.
```

This keeps the implementation evidence-driven and avoids architectural rework.
