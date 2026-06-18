# Phase 5-7 Holistic Review Issues

Review scope: Phase 5 Budget Utilization, Phase 6 Doctor ROI, and Phase 7 Data Quality against `tasks.md`, `finalplan.md`, the current backend/frontend implementation, and the live Supabase analytical views.

Review date: 2026-06-19

## Verdict

Phase 5-7 are implemented enough to render and return API data, but they are not yet production-grade or fully aligned with the promised architecture. The biggest gaps are not missing files; they are semantic correctness, contract drift, filter incompleteness, insufficient real-data tests, and UI drilldowns that do not fully expose uncertainty.

Do not proceed to Phase 8 AI until these issues are resolved. AI must only summarize deterministic, trustworthy service outputs. If budget, ROI, and data-quality semantics are still ambiguous, the AI layer will amplify bad conclusions.

## Evidence Snapshot

- Alembic revision in Supabase: `0018_data_quality_view`
- Materialized view counts:
  - `mv_budget_utilization`: 3,716 rows
  - `mv_doctor_roi`: 26,563 rows
  - `mv_data_quality`: 1 row
- Current quality metrics:
  - source files: 8 of 8 loaded
  - rows seen: 1,179,273
  - rows loaded: 423,654
  - rows skipped: 42
  - validation warnings: 9
  - match coverage: 61.38%
  - Pcode coverage: 100%
  - RCPA coverage: 99.26%
  - missing FX rows: 1,555
  - BTU/BTC reconciliation issues: 88
  - spend without plan: 2,334
  - plan without spend: 763
  - unmatched events in primary Phase 4 scope: 158
- Budget matching risk:
  - primary-scope matched plan/request rows: 460
  - distinct matched plan events: 45
  - plan events linked to multiple requests: 34
- Currency mix in primary-scope budget rows:
  - LKR official: 363 request rows, USD actual spend populated
  - NPR missing FX: 166 request rows, USD actual spend is zero/null-equivalent
- Targeted backend tests passed: `backend/tests/api/test_phase5_7_api.py` and `backend/tests/database/test_budget_doctor_data_quality_views.py`
- Targeted frontend test passed: `frontend/tests/phase5-7-pages.test.tsx`
- Frontend test emits Recharts zero-width/zero-height warnings, indicating layout/test-container fragility.

## P0 Blockers Before Phase 8

### PH5-001: Fix budget gap double-counting across multi-request plan matches

Problem: `mv_budget_utilization` emits one row per matched plan/request pair. The budget summary deduplicates `planned_budget_usd`, but it still sums `unspent_gap_usd` and `overrun_amount_usd` directly from row-level matches. When one plan event maps to multiple requests, the same planned budget can be compared repeatedly against each request, creating misleading gaps.

Evidence:
- 460 primary-scope matched plan/request rows represent only 45 distinct plan events.
- 34 plan events have more than one matched request.

Files:
- `database/views/mv_budget_utilization.sql`
- `backend/app/repositories/budget_repository.py`
- `backend/tests/database/test_budget_doctor_data_quality_views.py`

Tasks:
- [ ] Define the production budget grain explicitly: event-level, request-level, and summary-level.
- [ ] Add a grouped budget view or CTE that rolls matched requests to `plan_event_id` before calculating event-level unspent/overrun.
- [ ] Keep request-level rows for drilldown, but mark them as request evidence rather than independent budget gaps.
- [ ] Update budget summary to compute unspent/overrun from grouped event/request aggregates, not raw row pairs.
- [ ] Add a database fixture with one plan event matched to multiple requests and assert no duplicated planned budget gap.

Acceptance criteria:
- One plan event matched to N requests contributes its planned budget once to event-level gap metrics.
- Request-level drilldown still shows all N requests.
- Summary cards and chart totals reconcile to grouped detail rows.

### PH5-002: Stop aggregating mixed local currencies as one local total

Problem: Budget summary returns `actual_total_spend_local`, `confirmed_contracted_amount_local`, and other local fields as a single number even when multiple currencies are present. This is not financially valid. The current database contains both LKR and NPR rows in primary scope, and NPR has missing FX.

Files:
- `database/views/mv_budget_utilization.sql`
- `backend/app/schemas/budget.py`
- `backend/app/services/budget_service.py`
- `backend/app/repositories/budget_repository.py`
- `frontend/src/components/budget/BudgetComponents.tsx`
- `frontend/src/pages/BudgetUtilization.tsx`

