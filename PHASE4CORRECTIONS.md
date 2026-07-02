# Phase 4 Deep Audit Correction Log

Date audited: 2026-06-18

Scope audited:

- `tasks.md` Phase 4 / US2
- `finalplan.md`
- all 8 files in `data/raw/`
- Supabase canonical tables
- Supabase materialized views
- backend Phase 4 APIs
- frontend Execution Matrix dashboard

Instruction: do not implement yet. This file lists the remaining corrections required before Phase 4 can be called production-grade.

---

## Current Verdict

Phase 4 is close, but not fully production-grade yet.

Implementation update on 2026-06-18:

- Blocking semantic repairs have been implemented through Supabase migration `0014_phase4_semantic_repairs`.
- Derived snapshot provenance has been implemented through Supabase migration `0015_snapshot_provenance`.
- Workflow, execution, and intervention APIs now default to Nepal/Sri Lanka Apr-May 2026 Phase 4 production scope.
- Audit-only rows remain preserved and are available through `includeOutOfScope=true`.
- Verification passed: backend/ingestion tests, frontend tests, frontend production build, live Supabase smoke checks, and schema export.

Raw ingestion is correct. The canonical database mostly represents the raw files correctly. The remaining problems are not missing Excel ingestion. The remaining problems are Phase 4 semantic accuracy issues in the analytical layer, workflow API scoping, reason-code correctness, and stale contract docs.

The professional correction is not to force every row to match. The correct correction is:

1. keep all source data preserved,
2. use Nepal/Sri Lanka Apr-May 2026 as the default Phase 4 analytical scope,
3. classify out-of-scope and unmatched rows honestly,
4. make KPI numerators match their labels,
5. make every frontend card/table use the same backend definitions.

---

## Raw File To Supabase Verification

All 8 real files are present in `data/raw/` and are registered in Supabase by matching hash.

| Source file | Raw parse result | Supabase result | Status |
|---|---:|---:|---|
| `Consolidation report Nov'25 - 01 Jun'26 - AJ.xlsx` | 2,953 requests, 5,750 request-doctor rows | 2,953 `execution_requests`, 5,750 `request_doctors` | OK |
| `Executiion YP Planner All BU's Apr Month.xlsx` | 49 execution snapshot rows | 49 `execution_snapshots` | OK |
| `Execution YP Planner All Bu's May Month.xlsx` | 98 loaded, 39 skipped | 98 `execution_snapshots` | OK |
| `FY27 - Yearly Planner Template Nepal vf.xlsb` | 373 loaded, 3 skipped warnings | 373 `plan_events` | OK |
| `FY27 - Yearly Planner Template Sri Lanka vf1 NEW.xlsb` | 459 loaded | 459 `plan_events` | OK |
| `Nepal & Myanmar Apr'24-Mar'25 RCPA report.xlsb` | 125,167 online summary rows | 125,167 summary rows | OK |
| `Nepal & Myanmar RCPA Report Apr'25-mar'26.xlsb` | 134,753 online summary rows | 134,753 summary rows | OK |
| `Sri Lanka RCPA Report Apr'25 - Mar'26.xlsb` | 159,802 online summary rows | 159,802 summary rows | OK |

Supabase canonical totals:

| Table | Rows |
|---|---:|
| `source_files` | 8 |
| `plan_events` | 832 |
| `execution_snapshots` | 178 |
| `execution_requests` | 2,953 |
| `request_doctors` | 5,750 |
| `doctors` | 26,367 |
| `event_matches` | 3,813 |
| `rcpa_doctor_month_summary` | 292,742 |
| `rcpa_doctor_brand_summary` | 124,894 |
| `rcpa_country_brand_month_summary` | 2,086 |

Why `execution_snapshots = 178` while raw monthly snapshot rows are 147:

- 49 April monthly rows
- 98 May monthly rows
- 31 Sri Lanka May rows derived from consolidation because the May workbook has no Sri Lanka tab

This is expected and architecturally valid.

---

## Data That Is Correct

### 1. Source registration and period metadata are correct

All 8 source files have `period_start` and `period_end`.

Examples:

- Nepal planner: Apr 2026-Mar 2027
- Sri Lanka planner: Apr 2026-Mar 2027
- consolidation: Nov 2025-Sep 2026
- RCPA: Apr 2024-Mar 2026 depending on file

### 2. Primary Phase 4 scope is correctly identified

The four primary scope combinations exist and have all required source families:

| Country | Month | Planner | Snapshot | Consolidation |
|---|---|---|---|---|
| Nepal | 2026-04 | yes | yes | yes |
| Nepal | 2026-05 | yes | yes | yes |
| Sri Lanka | 2026-04 | yes | yes | yes |
| Sri Lanka | 2026-05 | yes | yes | yes |

### 3. Out-of-scope data is preserved

