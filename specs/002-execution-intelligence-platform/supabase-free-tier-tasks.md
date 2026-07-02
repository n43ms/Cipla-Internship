# Supabase Free-Tier Remediation Tasks

**Input**: `finalplan.md`, `specs/002-execution-intelligence-platform/`, `tasks.md`, live Supabase storage report showing `rcpa_prescriptions` at ~587 MB.

**Goal**: Keep the project on Supabase Free under the 500 MB limit without compromising the Phase 3 ingestion contract or later dashboard functionality. Supabase stores hot app-ready aggregates; local gitignored files preserve detailed RCPA evidence for reruns and debugging.

## Phase S1: Storage Model Correction

**Purpose**: Replace the storage-heavy RCPA online grain with compact Supabase summaries while keeping detailed RCPA extracts local.

- [X] TS001 Document the free-tier remediation plan in `specs/002-execution-intelligence-platform/supabase-free-tier-tasks.md`
- [X] TS002 Create a migration that truncates oversized `rcpa_prescriptions` data and creates compact RCPA summary tables in `database/migrations/versions/0008_supabase_free_tier_rcpa_storage.py`
- [X] TS003 Add doctor-month, doctor-brand, and country-brand-month RCPA summary builders in `ingestion/loaders/rcpa.py`
- [X] TS004 Add local detailed RCPA export support under `data/processed/` in `ingestion/processed_exports.py`
- [X] TS005 Update RCPA repository persistence to write compact summaries instead of the oversized SKU/source-grain online table in `ingestion/repositories/rcpa_repository.py`
- [X] TS006 Update ingestion orchestration so RCPA writes local detailed extracts and compact Supabase summaries in `ingestion/orchestrator.py`
- [X] TS007 Update RCPA loader and repository tests for the free-tier storage contract in `ingestion/tests/loaders/test_rcpa_loader.py` and `ingestion/tests/repositories/test_rcpa_repository.py`
- [X] TS008 Run backend and ingestion tests to verify the corrected Phase 1-3 path
- [X] TS009 Apply the migration to Supabase and verify the heavy table is emptied
- [X] TS010 Re-run RCPA ingestion and verify compact summary row counts and database size
- [X] TS011 Drop obsolete `rcpa_prescriptions` through Alembic after all active architecture references move to compact RCPA summaries in `database/migrations/versions/0009_drop_obsolete_rcpa_prescriptions.py`

## Resulting Data Contract

Supabase keeps:

- `rcpa_doctor_month_summary`: online doctor/month own-vs-competitor trend used for Doctor ROI, no-RCPA flags, Cipla share, and ROI quadrants.
- `rcpa_doctor_brand_summary`: online all-month doctor brand mix used for doctor detail drawers and brand opportunity analysis.
- `rcpa_country_brand_month_summary`: online country/month/brand market trend used for aggregate dashboards.
- `doctors`: master doctor metadata updated from RCPA summaries.

Local gitignored storage keeps:

- `data/raw/`: original Excel/XLSB files.
- `data/processed/rcpa_detail_*.csv.gz`: detailed RCPA aggregate extracts at the prior SKU-level grain for audit/debugging/reruns.

The old `rcpa_prescriptions` table is removed by Alembic head. Historical migrations still create and alter it on the way to head, but active code, docs, and Phase 4 work use the compact summary tables.
