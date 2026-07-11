# Tasks: Sponsorship ROI And Batch Upload Readiness

**Input**: `sponsorship-readiness-plan.md`, `ingestion_sponsorship.md`, `files/transcript5.txt`, existing `spec.md`, `plan.md`, `tasks.md`, and current repository architecture.

**Scope Boundary**: These tasks update the next phase around the clarified July 9 transcript and the July 10 received workbook package under `files/`. Source-specific production loaders, migrations, APIs, frontend pages, and AI context are not implementation-ready until the actual workbook profiles pass the gates in `sponsorship-readiness-plan.md`.

**Tests**: Required for profiling, source classification, batch upload validation, RCPA idempotency, storage-budget scripts, and deterministic classification. Documentation-only tasks require explicit checklist sections.

**Core Clarification**: The next phase is manual batch upload, not SFTP or SharePoint polling. The core product remains Doctor ROI quadranting. Sponsorship, engagement economics, RCPA history, and territory are evidence layers that explain the quadrant. The required source package is present and the previously open scope questions are resolved.

**Initial Preload Requirement**: The already received workbook package under `files/` must be ingested through the controlled CLI/backend ingestion path before treating dashboard upload as the primary business workflow. The preload should load the complete usable package, except one intentionally held-out non-critical file if a dashboard-upload demo is needed.

**Future Refresh Requirement**: The user-facing future-refresh workflow must be: business user uploads Excel files through **Upload new data/files** in the React dashboard, FastAPI validates and stages the batch, deterministic ingestion writes accepted source facts into Supabase, materialized views refresh, and the dashboard reflects the refreshed Doctor ROI, sponsorship/engagement, RCPA, data-quality, and ExecAI evidence. Upload-only validation is an intermediate gate, not the final product state.

**Final Deliverable Definition**: The feature is complete only when the received `files/` package can be pre-ingested into Supabase, views refresh, Doctor ROI evidence is visible in the frontend, and an accepted dashboard-uploaded future or held-out batch can update the same Supabase-backed canonical facts. Doctor ROI investment must include source-backed sponsorship and engagement value where available, and must show caveats instead of a misleading zero where sponsorship/engagement exists but amount is missing.

**Required Traceability**: Every new dashboard-visible sponsorship, engagement, economics, and RCPA metric must be traceable to source file identity, source type, doctor/P-code join, period, and relevant caveats. Do not store unbounded raw workbook rows in Supabase to achieve this; use compact facts, hashes, row references, aggregate counts, and local generated extracts where needed.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches separate files or independent test areas.
- **[Story]**: User story label for traceability.
- Every implementation task includes an exact file path.

---

## Phase 1: Received Package Registration And Planning Refresh

**Purpose**: Align project docs with the transcript5 clarifications and the actual July 10 workbook package before source-specific code changes start.

- [X] T001 Record the received file inventory, source labels, and known open questions in `docs/source-onboarding-playbook.md`
- [X] T002 [P] Update the source intake contract for the received file package in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T003 [P] Update the feature-gate policy to make SFTP, SharePoint polling, fake pages, and AI-over-raw-data explicitly out of scope in `docs/feature-gate-policy.md`
- [X] T004 [P] Update the source data policy with manual batch upload, SharePoint-as-source-location, labeled-file, and no-real-workbooks-in-git requirements in `docs/source-data-policy.md`
- [X] T005 [P] Update the data dictionary with clarified terms for sponsorship, engagement, FMV, contracted value, no-fee activity, paid engagement, cumulative RCPA, FS HQ, Location, PATCHNAME, and MSL territory in `docs/data-dictionary.md`
- [X] T006 Add official FX rates for Sri Lanka, Nepal, Oman, UAE, Myanmar, and Malaysia to the source contract and cross-link `files/transcript5.txt`, `sponsorship-readiness-plan.md`, and this task file from `docs/architecture.md`

**Checkpoint**: A reviewer can see that the July 9 decisions and July 10 files are the new source of truth.

---

## Phase 2: Batch Upload And Source Intake Foundation

**Purpose**: Build the reusable intake path for manually uploaded raw files without assuming final schemas.

### Tests

- [X] T007 [P] Add source manifest parser tests for labeled workbook batches in `ingestion/tests/test_source_manifest.py`
- [X] T008 [P] Add source fingerprint tests for received consolidated XLSX, doctor-wise HTML-XLS exports, cleaned presentable XLSX reports, ERS workbook, MSL workbook, unified monthly RCPA workbook, and confirmed historical RCPA XLSB files in `ingestion/tests/test_source_fingerprints.py`
- [X] T009 [P] Add duplicate-file/hash validation tests in `ingestion/tests/test_batch_upload_validation.py`
- [X] T010 [P] Add wrong-report quarantine tests in `ingestion/tests/test_batch_upload_validation.py`

