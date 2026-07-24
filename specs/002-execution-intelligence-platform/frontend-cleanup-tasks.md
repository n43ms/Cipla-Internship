# Tasks: Frontend Cleanup and Executive Positioning

**Input**: Frontend optimization plan from current chat, plus `plan.md`, `spec.md`, `contracts/dashboard-data-contract.md`, and `quickstart.md`.

**Purpose**: Make the Cipla EMEU dashboard feel more executive-grade by reducing warning noise, keeping pages stable during sort/refetch, renaming the assistant to ExecAI, strengthening the intro-page business story, and updating README positioning.

**Tests**: Required for warning disclosure behavior, table refetch behavior, ExecAI copy, intro-page copy, and README-safe branding changes where practical.

**Organization**: Tasks are grouped by independently testable frontend user story. The implementation should keep backend contracts unchanged and preserve all data-quality transparency required by the project constitution.

## Phase 1: Setup and Audit

**Purpose**: Establish the exact UI surface area before changing shared components.

- [X] T001 Audit all visible warning, limitation, freshness, FX, no-RCPA, and AI labels in `frontend/src/`, `frontend/tests/`, and `README.md`
- [X] T002 Audit React Query loading states for sort, pagination, filter, and detail-drawer refetches in `frontend/src/pages/ExecutionMatrix.tsx`, `frontend/src/pages/BudgetUtilization.tsx`, and `frontend/src/pages/DoctorRoi.tsx`
- [X] T003 Verify current test-file and test-definition counts with `rg` or test runner output before using exact reliability numbers in `frontend/src/App.tsx` or `README.md`
- [X] T004 Document the final copy source of truth for platform metrics and ExecAI naming in `specs/002-execution-intelligence-platform/frontend-cleanup-tasks.md`

**Copy source of truth**:

- Assistant name: ExecAI.
- AI technical description: embedded structured RAG assistant with query planning, FastAPI/PostgreSQL evidence retrieval, Gemini synthesis, deterministic fallback, redaction, and evidence validation.
- Product positioning: Cipla EMEU/PBP Doctor ROI and Execution Intelligence platform.
- Business scope copy to use when user-confirmed: 50+ regional investment decisions per month across 6 EMEU/PBP countries.
- Engineering scale copy to use: 1M+ raw rows normalized into auditable PostgreSQL KPI views; source-backed measured dry run in `docs/ingestion-runbook.md` recorded 1,179,273 rows seen and 423,693 rows loaded.
- Test count policy: current regex audit found 62 files/artifacts under test folders and 117 test definitions. Do not use unverified 78 files / 153 definitions in UI or README unless re-confirmed by a later test-count audit.

**Checkpoint**: All risky copy and behavior surfaces are known before implementation starts.

---

## Phase 2: Foundational UI Primitives

**Purpose**: Build reusable components so warning and loading changes do not become page-specific one-offs.

- [X] T005 [P] Create reusable compact warning disclosure component in `frontend/src/components/common/WarningDisclosure.tsx`
- [X] T006 [P] Create reusable table refetch overlay component in `frontend/src/components/common/TableLoadingOverlay.tsx`
- [X] T007 [P] Add warning severity, warning group, and disclosure prop types in `frontend/src/components/common/WarningDisclosure.tsx`
- [X] T008 [P] Add table overlay props for `isFetching`, `label`, `preserveRows`, and `aria-live` behavior in `frontend/src/components/common/TableLoadingOverlay.tsx`
- [X] T009 Update `frontend/src/components/common/DataStateComponents.tsx` so `DataFreshnessBanner` renders a compact one-line status with expandable warnings instead of full amber panels
- [X] T010 Update `frontend/src/components/common/DataStateComponents.tsx` so `LimitationList` remains reusable inside the disclosure body without controlling panel layout
- [X] T011 Add tests for collapsed, expanded, no-warning, keyboard, and screen-reader behavior in `frontend/tests/data-quality-states.test.tsx`

**Checkpoint**: Shared warning and table-loading primitives are ready for page adoption.

