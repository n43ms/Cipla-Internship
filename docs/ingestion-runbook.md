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
