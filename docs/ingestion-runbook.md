# Ingestion Runbook

## Purpose

This runbook explains how to profile and ingest the confidential Excel/XLSB workbooks into the canonical database model.

The raw files are never manually cleaned and never committed to git.

## Local File Placement

Place real workbooks in:

```text
data/raw/
```

Do not place real workbooks in `files/`, `docs/`, or `ingestion/tests/fixtures/`.

Ignore temporary Office lock files such as:

```text
~$Execution YP Planner All Bu's May Month.xlsx
```

The ingestion file registry skips these automatically.

## Required Environment

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies if needed:

```powershell
pip install -r backend\requirements.txt
pip install -r ingestion\requirements.txt
```

Required `.env` values:

```env
DATABASE_URL=postgresql+psycopg://...
DATA_DIR=data/raw
REPORTS_DIR=data/reports
COMPANY_LKR_PER_USD=310
```

## Profiling Without Database Writes

Run:

```powershell
python -m ingestion.main profile
```

Output:

```text
data/reports/workbook-profile-report.md
```

Use this before ingestion to verify:

- all expected files are discovered
- source types are correct
- canonical sheets are correct
- required-column coverage is acceptable
- unexpected sheets are documented but not loaded
- schema drift sections show mapped, unknown, missing, empty, and sample-value metadata

## Comparing Raw And Cleaned Workbooks

When the business provides both a raw recurring extract and a cleaned/presentable copy, compare them before changing loaders:

```powershell
python -m ingestion.main compare --raw data/raw/raw-export.xlsx --cleaned data/raw/cleaned-copy.xlsx
```

Output:

```text
data/reports/workbook-comparison-report.md
data/reports/workbook-comparison-report.json
```

Use the comparison report to identify:

- shared columns,
- raw-only columns,
- cleaned-only columns,
- normalized-header matches,
- rename candidates,
- canonical fields already covered by existing schema maps,
- columns requiring business decision.

Do not code against a cleaned-only shape unless the source intake contract confirms that it is the recurring source.

## Sponsorship Readiness Intake

The readiness MVP uses these documents:

- `docs/sponsorship-data-request.md`
- `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`
- `docs/feature-gate-policy.md`
- `docs/source-onboarding-playbook.md`
- `docs/storage-budget.md`

If even one file arrives, follow the source onboarding playbook before making loader, migration, backend, frontend, or AI changes.

## Dry-Run Ingestion

Run:

```powershell
python -m ingestion.main ingest --dry-run
```

This parses, normalizes, validates, and aggregates data without writing to Supabase.

Outputs:

```text
data/reports/ingestion-report.md
data/reports/ingestion-report.json
```

The latest real-file dry run completed with:

```text
files=8
rows_seen=1179273
rows_loaded=423693
rows_skipped=3
warnings=3
errors=0
```

`rows_loaded` counts compact online records. Detailed RCPA SKU-level aggregate evidence is
reported separately in the RCPA free-tier storage section and written to `data/processed/`.
The three warnings are skipped Nepal planner rows missing country, month, or event name. They
are treated as non-fatal skipped rows, not hidden.

The generated ingestion report includes Phase 4 scope coverage. The rule is fixed:

```text
Default Phase 4 KPIs = Nepal + Sri Lanka, Apr 2026 + May 2026 only.
```

Rows outside that scope are preserved in canonical tables for audit and future phases, but are
excluded from default Phase 4 KPI numerators and denominators. Use `includeOutOfScope=true` in
execution/intervention APIs only when auditing the full loaded workbook set.

## Source-Specific Dry Runs

Run only one source family:

```powershell
python -m ingestion.main ingest --source planner --dry-run
python -m ingestion.main ingest --source execution_snapshot --dry-run
python -m ingestion.main ingest --source consolidation --dry-run
python -m ingestion.main ingest --source rcpa --dry-run
```

## Database Ingestion

Before writing to Supabase, migrations and seed SQL must be applied.

Do not run database ingestion until:

- `alembic upgrade head` has completed
- countries are seeded
- calendar months are seeded
- exchange rates are seeded
- LKR official company rate is present

Then run:

```powershell
python -m ingestion.main ingest
```

Before large RCPA or future sponsorship/territory loads, check storage:

```powershell
.\scripts\db_size_report.ps1
```

This writes:

- audit rows
- source file identities
- validation issues
- plan events
- execution snapshots
- consolidation requests
- request doctors
- compact RCPA summaries
- local compressed RCPA detail extracts under `data/processed/`

After ingestion, refresh or recreate materialized views before checking the dashboard:

```powershell
python -m alembic upgrade head
```

The Phase 4 views classify scoped and out-of-scope records, expose unmatched reasons, and keep
matched request evidence separate from true executed snapshot evidence.

## Reruns

Reruns are expected.

File hashes prevent duplicate source file identity rows. RCPA summaries are replaced per source file
and use these online conflict grains:

```text
rcpa_doctor_month_summary:
source_file_id
country_id
calendar_month_id
pcode_normalized
currency_code

rcpa_doctor_brand_summary:
source_file_id
country_id
pcode_normalized
brand_group
own_or_competitor
currency_code

rcpa_country_brand_month_summary:
source_file_id
country_id
calendar_month_id
brand_group
own_or_competitor
currency_code
```

This means re-ingesting the same RCPA workbook updates the same summary rows instead of duplicating
them. Detailed SKU-level aggregate evidence is preserved locally in `data/processed/*.csv.gz`, not
in Supabase.

## Failure Recovery

If profiling fails:

1. Confirm the workbook is closed in Excel.
2. Remove any temporary `~$` lock files if Excel left them behind.
3. Run `python -m ingestion.main profile` again.

If dry-run ingestion reports warnings:

1. Read `data/reports/ingestion-report.md`.
2. Confirm whether skipped rows are true non-data rows.
3. Do not edit the workbook unless the business source file is truly wrong.

Validation error reporting should use `mv_latest_validation_errors` for current status. The raw
`validation_errors` table intentionally keeps historical warnings from previous ingestion runs.

If database ingestion fails:

1. Confirm migrations and seeds have been applied.
2. Confirm `DATABASE_URL` points to Supabase.
3. Re-run the same command after fixing the database setup.

## Confidentiality Rules

- Do not commit files in `data/raw/`.
- Do not commit generated detail extracts from `data/processed/`.
- Do not commit generated reports from `data/reports/`.
- Do not paste workbook excerpts into prompts unless explicitly needed.
- Do not expose database passwords or Supabase service keys.
- The frontend must not connect directly to Supabase.

## Readiness MVP Validation Commands

Focused readiness validation:

```powershell
.\.venv\Scripts\python.exe -m pytest ingestion\tests\test_profile_schema_drift.py ingestion\tests\test_workbook_compare.py ingestion\tests\test_cli_schema_readiness.py backend\tests\database\test_storage_budget_report.py -q
```

Style validation for touched readiness code:

```powershell
.\.venv\Scripts\python.exe -m ruff check ingestion\models.py ingestion\profiler.py ingestion\report.py ingestion\main.py ingestion\workbook_compare.py ingestion\tests\test_profile_schema_drift.py ingestion\tests\test_workbook_compare.py ingestion\tests\test_cli_schema_readiness.py backend\tests\database\test_storage_budget_report.py ingestion\tests\fixtures\build_fixtures.py
```