---

## Phase 3: User Story 1 - Subtle Warnings Without Hiding Trust Signals (Priority: P1)

**Goal**: Replace loud yellow warning blocks with compact, expandable warning panels while keeping data-quality limitations visible and auditable.

**Independent Test**: Load each dashboard page with warning-bearing mocked metadata and verify the page shows one compact warning row, expands details on click, and still exposes all underlying limitation text.

### Tests for User Story 1

- [X] T012 [P] [US1] Update freshness-warning tests for compact disclosure behavior in `frontend/tests/data-quality-states.test.tsx`
- [X] T013 [P] [US1] Update execution warning tests for source derivation and weak-match disclosure in `frontend/tests/execution-governance.test.tsx`
- [X] T014 [P] [US1] Update budget warning tests for FX and BTU/BTC disclosure in `frontend/tests/budget-utilization.test.tsx`
- [X] T015 [P] [US1] Update doctor ROI warning tests for no-RCPA and baseline limitation disclosure in `frontend/tests/doctor-roi.test.tsx`
- [X] T016 [P] [US1] Update Data Quality page tests to keep detailed audit warnings visible in `frontend/tests/data-quality-page.test.tsx`

### Implementation for User Story 1

- [X] T017 [US1] Replace `QualityPanel` large warning block with `WarningDisclosure` in `frontend/src/pages/ExecutionMatrix.tsx`
- [X] T018 [US1] Replace `FxWarning` amber card with `WarningDisclosure` in `frontend/src/components/budget/BudgetComponents.tsx`
- [X] T019 [US1] Replace Doctor ROI informational cyan block with subtle disclosure or neutral info panel in `frontend/src/pages/DoctorRoi.tsx`
- [X] T020 [US1] Ensure app-level freshness banner uses compact disclosure on non-quality pages in `frontend/src/App.tsx`
- [X] T021 [US1] Keep the Data Quality page as the expanded audit surface while aligning its warning styling in `frontend/src/pages/DataQuality.tsx`
- [X] T022 [US1] Remove duplicated warning copy where app-level and page-level metadata repeat the same limitations in `frontend/src/App.tsx` and `frontend/src/pages/*`

**Checkpoint**: Warning states are quieter by default, but no warning data is removed from the UI.

---

## Phase 4: User Story 2 - Stable Page Shell During Table Sort and Refetch (Priority: P2)

**Goal**: Sorting or paginating a table must not blank the entire page. Existing cards, charts, filters, and previous table rows should remain visible while only the affected table shows refetch feedback.

**Independent Test**: Sort each table and verify the page title, filters, KPI cards, charts, and previous rows remain mounted while the table shows a contained loading indicator.

### Tests for User Story 2

- [X] T023 [P] [US2] Add execution table refetch stability test in `frontend/tests/execution-governance.test.tsx`
- [X] T024 [P] [US2] Add workflow table refetch stability test in `frontend/tests/execution-governance.test.tsx`
- [X] T025 [P] [US2] Add budget table refetch stability test in `frontend/tests/budget-utilization.test.tsx`
- [X] T026 [P] [US2] Add doctor ROI table refetch stability test in `frontend/tests/doctor-roi.test.tsx`

### Implementation for User Story 2