Out-of-scope rows remain available for audit:

- Malaysia, Myanmar, Oman, UAE consolidation/execution rows
- Nepal/Sri Lanka historical consolidation rows before Apr 2026
- Nepal/Sri Lanka future planner rows after May 2026
- RCPA rows ending Mar 2026

This is correct. These rows should not be deleted.

### 4. Latest validation status is mostly correct

- historical `validation_errors`: 9
- latest current validation rows: 3

This correctly separates historical warning history from current-file warnings.

---

## Remaining Architectural Errors

## Error 1 - Workflow APIs are not Phase 4 scoped

Execution and intervention APIs default to Phase 4 scope. Workflow APIs do not.

Current API smoke result:

- `/api/execution/summary` defaults to scoped rows.
- `/api/interventions/mix` defaults to scoped rows.
- `/api/workflow/summary` returns all 2,953 consolidation rows.
- `/api/workflow/requests` returns all 2,953 consolidation rows.

This is wrong because the dashboard says Phase 4 scope is Nepal/Sri Lanka Apr-May 2026, but workflow numbers include Myanmar, Malaysia, Oman, UAE, historical months, and future months.

Concrete evidence:

For May 2026 workflow rows:

| Scope | Rows |
|---|---:|
| all May workflow rows | 439 |
| Nepal/Sri Lanka May rows | 346 |
| other-country May rows incorrectly included | 93 |

Country breakdown for May 2026:

| Country | Rows |
|---|---:|
| Sri Lanka | 246 |
| Nepal | 100 |
| Myanmar | 41 |
| UAE | 30 |
| Malaysia | 14 |
| Oman | 8 |

Correction required:

- Add `is_primary_phase4_scope`, `scope_status`, and `scope_reason` to `mv_workflow_governance`.
- Add `includeOutOfScope=false` default behavior to workflow repository/service/router.
- Add `includeOutOfScope=true` query param to workflow APIs.
- Pass the same scope flag from frontend workflow queries.
- Update workflow cards/tables to state whether they are scoped or audit-wide.

Priority: blocking.

---

## Error 2 - KPI execution rate uses raw executed snapshots, not planned events with executed evidence

Current `mv_execution_kpis.executed_events` counts raw `execution_snapshots.normalized_status = 'executed'` by country/month.

That means `event_execution_rate = executed snapshots / planned events`.

This can be misleading when executed snapshots do not match planned events.

Concrete evidence:

| Country | Month | Planned events | Matched events | Raw executed snapshots | Planned events with executed evidence | Unmatched executed snapshots |
|---|---|---:|---:|---:|---:|---:|
| Nepal | 2026-04 | 23 | 15 | 5 | 5 | 0 |
| Nepal | 2026-05 | 38 | 24 | 16 | 14 | 2 |
| Sri Lanka | 2026-04 | 30 | 18 | 9 | 9 | 0 |
| Sri Lanka | 2026-05 | 42 | 24 | 30 | 11 | 19 |

Sri Lanka May is the clearest problem:

- current dashboard says 30 executed snapshots
- only 11 planned events have matched executed evidence
- 19 executed snapshots are not matched to a planned event

Correction required:

- Keep raw `executed_snapshot_count` as an evidence count.
- Add `planned_events_with_executed_evidence`.
- Add `planned_events_with_action_due_evidence`.
- Change `event_execution_rate` to use `planned_events_with_executed_evidence / planned_events`.
- Rename current raw snapshot metric to `executed_snapshot_rows` or equivalent.
- Update backend schema/types/frontend labels so users see both:
  - executed snapshot evidence
  - planned events executed

Priority: blocking.

---

## Error 3 - `mv_intervention_mix.executed_snapshot_count` does not count snapshots

Current `mv_intervention_mix` logic makes `executed_count` and `executed_snapshot_count` both count distinct execution requests linked to executed snapshots.

Concrete evidence inside primary scope:

| Metric | Current value |
|---|---:|
| executed request links | 416 |
| distinct executed snapshots | 34 |
| executed match rows | 416 |
| action-due request links | 44 |
| distinct action-due snapshots | 11 |

This means the field name `executed_snapshot_count` is wrong. It is not counting snapshots. It is counting request links.

Correction required:

- Keep `executed_count` as request-level executed-with-snapshot evidence if that is the desired intervention metric.
- Rename or add:
  - `executed_request_count`
  - `executed_snapshot_count`
  - `action_due_request_count`
  - `action_due_snapshot_count`
- Update backend schemas and frontend table/chart labels accordingly.
- Prevent the chart from implying 416 distinct executed activities if those are request links under 34 snapshot groups.

Priority: blocking.

---

## Error 4 - Primary-scope unmatched snapshots have the wrong reason code

Primary-scope unmatched snapshots are currently labeled `no_planner_for_country`.

