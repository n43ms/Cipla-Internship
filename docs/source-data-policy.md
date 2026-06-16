# Source Data Policy

## Raw Workbook Handling

Real Cipla Excel and XLSB files are confidential source evidence.

Rules:

- Store real workbooks in `data/raw/`.
- Do not commit real `.xlsx`, `.xlsb`, `.xls`, `.csv`, or generated extracts.
- Do not manually clean or reformat the source workbooks before ingestion.
- Preserve original filenames when practical because filenames may contain period and market context.
- Use synthetic fixtures under `ingestion/tests/fixtures/` for tests.

## Why Originals Stay Dirty

The ingestion layer is responsible for explaining and normalizing messy source files:

- header detection,
- sheet selection,
- alias mapping,
- month parsing,
- Pcode normalization,
- financial mapping,
- validation errors,
- row counts and skipped row reporting.

Cleaning source workbooks manually would make ingestion non-reproducible and weaken auditability.