### Implementation

- [X] T011 Add source manifest models for file label, source type, raw-vs-cleaned, country scope, period scope, owner, export timestamp, and received package path in `ingestion/models.py`
- [X] T012 Implement source manifest loading and validation in `ingestion/source_manifest.py`
- [X] T013 Add source fingerprint rules for XLSX, XLSB, and CRM HTML-XLS files without hard-coding final business logic in `ingestion/source_fingerprints.py`
- [X] T014 Add duplicate-file and wrong-source validation to the ingestion orchestrator in `ingestion/orchestrator.py`
- [X] T015 Add a batch profile command that accepts a source manifest in `ingestion/main.py`
- [X] T016 Document the manual batch upload workflow and example manifest in `docs/ingestion-runbook.md`
- [X] T016A Add business-user dashboard upload flow backed by batch fingerprint validation in `backend/app/routers/ingestion.py`, `backend/app/services/ingestion_upload_service.py`, `frontend/src/components/ingestion/DataUploadPanel.tsx`, and `frontend/src/App.tsx`
- [X] T016B Add backend ingestion trigger/status workflow for an accepted uploaded batch so validated files can move from `data/uploads/<batch-id>/` into Supabase canonical tables after loader gates pass in `backend/app/routers/ingestion.py` and `backend/app/services/`
- [X] T016C Add frontend post-upload states for accepted-for-review, ingestion-running, Supabase-updated, views-refreshed, and dashboard-data-refreshed in `frontend/src/components/ingestion/DataUploadPanel.tsx`
- [ ] T016D Add integration tests proving an accepted dashboard-uploaded batch can be ingested, refresh materialized views, and update dashboard-visible API responses after source-specific loaders are implemented in `backend/tests/api/` and `frontend/tests/`

**Checkpoint**: Abhijeet or another business user can upload a future or intentionally held-out file package from the dashboard, see accepted/rejected files, and, after loader gates pass, run a controlled refresh that updates Supabase and dashboard-visible Doctor ROI evidence.

---

## Phase 3: Schema Profiling And Raw-Vs-Cleaned Comparison

**Purpose**: Safely inspect the incoming file package before loader, schema, or UI work.

### Tests

- [X] T017 [P] Add profiler tests for mapped fields, unknown columns, empty columns, header-row detection, row counts, country scope, period scope, and sample values across received XLSX, XLSB, and HTML-XLS files in `ingestion/tests/test_profile_schema_drift.py`
- [X] T018 [P] Add comparison tests for `Raw Reports -Point 1/Consolidated Raw Report` vs `Cleaned Presentable Version - Point 2` in `ingestion/tests/test_workbook_compare.py`
- [X] T019 [P] Add comparison tests for `Raw Reports -Point 1/Doctor Raw Report` vs `Cleaned Presentable Version - Point 2` in `ingestion/tests/test_workbook_compare.py`
- [X] T020 [P] Add CLI report-output tests for JSON and markdown profile reports in `ingestion/tests/test_cli_schema_readiness.py`

### Implementation

- [X] T021 Extend workbook profiling metadata in `ingestion/profiler.py`
- [X] T022 Extend profile models with mapped, unknown, missing, empty, sample-value, and header-row fields in `ingestion/models.py`
- [X] T023 Implement raw-vs-cleaned comparison utility in `ingestion/workbook_compare.py`
- [X] T024 Render profile and comparison reports in `ingestion/report.py`
- [X] T025 Wire profile comparison command into `ingestion/main.py`
- [X] T026 Document expected outputs and decision rules in `docs/ingestion-runbook.md`

**Checkpoint**: Incoming files can be accepted, rejected, or queued for loader work based on observed schema evidence.

---

## Phase 4: Clarified Business Source Contracts

**Purpose**: Convert transcript decisions into reviewable source contracts before implementation.

