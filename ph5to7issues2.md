# Phase 5-7 Holistic Review Issues 2

Review scope: Phase 5 Budget Utilization, Phase 6 Doctor ROI, and Phase 7 Data Quality against `tasks.md`, `finalplan.md`, `specs/002-execution-intelligence-platform/`, current backend/frontend code, and the live Supabase database.

Review date: 2026-06-19

## Verdict

Phase 5-7 are substantially corrected compared with the earlier review, but they are not yet flawless enough to call production-grade without caveats.

The main data path works:

- Supabase is on Alembic revision `0019_phase5_7_fix`.
- Phase 5-7 focused backend tests pass.
- Phase 5-7 focused frontend test passes.
- Frontend production build passes.
- Live APIs for budget, doctor ROI, data quality, and filters return 200.
- Real source workbook rows are represented in canonical tables and materialized views.

The remaining risks are mostly about production-grade clarity and decision safety:

- Doctor ROI default scope is broader than the Phase 4/5 dashboard scope.
- Doctor brand filtering is not brand-specific ROI; it is a doctor-in-brand-baseline filter.
- Data Quality still uses fixture/dry-run local reports, not real-workbook reports.
- Serial month parse count is not instrumented from actual parser diagnostics.
- Tests are still too shallow for the most important analytical edge cases.
- Frontend has chart sizing warnings, bundle-size warning, and visible encoding artifacts.

Do not proceed to Phase 8 AI until P0 and P1 issues below are resolved or explicitly accepted, because AI must summarize trustworthy deterministic services.

## Evidence Snapshot

Live Supabase checks:

| Check | Current Result |
|---|---:|
| Alembic revision | `0019_phase5_7_fix` |
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
| `mv_unmatched_events` | 3,176 |

Current Data Quality:

| Metric | Current Result |
|---|---:|
| Latest ingestion status | `completed` |
| Loaded files | 8 / 8 |
| Rows seen | 1,179,273 |
| Rows loaded | 423,654 |
| Rows skipped | 42 |
| Validation errors | 0 |
| Validation warnings | 3 |
| Match coverage | 61.38% |
| Pcode coverage | 100% |
| RCPA coverage | 99.26% |
| Missing FX rows | 1,555 |
| BTU/BTC reconciliation issues | 88 |
| Spend without plan | 2,334 |
| Plan without spend | 763 |
| Primary-scope unmatched records | 158 |
| Serial month parse count | 0 |
| Official LKR rate | `0.0032258065` USD per LKR |
| Actual attendance rows missing Pcode | 0 |

Country/source scope:

| Country | Requests | Planner Rows | Snapshot Rows | Doctor ROI Rows |
|---|---:|---:|---:|---:|
| UAE | 295 | 0 | 25 | 64 |
| Sri Lanka | 1,398 | 459 | 73 | 13,689 |
| Myanmar | 288 | 0 | 16 | 5,856 |
| Malaysia | 58 | 0 | 7 | 2 |
| Nepal | 876 | 373 | 45 | 6,905 |
| Oman | 38 | 0 | 12 | 47 |

Tests/build run during review:

- `python -m pytest backend/tests/api/test_phase5_7_api.py backend/tests/database/test_budget_doctor_data_quality_views.py -q`: 5 passed.
- `npm --prefix frontend test -- --run tests/phase5-7-pages.test.tsx`: 1 passed, but Recharts emitted zero-size chart warnings.
- `npm --prefix frontend run build`: passed, but Vite reported one 681.63 kB JS chunk.

## What Was Fixed Since The First Phase 5-7 Review

- Budget summary no longer uses raw matched pair rows for event-level unspent/overrun totals.
- Local budget totals are now returned by currency bucket.
- Budget page now has country/month filters and pagination.
- Doctor ROI now supports country, engagement month range, brand, speciality, doctor class, ROI segment, and pagination.
- Doctor ROI spend allocation deduplices actual attendance to request/Pcode grain before allocation.
- Doctor ROI exposes RCPA baseline period fields and separates unengaged opportunities from high-value engaged doctors.
- Data Quality validation scoping now uses latest run per file, reducing current warnings from historical 9 to current 3.
- Data Quality now exposes source file rows, unmatched groups, unmatched samples, FX quality, LKR seed metadata, and unallocated doctor spend fields.
- OpenAPI Phase 5-7 endpoint parameters align with generated FastAPI output for the checked endpoints.

## P0: Must Fix Before Phase 8 AI