Tasks:
- [ ] Return local totals grouped by `currency_code` instead of a single cross-currency local total.
- [ ] Keep USD totals only for rows with official/provisional FX.
- [ ] Exclude missing-FX currencies from USD totals and expose a separate `localOnlySpendByCurrency` section.
- [ ] In the frontend, show USD cards only for normalized rows and local-only cards/tables for missing-FX rows.
- [ ] Add tests for LKR official + NPR missing-FX mixed responses.

Acceptance criteria:
- The UI never displays a combined local total across LKR, NPR, or other currencies.
- Missing-FX spend is visible, but not silently included in USD comparisons.
- LKR uses the official company rate of `1 USD = 310 LKR`.

### PH5-003: Make budget filters real, not only backend query parameters

Problem: `/api/budget/summary` supports `country`, `month`, and `includeOutOfScope`, but `BudgetUtilization.tsx` always calls `getBudgetSummary()` with no filters. This violates the Phase 5 independent test requirement for selected country/month budget analysis.

Files:
- `frontend/src/pages/BudgetUtilization.tsx`
- `frontend/src/api/budget.ts`
- `frontend/src/store/filterStore.ts` if introduced now, otherwise Phase 9 global filter work must be pulled forward

Tasks:
- [ ] Add country/month/filter controls to Budget Utilization or integrate with a shared filter store.
- [ ] Include filters in React Query keys.
- [ ] Show active filters in page header or metadata.
- [ ] Add frontend tests proving the page calls `/api/budget/summary?country=...&month=...`.

Acceptance criteria:
- Users can inspect budget for a selected country/month.
- Query keys change when filters change.
- Empty states are scoped to selected filters.

### PH6-001: Add missing Doctor ROI filters required by the plan

Problem: The plan and dashboard contract require doctor ROI filtering by country, month range, brand, speciality, doctor class, and ROI segment. The backend currently supports only `country`, `segment`, and `quadrant`. The frontend exposes no filters and always loads the first 50 rows.

Files:
- `backend/app/routers/doctors.py`
- `backend/app/repositories/doctor_repository.py`
- `backend/app/services/doctor_service.py`
- `database/views/mv_doctor_roi.sql`
- `frontend/src/api/doctors.ts`
- `frontend/src/pages/DoctorRoi.tsx`
- `frontend/src/components/doctors/DoctorRoiComponents.tsx`
- `specs/002-execution-intelligence-platform/contracts/openapi.yaml`

Tasks:
- [ ] Decide whether month filtering should apply to engagement window, RCPA window, or both; document it.
- [ ] Add backend filters for `monthStart`, `monthEnd`, `brand`, `speciality`, `doctorClass`, and `roiSegment`.
- [ ] Align parameter names: use `roiSegment` externally, not `segment`, unless the contract is deliberately changed.
- [ ] Add frontend filter controls and include them in query keys.
- [ ] Add database/API tests for every filter and combinations that return empty results.

Acceptance criteria:
- Doctor ROI can answer "for this market, period, brand/speciality/class, which doctors are opportunities?"
- API, OpenAPI, frontend types, and page controls use the same parameter names.

### PH6-002: Fix doctor spend allocation grain before using ROI as decision support

Problem: `mv_doctor_roi` allocates request spend across actual-attendance Pcodes. It counts distinct Pcodes as the denominator, but the allocation joins raw `request_doctors` rows. If a future request contains duplicate actual rows for the same Pcode, spend can be allocated more than once to that doctor. Current live data has zero duplicate actual Pcode groups, but production logic should be safe by construction.

Files:
- `database/views/mv_doctor_roi.sql`
- `ingestion/loaders/request_doctors.py`
- `ingestion/validators/doctor_quality.py`
- `backend/tests/database/test_budget_doctor_data_quality_views.py`

Tasks:
- [ ] Deduplicate actual attendance to `execution_request_id + country_id + pcode_normalized` before spend allocation.
- [ ] Preserve raw duplicate rows in `request_doctors` for audit, but allocate spend from a deduped CTE.
- [ ] Add a test fixture with duplicated actual Pcode rows and assert spend is allocated once.

Acceptance criteria:
- Doctor spend allocation is idempotent to duplicate attendance tokens.
- Data quality can still report duplicate raw doctor entries separately.

