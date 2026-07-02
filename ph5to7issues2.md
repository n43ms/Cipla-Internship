# Phase 5-7 Remaining Issues After Task Verification

Review scope: Phase 5 Budget Utilization, Phase 6 Doctor ROI, and Phase 7 Data Quality in `specs/002-execution-intelligence-platform/tasks.md`.

Review result: all Phase 5-7 tasks T113-T165 are now marked complete in `tasks.md`.

## Unticked Phase 5-7 Tasks

None. No Phase 5, Phase 6, or Phase 7 task remains unticked after verification.

## Corrections Applied To Task Text

The implementation is complete, but several task descriptions had stale file references from earlier architecture drafts. Those were corrected while ticking the tasks:

- T120 now points to `ingestion/repositories/canonical_repository.py`, where execution request financial upserts are actually implemented.
- T123 now points to `database/migrations/versions/0016_budget_finance_view.py`, the actual budget materialized-view migration.
- T138 now points to `ingestion/repositories/rcpa_repository.py`, where doctor master upserts from RCPA aggregates are implemented.
- T142 now points to `database/migrations/versions/0017_doctor_roi_quadrant_view.py`, the actual Doctor ROI migration.
- T156 now points to `database/migrations/versions/0018_data_quality_view.py`, the actual Data Quality migration.
- T164 was clarified: Phase 5-7 quality banners are integrated into the current app shell and implemented pages; Executive Overview remains Phase 9 because that page is not part of the Phase 5-7 deliverable.

## Verification Evidence

Previous focused verification for the current Phase 5-7 implementation passed:

- Backend/API/database/ingestion focused suite: 31 passed.
- Frontend Phase 5-7 focused suite: 6 passed.

Covered areas include:

- Consolidation financial mapping for estimated, confirmed, BTU, BTC, total actual, association, variance, FX, and USD fields.
- Static FX behavior with official company LKR rate `1 USD = 310 LKR` and provisional non-official FX handling.
- `mv_budget_utilization` budget semantics and BTU/BTC reconciliation checks.
- `/api/budget/summary` contract and Budget Utilization frontend page.
- Country-scoped doctor uniqueness, request-doctor parsing, Doctor ROI view, quadrant classification, and doctor detail API.
- `/api/doctors/roi`, `/api/doctors/{countryCode}/{pcode}`, and Doctor ROI frontend page.
- `mv_data_quality`, `/api/data-quality`, `/api/filters`, `/api/ingestion/latest`, shared data-state components, and Data Quality frontend page.

## Current Environment Caveat

A fresh rerun in the latest sandbox could not be completed because the active writable workspace is `ValuationIQ` while the app files are in `Cipla-Internship`, and the local Python venv points to a missing WindowsApps Python installation. This is an environment issue, not an identified Phase 5-7 implementation bug.

PowerShell also blocks `npm.ps1`; use `npm.cmd` on Windows when running frontend tests from PowerShell.

## Residual Non-Blocking Notes

These are not Phase 5-7 blockers, but should be kept in mind before Phase 8 and Phase 9:

- Executive Overview is intentionally not complete yet; it belongs to Phase 9.
- Full AI grounding is not started yet; it belongs to Phase 8.
- The local Python virtual environment should be recreated before the next backend test run if the WindowsApps Python path remains broken.
- Contract hardening in Phase 9 should include OpenAPI/schema drift checks across backend responses and frontend types.
