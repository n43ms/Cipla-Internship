# Tasks: Sponsorship And Territory Readiness

**Input**: Design documents from `specs/002-execution-intelligence-platform/`, current completed `tasks.md`, `ingestion_sponsorship.md`, and `sponsorship-readiness-plan.md`

**Prerequisites**: `plan.md`, `spec.md`, `tasks.md`, `data-model.md`, `contracts/`, `quickstart.md`, `ingestion_sponsorship.md`, `sponsorship-readiness-plan.md`

**Tests**: Required for ingestion/profiling code, schema-drift comparison, CLI behavior, and storage-report scripting. Documentation-only tasks require reviewable checklists instead of automated tests.

**Scope Boundary**: These tasks are intentionally limited to work that is safe before new business data arrives. Do not create sponsorship/accommodation/territory database tables, loaders, routers, frontend pages, or AI context until actual source files have passed the data-arrival gates in `sponsorship-readiness-plan.md`.

**Organization**: Tasks are grouped by independently testable readiness stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches separate files or has no dependency on incomplete tasks.
- **[Story]**: User story label for traceability.
- Every task includes an exact file path.

---

## Phase 1: Setup (Shared Planning Artifacts)

**Purpose**: Create the non-code artifacts that make the next phase executable without guessing source schemas.

- [ ] T001 Create the source intake contract template in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [ ] T002 [P] Create the business data request package in `docs/sponsorship-data-request.md`
- [ ] T003 [P] Create the feature gate policy for unavailable sponsorship/territory surfaces in `docs/feature-gate-policy.md`
- [ ] T004 [P] Create the storage budget runbook in `docs/storage-budget.md`
- [ ] T005 Update the source data policy with raw-recurring-extract and raw-vs-cleaned comparison rules in `docs/source-data-policy.md`

**Checkpoint**: Business stakeholders can understand exactly what data to send, and engineering has written rules preventing speculative implementation.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add generic profiling/comparison foundations that every later data-source slice needs.

**CRITICAL**: No source-specific sponsorship, doctor-contract, accommodation, or territory implementation should begin until this phase is complete.

- [ ] T006 [P] Add schema-drift fixture builders for raw and cleaned workbook variants in `ingestion/tests/fixtures/build_fixtures.py`
- [ ] T007 [P] Add schema-drift fixture documentation in `ingestion/tests/fixtures/README.md`
- [ ] T008 [P] Add tests for profile fields covering mapped columns, unknown columns, empty columns, required missing fields, and sample value capture in `ingestion/tests/test_profile_schema_drift.py`
- [ ] T009 [P] Add tests for raw-vs-cleaned workbook comparison output in `ingestion/tests/test_workbook_compare.py`
- [ ] T010 [P] Add tests for profile and comparison CLI behavior in `ingestion/tests/test_cli_schema_readiness.py`
- [ ] T011 Extend profile models with mapped, unknown, missing, empty, and sample-value metadata in `ingestion/models.py`
- [ ] T012 Extend workbook profiling to populate schema-drift metadata without adding sponsorship-specific required fields in `ingestion/profiler.py`
- [ ] T013 Implement a generic raw-vs-cleaned workbook comparison utility in `ingestion/workbook_compare.py`
- [ ] T014 Extend profile report markdown with schema-drift and unknown-column sections in `ingestion/report.py`
- [ ] T015 Add profile comparison CLI command for raw-vs-cleaned reports in `ingestion/main.py`

**Checkpoint**: Any incoming raw file can be profiled and compared against a cleaned file before changing loaders or schema maps.

---

## Phase 3: User Story 1 - Request A Complete Data Package (Priority: P1) MVP

**Goal**: Give Abhijeet/Anil/Varad a precise, implementation-friendly data request and source contract so the team sends data that can be used without manual cleanup.

**Independent Test**: A reviewer can open the data request and source intake contract and verify that every source needed by `ingestion_sponsorship.md` has owner, cadence, fields, file-shape, identity, money, doctor, territory, and validation-example requirements.

### Tests for User Story 1

