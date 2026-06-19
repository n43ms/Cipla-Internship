# Phase 5-7 Holistic Review Issues 2

Review scope: Phase 5 Budget Utilization, Phase 6 Doctor ROI, and Phase 7 Data Quality against `tasks.md`, `finalplan.md`, `specs/002-execution-intelligence-platform/`, current backend/frontend code, generated reports, and live Supabase data.

Review date: 2026-06-19

## Verdict

Phase 5-7 are substantially implemented and the main app path is working, but the system is not yet fully production-grade. The remaining issues are mostly contract correctness, decision-safety, dashboard clarity, test depth, and operational hardening.

The app is no longer blocked by missing FX or broken Phase 5-7 pages. However, do not treat the current state as flawless or ready for AI summarization until the P0 issues below are fixed or explicitly accepted.

## Evidence Snapshot

Commands/checks run during this review:

- `.\.venv\Scripts\python.exe -m pytest backend/tests/api/test_phase5_7_api.py backend/tests/database/test_budget_doctor_data_quality_views.py ingestion/tests/test_money_normalizer.py -q`: `7 passed`
- `npm --prefix frontend test -- --run tests/phase5-7-pages.test.tsx`: `1 passed`
- `npm --prefix frontend run build`: passed
- Live API smoke checks:
  - `/api/budget/summary?pageSize=3`: 200
  - `/api/doctors/roi?pageSize=3`: 200
  - `/api/doctors/roi?pageSize=3&includeOutOfScope=true`: 200
  - `/api/data-quality`: 200
  - `/api/filters`: 200

Live Supabase state:

| Check | Current Result |
|---|---:|
| Alembic revision | `0021_cleanup_fx_seeds` |
| `source_files` | 8 |
| `plan_events` | 832 |
| `execution_snapshots` | 178 |
| `execution_requests` | 2,953 |
| `request_doctors` | 5,750 |
| `doctors` | 26,367 |
| `rcpa_doctor_month_summary` | 292,742 |
| `rcpa_doctor_brand_summary` | 124,894 |
| `mv_budget_utilization` | 3,716 |
| `mv_doctor_roi` | 26,563 |
| `mv_data_quality` | 1 |

Data Quality live values:

| Metric | Current Result |
|---|---:|
| Loaded files | 8 / 8 |
| Rows seen | 1,179,273 |
| Rows loaded | 423,654 |
| Rows skipped | 42 |
| Validation errors | 0 |
| Validation warnings | 3 |
| Match coverage | 61.38% |
| Pcode coverage | 100% |
| RCPA coverage | 99.26% |
| Missing FX rows | 0 |
| Provisional FX rows | 1,555 |
| BTU/BTC reconciliation issues | 88 |
| Spend without plan | 2,334 |
| Plan without spend | 763 |
| Primary-scope unmatched records | 158 |
| Serial month parse count | 0 |
| Actual attendance rows missing Pcode | 0 |
| Stale ingestion | false |

Country/source coverage:

| Country | Requests | Planner Rows | Snapshot Rows | Doctor ROI Rows | No-RCPA ROI Rows |
|---|---:|---:|---:|---:|---:|
| UAE | 295 | 0 | 25 | 64 | 64 |
| Sri Lanka | 1,398 | 459 | 73 | 13,689 | 77 |
| Myanmar | 288 | 0 | 16 | 5,856 | 6 |
| Malaysia | 58 | 0 | 7 | 2 | 2 |
| Nepal | 876 | 373 | 45 | 6,905 | 0 |
| Oman | 38 | 0 | 12 | 47 | 47 |

Primary-scope unmatched records:

| Source | Reason | Rows |
|---|---|---:|
| consolidation | consolidation_only | 69 |
| planner | planner_only | 52 |
| execution_snapshot | snapshot_only_no_matching_plan | 37 |

## Already Corrected Since The First Phase 5-7 Review

- Missing FX is fixed: live Data Quality now shows `missing_fx_count = 0`.
- Non-LKR public FX is marked `provisional`; LKR remains `official` company FX at `1 USD = 310 LKR`.
- Mixed top-level local budget totals are now nullable when multiple currencies are present.
- Budget page has country/month filters and pagination.
- Doctor ROI page has country, month range, brand baseline, speciality, doctor class, ROI segment, out-of-scope toggle, pagination, and brand-mix drawer rendering.
- Doctor ROI defaults to Nepal/Sri Lanka unless a country is selected or `includeOutOfScope=true`.
- Data Quality now exposes source file rows, unmatched groups, unmatched samples, FX quality, LKR seed metadata, and unallocated doctor-spend fields.
- Real ingestion report JSON/MD is now generated from the eight workbooks and reconciles to Supabase row counts.
- Frontend build no longer emits the previous large initial chunk warning.