### PH6-003: Expose unallocated doctor spend caused by missing or invalid Pcodes

Problem: ROI only allocates spend to actual attended doctors with parsed Pcodes. If future rows have actual attendees without valid Pcodes, that spend disappears from doctor ROI instead of appearing as unallocated spend. Current live actual rows are all parsed, but the architecture must handle bad workbooks.

Files:
- `database/views/mv_doctor_roi.sql`
- `database/views/mv_data_quality.sql`
- `backend/app/schemas/data_quality.py`
- `frontend/src/pages/DataQuality.tsx`

Tasks:
- [ ] Add `unallocated_doctor_spend_local/usd` and `actual_attendance_missing_pcode_count` to the quality layer.
- [ ] Add a Data Quality section for doctor ROI allocation loss.
- [ ] Add tests for missing actual Pcode rows.

Acceptance criteria:
- No spend is silently excluded from ROI.
- Users can see when doctor ROI is incomplete because attendance Pcodes were missing.

### PH7-001: Fix validation error scoping to latest run per file

Problem: `mv_data_quality.validation_latest` joins validation errors to latest file runs by `source_file_id` only, not by the exact latest `ingestion_run_id`. `DataQualityRepository.validation_issues()` also reads the latest five ingestion runs globally. This can overcount or display stale historical validation issues after reruns.

Files:
- `database/views/mv_data_quality.sql`
- `backend/app/repositories/data_quality_repository.py`
- `backend/tests/database/test_budget_doctor_data_quality_views.py`
- `backend/tests/api/test_phase5_7_api.py`

Tasks:
- [ ] Include `ingestion_run_id` in `latest_file_runs`.
- [ ] Join validation errors by both `source_file_id` and latest file-level `ingestion_run_id`.
- [ ] Change validation drilldown query to latest run per file, not latest five global runs.
- [ ] Add a test where an old warning is fixed in a later run and no longer appears in current quality output.

Acceptance criteria:
- Data Quality shows current validation issues only, while audit history remains queryable separately.
- Re-running a corrected file reduces current warning/error counts.

### PH7-002: Add unmatched record drilldown by source and reason

Problem: Phase 7 requires unmatched records by source and drilldowns. The current Data Quality page shows only `unmatchedEventCount`. It does not expose unmatched records, source type, reason, candidate match, or remediation category.

Files:
- `database/views/mv_data_quality.sql`
- `database/views/mv_unmatched_events.sql`
- `backend/app/repositories/data_quality_repository.py`
- `backend/app/schemas/data_quality.py`
- `frontend/src/pages/DataQuality.tsx`

Tasks:
- [ ] Add `/api/data-quality/unmatched` or include paginated unmatched records in the data-quality response.
- [ ] Group unmatched counts by source type and reason code.
- [ ] Render an unmatched records table with source, country, month, event name, reason, candidate match, confidence, and source row reference.
- [ ] Add frontend tests for unmatched records table.

Acceptance criteria:
- Users can tell whether unmatched records are planner-only, request-only, snapshot-only, out-of-scope, or name mismatch.
- Data Quality supports operational remediation, not just a warning count.

### PH7-003: Complete required data-quality metrics from the contract

Problem: `mv_data_quality` does not expose several fields promised in `dashboard-data-contract.md`: unmatched records by source, Excel serial month parse count, static FX seed date, and explicit official LKR rate status/date. It also does not expose file-level rows loaded/skipped by workbook.

Files:
- `database/views/mv_data_quality.sql`
- `backend/app/schemas/data_quality.py`
- `backend/app/services/data_quality_service.py`
- `frontend/src/pages/DataQuality.tsx`
- `specs/002-execution-intelligence-platform/contracts/dashboard-data-contract.md`

Tasks:
- [ ] Add serial month parse count from ingestion summaries or validation/profile JSON.
- [ ] Add static FX seed date and official LKR 310 status from `exchange_rates`.
- [ ] Add file-level row counts and statuses from latest file runs.
- [ ] Add unmatched by source and reason breakdown.
- [ ] Update API schema and UI.

Acceptance criteria:
- Every required Data Quality contract field is returned by the API and visible or drillable in the UI.

## P1 High Priority Architecture Issues

### PH5-004: Centralize FX policy instead of hardcoding conversion behavior in ingestion only

Problem: LKR conversion is implemented in ingestion normalization, while the database also has `exchange_rates`. The plan expects seeded FX governance. Production code should use one source of truth for official/provisional/missing rates.