- [X] T027 [US1] Add raw consolidated intervention report contract with observed fields including `FS HQ`, `REQ_ID`, intervention dates, intervention type/subtype, BTC/BTU expenses, Association Contract ID, Expected PCODE, and Actual PCODE in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T028 [US1] Add raw doctor-wise intervention report contract with HTML-XLS preamble/header-row handling and observed fields including `DR code`, doctor name, doctor segment, FS HQ, FMV amount, Contract ID, Contracted Amount, and Status in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T029 [US1] Add clean business report contract as comparison-only source with `CON_AMOUNT`, `FMVROLE`, `TYPE`, and `SUBTYPE` handling in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T030 [US1] Add historical smart-contract ERS contract and confirmed historical RCPA backfill contract for the root-level historical RCPA XLSB files in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T031 [US1] Add monthly cumulative RCPA contract with 3rd-of-month cadence, same-header expectation, cumulative coverage, six-BU sheet handling, `Pcode`, `Location`, and `PATCHNAME` requirements in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T032 [US1] Add official FX rate contract for Sri Lanka 368.90, Nepal 89, Oman 0.46, UAE 1.00, Myanmar 4300, and Malaysia 4.39 in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- [X] T033 [US1] Add MSL doctor-master contract with `Pcode`, `Location`, `Territory Id`, `Patch`, `Patchsname`, and `Legacy Code` handling in `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`

**Checkpoint**: The source contract reflects the actual planned file package and does not ask for broad unnecessary data.

---

## Phase 5: Intervention And Doctor Engagement Spine

**Trigger**: Received consolidated XLSX and doctor-wise HTML-XLS reports are profiled and source contracts pass review.

**Goal**: Normalize the operational spine that all sponsorship and ROI evidence depends on.

### Tests

- [X] T034 [P] [US2] Add synthetic raw consolidated fixture from observed columns, including FS HQ and BTC/BTU expense fields, in `ingestion/tests/fixtures/build_fixtures.py`
- [X] T035 [P] [US2] Add synthetic raw doctor-wise HTML-XLS fixture from observed row-4 headers, including FMV amount and Contracted Amount, in `ingestion/tests/fixtures/build_fixtures.py`
- [X] T036 [P] [US2] Add consolidated loader tests for intervention ID, event name, type, subtype, expenses, country, and period fields in `ingestion/tests/loaders/test_consolidated_intervention_loader.py`
- [X] T037 [P] [US2] Add doctor-wise loader tests for doctor name, P-code, doctor segment, intervention ID, FMV amount, contracted value amount, amount paid, and contract type in `ingestion/tests/loaders/test_doctor_wise_intervention_loader.py`
- [X] T038 [P] [US2] Add join/reconciliation tests between doctor-wise rows and consolidated intervention rows in `ingestion/tests/test_intervention_doctor_reconciliation.py`

### Implementation

- [X] T039 [US2] Add observed aliases to schema maps for consolidated and doctor-wise reports in `ingestion/schema_maps.py`
- [X] T040 [US2] Implement consolidated intervention loader in `ingestion/loaders/consolidated_intervention.py`
- [X] T041 [US2] Implement doctor-wise intervention loader in `ingestion/loaders/doctor_wise_intervention.py`
- [X] T042 [US2] Implement doctor-to-intervention reconciliation in `ingestion/normalizers/intervention_reconciliation.py`
- [X] T043 [US2] Persist compact canonical intervention and doctor engagement facts in `ingestion/repositories/`
- [X] T044 [US2] Add data-quality output for missing P-code, missing intervention ID, missing FMV, missing contracted value, and unjoined rows in `ingestion/report.py`
- [X] T044A [US2] Add accepted-upload-batch ingestion path that consumes `data/uploads/<batch-id>/source-manifest.json` and writes consolidated intervention plus doctor engagement facts to Supabase after validation in `ingestion/orchestrator.py` and `backend/app/services/ingestion_upload_service.py`
- [ ] T044B [US2] Add integration test proving a dashboard-uploaded accepted synthetic consolidated plus doctor-wise batch reaches canonical Supabase-facing repositories without hand-editing files in `backend/tests/api/test_ingestion_upload_api.py`

**Checkpoint**: Doctor-level engagement and event facts are queryable and auditable before sponsorship classification starts.

---

## Phase 6: FMV, Contracted Value, Expenses, And FX

**Trigger**: Doctor-wise economics and official FX fields are confirmed.

**Goal**: Make ROI economics defensible across local currencies.

### Tests

- [X] T045 [P] [US3] Add tests for local FMV, contracted value, and contract saving calculations in `ingestion/tests/test_contract_economics.py`
- [X] T046 [P] [US3] Add tests for expense category normalization from consolidated report columns in `ingestion/tests/test_expense_normalization.py`
- [X] T047 [P] [US3] Add tests for official FX conversion and missing-FX quality flags in `ingestion/tests/test_fx_conversion.py`

### Implementation