## P0: Must Fix Before Phase 8 AI

### PH5-7-001: Fix frontend/API numeric contract drift

Problem: FastAPI/Pydantic serializes many `Decimal` fields as JSON strings, but `frontend/src/types/api.ts` declares them as `number`. Live examples:

- `/api/doctors/roi?pageSize=1`: `totalRoiSpendUsd`, `ciplaPrescriptionQty`, and `quadrantX` are strings.
- `/api/data-quality`: `matchCoverage`, `officialLkrRateToUsd`, and `unallocatedDoctorSpendUsd` are strings.
- `/api/budget/summary`: local currency bucket amounts are strings.

Why this matters: The current UI often coerces values with `Number(...)`, but not consistently. AI context builders and future charts may treat strings as numbers incorrectly. This is a real contract mismatch between backend, OpenAPI, and frontend types.

Files:

- `backend/app/schemas/budget.py`
- `backend/app/schemas/doctors.py`
- `backend/app/schemas/data_quality.py`
- `frontend/src/api/client.ts`
- `frontend/src/types/api.ts`
- `specs/002-execution-intelligence-platform/contracts/openapi.yaml`

Tasks:

- [ ] Decide the contract rule: either backend emits JSON numbers for dashboard numeric values, or frontend types model decimals as strings and parse them explicitly.
- [ ] Add a single API parsing/normalization layer if frontend keeps numeric chart/card logic.
- [ ] Update `frontend/src/types/api.ts` to match the real wire contract.
- [ ] Add contract tests that fail if numeric wire types drift silently.
- [ ] Regenerate or update OpenAPI after the decision.

Acceptance criteria:

- Frontend runtime types match actual API JSON.
- Charts/cards/tables use deliberate numeric parsing, not accidental JavaScript coercion.
- AI context code cannot accidentally receive stringified numbers as business metrics.

### PH5-7-002: Replace shallow Phase 5-7 tests with data-driven regression tests

Problem: Current database tests mostly assert SQL text fragments rather than executing edge-case datasets. API tests monkeypatch services instead of proving real DB semantics. Frontend has one broad render test.

Why this matters: The important historical bugs in this project were semantic, not syntax-level: double-counted budget gaps, validation scoping, mixed currencies, duplicate attendance allocation, no-RCPA behavior, and brand-filter representation. The current tests would not reliably catch many of those regressions.

Files:

- `backend/tests/database/test_budget_doctor_data_quality_views.py`
- `backend/tests/api/test_phase5_7_api.py`
- `frontend/tests/phase5-7-pages.test.tsx`
- `ingestion/tests/fixtures/`

Tasks:

- [ ] Add DB fixtures for one plan event matched to multiple requests and assert grouped budget gap totals.
- [ ] Add mixed official/provisional FX fixtures and assert local/normalized output.
- [ ] Add duplicate actual-attendance Pcode fixture and assert Doctor ROI spend is allocated once.
- [ ] Add no-RCPA and historical-baseline fixture rows and assert ROI labels/limitations.
- [ ] Add latest-run-per-file validation fixture and assert stale warnings disappear after corrected rerun.
- [ ] Add frontend tests for filters, pagination, drawer brand mix, no-RCPA states, FX warnings, and Data Quality unmatched/source tables.

Acceptance criteria:

- Phase 5-7 analytical regressions fail in tests before reaching Supabase.
- Frontend tests verify core workflows, not only that pages render.

### PH5-7-003: Make Doctor ROI metadata derive from full filtered results, not current page rows

Problem: `DoctorService.roi()` builds `no_rcpa`, `missing_fx`, and `provisional_fx` flags from the current paginated page only. `DoctorRoiCards` also calculates dark-horse and no-RCPA counts from the current page rows only.

Evidence:

- Live `/api/doctors/roi?pageSize=3` returns `dataQualityFlags: []`.
- Primary-scope Doctor ROI still contains 77 Sri Lanka no-RCPA rows.

Why this matters: Users can see a clean header on page 1 even when the filtered result set contains no-RCPA or FX-quality caveats later. This is a data clarity issue.

Files:

- `backend/app/repositories/doctor_repository.py`
- `backend/app/services/doctor_service.py`
- `frontend/src/components/doctors/DoctorRoiComponents.tsx`

Tasks:

- [ ] Return aggregate quality counts for the full filtered Doctor ROI result set.
- [ ] Build `meta.dataQualityFlags` from full filtered aggregates, not current page rows.
- [ ] Show card counts from `segmentCounts`/aggregate counts rather than `data.rows`.
- [ ] Add tests where page 1 has clean rows but later pages contain no-RCPA/provisional-FX rows.

Acceptance criteria:

- Doctor ROI warnings reflect the selected result set, not just the currently visible page.
- Summary cards do not change meaning when the user pages through results.

### PH5-7-004: Fix Budget table gap representation for overruns

Problem: `BudgetGapTable` displays `row.unspentGapUsd ?? row.overrunAmountUsd`. If `unspentGapUsd` is `0` and `overrunAmountUsd` is positive, the table displays `0` because `0` is not nullish.

Why this matters: Event rows with overruns can be visually hidden as zero gaps. That violates the Phase 5 goal of showing unused budget and overruns clearly.

Files:

- `frontend/src/components/budget/BudgetComponents.tsx`
- `backend/app/schemas/budget.py`

Tasks:

- [ ] Render unspent and overrun as separate columns, or render a signed variance with explicit `unspent`/`overrun` label.
- [ ] Add an overrun fixture to frontend tests.
- [ ] Add row-level status styling for plan-only, request-only, matched gap, and matched overrun.

Acceptance criteria:

- A positive overrun is never hidden behind a zero unspent value.
- The budget table explains whether the row is underused, overrun, spend-without-plan, or plan-without-spend.

### PH5-7-005: Regenerate real workbook profile report

Problem: `data/reports/ingestion-report.md` and JSON now describe the real eight workbooks, but `data/reports/workbook-profile-report.md` still describes tiny fixture files (`consolidation_tiny.xlsx`, `execution_may_tiny.xlsx`, etc.).

Why this matters: Phase 7 is the trust layer. A stale workbook profile report creates audit confusion because one report proves real data and the other proves fixture data.

Files:

- `data/reports/workbook-profile-report.md`
- `ingestion/report.py`
- `ingestion/main.py`

Tasks:

- [ ] Regenerate workbook profile report from `data/raw/`.
- [ ] Label fixture profile reports separately if they are still needed.
- [ ] Ensure the profile report reconciles to the same eight source files as Supabase.

Acceptance criteria:

- The current profile report lists the eight real source workbooks, not fixture files.
- Report consumers can tell real-data reports apart from fixture/test reports.

## P1: High Priority Production Hardening

### PH5-001: Add budget sorting and row-grain semantics

Problem: Budget rows are paginated but not sortable. Rows also expose `matchStatus`, but not a clear business grain such as `matched_request_evidence`, `plan_without_spend`, or `spend_without_plan`.

Why this matters: There are 617 primary-scope budget rows. Users need to rank by overrun, unspent gap, actual spend, FX status, and reconciliation status.

Tasks:

- [ ] Add `sort` and `sortDirection` query params to `/api/budget/summary`.
- [ ] Support sort keys: `unspentGapUsd`, `overrunAmountUsd`, `actualSpendUsd`, `plannedBudgetUsd`, `fxRateStatus`, `btuBtcReconciliationStatus`, and `matchStatus`.
- [ ] Add a `rowGrain` or `rowKind` field to the API.
- [ ] Add frontend sort controls and visible row-grain badges.
- [ ] Add API/frontend tests for sorting.

Acceptance criteria:

- Users can intentionally find the largest gaps/overruns.
- Request evidence rows cannot be mistaken for grouped budget totals.

### PH6-001: Decide whether brand filter must become true brand-specific ROI

Problem: The Doctor ROI brand filter currently means "doctors with selected brand in RCPA baseline", while displayed ROI metrics remain all-brand doctor totals. The UI note says this, so it is not hidden, but the product behavior is still weaker than a true brand-specific ROI workflow.

Tasks:

- [ ] Confirm product decision:
  - Option A: keep brand as baseline inclusion filter and expose `brandFilterMode = inclusion_only` in API/meta.
  - Option B: implement selected-brand ROI metrics from `rcpa_doctor_brand_summary`.