Files:
- `ingestion/normalizers/money.py`
- `ingestion/constants.py`
- `database/seeds/exchange_rates_static.sql`
- `database/views/mv_budget_utilization.sql`
- `docs/data-dictionary.md`

Tasks:
- [ ] Document the current allowed static FX rates in one place.
- [ ] Make ingestion use shared constants generated from seeds or explicitly validate seed parity.
- [ ] Add a test that LKR is official at 310 and non-seeded currencies are missing, not guessed.

Acceptance criteria:
- Changing FX policy does not require hunting across ingestion, SQL, and docs.

### PH5-005: Add budget row pagination and sortable drilldown

Problem: Budget repository hard-limits rows to 100. The UI does not expose pagination or sorting. For 3,716 budget rows, this hides data without telling users.

Files:
- `backend/app/repositories/budget_repository.py`
- `backend/app/schemas/budget.py`
- `backend/app/routers/budget.py`
- `frontend/src/components/budget/BudgetComponents.tsx`

Tasks:
- [ ] Add `page`, `pageSize`, `sort`, and `status` filters for budget rows.
- [ ] Return total row count separately from summary.
- [ ] Add table pagination and visible "showing X of Y" state.

Acceptance criteria:
- The budget drilldown is complete and navigable, not capped invisibly.

### PH6-004: Replace arbitrary doctor identity aggregation with deterministic precedence

Problem: `mv_doctor_roi` uses `max()` over doctor names/classes/specialities from RCPA and attendance. That is lexicographic, not business-correct. The displayed doctor name/class may be arbitrary.

Files:
- `database/views/mv_doctor_roi.sql`
- `docs/data-dictionary.md`

Tasks:
- [ ] Define precedence: latest RCPA doctor master, latest attendance, or most recent non-null value.
- [ ] Implement deterministic ordering with `distinct on` or window functions.
- [ ] Add tests where older and newer doctor names differ.

Acceptance criteria:
- Doctor profile fields are stable and explainable.

### PH6-005: Separate "dark horse" from already-engaged low-spend high-prescription doctors

Problem: `dark_horse_flag` is true for any low-spend/high-prescription doctor, including already-engaged doctors. The business story asks for missed opportunities and high-prescribing unengaged doctors. Already-engaged doctors should be labeled differently from unengaged dark horses.

Files:
- `database/views/mv_doctor_roi.sql`
- `backend/app/schemas/doctors.py`
- `frontend/src/components/doctors/DoctorRoiComponents.tsx`

Tasks:
- [ ] Define dark horse as high-prescribing and unengaged or minimally engaged.
- [ ] Add separate flags such as `high_value_engaged_flag` and `dark_horse_unengaged_flag`.
- [ ] Update UI labels to avoid implying all low-effort/high-reward doctors are missed opportunities.

Acceptance criteria:
- Doctor ROI distinguishes retention/value from acquisition/missed-opportunity targets.

### PH6-006: Make RCPA coverage periods explicit in Doctor ROI

Problem: RCPA data ends before FY27 execution months. Doctor ROI joins engagement and RCPA, but the page does not make the period mismatch explicit at row level. Users may assume prescriptions are from the same execution period.

Files:
- `database/views/mv_doctor_roi.sql`
- `backend/app/schemas/doctors.py`
- `frontend/src/pages/DoctorRoi.tsx`
- `frontend/src/components/doctors/DoctorRoiComponents.tsx`

Tasks:
- [ ] Add first/last RCPA month per doctor.
- [ ] Add engagement period and RCPA period metadata to the API.
- [ ] Show a page-level and row-level note when RCPA period is historical baseline, not same-month outcome.

Acceptance criteria:
- Users cannot mistake historical RCPA baseline for post-event impact.

### PH7-004: Make stale ingestion threshold configurable

Problem: `mv_data_quality` hardcodes stale ingestion as `14 days`. This should be a documented operational policy and configurable for deployment.

Files:
- `database/views/mv_data_quality.sql`
- `backend/app/config.py`
- `backend/app/services/data_quality_service.py`
- `docs/ingestion-runbook.md`

Tasks:
- [ ] Add `DATA_FRESHNESS_MAX_AGE_DAYS` setting.
- [ ] Use backend service logic or a parameterized config table rather than hardcoded SQL where possible.
- [ ] Document expected ingestion cadence.