- [X] T048 [US3] Add contract economics normalizer in `ingestion/normalizers/contract_economics.py`
- [X] T049 [US3] Add expense normalizer for travel, accommodation, venue, taxi, BTU, BTC, total expenses, and observed expense headers in `ingestion/normalizers/expenses.py`
- [X] T050 [US3] Add official FX intake and conversion handling in `ingestion/normalizers/fx.py`
- [X] T051 [US3] Add compact persistence for local and converted economics fields in `ingestion/repositories/`
- [X] T052 [US3] Add FMV-vs-contracted savings to reporting output in `ingestion/report.py`
- [X] T052A [US3] Define and test Doctor ROI investment calculation rules that include source-backed sponsorship spend, paid engagement spend, contracted value, FMV, and doctor-attributable BTC/BTU/actual expenses without treating missing amounts as zero in `backend/tests/database/test_doctor_roi_view.py`
- [X] T052B [US3] Add amount-missing caveat propagation for doctors with sponsorship or engagement evidence but no reliable spend amount in `ingestion/report.py` and `backend/app/services/doctor_service.py`

**Checkpoint**: The system can distinguish doctor fee/honorarium, expenses, contracted value, FMV value, and negotiated saving.

---

## Phase 7: Sponsorship And Engagement Classification

**Trigger**: Actual label values are observed in the profiled raw reports.

**Goal**: Classify only true sponsorship as sponsorship and preserve other engagements separately.

### Tests

- [X] T053 [P] [US4] Add classifier tests for National Conference and International Conference as sponsorship in `ingestion/tests/test_sponsorship_classification.py`
- [X] T054 [P] [US4] Add classifier tests for ERS/ATS/World Asthma/World COPD as observed international subtypes or event names, not independent hard-coded sponsorship roots, in `ingestion/tests/test_sponsorship_classification.py`
- [X] T055 [P] [US4] Add classifier tests for No Fee Agreement as no-fee engagement, not sponsorship, in `ingestion/tests/test_engagement_classification.py`
- [X] T056 [P] [US4] Add classifier tests for speaker, consultancy, advisory board, and paid honorarium engagements in `ingestion/tests/test_engagement_classification.py`
- [X] T057 [P] [US4] Add tests that classification records raw label, normalized class, reason, and confidence in `ingestion/tests/test_engagement_classification.py`

### Implementation

- [X] T058 [US4] Implement deterministic sponsorship classifier in `ingestion/normalizers/sponsorship.py`
- [X] T059 [US4] Implement deterministic engagement/service classifier in `ingestion/normalizers/engagements.py`
- [X] T060 [US4] Persist sponsorship facts and non-sponsorship engagement facts compactly after observed schemas justify migrations in `database/migrations/`
- [X] T061 [US4] Add or extend materialized views for sponsorship and engagement summaries in `database/views/`
- [X] T062 [US4] Add data-quality warnings for unclassified labels, missing P-code, missing date, and missing economics fields in `ingestion/report.py`

**Checkpoint**: Sponsorship, no-fee, paid speaker, consultancy, advisory, and other services are separately analyzable.

---

## Phase 8: Historical RCPA Backfill

**Trigger**: Confirmed historical RCPA files are profiled.

**Goal**: Improve Doctor ROI baselines without overloading Supabase or hiding manual mapping caveats.

### Tests

- [X] T063 [P] [US5] Add historical RCPA fixture from confirmed historical RCPA columns, not from ERS smart-contract rows alone, in `ingestion/tests/fixtures/build_fixtures.py`
- [X] T064 [P] [US5] Add loader tests for prescription quantity, month/date, P-code, patch, territory, brand/therapy dimensions, and competitor-filter metadata in `ingestion/tests/loaders/test_historical_rcpa_loader.py`
- [X] T065 [P] [US5] Add mapping-provenance tests for system-supplied, manual/legacy, source-supplied, and unknown P-code periods in `ingestion/tests/test_rcpa_mapping_provenance.py`
- [X] T066 [P] [US5] Add storage-budget tests or script-output checks before and after historical load in `backend/tests/database/test_storage_budget_report.py`

### Implementation

- [X] T067 [US5] Implement historical RCPA loader after profiling the confirmed historical RCPA package in `ingestion/loaders/historical_rcpa.py`
- [X] T068 [US5] Implement mapping provenance logic in `ingestion/normalizers/rcpa_provenance.py`
- [X] T069 [US5] Persist compact doctor-month and doctor-brand summaries only in `ingestion/repositories/rcpa_repository.py`
- [X] T070 [US5] Refresh Doctor ROI materialized views after historical load in `database/views/`
- [X] T071 [US5] Add RCPA coverage, competitor-filter caveat, and manual-mapping caveat to ingestion reports in `ingestion/report.py`
- [X] T072 [US5] Document historical RCPA scope, manual-before-1-Nov mapping rule, and source-derived caveats in `docs/source-onboarding-playbook.md`

