# Source Onboarding Playbook

## One-File-Arrived Workflow

Use this workflow when any new sponsorship, contract, RCPA, doctor master, territory, or accommodation file arrives.

1. Store the real file outside git.
2. Fill `specs/002-execution-intelligence-platform/contracts/source-intake-contract.md`.
3. Run the workbook profile command.
4. If raw and cleaned versions exist, run the workbook comparison command.
5. Review mapped, unknown, missing, empty, and sample-value sections.
6. Identify confirmed columns, labels, joins, and gaps.
7. Create a tiny synthetic fixture that mirrors the observed shape but contains no real data.
8. Write failing tests for the proven behavior.
9. Update schema maps or loaders only for proven fields.
10. Estimate storage before any persistence changes.
11. Create a new source-specific task file only if gates pass.

## Commands

Profile a folder:

```powershell
python -m ingestion.main profile --data-dir data/raw
```

Compare raw and cleaned files:

```powershell
python -m ingestion.main compare --raw data/raw/raw.xlsx --cleaned data/raw/cleaned.xlsx
```

Check database storage:

```powershell
.\scripts\db_size_report.ps1
```

## Post-Data Task File Rule

Do not add sponsorship/territory implementation tasks to the readiness MVP file. Create a new post-data task file only after the source profile proves:

- actual columns,
- exact labels,
- stable join keys,
- source cadence,
- expected row count,
- storage impact,
- fixture coverage.

The post-data task file must start with ingestion and tests. Database, backend, frontend, and AI work come after deterministic source handling exists.