- [X] T027 [US2] Split initial page loading from table query refetch state in `frontend/src/pages/BudgetUtilization.tsx`
- [X] T028 [US2] Add previous-data or placeholder-data behavior for budget summary table queries in `frontend/src/pages/BudgetUtilization.tsx`
- [X] T029 [US2] Pass contained table fetching state into `BudgetGapTable` in `frontend/src/pages/BudgetUtilization.tsx` and `frontend/src/components/budget/BudgetComponents.tsx`
- [X] T030 [US2] Split initial page loading from doctor ROI table refetch state in `frontend/src/pages/DoctorRoi.tsx`
- [X] T031 [US2] Add previous-data or placeholder-data behavior for doctor ROI table queries in `frontend/src/pages/DoctorRoi.tsx`
- [X] T032 [US2] Pass contained table fetching state into `DoctorRoiTable` in `frontend/src/pages/DoctorRoi.tsx` and `frontend/src/components/doctors/DoctorRoiComponents.tsx`
- [X] T033 [US2] Split execution page loading into initial required queries and independent table refetch queries in `frontend/src/pages/ExecutionMatrix.tsx`
- [X] T034 [US2] Add previous-data or placeholder-data behavior for execution event and workflow request queries in `frontend/src/pages/ExecutionMatrix.tsx`
- [X] T035 [US2] Pass contained fetching state into `EventMatrixTable` and `WorkflowRequestTable` in `frontend/src/pages/ExecutionMatrix.tsx`
- [X] T036 [US2] Ensure sort header clicks remain responsive and do not cause layout shift in `frontend/src/components/common/SortableTable.tsx`

**Checkpoint**: All table sort and pagination operations preserve page context and show only contained loading states.

---

## Phase 5: User Story 3 - ExecAI Product Naming and Assistant Polish (Priority: P3)

**Goal**: Rename visible "Grounded AI" copy to ExecAI while preserving the accurate structured-RAG explanation.

**Independent Test**: Search the frontend and README for visible "Grounded AI" labels and verify all user-facing references are replaced with ExecAI.

### Tests for User Story 3

- [X] T037 [P] [US3] Update AI assistant label tests from Grounded AI to ExecAI in `frontend/tests/ai-assistant.test.tsx`
- [X] T038 [P] [US3] Add app-shell assertion for ExecAI nav or assistant entry text in `frontend/tests/app-shell.test.tsx`

### Implementation for User Story 3

- [X] T039 [US3] Rename assistant drawer button, aria labels, drawer title, and workflow label to ExecAI in `frontend/src/components/ai/AiAssistantPanel.tsx`
- [X] T040 [US3] Rewrite assistant description as structured RAG with query planning, PostgreSQL/FastAPI evidence retrieval, Gemini synthesis, fallback, redaction, and evidence validation in `frontend/src/components/ai/AiAssistantPanel.tsx`
- [X] T041 [US3] Replace nav subtitle "Grounded AI" copy with ExecAI copy in `frontend/src/App.tsx`
- [X] T042 [US3] Replace README architecture and feature references from grounded AI assistant to ExecAI structured RAG assistant in `README.md`
- [X] T043 [US3] Confirm backend route names, schema names, and module names stay unchanged in `backend/app/routers/ai.py` and `backend/app/services/ai/`

**Checkpoint**: ExecAI is the visible product name; backend technical boundaries remain stable.

---

## Phase 6: User Story 4 - Executive Intro Page Positioning (Priority: P4)

**Goal**: Make the intro page explicitly communicate the business objective, Doctor ROI priority, platform scale, dashboard capabilities, ExecAI, and reliability story.

**Independent Test**: Render the intro page and verify it describes the platform rather than only the builder, uses verified or clearly confirmed metrics, and keeps text readable on desktop and mobile.

### Tests for User Story 4

- [X] T044 [P] [US4] Add intro-page business objective tests in `frontend/tests/app-shell.test.tsx`
- [X] T045 [P] [US4] Add responsive text fit smoke test for intro-page metric panels in `frontend/tests/app-shell.test.tsx`

### Implementation for User Story 4

- [X] T046 [US4] Refactor `EntryScreen` copy into business-first platform messaging in `frontend/src/App.tsx`
- [X] T047 [US4] Add intro-page stat or capability cards for Doctor ROI, execution governance, budget control, workflow bottlenecks, data quality, and ExecAI in `frontend/src/App.tsx`
- [X] T048 [US4] Use the platform wording "Doctor ROI and Execution Intelligence platform for Cipla EMEU/PBP" in `frontend/src/App.tsx`
- [X] T049 [US4] Include "50+ regional investment decisions/month", "6 countries", and "1M+ raw rows" only after confirming these numbers are intended business claims in `frontend/src/App.tsx`
- [X] T050 [US4] Use measured repo/test counts or omit exact test-count numbers if `78 files` and `153 definitions` are not confirmed in `frontend/src/App.tsx`
- [X] T051 [US4] Reduce repeated gradient text and establish clearer type hierarchy in `frontend/src/App.tsx` and `frontend/src/styles.css`
- [X] T052 [US4] Keep Cipla branding visible but avoid logo/background treatments that overpower the platform content in `frontend/src/App.tsx`