**Checkpoint**: Historical RCPA improves Doctor ROI context while preserving provenance and storage discipline.

---

## Phase 9: Monthly Cumulative RCPA Refresh

**Trigger**: Received standard monthly cumulative RCPA workbook is profiled.

**Goal**: Make RCPA refresh idempotent for manual uploads.

### Tests

- [X] T073 [P] [US6] Add monthly cumulative RCPA fixture from observed six-BU workbook columns, including `Pcode`, `Location`, and `PATCHNAME`, in `ingestion/tests/fixtures/build_fixtures.py`
- [X] T074 [P] [US6] Add tests that detect covered month range from cumulative files in `ingestion/tests/test_monthly_rcpa_refresh.py`
- [X] T075 [P] [US6] Add tests that rerunning the same cumulative file does not duplicate doctor-month summaries in `ingestion/tests/test_monthly_rcpa_refresh.py`
- [X] T076 [P] [US6] Add tests for partial-month and missing-P-code freshness flags in `ingestion/tests/test_monthly_rcpa_refresh.py`

### Implementation

- [X] T077 [US6] Implement monthly cumulative RCPA loader or mode in `ingestion/loaders/monthly_rcpa.py`
- [X] T078 [US6] Implement replacement/upsert behavior by doctor/month/brand grain in `ingestion/repositories/rcpa_repository.py`
- [X] T079 [US6] Add latest RCPA freshness metadata to backend response meta in `backend/app/services/`
- [X] T080 [US6] Add ingestion summary output for inserted, replaced, skipped, and duplicate rows in `ingestion/report.py`

**Checkpoint**: Monthly RCPA files can be uploaded repeatedly without corrupting Doctor ROI.

---

## Phase 9B: Initial Received-Package Preload

**Trigger**: Raw intervention, doctor-wise engagement, historical RCPA, monthly RCPA, ERS/MSL handling, FX, and classification loaders are implemented and tested.

**Goal**: Populate the dashboard from the already received `files/` package without requiring a business user to upload the current package through the dashboard.

- [X] T080A [US6] Build a preload source manifest for the July 10 `files/` package, excluding only one explicitly selected non-critical file for upload-demo validation if useful, in `docs/ingestion-runbook.md`
- [X] T080B [US6] Add CLI/backend preload command or documented invocation that ingests the received `files/` package through the same deterministic loaders used by dashboard upload in `ingestion/main.py`
- [X] T080C [US6] Add preload validation output for loaded files, held-out file, rejected files, row counts, warnings, and caveats in `ingestion/report.py`
- [X] T080D [US6] Run the preload against the received package, refresh Supabase materialized views, and record sanitized verification results in `docs/ingestion-runbook.md`
- [X] T080E [US6] Verify one held-out file can be uploaded through **Upload new data/files** and reaches the same accepted-batch ingestion path without changing loader semantics in `backend/tests/api/` and `frontend/tests/`
- [X] T080F [US6] Ingest the MSL doctor master as compact reference enrichment, upsert doctor-master coverage, and deterministically fill missing engagement P-codes only for unique country-plus-doctor-name matches in `ingestion/loaders/msl_doctor_master.py`, `ingestion/repositories/canonical_repository.py`, and `database/migrations/versions/0027_msl_doctor_master.py`

**Checkpoint**: The current dashboard is seeded from the received package, and dashboard upload remains the future-refresh and demo-validation path.

---

## Phase 10: Sponsorship And Engagement Outcome Views

**Trigger**: Engagement facts and RCPA summaries are loaded.

**Goal**: Explain Doctor ROI quadrants with deterministic post-engagement evidence.

### Tests

- [X] T081 [P] [US7] Add database/view tests for sponsorship count, paid engagement count, no-fee count, spend, FMV, contracted value, expenses, and contract saving in `backend/tests/database/test_sponsorship_outcome_views.py`
- [X] T082 [P] [US7] Add database/view tests for pre-window and post-window RCPA movement without causal wording in `backend/tests/database/test_sponsorship_outcome_views.py`
- [X] T083 [P] [US7] Add confidence and caveat tests for insufficient RCPA windows and manual mapping periods in `backend/tests/database/test_sponsorship_outcome_views.py`

### Implementation