- [ ] T016 [P] [US1] Add a documentation completeness checklist for the business data request in `docs/sponsorship-data-request.md`
- [ ] T017 [P] [US1] Add a source contract review checklist in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`

### Implementation for User Story 1

- [ ] T018 [US1] Fill the source intake contract with sections for raw consolidation, cleaned consolidation, doctor contract report, historical RCPA, monthly RCPA, MSL doctor master, territory mapping, accommodation/travel, sponsorship labels, and validation examples in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [ ] T019 [US1] Fill the business request with concise priority order, exact field lists, preferred formats, and non-negotiable raw-file rules in `docs/sponsorship-data-request.md`
- [ ] T020 [US1] Add a Teams-message and email-outline appendix for requesting the data package in `docs/sponsorship-data-request.md`
- [ ] T021 [US1] Cross-link the source intake contract and data request from the ingestion runbook in `docs/ingestion-runbook.md`

**Checkpoint**: The data request can be sent without requiring additional context from chat history.

---

## Phase 4: User Story 2 - Profile And Compare New Files Before Coding (Priority: P1)

**Goal**: Make it possible to inspect incoming raw and cleaned files, detect schema drift, and produce an engineering decision report before writing source-specific loaders or migrations.

**Independent Test**: Running the profile and comparison tests against synthetic raw/cleaned fixtures produces a report with mapped columns, unknown columns, missing required columns, removed columns, renamed candidates, and action-required fields.

### Tests for User Story 2

- [ ] T022 [P] [US2] Add failing profiler assertions for mapped canonical fields and unknown raw columns in `ingestion/tests/test_profile_schema_drift.py`
- [ ] T023 [P] [US2] Add failing profiler assertions for empty columns and representative sample values in `ingestion/tests/test_profile_schema_drift.py`
- [ ] T024 [P] [US2] Add failing comparison assertions for raw-only, cleaned-only, shared, and renamed-candidate columns in `ingestion/tests/test_workbook_compare.py`
- [ ] T025 [P] [US2] Add failing CLI assertions that comparison reports write markdown and JSON outputs in `ingestion/tests/test_cli_schema_readiness.py`

### Implementation for User Story 2

- [ ] T026 [US2] Implement mapped canonical field capture and unknown column capture in `ingestion/profiler.py`
- [ ] T027 [US2] Implement missing required field and empty column capture in `ingestion/profiler.py`
- [ ] T028 [US2] Implement bounded representative sample values for risky columns in `ingestion/profiler.py`
- [ ] T029 [US2] Implement raw-only, cleaned-only, shared, and normalized-header comparison logic in `ingestion/workbook_compare.py`
- [ ] T030 [US2] Add JSON serialization support for profile comparison output in `ingestion/workbook_compare.py`
- [ ] T031 [US2] Add markdown rendering for profile comparison reports in `ingestion/report.py`
- [ ] T032 [US2] Wire the comparison command into the ingestion CLI without changing existing ingest behavior in `ingestion/main.py`
- [ ] T033 [US2] Document the profile-and-compare workflow with example commands and expected outputs in `docs/ingestion-runbook.md`

**Checkpoint**: New data can be inspected safely before modifying any source-specific ingestion code.

---

## Phase 5: User Story 3 - Protect Supabase Free-Tier Storage Before New Loads (Priority: P2)

**Goal**: Make database size visible before and after large RCPA/sponsorship/territory experiments, so compact-mode decisions are enforced before storage is exhausted.

**Independent Test**: Running the storage script or documented SQL returns total database size, largest tables/views, RCPA summary sizes, AI log size, and free-tier headroom without printing secrets.

### Tests for User Story 3

- [ ] T034 [P] [US3] Add script-output contract tests for storage report parsing in `backend/tests/database/test_storage_budget_report.py`
- [ ] T035 [P] [US3] Add documentation verification checklist for pre-load and post-load storage checks in `docs/storage-budget.md`

### Implementation for User Story 3

- [ ] T036 [US3] Add a PowerShell database size report script that reads `DATABASE_URL` safely and prints size/headroom/table breakdowns in `scripts/db_size_report.ps1`
- [ ] T037 [US3] Add SQL snippets for total size, top relations, RCPA summaries, materialized views, and AI logs in `docs/storage-budget.md`
- [ ] T038 [US3] Document compact-mode storage rules and explicit no-raw-RCPA-online rules in `docs/storage-budget.md`
- [ ] T039 [US3] Link the storage budget runbook from `docs/ingestion-runbook.md`

**Checkpoint**: Before a large file is loaded, the engineer can measure whether Supabase has enough room and decide compact/local storage behavior.

---

## Phase 6: User Story 4 - Gate Future Sponsorship, Contract, RCPA, Territory, And AI Work (Priority: P2)

**Goal**: Prevent accidental placeholder implementation by documenting exact gates and deferred tasks for each future source-specific slice.

**Independent Test**: A reviewer can verify that each future implementation area has required data-arrival gates, forbidden pre-data work, allowed post-data work, and acceptance criteria.

### Tests for User Story 4

- [ ] T040 [P] [US4] Add a gate review checklist for raw consolidation, sponsorship classification, doctor contract report, historical RCPA, monthly RCPA, territory, accommodation, and AI extension in `docs/feature-gate-policy.md`
- [ ] T041 [P] [US4] Add a data-gated glossary checklist for sponsorship and territory planned terms in `docs/data-dictionary.md`

### Implementation for User Story 4

- [ ] T042 [US4] Document forbidden pre-data work including sponsorship tables, loaders, routers, frontend pages, and AI context in `docs/feature-gate-policy.md`
- [ ] T043 [US4] Document allowed post-data vertical-slice order for raw consolidation, doctor contract report, RCPA backfill, monthly RCPA, sponsorship outcomes, doctor detail, sponsorship page, territory, and AI in `docs/feature-gate-policy.md`
- [ ] T044 [US4] Add planned data-gated definitions for sponsorship event, sponsorship doctor, no-fee service, post-sponsorship movement, accommodation support, territory opportunity, and manual P-code provenance in `docs/data-dictionary.md`
- [ ] T045 [US4] Add implementation-ready task templates for future post-data slices in `specs/002-execution-intelligence-platform/sponsorship-readiness-tasks.md`
- [ ] T046 [US4] Cross-link `sponsorship-readiness-plan.md`, `sponsorship-readiness-tasks.md`, and `ingestion_sponsorship.md` from `docs/architecture.md`

**Checkpoint**: Anyone continuing the project knows exactly what is safe now and what is blocked until real files arrive.

---

## Phase 7: User Story 5 - Prepare Source-Specific Onboarding Playbooks Without Implementing Them (Priority: P3)

**Goal**: Create operational playbooks for how to implement each future slice after data arrives, without adding speculative source-specific code.

**Independent Test**: Each playbook explains trigger data, profiling commands, fixture creation, tests to add, implementation files to touch, storage checks, and acceptance criteria.

### Tests for User Story 5

- [ ] T047 [P] [US5] Add onboarding checklist validation sections for each future source in `docs/source-onboarding-playbook.md`

### Implementation for User Story 5

- [ ] T048 [US5] Create the source onboarding playbook covering raw consolidation and sponsorship classification in `docs/source-onboarding-playbook.md`
- [ ] T049 [US5] Extend the source onboarding playbook with doctor contract report and contract-ID reconciliation steps in `docs/source-onboarding-playbook.md`
- [ ] T050 [US5] Extend the source onboarding playbook with historical RCPA and monthly RCPA refresh steps in `docs/source-onboarding-playbook.md`
- [ ] T051 [US5] Extend the source onboarding playbook with MSL/doctor master and territory mapping steps in `docs/source-onboarding-playbook.md`
- [ ] T052 [US5] Extend the source onboarding playbook with accommodation/travel handling rules that remain blocked until data proves a separate source in `docs/source-onboarding-playbook.md`
- [ ] T053 [US5] Extend the source onboarding playbook with AI-extension readiness rules requiring deterministic backend services first in `docs/source-onboarding-playbook.md`

**Checkpoint**: When Abhijeet sends data, the next engineer can follow a deterministic playbook instead of improvising.

---

## Final Phase: Polish & Cross-Cutting Validation

**Purpose**: Verify the readiness work is coherent, non-speculative, and connected to existing project docs.

- [ ] T054 [P] Run focused ingestion tests for profiler and comparison behavior and record commands in `docs/ingestion-runbook.md`
- [ ] T055 [P] Run the storage budget script against the configured database and record a sanitized example output in `docs/storage-budget.md`
- [ ] T056 Review `git status` to confirm no real workbooks, generated extracts, reports, or secrets were added and document the result in `docs/source-data-policy.md`
- [ ] T057 Review `sponsorship-readiness-tasks.md` to confirm no task creates speculative sponsorship/accommodation/territory migrations, loaders, frontend pages, or AI contexts before data arrives in `specs/002-execution-intelligence-platform/sponsorship-readiness-tasks.md`
- [ ] T058 Update `README.md` with a short pointer to the sponsorship readiness docs and data request package

---

## Blocked Future Work: Do Not Start Until Data Gates Pass

These are intentionally not implementation tasks yet. Convert them into a separate post-data task file only after real files are profiled and the relevant gates pass.

```text
Blocked until raw consolidation samples:
  - final sponsorship classifier rules
  - sponsorship normalizer
  - consolidation alias changes