Acceptance criteria:
- Freshness policy can be changed without editing a materialized view.

## P1 Contract and Test Gaps

### PHX-001: Align OpenAPI with actual backend schemas

Problem: `contracts/openapi.yaml` is stale for Phase 5-7. Examples:
- Budget contract uses `plannedBudget`, `confirmedContractedAmount`, `actualTotalSpend`, `currencyCode`, `missingFx`; actual API uses `plannedBudgetUsd`, `confirmedContractedAmountUsd`, `actualTotalSpendUsd`, `currencyCodes`, `missingFxCount`, etc.
- Doctor ROI contract uses `monthStart`, `monthEnd`, and `roiSegment`; actual API uses `segment` and `quadrant` and has no month range.
- Filters contract expects `meta` and string arrays; actual filters return option objects and no `meta`.
- Data Quality contract is narrower than the implemented response and still uses older field names.

Files:
- `specs/002-execution-intelligence-platform/contracts/openapi.yaml`
- `backend/app/main.py`
- `backend/tests/contracts/test_openapi_schema_contract.py` to create

Tasks:
- [ ] Regenerate or manually update OpenAPI to match FastAPI schemas.
- [ ] Add a contract test comparing `create_app().openapi()` against the committed YAML for all Phase 5-7 endpoints.
- [ ] Decide whether OpenAPI is generated source or hand-maintained source; document that policy.

Acceptance criteria:
- Frontend types, backend response models, and committed OpenAPI cannot drift silently.

### PHX-002: Strengthen Phase 5-7 database tests with real edge-case fixtures

Problem: Current tests mostly prove that views can be created or mocked schemas serialize. They do not catch the important analytical risks: multi-request budget double counting, latest-run-per-file validation scoping, mixed-currency aggregation, duplicate doctor attendance, missing-Pcode allocation loss, or historical RCPA period mismatch.

Files:
- `backend/tests/database/test_budget_doctor_data_quality_views.py`
- `backend/tests/api/test_phase5_7_api.py`
- `ingestion/tests/fixtures/xlsx/`

Tasks:
- [ ] Add minimal fixture rows for each edge case.
- [ ] Assert exact expected numerical outputs from materialized views.
- [ ] Add API tests against a real migrated test database, not only monkeypatched service methods.
- [ ] Add regression tests for LKR 310 conversion.

Acceptance criteria:
- A wrong SQL aggregate fails tests before it reaches Supabase.

### PHX-003: Expand frontend tests beyond render smoke tests

Problem: `frontend/tests/phase5-7-pages.test.tsx` has one broad render test. It does not test filtering, pagination, missing FX states, no-RCPA states, unmatched table behavior, drawer brand mix, or chart overflow resilience.

Files:
- `frontend/tests/phase5-7-pages.test.tsx`
- `frontend/src/pages/BudgetUtilization.tsx`
- `frontend/src/pages/DoctorRoi.tsx`
- `frontend/src/pages/DataQuality.tsx`

Tasks:
- [ ] Add tests for each page's loading, error, empty, and partial-data states.
- [ ] Add tests for filter changes updating API URLs.
- [ ] Add tests for missing FX and no-RCPA warnings.
- [ ] Add tests that doctor detail displays brand mix.
- [ ] Add tests for data-quality unmatched records table.

Acceptance criteria:
- Frontend regressions in critical dashboard workflows are caught by focused tests.

## P2 Frontend Product Completeness Issues

### PH5-006: Budget page needs clearer financial hierarchy

Problem: The page renders budget cards and a chart, but it does not clearly separate planned USD, confirmed/contracted local/USD, direct BTU, overhead BTC, total actual, missing-FX local-only spend, and unmatched spend.

Tasks:
- [ ] Add a "Financial interpretation" section explaining confirmed vs estimated vs actual.
- [ ] Show local and USD values side by side only when currency is single or grouped.
- [ ] Make missing-FX rows visually distinct.
- [ ] Add BTU/BTC reconciliation issue badge in row table.

Acceptance criteria:
- A business user can tell exactly which spend is normalized, which is local-only, and which is unmatched.

### PH6-007: Doctor detail drawer does not render brand mix

Problem: The backend returns `brandMix`, but `DoctorRoi.tsx` only shows engagement history and prescription trend.

Files:
- `frontend/src/pages/DoctorRoi.tsx`
- `frontend/src/components/doctors/DoctorRoiComponents.tsx`