- [X] T084 [US7] Add or extend materialized view for doctor sponsorship and engagement outcomes in `database/views/`
- [X] T085 [US7] Extend Doctor ROI backend repository queries with sponsorship, engagement, economics, and RCPA evidence in `backend/app/repositories/doctor_roi_repository.py`
- [X] T086 [US7] Extend Doctor ROI service limitations and confidence output in `backend/app/services/doctor_roi_service.py`
- [X] T087 [US7] Extend Doctor ROI schemas with sponsorship and engagement evidence contracts in `backend/app/schemas/doctor_roi.py`
- [X] T087A [US7] Add backend contract tests proving refreshed Supabase views expose updated sponsorship/engagement/RCPA evidence through Doctor ROI APIs after accepted-batch ingestion in `backend/tests/api/test_doctor_api.py`
- [X] T087B [US7] Add view/query tests proving prior sponsorship or engagement changes Doctor ROI investment metrics where amount is known and creates an explicit caveat where amount is missing in `backend/tests/database/test_sponsorship_outcome_views.py`

**Checkpoint**: The backend can answer why a doctor is in a quadrant using deterministic evidence.

---

## Phase 11: Doctor ROI Detail UI Extension

**Trigger**: Outcome API contract exists.

**Goal**: Add the evidence to the existing Doctor ROI workflow before creating a separate page.

### Tests

- [X] T088 [P] [US8] Add frontend tests for sponsorship background in the Doctor ROI detail drawer in `frontend/tests/doctor-roi.test.tsx`
- [X] T089 [P] [US8] Add frontend tests for paid engagement economics, no-fee history, FMV-vs-contracted value, expenses, RCPA movement, and caveats in `frontend/tests/doctor-roi.test.tsx`
- [X] T090 [P] [US8] Add empty and low-confidence state tests for missing sponsorship or missing RCPA evidence in `frontend/tests/doctor-roi.test.tsx`

### Implementation

- [X] T091 [US8] Extend Doctor ROI API types in `frontend/src/types/api.ts`
- [X] T092 [US8] Extend Doctor ROI detail API client handling in `frontend/src/api/doctorRoi.ts`
- [X] T093 [US8] Add sponsorship and engagement evidence sections to the Doctor ROI detail drawer in `frontend/src/pages/DoctorRoi.tsx`
- [X] T094 [US8] Add reusable economics and evidence components in `frontend/src/components/doctors/DoctorRoiComponents.tsx`
- [X] T095 [US8] Ensure wording uses association language, not causal uplift, in `frontend/src/pages/DoctorRoi.tsx`
- [X] T095A [US8] Add Doctor ROI table and detail states that distinguish true zero spend, prior sponsorship with known amount, prior sponsorship with amount unavailable, and weak doctor/P-code linkage in `frontend/src/pages/DoctorRoi.tsx`
- [X] T095B [US8] Add frontend test proving a doctor with current zero execution spend but prior sponsorship evidence no longer appears as a plain zero-investment doctor in `frontend/tests/doctor-roi.test.tsx`

**Checkpoint**: Clicking a doctor shows sponsorship, engagement, spend, and RCPA context without leaving the core Doctor ROI page.

---

## Phase 12: Territory Intelligence, Gated Add-On

**Trigger**: Territory/patch fields are confirmed or an MSL/doctor master file is provided.

**Goal**: Add territory opportunity only after core Doctor ROI is stable.

### Tests

- [X] T096 [P] [US9] Add territory field profiling tests in `ingestion/tests/test_territory_profile.py`
- [X] T097 [P] [US9] Add territory observation loader tests for country, patch, territory, period, doctor count, prescription quantity, engagement count, and spend in `ingestion/tests/loaders/test_territory_loader.py`
- [X] T098 [P] [US9] Add deterministic tests for underserved and overserved territory labels, and assert no separate self-serving label is emitted, in `backend/tests/database/test_territory_opportunity.py`

### Implementation

- [X] T099 [US9] Implement territory observation extraction from confirmed report fields in `ingestion/normalizers/territory.py`
- [X] T100 [US9] Use the received MSL doctor master as reference enrichment for doctor identity, territory metadata, and safe missing-P-code backfill while keeping source-backed report fields as transaction facts
- [X] T101 [US9] Add compact territory opportunity view in `database/views/` after data quality is sufficient
- [X] T102 [US9] Add backend territory service and route only after view validation in `backend/app/services/` and `backend/app/routers/`
- [X] T103 [US9] Add a Territory Intelligence page only after validation examples pass in `frontend/src/pages/`
- [X] T103A [US9] Expose MSL territory metadata and doctor-master coverage in Doctor ROI rows and the detail drawer without changing ROI spend math in `database/views/mv_doctor_roi.sql`, `backend/app/schemas/doctors.py`, `backend/app/services/doctor_service.py`, `frontend/src/types/api.ts`, and `frontend/src/pages/DoctorRoi.tsx`