That is false for Nepal/Sri Lanka Apr-May 2026 because planner coverage exists.

Concrete evidence:

| Country | Month | Unmatched snapshot rows | Current reason |
|---|---|---:|---|
| Nepal | 2026-05 | 6 | `no_planner_for_country` |
| Sri Lanka | 2026-05 | 31 | `no_planner_for_country` |

Correct reason should be one of:

- `snapshot_only_no_matching_plan`
- `no_matching_planner_event`
- `snapshot_name_not_in_planner`

Correction required:

- Update `event_matcher.py` unmatched snapshot reason logic.
- Backfill existing `event_matches`.
- Refresh `mv_execution_event_matrix` and `mv_unmatched_events`.
- Update frontend reason label mapping if needed.

Priority: blocking.

---

## Error 5 - Execution repository loses `scopeReasons`

`/api/execution/summary` returns:

```json
"scopeStatuses": ["primary_phase4_scope"],
"scopeReasons": []
```

This is wrong. The repository iterates the SQLAlchemy result once to build statuses and then reuses the exhausted iterator to build reasons.

Correction required:

- Materialize `scope_rows = list(...)` before deriving both statuses and reasons.
- Add API test proving `scopeReasons` is not empty when scope rows exist.

Priority: medium.

---

## Error 6 - Frontend reason/scope column is semantically noisy for matched rows

For matched rows, the table can show `primary phase4 scope` under a column called `Reason / scope`.

That is not technically wrong, but it is weak UX. Matched rows should not look like they have a reason problem.

Correction required:

- For matched rows, show `Matched evidence` or blank reason.
- For unmatched/weak rows, show unmatched reason.
- For out-of-scope rows, show scope reason.
- Keep full detail in drawer.

Priority: medium.

---

## Error 7 - Planner natural duplicate groups need explicit classification

The planner contains 7 duplicate natural-grain groups by source file, country, month, event type, and normalized event name.

Examples:

| Country | Month | Event | Rows |
|---|---|---|---:|
| Nepal | 2026-04 | Scope CME | 2 |
| Nepal | 2026-05 | SMART CME | 2 |
| Nepal | 2026-11 | Scope CME | 4 |
| Sri Lanka | 2026-05 | FloBume campaign | 2 |

These may be legitimate repeated planned instances, but the system currently has no explicit `planned_instance_count`, `duplicate_group_id`, or duplicate classification.

Correction required:

- Add a validation/report section for repeated planner natural grains.
- Decide whether duplicates are legitimate repeated events or accidental duplicated rows.
- If legitimate, expose `planned_instance_count` or preserve source row-level grain explicitly.
- If accidental, dedupe or mark as duplicate before KPI aggregation.

Priority: medium.

---

## Error 8 - Derived Sri Lanka May snapshots have weak source-row provenance

All 31 Sri Lanka May derived snapshots use the consolidation source file and `source_row_number = 0`.

That creates one duplicate source-row group:

- file: consolidation workbook
- sheet: `Working`
- source row: `0`
- rows: 31

This is not data corruption because these rows are derived aggregates, not literal source rows. But the provenance should be explicit.

Correction required:

- Add `source_derivation_json` or stronger source reference metadata for derived snapshots.
- Store contributing consolidation request IDs or source rows for each derived snapshot group.
- In the frontend drawer, show that the snapshot is derived and not a literal Excel row.

Priority: medium.

---

## Error 9 - OpenAPI and dashboard contract files are stale

The spec contract files do not mention current Phase 4 fields/params:

- `includeOutOfScope`
- `primaryScope`
- `scopeStatuses`
- `scopeReasons`
- `unmatchedReasonCode`
- `unmatchedReasonDetail`
- `matchGrain`
- `matchedRequestCount`
- `executedSnapshotCount`
- `matchedWithoutExecutionCount`

Correction required:

- Update `specs/002-execution-intelligence-platform/contracts/openapi.yaml`.
- Update `specs/002-execution-intelligence-platform/contracts/dashboard-data-contract.md`.
- Add contract tests or schema export checks so backend Pydantic schemas and written OpenAPI contracts do not drift.

Priority: medium.

---

## Error 10 - Workflow materialized view has no Phase 4 scope fields

`mv_workflow_governance` has no:

- `is_primary_phase4_scope`
- `scope_status`
- `scope_reason`

This is the root cause of workflow API pollution.

Correction required:

- Join `phase4_analysis_scope` in `mv_workflow_governance`.
- Add indexes for scope filtering.
- Update migration and schema export.

Priority: blocking.

---

## Error 11 - HCP execution rate may include unmatched snapshot HCPs

Current HCP execution rate uses:

```text
sum(execution_snapshots.engaged_hcps) / sum(plan_events.planned_total_hcps)
```

