# Source Data Policy

## Raw Workbook Handling

Real Cipla Excel and XLSB files are confidential source evidence.

Rules:

- Store real workbooks in `data/raw/`.
- Do not commit real `.xlsx`, `.xlsb`, `.xls`, `.csv`, or generated extracts.
- Do not manually clean or reformat the source workbooks before ingestion.
- Preserve original filenames when practical because filenames may contain period and market context.
- Use synthetic fixtures under `ingestion/tests/fixtures/` for tests.

## Raw Recurring Extracts Vs Cleaned Presentation Files

Treat raw recurring extracts and cleaned files differently:

- A raw recurring extract is the ingestion source of truth only if it is exported directly from the source system without deleted columns, renamed headers, or manual cleanup.
- A cleaned/presentable file is useful for understanding business meaning, but it is not implementation evidence unless the business confirms it is the recurring file shape.
- When both versions exist, run the raw-vs-cleaned comparison workflow before changing schema maps, loaders, migrations, APIs, frontend pages, or AI context.
- If only a cleaned file arrives, profile it and record it as `presentation source`; do not build recurring ingestion around it without confirmation.
- If no data arrives, only readiness tooling and documentation may be built.

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

## Readiness MVP Validation

The sponsorship readiness MVP intentionally avoids committing real workbooks, generated extracts, or secrets. Before completing readiness work, run:

```powershell
git status --short
```

Confirm that no real `.xlsx`, `.xlsb`, `.xls`, `.csv`, generated report, `.env`, or processed extract has been added.

Latest readiness MVP review:

```text
No real workbooks, generated extracts, generated reports, or secrets were added.
Only synthetic fixture workbooks under ingestion/tests/fixtures/xlsx are part of the readiness test surface.
```