**Checkpoint**: Territory remains a controlled add-on, not a distraction from finishing Doctor ROI.

---

## Phase 13: ExecAI Sponsorship And ROI Evidence Extension

**Trigger**: Deterministic Doctor ROI evidence services exist.

**Goal**: Let ExecAI explain evidence with grounded context.

### Tests

- [X] T104 [P] [US10] Add query planner tests for doctor quadrant explanation, sponsorship history, paid engagements, no-fee services, FMV/contracted value, RCPA trend, and territory if available in `backend/tests/ai/test_query_planner.py`
- [X] T105 [P] [US10] Add context-builder cap tests for sponsorship and engagement evidence in `backend/tests/ai/test_context_builder.py`
- [X] T106 [P] [US10] Add answer-policy tests preventing causal uplift claims in `backend/tests/ai/test_answer_policy.py`
- [X] T107 [P] [US10] Add redaction tests for doctor names, P-codes, contract IDs, and sensitive money fields if configured in `backend/tests/ai/test_redaction.py`

### Implementation

- [X] T108 [US10] Extend AI query planner topics in `backend/app/services/ai/query_planner.py`
- [X] T109 [US10] Extend context builder with compact sponsorship and engagement evidence in `backend/app/services/ai/context_builder.py`
- [X] T110 [US10] Extend answer policy with association-only language in `backend/app/services/ai/answer_policy.py`
- [X] T111 [US10] Extend response contract evidence references in `backend/app/services/ai/response_contract.py`
- [X] T112 [US10] Update ExecAI suggested prompts only after backend context passes tests in `frontend/src/components/ai/AiAssistantPanel.tsx`

**Checkpoint**: ExecAI can explain a doctor's quadrant using grounded sponsorship, engagement, spend, RCPA, and optional territory evidence.

---

## Phase 14: Business Validation And Cross-Checks

**Purpose**: Validate outputs against source-level reconciliations and selected business spot checks where available.

- [ ] T113 [P] Validate one internationally sponsored doctor against business expectation and record the sanitized result in `docs/source-onboarding-playbook.md`
- [ ] T114 [P] Validate one no-fee or prior-sponsorship doctor if present and record caveats in `docs/source-onboarding-playbook.md`
- [ ] T115 [P] Validate one FMV greater than contracted value example and record expected saving math in `docs/source-onboarding-playbook.md`
- [ ] T116 [P] Validate one cumulative RCPA rerun and record idempotency result in `docs/ingestion-runbook.md`
- [ ] T117 [P] Validate one underserved or overserved territory against source-level territory/RCPA/spend reconciliation if territory data is available in `docs/source-onboarding-playbook.md`
- [ ] T118 [P] Run storage budget report before and after historical RCPA load and record sanitized output in `docs/storage-budget.md`
- [X] T118A [P] Apply post-preload Supabase storage cleanup by removing persistent MSL staging rows, slimming doctor-brand RCPA serving storage, retaining doctor-month ROI history, and recording before/after size results in `docs/storage-budget.md`
- [ ] T119 [P] Compare selected Doctor ROI rankings against deterministic source-data reconciliation from the same dataset and record mismatches for review in `docs/source-onboarding-playbook.md`

**Checkpoint**: The system is not just technically passing tests; it agrees with business-known examples or documents why it differs.

**Current status**: Post-load storage is recorded in `docs/storage-budget.md`; a true pre-load
measurement was not captured before the first successful Supabase write, so T118 remains open for
the next large refresh. T113-T117 and T119 remain open until business-known validation examples are
provided or selected for review.

---

## Final Phase: Polish And Documentation

- [X] T120 Update `README.md` with the clarified batch-upload source strategy and sponsorship ROI scope
- [X] T121 Update `docs/architecture.md` with manual batch upload, source profiling, and deterministic evidence boundaries
- [X] T121A Update dashboard refresh documentation to state that uploaded files update visible data only after accepted-batch ingestion writes Supabase facts and refreshes materialized views in `docs/ingestion-runbook.md` and `docs/architecture.md`
- [X] T122 Update `docs/storage-budget.md` with final compact-mode decisions after RCPA profiling
- [X] T123 Update `docs/source-data-policy.md` to confirm no real workbooks, generated extracts, reports, or secrets were added to git
- [X] T124 Run focused ingestion, backend, database, frontend, and AI tests touched by this phase and record commands in `docs/ingestion-runbook.md`
- [X] T125 Review this task file to confirm no remaining task asks for SFTP, SharePoint polling, fake pages, or AI over raw workbook rows