### PH5-7-001: Regenerate real-workbook ingestion reports

Problem: `data/reports/ingestion-report.md`, `data/reports/ingestion-report.json`, and `data/reports/workbook-profile-report.md` still describe tiny fixture/dry-run files, not the real eight workbooks loaded into Supabase.

Why this matters: Phase 7 is the trust layer. The database is populated with real data, but the local report artifacts currently prove only fixture behavior. This creates audit confusion and makes demos harder to defend.

Evidence:

- Local report says 4 files and 4 rows seen.
- Supabase has 8 source files and 1,179,273 rows seen.

Tasks:

- [ ] Generate a real-workbook profile report from `data/raw/`.
- [ ] Generate a real-workbook ingestion report from current Supabase run metadata.
- [ ] Label reports clearly as `real-data` vs `fixture-dry-run`.
- [ ] Keep reports gitignored if they may expose sensitive source details.

Acceptance criteria:

- Local reports reconcile to Supabase source file counts and row counts.
- Fixture reports cannot be mistaken for the production dataset.

### PH6-001: Make Doctor ROI default scope explicit and safe

Problem: Doctor ROI currently returns all countries by default, including UAE, Oman, Malaysia, and Myanmar. Execution and budget default to the Phase 4 primary analytical scope, but Doctor ROI does not.

Why this matters: A user can see 26,563 doctors and interpret the full country universe as equally supported. In reality, planner and RCPA coverage differ by country:

- Nepal and Sri Lanka have planner data.
- Myanmar has RCPA and execution/request evidence but no planner rows.
- UAE/Oman/Malaysia have request/snapshot evidence but no RCPA baseline.

Tasks:

- [ ] Decide and document Doctor ROI default scope: either primary countries only or all countries with strong scope warnings.
- [ ] Add `includeOutOfScope` or `scope` semantics to `/api/doctors/roi`.
- [ ] Add country-scope warning cards when rows include countries without planner or RCPA coverage.
- [ ] Make the page header say whether the view is "primary market ROI" or "all loaded country ROI".
- [ ] Add tests proving default scope behavior.

Acceptance criteria:

- A business user cannot mistake broader loaded evidence for fully comparable primary-scope ROI.
- Doctor ROI scope behavior is consistent with Execution/Budget scope rules or explicitly documented as different.

### PH6-002: Fix brand filter semantics in Doctor ROI

Problem: The `brand` filter checks whether a doctor has that brand in `rcpa_doctor_brand_summary`, but the ROI metrics shown remain all-brand doctor totals.

Why this matters: If a user selects a brand, they may assume prescription quantity, share, and ROI values are brand-specific. They are not. This is a representation mismatch.

Tasks:

- [ ] Choose the correct product behavior:
  - Option A: keep brand filter as a doctor inclusion filter and label it as "Doctors with selected brand in RCPA baseline".
  - Option B: compute brand-specific doctor ROI metrics from `rcpa_doctor_brand_summary`.
- [ ] If Option B, add brand-specific columns such as selected-brand Cipla qty/value, competitor qty/value, share, and spend-per-selected-brand-prescription.
- [ ] Update backend schema, OpenAPI, frontend labels, and tests.
- [ ] Add a regression test proving selected brand values do not silently show all-brand totals.

Acceptance criteria:

- Selecting a brand produces either clearly labeled inclusion filtering or true brand-specific metrics.
- The UI cannot imply false brand-level ROI precision.

### PH7-001: Instrument serial month parsing from the parser, not validation text

Problem: `serial_month_parse_count` is currently `0` and is computed by searching latest validation messages for the word `serial`. That does not prove whether Excel serial month values were parsed successfully.

Why this matters: Excel serial dates were a known source-file risk. If successful serial parsing is not instrumented, Data Quality cannot validate that risk.

Tasks:

- [ ] Add parser diagnostics that count month inputs by source format: text, date object, Excel serial, failed.
- [ ] Persist those diagnostics into ingestion run/file profile JSON or a dedicated quality table.
- [ ] Update `mv_data_quality` to read the real diagnostic count.
- [ ] Add an ingestion fixture and DB/API test where serial month values produce a positive serial count.

Acceptance criteria:

- Data Quality can show successful serial-month parsing, not just serial-related warnings.
- The count is sourced from ingestion diagnostics, not string matching.

### PH7-002: Make local/online row semantics clear for RCPA aggregation