**Checkpoint**: The intro page reads like a serious executive analytics product and is visually stable across viewport sizes.

---

## Phase 7: User Story 5 - README Product and Achievement Positioning (Priority: P5)

**Goal**: Rewrite the README so the repo clearly communicates the business objective, architecture, core features, ExecAI, confidentiality constraints, and validation workflow.

**Independent Test**: A reviewer can understand in under one minute what business problem the system solves, how the architecture works, and how to run or validate it.

### Tests for User Story 5

- [X] T053 [P] [US5] Add README copy check for ExecAI and Doctor ROI terms using a simple text assertion command in `README.md`

### Implementation for User Story 5

- [X] T054 [US5] Rewrite README title and opening description around Cipla EMEU Doctor ROI and Execution Intelligence in `README.md`
- [X] T055 [US5] Add business objective section covering doctor investment decisions, dark-horse opportunities, execution tracking, budget governance, workflow bottlenecks, and data quality in `README.md`
- [X] T056 [US5] Add architecture section with local Excel/XLSB ingestion, Python ETL, Supabase PostgreSQL, FastAPI, React dashboard, and ExecAI in `README.md`
- [X] T057 [US5] Add feature section for ROI quadrants/tables, execution matrix, budget utilization, workflow governance, intervention mix, warnings, drilldowns, and structured RAG querying in `README.md`
- [X] T058 [US5] Add data trust and confidentiality section covering local raw files, gitignored generated extracts, backend-only secrets, and no frontend Supabase/AI-provider access in `README.md`
- [X] T059 [US5] Add validation section with frontend test/build commands and existing full-stack validation commands in `README.md`
- [X] T060 [US5] Add metrics note that separates measured engineering-volume metrics from user-confirmed business-impact metrics in `README.md`

**Checkpoint**: README positioning matches the final app narrative and does not overclaim unverified metrics.

---

## Phase 8: Polish and Cross-Cutting Validation

**Purpose**: Confirm the cleanup is consistent, accessible, responsive, and safe to demo.

- [X] T061 [P] Run text search to confirm no visible Grounded AI copy remains in `frontend/src/`, `frontend/tests/`, and `README.md`
- [X] T062 [P] Run text search to confirm warning disclosure copy does not hide data-quality terminology in `frontend/src/`
- [X] T063 [P] Run `npm test --prefix frontend` and record failures or pass result in `specs/002-execution-intelligence-platform/frontend-cleanup-tasks.md`
- [X] T064 [P] Run `npm run build --prefix frontend` and record failures or pass result in `specs/002-execution-intelligence-platform/frontend-cleanup-tasks.md`
- [X] T065 Manually inspect desktop and mobile layouts for the intro page, Execution, Budget, Doctor ROI, Data Quality, and ExecAI drawer in `frontend/src/App.tsx`
- [X] T066 Update any stale frontend snapshots or assertions caused only by intentional copy/layout changes in `frontend/tests/`
- [X] T067 Update `specs/002-execution-intelligence-platform/quickstart.md` if warning behavior or ExecAI naming changes expected frontend validation steps

**Validation results**:

- `npm test --prefix frontend`: passed, 8 test files and 18 tests. Existing React act warnings remain in `frontend/tests/phase5-7-pages.test.tsx`, but the suite exits successfully with 100% pass rate.
- `npm run build --prefix frontend`: passed in 9.85s. Vite emitted the existing Node experimental type-stripping warning, then built successfully.
- `python -m pytest backend/tests/`: passed, 98/98 tests passing including 7 auth contract tests in `test_auth.py`.
- Browser smoke check: passed at `1440x900` and `390x844` against `http://127.0.0.1:5173`; intro title, ExecAI, inline email/passcode form, and navigation dropdowns were visible, with no horizontal overflow and no console errors.
- Text search: no visible `Grounded AI`/`grounded AI` copy remains in `frontend/src`, `frontend/tests`, `README.md`, quickstart, plan, task docs, or AI service docs outside this completed task checklist's historical wording.