---

## Blocked Future Work

Do not start these until their gates pass:

```text
Blocked until actual consolidated and doctor-wise reports are profiled:
  - production intervention loader
  - production doctor-wise loader
  - canonical migrations for engagement facts

Blocked until actual labels are observed:
  - final National/International sponsorship classifier
  - no-fee/speaker/consultancy/advisory classifier
  - ERS/ATS/special congress subtype mapping

Blocked until company-provided official FX list is encoded:
  - cross-market USD comparisons
  - final FMV/contracted saving KPIs

Blocked until confirmed historical RCPA package is profiled:
  - two-year Doctor ROI backfill
  - pre/post engagement movement views
  - manual mapping provenance persistence

Blocked until monthly cumulative RCPA sample is profiled:
  - recurring RCPA refresh mode
  - cumulative replacement/upsert logic

Blocked until deterministic outcome services exist:
  - Doctor ROI sponsorship evidence UI
  - ExecAI sponsorship and engagement context

Blocked until territory fields are confirmed and core Doctor ROI is stable:
  - territory opportunity view
  - territory API/UI
  - territory AI context
```

---

## Execution Order

1. Complete planning artifact refresh.
2. Build dashboard batch upload and profiling foundations.
3. Profile Abhijeet's labeled `files/` package.
4. Implement accepted-batch ingestion trigger/status so future uploaded files can move into Supabase after validation.
5. Implement intervention and doctor engagement spine.
6. Implement FMV, contracted value, expense, and FX handling.
7. Implement sponsorship and engagement classification.
8. Load historical RCPA compact summaries.
9. Implement monthly cumulative RCPA refresh.
10. Pre-ingest the already received `files/` package through CLI/backend ingestion, optionally holding out one non-critical file for upload-demo validation.
11. Refresh Supabase materialized views and dashboard-visible API responses after preload.
12. Verify the held-out or future file can refresh through dashboard upload using the same loaders.
13. Build outcome views and Doctor ROI detail evidence.
14. Extend ExecAI.
15. Add territory only after core Doctor ROI is finalized and territory fields validate.

## Final Workflow Acceptance Checklist

- [X] The already received `files/` package can be pre-ingested through CLI/backend ingestion without requiring dashboard upload.
- [X] One intentionally held-out or future file can be uploaded from the dashboard without preparing a manifest manually.
- [X] The upload result clearly identifies accepted files, rejected files, duplicate files, unknown files, and unreadable files.
- [X] Accepted uploaded files can be ingested into Supabase through deterministic loaders.
- [X] Supabase canonical facts contain intervention, doctor engagement, economics, sponsorship/engagement classification, and compact RCPA summaries.
- [X] Materialized views refresh after ingestion and expose updated Doctor ROI evidence.
- [X] Doctor ROI calculation credits sponsorship/engagement investment when the amount is source-backed.
- [X] Doctors with prior sponsorship/engagement but missing amount are shown with an explicit caveat instead of a misleading plain zero.
- [X] Doctor ROI table shows summary evidence flags; Doctor ROI detail drawer shows full doctor history.
- [X] Doctor ROI detail drawer shows MSL doctor-master coverage and territory mapping where available.
- [X] Data Quality shows upload, join, missing amount, missing P-code, and manual RCPA mapping caveats.
- [X] ExecAI answers sponsorship/engagement/RCPA questions from refreshed backend evidence only.
- [X] No raw workbook rows, generated upload batches, secrets, or generated reports are committed to git.

## Notes

- All real workbooks stay out of git.
- CLI/backend preload is the intended initial-load mechanism for the already received `files/` package.
- Manual dashboard batch upload is the intended future-refresh mechanism after the preload.
- Uploaded files must update dashboard data only through the accepted-batch ingestion path: validate, ingest to Supabase, refresh materialized views, then refresh frontend API data.
- Preloaded files must update dashboard data only through the same deterministic loaders, Supabase facts, and materialized-view refresh path.
- SFTP and SharePoint polling are explicitly out of scope.
- National and International Conference are the only default sponsorship labels.
- No-fee, speaker, consultancy, advisory, and paid honorarium are engagement evidence, not sponsorship by default.
- FMV amount and contracted value amount are critical ROI economics fields.
- Official FX rates have been provided and must be used as the only FX source; no internet-rate fallback is allowed.
- Monthly RCPA is cumulative and must be loaded idempotently.
- Historical RCPA scope is confirmed; ERS remains a separate historical smart-contract/conference input.
- Territory is valuable but secondary to finishing the core Doctor ROI product.
