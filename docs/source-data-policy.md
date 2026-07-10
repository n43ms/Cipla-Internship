# Source Data Policy

## Raw Workbook Handling

Real Cipla Excel/XLSB/HTML-XLS files are confidential source evidence.

Rules:

- Keep real source files in local ignored storage such as `files/`, `data/raw/`, or dashboard-generated `data/uploads/` batches.
- Do not commit real `.xlsx`, `.xlsb`, `.xls`, `.csv`, generated extracts, `.env`, credentials, reports with business data, or processed outputs.
- Do not manually clean, rename headers, delete columns, or reformat source workbooks before profiling.
- Preserve original filenames when practical because filenames carry market, month, and source context.
- Use synthetic fixtures under `ingestion/tests/fixtures/` for tests.

## Received July 10 Package

The received package is valid for profiling:

- raw consolidated Smart Contract report,
- raw doctor-wise Smart Contract reports,
- cleaned presentable reports,
- historical smart-contract ERS workbook,
- historical RCPA XLSB workbooks,
- unified monthly all-BU RCPA workbook,
- MSL doctor master.

The app phase still uses manual batch upload. SharePoint is only the business storage/export location, not an integration target.

Dashboard uploads save files under `data/uploads/<batch-id>/`, generate a manifest for accepted
files, and write an upload summary. These generated batch folders are confidential local artifacts
and must not be committed.

## Raw Vs Cleaned Files

- Raw exports are ingestion source of truth.
- Cleaned/presentable files are comparison and validation evidence only.
- When both variants exist, compare them before schema-map, loader, migration, API, UI, or AI work.
- If a cleaned file has useful derived fields, document the transformation instead of treating the cleaned workbook as raw truth.

## FX Policy

Use only company-provided FX values:

| Market | 1 USD equals |
|---|---:|
| Sri Lanka | 368.90 |
| Nepal | 89 |
| Oman | 0.46 |
| UAE | 1.00 |
| Myanmar | 4300 |
| Malaysia | 4.39 |

Internet/public FX rates are not allowed for this phase.

## Why Originals Stay Dirty

The ingestion layer must handle:

- header detection,
- CRM HTML-XLS exports,
- sheet selection,
- alias mapping,
- month parsing,
- P-code normalization,
- financial mapping,
- validation errors,
- duplicate detection,
- row counts and skipped-row reporting.

Manual cleanup would make ingestion non-reproducible and weaken auditability.

## Git Safety Check

Before committing readiness or implementation work, run:

```powershell
git status --short
```

Confirm no real workbook, generated extract, generated report, `.env`, credential, or processed output is staged.