Problem: Data Quality reports `rows_seen` and `rows_loaded`, but for RCPA, loaded rows are compact summary rows, not raw prescription rows. This is architecturally correct for Supabase storage, but the labels are ambiguous.

Why this matters: Users may think most RCPA rows were dropped. In reality, they were aggregated before persistence.

Tasks:

- [ ] Rename or supplement RCPA report metrics with `rawRowsSeen`, `summaryRowsWritten`, and `detailExtractRows`.
- [ ] Show the compact-online-storage rule in Data Quality.
- [ ] Add source-file detail that explains RCPA aggregation by workbook.

Acceptance criteria:

- RCPA row-count differences are interpreted as aggregation, not data loss.

## P1: High Priority Production Hardening

### PH5-001: Remove or deprecate mixed-currency top-level local totals

Problem: The budget API still returns top-level local totals such as `actualTotalSpendLocal` even when multiple currencies exist. The frontend mostly uses grouped local currency totals, but the API shape can still be misused by future UI or AI code.

Current evidence:

- Primary-scope budget rows include LKR official and NPR missing-FX rows.
- `localTotalsByCurrency` is correct.
- Top-level local totals are still cross-currency sums.

Tasks:

- [ ] Return top-level local totals only when exactly one currency is present, or mark them deprecated/internal.
- [ ] Prefer `localTotalsByCurrency` everywhere in frontend and AI context builders.
- [ ] Add schema documentation warning that cross-currency local totals are invalid.

Acceptance criteria:

- No consumer can accidentally present `LKR + NPR` as one local number.

### PH5-002: Add budget drilldown sorting and stronger row-grain labels

Problem: Budget rows are paginated but not sortable, and matched request rows can still look like independent event budget gaps.

Tasks:

- [ ] Add sort parameters for gap, actual spend, planned amount, FX status, BTU/BTC status, and match status.
- [ ] Add a visible row-grain field: `plan_event`, `matched_request_evidence`, `spend_without_plan`, `plan_without_spend`.
- [ ] In the table, distinguish grouped summary totals from request evidence rows.
- [ ] Add tests for pagination and sort query parameters.

Acceptance criteria:

- Users can navigate all 617 primary-scope budget rows predictably.
- Request evidence rows cannot be confused with grouped event-level budget calculations.

### PH6-003: Add true Doctor ROI sorting

Problem: Doctor ROI is sorted by fixed SQL order only. The UI does not expose sort controls for the core business workflows.

Tasks:

- [ ] Add sort parameters for dark-horse priority, Cipla prescriptions, total ROI spend, spend per Cipla prescription, last engagement date, and engagement count.
- [ ] Add frontend sort controls.
- [ ] Add API and frontend tests for sort order.

Acceptance criteria:

- A user can intentionally rank opportunities instead of relying on hardcoded default order.

### PH6-004: Add row-level RCPA baseline clarity in Doctor ROI table

Problem: The page-level note says RCPA is historical baseline, but table rows do not show RCPA first/last month unless the drawer is opened.

Tasks:

- [ ] Add compact RCPA period text in each doctor row or a visible table column.
- [ ] Add a no-RCPA badge directly in the table.
- [ ] Add a tooltip or detail explaining that engagement period and RCPA period are different.

Acceptance criteria:

- Users understand period mismatch before opening a doctor drawer.

### PH7-003: Make unmatched records drilldown paginated and filterable

Problem: Data Quality includes an unmatched records sample, but it is limited and not paginated/filterable.

Tasks:

- [ ] Add `/api/data-quality/unmatched` with pagination and filters by country, month, source type, reason, and confidence.
- [ ] Keep the summary endpoint lightweight.
- [ ] Add a full unmatched table UI with pagination.

Acceptance criteria:

- Data Quality supports real remediation of all unmatched records, not just a sample.

### PH7-004: Move data freshness threshold out of hardcoded SQL

Problem: `mv_data_quality` hardcodes stale ingestion as `14 days`.

Tasks:

- [ ] Add `DATA_FRESHNESS_MAX_AGE_DAYS` setting or a small DB config table.
- [ ] Compute stale/fresh status in service logic or from configurable SQL.
- [ ] Document expected ingestion cadence.

Acceptance criteria:

- Freshness policy can change without editing and remigrating a materialized view.

### PHX-001: Replace string-presence database tests with data-driven regression tests

Problem: `backend/tests/database/test_budget_doctor_data_quality_views.py` mostly checks that SQL text contains expected fragments. It does not execute realistic edge-case rows.

Tasks:

- [ ] Add real migrated test database fixtures for:
  - one plan event matched to multiple requests,
  - mixed official/missing FX currencies,
  - duplicate actual attendance Pcodes,
  - missing actual Pcodes,
  - old validation warning fixed in a later file run,
  - serial month parser diagnostics,
  - no-RCPA country rows.
- [ ] Assert exact view outputs and API responses.

Acceptance criteria:

- The important analytical bugs fail tests before reaching Supabase.

### PHX-002: Expand frontend tests beyond one render smoke test

Problem: `frontend/tests/phase5-7-pages.test.tsx` is still a single broad render test.

Tasks:

- [ ] Add budget filter-change tests proving query URLs include selected country/month/page.
- [ ] Add Doctor ROI filter, pagination, drawer, brand mix, no-RCPA, and historical-baseline tests.
- [ ] Add Data Quality unmatched/source/FX table tests.
- [ ] Add loading, error, empty, and partial-data state tests for each page.

Acceptance criteria:

- Critical Phase 5-7 UI behavior is tested, not just initial rendering.

## P2: UI Polish and Demo Quality

### PHUI-001: Fix Recharts zero-size warnings in tests and layout

Problem: Vitest passes but Recharts emits repeated warnings that chart width/height are zero in the jsdom container.

Tasks:

- [ ] Add a reliable test layout shim for `ResizeObserver`, `offsetWidth`, `offsetHeight`, and `getBoundingClientRect`.
- [ ] Verify dashboard charts in browser at desktop and mobile widths.
- [ ] Keep chart containers with stable min height and no overflow.

Acceptance criteria:

- Frontend tests run without chart sizing warnings.
- Charts do not overlap labels or flow out of cards.

### PHUI-002: Fix visible encoding artifacts

Problem: Some frontend strings render `Â·` instead of a normal separator.

Known files:

- `frontend/src/components/budget/BudgetComponents.tsx`
- `frontend/src/components/doctors/DoctorRoiComponents.tsx`

Tasks:

- [ ] Replace `Â·` with ASCII separators such as `-` or `|`.
- [ ] Search the frontend for additional encoding artifacts.

Acceptance criteria:

- No mojibake appears in the dashboard UI.

### PHUI-003: Split the frontend bundle

Problem: Vite reports a 681.63 kB minified JS chunk.

Tasks:

- [ ] Add route-level lazy loading for dashboard pages.
- [ ] Consider manual chunks for Recharts and vendor libraries.
- [ ] Re-run production build and record chunk sizes.

Acceptance criteria:

- Initial dashboard bundle is materially smaller, or the chunk-size warning is intentionally documented.

### PHUI-004: Add consistent shared filter context

Problem: Budget and Doctor ROI now have page-local filters, while Execution has its own filters. This is usable, but not the final shared dashboard behavior in `finalplan.md`.

Tasks:

- [ ] Add a minimal Zustand filter store for country/month shared across Execution, Budget, Doctor ROI, and Data Quality.
- [ ] Keep page-specific filters local or namespaced.
- [ ] Show selected scope consistently in page headers.

Acceptance criteria:

- Users can compare execution, budget, and ROI under the same selected country/month without resetting each page.

## Data Mismatch And Representation Notes

These are not necessarily bugs, but they must remain visible:

- Match coverage is 61.38%, so execution and budget metrics should continue to show weak/unmatched warnings.
- Primary-scope unmatched records still include 69 consolidation-only, 52 planner-only, and 37 snapshot-only records.
- NPR has missing FX, so Nepal spend cannot be fully represented in USD until a company NPR rate is supplied.
- Doctor ROI combines historical RCPA baseline through Mar 2026 with execution engagement through May 2026.
- Countries without RCPA should not appear as comparable doctor ROI markets unless explicitly marked no-RCPA.
- Local `SCHEMA.sql` is a full Supabase dump including internal Supabase objects; for engineering review, add an app-only schema snapshot or docs so reviewers are not forced to read storage/auth internals.

## Recommended Fix Order

1. Regenerate real-workbook reports and fix Data Quality row-count wording.
2. Decide Doctor ROI default scope and brand-filter semantics.
3. Remove/deprecate mixed-currency top-level local totals.
4. Instrument serial month parse counts from ingestion diagnostics.
5. Add unmatched records pagination/filtering.
6. Add data-driven DB regression tests for the exact analytical risks.
7. Fix frontend chart warnings, encoding artifacts, and bundle splitting.
8. Add shared filter context after the page-level APIs are stable.