---

## Phase 9: Authentication & Access Control Gate (Completed)

**Purpose**: Implement dual-tier authentication (`adityaxnema@gmail.com` -> `"Guddan@1205"`, `@cipla.com` -> `"AdityaIntern@2026"`) with strict single-node replacement on the landing page while preserving 100% of header navigation dropdowns, logos, and UI layout.

- [X] T068 [P] Implement Backend Auth Router exposing `POST /api/auth/login` and `POST /api/auth/change-password` in `backend/app/routers/auth.py`
- [X] T069 [P] Write unit and contract tests for authentication and Master Admin immutability in `backend/tests/api/test_auth.py` (7 passing)
- [X] T070 Register auth router in `backend/app/routers/__init__.py`
- [X] T071 Substitute ONLY lines 234-245 (the static entrance button node) in `frontend/src/App.tsx` with inline Email + Passcode login form linking to `POST /api/auth/login` while preserving 100% of header styling, logo badge (`CiplaLogoPlaceholder`), navigation dropdowns (`PRIMARY_PAGES`, `OPERATIONS_PAGES`), and `UtilityMenu`
- [X] T072 Create automated PowerShell validation script `scripts/validate_auth.ps1`
- [X] T073 Update frontend test suite assertions in `frontend/tests/` to support `/enter dashboard|click to continue/i` button matchers


---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 Setup and Audit**: No dependencies.
- **Phase 2 Foundational UI Primitives**: Depends on Phase 1.
- **US1 Subtle Warnings**: Depends on Phase 2.
- **US2 Stable Sort and Refetch**: Depends on Phase 2 and can run in parallel with US1 after primitives exist.
- **US3 ExecAI Naming**: Can run after Phase 1 and does not depend on US1 or US2.
- **US4 Intro Page Positioning**: Depends on Phase 1 metric verification and can run after US3 copy direction is settled.
- **US5 README Positioning**: Depends on US3 naming and Phase 1 metric verification.
- **Phase 8 Polish**: Depends on all selected user stories.

### User Story Dependencies

- **US1**: Requires `WarningDisclosure`.
- **US2**: Requires `TableLoadingOverlay` and React Query loading audit.
- **US3**: Independent of warning/loading work.
- **US4**: Depends on metric verification to avoid unsubstantiated claims.
- **US5**: Depends on final visible product terms.

### Parallel Opportunities

- T005-T008 can be implemented in parallel after T001-T004.
- T012-T016 can be written in parallel because they touch separate test scopes.
- T023-T026 can be written in parallel because they touch page-specific test cases.
- T037-T038 can run in parallel with T044-T045.
- T054-T060 can be drafted in parallel with UI changes once the final claims are verified.

---

## Implementation Strategy

### MVP Cleanup First

1. Complete Phase 1 audit.
2. Build `WarningDisclosure` and `TableLoadingOverlay`.
3. Implement US1 and US2 because they directly affect dashboard usability.
4. Validate with frontend tests and build.

### Branding and Positioning Increment

1. Implement US3 ExecAI naming.
2. Implement US4 intro-page positioning.
3. Implement US5 README positioning.
4. Re-run text search, tests, and build.

### Quality Bar

- Keep route handlers, backend schemas, and API contracts unchanged.
- Do not remove warnings; make them easier to scan and expand.
- Do not use unverified business metrics as hard facts unless the user confirms them.
- Preserve loading, error, empty, stale-data, weak-match, missing-FX, and no-RCPA states.
- Prefer reusable components over page-specific styling.
- Keep UI text readable on mobile and desktop without text overlap or layout shift.
