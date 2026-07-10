# Source Onboarding Playbook

## Current Received Package

The July 10 package is the source of truth for the next sponsorship ROI implementation phase.

| Point | Source | Path | Status | Use |
|---|---|---|---|---|
| 1 | Raw consolidated intervention report | `files/Raw Reports -Point 1/Consolidated Raw Report/Consolidate report All Bu's Nov'25 - 9 Jul'26.xlsx` | received | Event/intervention spine, expenses, BTC/BTU, expected/actual P-codes, HQ/territory context |
| 1 | Raw doctor-wise intervention reports | `files/Raw Reports -Point 1/Doctor Raw Report/` | received | Doctor-level Smart Contract rows, FMV amount, contracted amount, contract ID, doctor/P-code linkage |
| 2 | Cleaned presentable reports | `files/Cleaned Presentable Version - Point 2/` | received | Business-facing comparison only, not source of truth |
| 5 | Historical smart-contract ERS file | `files/Historical Smart Contracts-Point 5/ERS.xlsx` | received | Historical ERS/international-conference evidence |
| 5 | Historical RCPA files | root-level historical RCPA `.xlsb` files under `files/` | confirmed | Historical RCPA backfill |
| 6 | Monthly cumulative RCPA workbook | `files/RCPA Report All Bu's Apr'26 - 03 Jul'26.xlsx` | received | Unified all-BU monthly RCPA sample |
| 7 | MSL doctor master | `files/MSL Doctor Master File Point 7/MSL.xlsx` | received | Territory/patch/legacy-code enrichment if report-level fields are insufficient |

## Confirmed Business Rules

- Manual batch upload is the intended refresh mechanism for this phase.
- Daily extracts are saved in SharePoint, but the app should not implement SharePoint polling or SFTP.
- National Conference and International Conference are sponsored by Cipla.
- ERS is part of International, not a separate sponsorship category.
- No Fee Agreement usually follows prior sponsorship/agreement, but charity, philanthropy, or other reasons can exist.
- No-fee, speaker, consultancy, advisory, and paid honorarium are engagement evidence, not sponsorship by default.
- Accommodation and travel are under expenses; BTC/BTU are the relevant expense basis.
- Doctor-level contract data is part of Point 1; no separate doctor-contract source is required.
- `FQ HQ` in meeting/email language is equivalent to observed `FS HQ`.
- The all-BU RCPA workbook is the unified monthly sample package for convenience.
- Historical RCPA scope is confirmed through the root-level historical RCPA workbooks.
- External Varad validation output is not required for this phase.

## Official FX Rates

Use only these company-provided values. Do not use internet-rate fallback.

| Market | 1 USD equals |
|---|---:|
| Sri Lanka | 368.90 |
| Nepal | 89 |
| Oman | 0.46 |
| UAE | 1.00 |
| Myanmar | 4300 |
| Malaysia | 4.39 |

## Onboarding Workflow

1. Register the received file package in a source manifest.
2. Fingerprint each file by path, extension, signature, sheet/table shape, and required header evidence.
3. Profile every workbook/export before loader work.
4. Compare raw reports against cleaned presentable reports.
5. Record observed headers, row counts, source periods, source countries, and sample label values.
6. Create tiny synthetic fixtures from observed shapes only.
7. Write failing tests for each source-specific loader or classifier behavior.
8. Implement deterministic source handling.
9. Estimate storage before historical RCPA persistence.
10. Refresh materialized views only after compact canonical facts are validated.

## Source-Specific Notes

### Raw Consolidated Intervention

Observed priority fields:

```text
DIVISION
FS HQ
REQ_ID
Intervention Start Date
Intervention End Date
INTERVENTION DATE
INTERVENTION NAME
INTERVENTION TYPE
INTERVENTION SUB TYPE
TOTAL BTC
EXPECTED BTU
TOTAL ACTUAL EXPENSES FOR INTERVENTION
ACTUAL EXPENSE AGAINST BTU
TOTAL ACTUAL BTC EXPENSE
Association Contract ID
Association Amount
Expected PCODE
Actual PCODE
```

### Raw Doctor-Wise Intervention

These are CRM HTML exports saved with `.xls` extension. The real header row appears after title/filter preamble rows.

Observed priority fields:

```text
Division name
FS HQ
Intervention No.
Type of intervention
INTERVENTION SUBTYPE
Intervention Name
DR code
Doctor Segment
Doctor Name
Estimated Intervention Amount
BTU Expense
BTC Expense
Total Actual intervention Exp Amt
FMV amount
Contract ID
Contracted Amount
Status
```

### Monthly RCPA

The unified workbook has BU sheets for Malaysia, Myanmar, Nepal, Oman, Sri Lanka, and UAE.

Observed priority fields:

```text
BU
Location
Month
Doctor Name
Pcode
Customer Type
Speciality
Class
PATCHNAME
```

### MSL Doctor Master

Observed priority fields:

```text
Pcode
Doctor Name
BU
Location
Territory Id
Taskforce
Repname
REPCODE
Patch
Patchsname
Legacy Code
```

## Validation Checks

Required source-level checks:

- One National or International conference row is classified as sponsorship.
- ERS is handled as International/subtype evidence.
- One no-fee row is classified as engagement evidence, not sponsorship.
- One speaker/consultancy/advisory row is classified as paid/service engagement.
- One doctor-wise row computes FMV minus contracted amount.
- BTC/BTU/total actual expenses reconcile where fields are present.
- Historical RCPA rows before 1 Nov are marked manual mapping.
- Monthly cumulative RCPA rerun is idempotent.
- Territory context uses `FS HQ`, RCPA `Location`/`PATCHNAME`, and MSL `Location`/`Patch` consistently.

## Commands

Profile a folder:

```powershell
python -m ingestion.main profile --data-dir files
```

Compare raw and cleaned files:

```powershell
python -m ingestion.main compare --raw <raw-file> --cleaned <cleaned-file>
```

Check database storage:

```powershell
.\scripts\db_size_report.ps1
```

## Rule

No real Cipla workbook belongs in committed test fixtures. Tests must use synthetic fixture workbooks built from observed shapes with fake rows.