Tasks:
- [ ] Add brand mix table/chart to the drawer.
- [ ] Show own vs competitor values.
- [ ] Add empty state when brand mix is unavailable.

Acceptance criteria:
- Doctor detail fulfills the planned profile, engagement, prescription trend, and brand mix workflow.

### PH6-008: Doctor ROI page lacks pagination and result-count transparency

Problem: Backend supports pagination, but frontend loads `pageSize: 50` with no pagination controls. For 26,563 ROI rows, this hides almost all records.

Tasks:
- [ ] Add pagination controls and total row display.
- [ ] Add sorting options for dark-horse, prescription quantity, spend, and spend per prescription.
- [ ] Keep selected filters across page changes.

Acceptance criteria:
- Users can navigate the complete doctor universe, not only the first 50 rows.

### PH7-005: Data Quality page is a summary, not the promised trust console

Problem: Current page shows KPI cards and validation drilldown only. It does not show file-level row counts, unmatched rows, source derivation notes, FX seed details, workflow/intervention drilldowns, or row-level remediation guidance.

Tasks:
- [ ] Add file participation table.
- [ ] Add unmatched records table.
- [ ] Add FX quality table.
- [ ] Add workflow/intervention coverage sections.
- [ ] Add source derivation notes visibly, especially Sri Lanka May derived snapshots.

Acceptance criteria:
- Data Quality page can be used to decide whether a KPI is safe to act on.

### PHX-004: Shared filter architecture is still missing

Problem: Finalplan calls for React Query plus Zustand global filters. Phase 9 includes global filters, but Phase 5-7 pages already need shared country/month/filter context to be credible. Current `App.tsx` uses local page state only.

Files:
- `frontend/src/App.tsx`
- `frontend/src/store/filterStore.ts`
- `frontend/src/components/common/FilterBar.tsx`

Tasks:
- [ ] Pull forward a minimal shared filter store for country/month.
- [ ] Add page-specific filters for budget and doctor ROI.
- [ ] Ensure every query key includes active filters.
- [ ] Show selected filters consistently across pages.

Acceptance criteria:
- Execution, budget, doctor ROI, and data quality can be compared under the same selected scope.

## P2 Documentation and Task-State Issues

### PHDOC-001: Update `tasks.md` completion states after fixing real gaps

Problem: Phase 5-7 tasks are marked complete, but several completion claims are broader than the implementation:
- T149 claims filters and top-opportunity lists are implemented, but frontend Doctor ROI has no filters.
- T154/T163 claim unmatched records table and coverage sections, but Data Quality page does not render unmatched records or full coverage drilldowns.
- T151 claims serial-month and FX seed metrics, but `mv_data_quality` does not expose them.

Tasks:
- [ ] After implementation, update task notes or split completed/incomplete sub-tasks.
- [ ] Avoid marking broad tasks complete when only a thin render path exists.

Acceptance criteria:
- `tasks.md` accurately reflects shipped behavior.

### PHDOC-002: Update data dictionary and dashboard contract with final semantics

Problem: The docs do not yet fully specify budget grains, doctor spend allocation, RCPA period mismatch, local-vs-USD aggregation rules, and validation scoping.

Files:
- `docs/data-dictionary.md`
- `specs/002-execution-intelligence-platform/contracts/dashboard-data-contract.md`
- `specs/002-execution-intelligence-platform/quickstart.md`

Tasks:
- [ ] Document budget summary grain and request evidence grain.
- [ ] Document doctor spend allocation and unallocated spend policy.
- [ ] Document RCPA-as-baseline, not same-month outcome.
- [ ] Document latest-run-per-file data-quality semantics.

Acceptance criteria:
- A future engineer can understand the business math without reverse-engineering SQL.

## Recommended Fix Order

1. Fix contracts first enough to define the target response shapes for Phase 5-7.
2. Fix budget aggregation grain and mixed-currency behavior.
3. Fix Doctor ROI filters, spend allocation safety, and period coverage metadata.
4. Fix Data Quality latest-run scoping and add missing drilldowns.
5. Upgrade frontend pages to expose filters, pagination, local/USD clarity, brand mix, and unmatched records.
6. Add database and API regression tests for every issue above.
7. Refresh materialized views in Supabase and verify counts/metrics again.
8. Only then proceed to Phase 8 AI.