Because raw snapshots can be unmatched, this can mix unmatched execution evidence into a planned-event denominator.

Correction required:

- Add both raw and matched HCP metrics:
  - `raw_engaged_hcps`
  - `matched_engaged_hcps`
  - `planned_hcps`
  - `matched_hcp_execution_rate`
- Use matched HCP rate for plan-vs-actual KPI.
- Keep raw snapshot HCP count as source evidence.

Priority: high.

---

## Error 12 - Tests do not fully lock Phase 4 production semantics

Existing tests pass, but they do not catch the issues above.

Correction required:

Add tests for:

- workflow default scope excludes out-of-scope rows
- workflow `includeOutOfScope=true` includes audit rows
- `event_execution_rate` uses planned events with executed evidence, not raw unmatched snapshots
- `executed_snapshot_count` counts distinct snapshots
- unmatched snapshots in primary scope get `snapshot_only_no_matching_plan`, not `no_planner_for_country`
- `scopeReasons` is populated
- OpenAPI contracts include Phase 4 fields and query params
- frontend labels distinguish request links from snapshot counts

Priority: blocking.

---

## Corrections To Implement Next

### Phase 4K - Scope Workflow Governance

- [ ] P4R051 Add Phase 4 scope fields to `mv_workflow_governance`.
- [ ] P4R052 Add default scoped filtering plus `includeOutOfScope=true` to workflow repository/service/router.
- [ ] P4R053 Update frontend workflow requests to pass the same out-of-scope toggle.
- [ ] P4R054 Update workflow cards/table labels to state scoped vs audit-wide data.

### Phase 4L - Correct Execution KPI Semantics

- [ ] P4R055 Split raw snapshot counts from planned-event execution counts in `mv_execution_kpis`.
- [ ] P4R056 Add `planned_events_with_executed_evidence` and `planned_events_with_action_due_evidence`.
- [ ] P4R057 Change `event_execution_rate` to planned events with executed evidence divided by planned events.
- [ ] P4R058 Add matched/raw HCP metrics and use matched HCP execution rate for plan-vs-actual.

### Phase 4M - Correct Intervention Mix Semantics

- [ ] P4R059 Replace misleading intervention count fields with explicit request-link and snapshot-count fields.
- [ ] P4R060 Update backend intervention schemas/types/repository/service to expose the corrected fields.
- [ ] P4R061 Update intervention chart/table labels to avoid implying 416 distinct snapshots when there are 34.

### Phase 4N - Correct Reason Codes

- [ ] P4R062 Replace primary-scope unmatched snapshot reason `no_planner_for_country` with `snapshot_only_no_matching_plan`.
- [ ] P4R063 Backfill existing event matches with corrected reason codes.
- [ ] P4R064 Refresh affected materialized views and verify reason distributions.

### Phase 4O - Repair API Metadata and Contracts

- [ ] P4R065 Fix `scopeReasons` iterator bug in execution repository.
- [ ] P4R066 Update OpenAPI and dashboard data contracts for Phase 4 fields/params.
- [ ] P4R067 Add API/contract tests that prevent schema drift.

### Phase 4P - Clarify Duplicate/Derived Provenance

- [ ] P4R068 Add validation/report output for repeated planner natural grains.
- [ ] P4R069 Classify planner duplicates as legitimate repeated instances or accidental duplicates.
- [ ] P4R070 Improve derived Sri Lanka May snapshot provenance with contributing request/source references.

### Phase 4Q - Final Production Gate

- [ ] P4R071 Run backend and ingestion tests.
- [ ] P4R072 Run frontend tests.
- [ ] P4R073 Run frontend production build.
- [ ] P4R074 Apply Supabase migration and refresh materialized views.
- [ ] P4R075 Smoke-test:
  - `/api/execution/summary`
  - `/api/execution/events`
  - `/api/workflow/summary`
  - `/api/workflow/requests`
  - `/api/interventions/mix`
- [ ] P4R076 Verify raw-to-database counts again after corrections.

---

## Phase 4 Completion Definition After This Audit

Phase 4 is complete only when:

1. Raw-to-canonical counts still match all 8 workbooks.
2. Default execution, workflow, and intervention APIs all use Nepal/Sri Lanka Apr-May 2026 only.
3. `includeOutOfScope=true` consistently exposes audit rows across execution, workflow, and intervention APIs.
4. Event execution rate means planned events with executed evidence, not raw unmatched snapshots.
5. Intervention snapshot fields count snapshots, and request fields count requests.
6. Unmatched reason codes are factually correct for primary and out-of-scope rows.
7. Workflow cards no longer include out-of-scope countries/months by default.
8. Frontend labels make grain obvious: planned events, matched evidence, request links, snapshots, and unmatched reasons.
9. Contract docs match actual backend response fields.
10. Tests catch all critical semantics above.