- [ ] If Option B, return selected-brand Cipla qty/value, competitor qty/value, share, and spend-per-selected-brand-prescription.
- [ ] If Option A, make labels and exports impossible to misread as brand-specific ROI.
- [ ] Add regression tests for selected-brand behavior.

Acceptance criteria:

- Selecting a brand cannot imply false brand-specific ROI precision.
- The API tells consumers what the brand filter means.

### PH6-002: Clarify Doctor ROI month filtering semantics

Problem: Month filters apply to engagement evidence, but unengaged RCPA doctors with null engagement dates remain visible. This is useful for opportunities, but it can surprise users who expect a strict period filter.

Files:

- `backend/app/repositories/doctor_repository.py`
- `backend/app/services/doctor_service.py`
- `frontend/src/pages/DoctorRoi.tsx`

Tasks:

- [ ] Add explicit filter mode metadata: `engagement_period_filter`.
- [ ] Consider a toggle: `showUnengagedBaselineOpportunities`.
- [ ] Show active filter semantics beside the month controls.
- [ ] Add tests for month-filtered ROI with unengaged baseline doctors.

Acceptance criteria:

- A user understands why unengaged doctors can appear under an engagement month filter.

### PH6-003: Add true Doctor ROI sorting

Problem: Doctor ROI has a fixed SQL order. The UI has pagination but no sort controls for the primary workflows.

Tasks:

- [ ] Add backend sort keys: `darkHorse`, `ciplaPrescriptionQty`, `totalRoiSpendUsd`, `spendPerCiplaPrescriptionUsd`, `lastEngagementDate`, and `engagementCount`.
- [ ] Add frontend sort controls.
- [ ] Add tests for sort order.

Acceptance criteria:

- Users can rank doctors by opportunity, value, spend, engagement, and inefficient spend.

### PH7-001: Add paginated/filterable unmatched record endpoint

Problem: Data Quality includes only a 50-row unmatched sample. It groups unmatched counts by source/reason, but it does not support full remediation of all unmatched rows.

Files:

- `backend/app/repositories/data_quality_repository.py`
- `backend/app/routers/data_quality.py`
- `frontend/src/pages/DataQuality.tsx`

Tasks:

- [ ] Add `/api/data-quality/unmatched` with `page`, `pageSize`, `country`, `month`, `sourceType`, `reasonCode`, and confidence filters.
- [ ] Keep `/api/data-quality` summary lightweight.
- [ ] Add full unmatched table with pagination.
- [ ] Add tests for unmatched pagination and filters.

Acceptance criteria:

- Users can inspect and remediate all unmatched records, not only a sample.

### PH7-002: Move stale-ingestion threshold out of materialized-view SQL

Problem: `mv_data_quality.sql` hardcodes stale ingestion as `14 days`.

Why this matters: Freshness policy is operational configuration. It should not require a view migration to change demo cadence.

Files:

- `database/views/mv_data_quality.sql`
- `backend/app/config.py`
- `backend/app/services/data_quality_service.py`
- `docs/ingestion-runbook.md`

Tasks:

- [ ] Add `DATA_FRESHNESS_MAX_AGE_DAYS` setting or a small DB config table.
- [ ] Compute stale status in backend service or from configurable DB policy.
- [ ] Document expected ingestion cadence.
- [ ] Add tests for stale threshold behavior.

Acceptance criteria:

- Freshness policy changes without editing/remigrating `mv_data_quality`.

### PH7-003: Improve RCPA row-count wording in Data Quality

Problem: Data Quality shows total `rowsSeen` and `rowsLoaded`, but the UI does not explain that RCPA raw rows are aggregated into compact online summaries and detailed local extracts.

Evidence:

- Real ingestion report explains `Online Rows` and `Detail Rows`.
- Data Quality page only shows generic row counts.

Tasks:

- [ ] Add `rawRowsSeen`, `summaryRowsWritten`, and `detailExtractRows` to source-file quality for RCPA files.
- [ ] Show "compact online summary" wording in Data Quality.
- [ ] Link/report local extract path only in local reports, not public dashboard UI if sensitive.

Acceptance criteria:

- Users understand RCPA aggregation as intentional storage optimization, not missing data.

### PH7-004: Show all promised Data Quality metrics in the UI

Problem: The Data Quality page does not visibly show every Phase 7 metric promised in `tasks.md`. It shows several, but serial-month count and intervention-type coverage are not presented as first-class visible metrics.

Files:

- `frontend/src/pages/DataQuality.tsx`
- `backend/app/schemas/data_quality.py`

Tasks:

- [ ] Add visible cards/rows for `serialMonthParseCount` and `interventionTypeCoverage`.
- [ ] Add visible note for provisional FX count and public-rate status.
- [ ] Add source derivation note for Sri Lanka May derived snapshots in the page body, not only meta.

Acceptance criteria:

- T163 is honestly satisfied in the visible page, not only in API payload.

### PHX-001: Add safe database diagnostics and avoid broad joins on Supabase free tier

Problem: A broad diagnostic query joining countries to requests, planner rows, snapshots, and `mv_doctor_roi` hit Supabase temp-space limits: `No space left on device`.

Why this matters: The app can operate, but production diagnostics/reviews must not require large cartesian joins or temp-heavy queries. Supabase free tier remains a real operational constraint.

Tasks:

- [ ] Add pre-aggregated diagnostic views or scripts for country/source coverage.
- [ ] Document safe review SQL in `docs/ingestion-runbook.md` or `docs/demo-validation.md`.
- [ ] Add indexes or materialized summaries where repeated diagnostics are needed.
- [ ] Avoid using full `SCHEMA.sql` or ad hoc joins as the normal review path.

Acceptance criteria:

- Reviewers can inspect source coverage and quality without triggering temp-space failures.

## P2: Product/UI Quality

### PHUI-001: Add shared filter context

Problem: Execution, Budget, and Doctor ROI each manage local filters. This is usable, but the final architecture asks for shared dashboard scope through React Query plus Zustand.

Tasks:

- [ ] Add a minimal `filterStore` for country/month.
- [ ] Keep page-specific filters local or namespaced.
- [ ] Show active global scope consistently in headers.
- [ ] Ensure query keys include shared and page-specific filters.

Acceptance criteria:

- A user can compare Execution, Budget, Doctor ROI, and Data Quality under the same selected country/month without resetting each page.

### PHUI-002: Add stronger empty/error/partial states for Phase 5-7 filters

Problem: Pages have basic loading/error/empty states, but filter-specific no-data explanations are thin.

Tasks:

- [ ] Budget empty state should mention selected country/month and whether out-of-scope is excluded.
- [ ] Doctor ROI empty state should distinguish no attendance, no RCPA baseline, and too-restrictive filters.
- [ ] Data Quality should handle no unmatched records and no validation issues with specific success copy.
- [ ] Add tests for these states.

Acceptance criteria:

- Empty states explain what the user can do next without implying data loss.

### PHUI-003: Add browser-level layout verification for Phase 5-7

Problem: Unit tests pass and previous chart sizing warnings are fixed, but there is no recorded browser screenshot/layout verification after the latest Phase 5-7 changes.

Tasks:

- [ ] Run the frontend against the backend locally.
- [ ] Verify Budget, Doctor ROI, and Data Quality at desktop and mobile widths.
- [ ] Check chart overflow, table scroll behavior, drawer behavior, and sticky nav.
- [ ] Record issues or screenshots in `docs/demo-validation.md`.

Acceptance criteria:

- Phase 5-7 pages are visually demo-safe, not just test-safe.

## Data Mismatch And Representation Notes

These are not necessarily implementation bugs, but they must remain visible in the product:

- Match coverage is 61.38%; execution and budget metrics must continue to show weak/unmatched warnings.
- Primary-scope unmatched records still include 69 consolidation-only, 52 planner-only, and 37 snapshot-only records.
- 1,555 execution request rows use provisional public FX. They are usable for provisional USD analysis but not official finance reporting.
- Doctor ROI mixes FY27 engagement evidence with historical RCPA baseline ending March 2026.
- UAE, Oman, and Malaysia have request/snapshot evidence but no RCPA coverage; Myanmar has no planner rows. These markets are not comparable to Nepal/Sri Lanka primary-scope ROI without warnings.
- 50 plan events have multiple matched/weak request rows; budget summaries group these, but detail rows still need clear grain labels.

## Recommended Fix Order

1. Fix frontend/API numeric contract drift.
2. Add full-result Doctor ROI quality aggregates and fix page-based card counts.
3. Fix Budget overrun display.
4. Regenerate real workbook profile report.
5. Add data-driven DB/API/frontend regression tests.
6. Add budget/doctor sorting and unmatched record pagination.
7. Move stale-ingestion policy to config.
8. Improve Data Quality UI wording for RCPA aggregation, serial months, intervention coverage, and provisional FX.
9. Add shared filter context and browser layout verification.

