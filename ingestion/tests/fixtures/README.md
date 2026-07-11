# Synthetic Workbook Fixtures

Use this folder for tiny, non-confidential workbooks that reproduce source quirks
without copying real Cipla data.

Fixture goals:

- planner canonical sheet selection,
- April/May execution status differences,
- consolidation financial and workflow columns,
- multi-doctor fields,
- RCPA aliases,
- Excel serial month values,
- text-preserved Pcodes,
- local currency and FX edge cases.

Real source workbooks belong in `data/raw/` and must never be committed.

## Schema-Readiness Fixtures

`schema_drift_raw.xlsx` and `schema_drift_cleaned.xlsx` are synthetic readiness
fixtures. They exist only to prove generic profiler and raw-vs-cleaned comparison
behavior:

- mapped canonical columns are detected through existing aliases,
- unknown columns are reported without creating source-specific code,
- empty columns are surfaced,
- representative sample values are bounded,
- raw-only and cleaned-only columns are visible before loader changes.

Do not copy real Cipla workbook rows into these files. When real sponsorship or
territory data arrives, create a new tiny synthetic fixture that preserves the
observed column shape and edge case while replacing all business values.
