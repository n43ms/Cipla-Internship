# Quickstart: Validate the Architecture End to End

This guide proves the planned system works as a real data product before UI polish or AI is considered complete.

## Prerequisites

- Python 3.11
- Node.js 20+
- Supabase PostgreSQL project or local PostgreSQL database
- Real source workbooks placed locally under `data/raw/`
- `.env` configured from `.env.example`
- Alembic configured with `sqlalchemy.url` resolved from `DATABASE_URL`
- Static FX seed file available under `database/seeds/exchange_rates_static.sql` or equivalent migration seed; temporary manual rates must be marked `provisional`

Required environment variables:

```text
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
DATA_DIR=data/raw
ENVIRONMENT=local
AI_PROVIDER=
AI_API_KEY=
```

`AI_PROVIDER` and `AI_API_KEY` may remain unset until the AI milestone.

The XLSB reader stack is `python-calamine` first and `pyxlsb` fallback. Do not manually convert XLSB files before ingestion.

## 1. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r ingestion/requirements.txt
npm install --prefix frontend
```

## 2. Prepare Local Data

Place the supplied workbooks in `data/raw/`:

- `Nepal & Myanmar Apr'24-Mar'25 RCPA report.xlsb`
- `Nepal & Myanmar RCPA Report Apr'25-mar'26.xlsb`
- `Sri Lanka RCPA Report Apr'25 - Mar'26.xlsb`
- `FY27 - Yearly Planner Template Nepal vf.xlsx`
- `FY27 - Yearly Planner Template Sri Lanka vf1 NEW.xlsx`
- `Consolidation report Nov'25 - 01 Jun'26 - AJ.xlsx`
- `Executiion YP Planner All BU's Apr Month.xlsx`
- `Execution YP Planner All Bu's May Month.xlsx`

Confirm these files are ignored by git.

```bash
git status --ignored --short data/raw
```

## 3. Rebuild Database

Initialize Alembic once if the repo has not been initialized yet:

```bash
alembic init database/migrations
```

Configure `alembic.ini` or `database/migrations/env.py` so `DATABASE_URL` is used as the SQLAlchemy URL. Then run:

```bash
alembic upgrade head
```

Expected outcome:

- reference tables exist,
- static exchange-rate seeds exist for supported currencies with documented `rate_date`, `source`, and `rate_status`,
- canonical tables exist,
- reconciliation tables exist,
- materialized views compile.

## 4. Profile Workbooks

```bash
python -m ingestion.main profile --data-dir data/raw --output data/reports/profile.json
```

Expected outcome:

- all eight files are classified,
- RCPA XLSB files report column aliases,
- RCPA month cells stored as Excel serial numbers are detected as valid month values,
- Nepal planner marks `Yearly Planner FY27 v2` as canonical,
- Sri Lanka planner marks `YP FY27` as canonical,
- consolidation uses `Working`,
- consolidation profile detects transcript-critical fields: `ESTIMATED INTERVENTION`, `APPROVE/CONFIRMED TOTAL INTERVENTION`, `TOTAL ACTUAL EXPENSES FOR INTERVENTION`, `ACTUAL EXPENSE AGAINST BTU`, `TOTAL ACTUAL BTC EXPENSE`, `INTERVENTION TYPE`, request pending columns, post/report pending columns, and Level 1-6 approval columns,
- May execution reports missing Sri Lanka country tab as a limitation.

## 5. Ingest, Reconcile, and Refresh

```bash
python -m ingestion.main ingest --source all
python -m ingestion.main reconcile
python -m ingestion.main refresh-views
python -m ingestion.main report --output data/reports/latest-ingestion.md
```

Expected outcome:

- ingestion run status is `completed` or `completed_with_warnings`,
- valid rows are loaded,
- invalid rows are listed with validation reasons,
- RCPA rows are aggregated before database write,
- repeated ingestion of the same RCPA file updates the same aggregate rows instead of duplicating them,
- event matches include matched, weak, and unmatched records,
- Sri Lanka May execution evidence is derived from consolidation records and marked `derived_from_consolidation`,
- budget outputs separate estimated/FMV-like value, confirmed/contracted value, direct HCP/BTU spend, overhead/BTC spend, and total actual spend,
- workflow governance outputs request approval, request confirmation, report approval, and report confirmation states,
- intervention mix outputs are grouped by source `INTERVENTION TYPE` and `INTERVENTION SUB TYPE`,
- doctor ROI outputs include quadrant labels and dark-horse flags when RCPA/spend data is sufficient,
- KPI views return rows.

## 6. Run Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Smoke checks:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/filters
curl http://localhost:8000/api/ingestion/latest
curl "http://localhost:8000/api/execution/summary?country=Nepal&month=2026-05"
```

Expected outcome:

- health returns `ok`,
- filters include countries and months,
- KPI responses include ingestion metadata and limitations.

## 7. Run Frontend

```bash
npm run dev --prefix frontend
```

Expected outcome:

- executive overview renders,
- global filters load from API,
- stale/weak/missing-data warnings are visible when applicable,
- execution matrix drills into event-level records,
- budget and doctor ROI pages handle missing FX or no-RCPA states.

## 8. Test Suite

Synthetic test fixtures live under:

```text
ingestion/tests/fixtures/
|-- xlsx/
|-- xlsb/
`-- expected/
```

Each workbook fixture should contain three to five rows. Required fixture cases:

- RCPA XLSB with `O & C`, `Own/Competitor`, `Active Status`, and `Status Doctor` aliases,
- RCPA month as Excel serial number,
- planner with multiple candidate Nepal sheets,
- April execution status using `1` and blank,
- May execution with no Sri Lanka tab,
- consolidation row with multiple expected/actual doctors and Pcodes,
- currency rows with present and missing FX.
- budget rows where estimated differs from confirmed and BTU + BTC reconcile to total actual expense.
- workflow rows with request approved, rejected, sent for correction, pending with owner, report draft, report approved, and report sent for correction statuses.

```bash
pytest ingestion/tests backend/tests
npm test --prefix frontend
```

Required coverage:

- RCPA XLSB alias parsing,
- month normalization including Excel serial numbers,
- Pcode text normalization,
- planner canonical sheet selection,
- April and May execution status normalization,
- missing Sri Lanka May execution derivation from consolidation,
- consolidation multi-doctor parsing,
- static FX seed and missing-FX behavior,
- provisional FX labeling and replacement path for future official FX,
- confirmed-vs-estimated variance,
- BTU/BTC spend split and reconciliation warning behavior,
- workflow governance status mapping,
- intervention-type grouping,
- ROI quadrant and dark-horse classification,
- AI question redaction,
- RCPA aggregate idempotency conflict target,
- event reconciliation,
- KPI view query contracts,
- frontend loading/error/empty/data-quality states.

## 9. Deployment Validation

Deploy backend, frontend, and database only after local ingestion succeeds.

Expected deployed behavior:

- dashboard access is protected,
- frontend calls backend only,
- backend holds database and AI secrets,
- ingestion can be rerun locally and views refreshed,
- demo works even when latest ingestion has warnings.