Blocked until doctor contract report:
  - doctor contract loader
  - contract-ID reconciliation
  - unmatched contract data-quality output

Blocked until historical RCPA files:
  - manual P-code provenance persistence
  - historical RCPA storage/retention policy changes
  - sponsorship pre/post RCPA outcome views

Blocked until monthly RCPA samples:
  - monthly RCPA replacement/append logic changes
  - recurring RCPA freshness rules beyond current data quality

Blocked until territory/doctor master data:
  - territory assignment tables
  - territory opportunity materialized view
  - territory dashboard/API

Blocked until deterministic services exist:
  - sponsorship frontend page
  - territory frontend page
  - sponsorship/territory AI context
  - AI suggested prompts for unavailable data
```

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 only for scope clarity; blocks source-specific data onboarding.
- **US1 Data Package Request**: Can start after Setup.
- **US2 Profile And Compare Tooling**: Depends on Foundational tests/fixtures and can proceed in parallel with US1 docs.
- **US3 Storage Safeguards**: Can proceed in parallel with US1 and US2 after Setup.
- **US4 Gates And Deferred Work**: Depends on Setup and should incorporate decisions from US1-US3.
- **US5 Source Onboarding Playbooks**: Depends on US4 gates.
- **Polish**: Depends on selected readiness stories being complete.

### User Story Completion Order

1. **US1 Data Package Request (P1)**: highest value immediately because it unblocks business data collection.
2. **US2 Profile And Compare Tooling (P1)**: required before changing loaders for incoming raw files.
3. **US3 Storage Safeguards (P2)**: required before large RCPA or new materialized views.
4. **US4 Gates And Deferred Work (P2)**: prevents speculative implementation.
5. **US5 Source Onboarding Playbooks (P3)**: makes post-data implementation repeatable.

### MVP Scope

The readiness MVP is:

```text
Phase 1 + Phase 2 + US1 + US2
```

This is enough to request data and safely inspect it when it arrives.

### Full Pre-Data Scope

The complete pre-data scope is:

```text
Phase 1 through Phase 7 + Final Phase
```

This leaves the repository ready for source-specific vertical slices without adding speculative implementation.

---

## Parallel Execution Examples

### Setup Parallel Work

```text
T002, T003, and T004 can run in parallel because they create separate docs.
```

### Foundational Parallel Work

```text
T006, T007, T008, T009, and T010 can run in parallel before implementation starts.
T011-T015 should be done after tests are written.
```

### User Story 1 Parallel Work

```text
T016 and T017 can run in parallel.
T018-T020 should be completed before T021 cross-links the runbook.
```

### User Story 2 Parallel Work

```text
T022, T023, T024, and T025 can run in parallel.
T026-T028 touch profiler behavior and should be coordinated.
T029 and T030 can run before T031.
T032 should happen after comparison output exists.
```

### User Story 3 Parallel Work

```text
T034 and T035 can run in parallel.
T036 and T037 can run in parallel after output expectations are defined.
T039 depends on T037-T038.
```

### User Story 4 Parallel Work

```text
T040 and T041 can run in parallel.
T042 and T043 both update feature-gate policy and should be serialized.
T044 can run in parallel with T042-T043.
T046 should run after cross-links exist.
```

### User Story 5 Parallel Work

```text
T048-T053 all update the same playbook and should be serialized for clarity.
```

---

## Implementation Strategy

### Readiness MVP First

1. Complete Setup.
2. Complete Foundational profiling/comparison tests.
3. Complete US1 data package request.
4. Complete US2 profile/compare tooling.
5. Stop and validate by running profiler/comparison commands against synthetic fixtures.

### Full Pre-Data Delivery

1. Add storage budget safeguards.
2. Add feature-gate policy.
3. Add source onboarding playbooks.
4. Polish documentation links and verification notes.

### Post-Data Delivery Strategy

When real data arrives, do not continue from guesses. Create a new post-data task file using:

```text
profile results
confirmed source labels
confirmed join keys
storage budget estimate
synthetic fixture derived from real source shape
```

Then implement one vertical slice at a time:

```text
raw consolidation -> sponsorship classification -> doctor contract report -> RCPA backfill -> monthly RCPA refresh -> sponsorship outcomes -> doctor detail -> sponsorship page -> territory -> AI
```

---

## Notes

- All real workbooks stay out of git.
- All source-specific implementation remains blocked until profile reports exist.
- Do not add visible frontend navigation for data that does not exist.
- Do not send sponsorship or territory prompts to AI until deterministic backend services exist.
- Do not create database migrations for speculative entities before source schemas are confirmed.
- KPI and classification logic must remain deterministic and test-covered.
- Supabase remains the compact serving database, not the raw data lake.

