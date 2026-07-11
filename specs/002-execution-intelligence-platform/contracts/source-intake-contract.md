# Source Intake Contract

This contract records the received sponsorship ROI source package and the gates required before implementation.

## Package Summary

| Field | Value |
|---|---|
| Package received date | 2026-07-10 |
| Business owner | Abhijeet Mudila / EMEU PBP |
| Source location | SharePoint export copied locally under `files/` |
| Refresh strategy | Manual batch upload |
| Production integration out of scope | SFTP, SharePoint polling, data-lake auto-discovery |
| Implementation status | Profile-ready, not loader-ready until profiles and fixtures pass |

## Official FX Rates

Use only company-provided values.

| Market | 1 USD equals |
|---|---:|
| Sri Lanka | 368.90 |
| Nepal | 89 |
| Oman | 0.46 |
| UAE | 1.00 |
| Myanmar | 4300 |
| Malaysia | 4.39 |

## Source Contracts

### Point 1A: Raw Consolidated Intervention Report

| Field | Value |
|---|---|
| Path | `files/Raw Reports -Point 1/Consolidated Raw Report/Consolidate report All Bu's Nov'25 - 9 Jul'26.xlsx` |
| Source system | Smart Contract / CRM reporting |
| File type | `.xlsx` |
| Raw recurring source | yes |
| Observed shape | one sheet, 3,568 rows, 87 columns |
| Canonical use | intervention/event spine, expenses, expected/actual P-codes, HQ/territory evidence |

Required observed fields:

```text
DIVISION
FS HQ
REQ_ID
Intervention Start Date
Intervention End Date
REQUESTDATE
INTERVENTION DATE
Month
INTERVENTION NAME
INTERVENTION TYPE
INTERVENTION SUB TYPE
ESTIMATED INTERVENTION
TOTAL BTC
EXPECTED BTU
APPROVE/CONFIRMED TOTAL INTERVENTION
TOTAL ACTUAL EXPENSES FOR INTERVENTION
ACTUAL EXPENSE AGAINST BTU
TOTAL ACTUAL BTC EXPENSE
Association Contract ID
Association Amount
Expected PCODE
Actual PCODE
ACTUAL DATE OF INTERVENTION
```

Profile gates:

- [ ] Header row detected.
- [ ] Row count recorded.
- [ ] Required fields mapped.
- [ ] Unknown fields reviewed.
- [ ] BTC/BTU/total expense relationship profiled.
- [ ] `FS HQ` recorded as the territory/HQ field equivalent to the transcript's `FQ HQ` wording.

### Point 1B: Raw Doctor-Wise Intervention Reports

| Field | Value |
|---|---|
| Path | `files/Raw Reports -Point 1/Doctor Raw Report/` |
| Source system | Smart Contract / CRM reporting |
| File type | `.xls` CRM HTML export |
| Raw recurring source | yes |
| Observed shape | title/filter preamble, real headers on row 4 in inspected Sri Lanka file |
| Canonical use | doctor-level engagement, P-code, FMV, contracted amount, contract ID |

Files:

```text
Doctor Wise Intervention Report - Nepal.xls
Doctor Wise Intervention Report - Oman.xls
Doctor Wise Intervention Report - UAE.xls
Doctor Wise Intervention Report -Malaysia.xls
Doctor Wise Intervention Report -Sri Lanka.xls
Consolidated Intervention Report - Myanmar.xls
```

Required observed fields:

```text
Division name
Region
TERRITORY_CODE
FS HQ
Request Date
Expected Intervention date
Intervention No.
Type of intervention
INTERVENTION SUBTYPE
Intervention Name
DR code
Doctor Segment
Doctor Name
Estimated Intervention Amount
BTU Expense
Expense Against Advance
BTC Expense
Total Actual intervention Exp Amt
Actual intervention date
FMV Speciality
FMV Tier
FMV Role
FMV amount
Contract ID
Contracted Amount
Status
```

Profile gates:

- [ ] HTML-XLS parser handles title/filter preamble.
- [ ] Header row detected per file.
- [ ] Country/BU scope inferred from file/filter rows.
- [ ] P-code field maps from `DR code`.
- [ ] FMV and contracted amount fields are present.
- [ ] Contract ID is present where expected.

### Point 2: Cleaned Presentable Reports

| Field | Value |
|---|---|
| Path | `files/Cleaned Presentable Version - Point 2/` |
| File type | `.xlsx` |
| Raw recurring source | no |
| Canonical use | raw-vs-cleaned comparison and business-facing validation |

Files:

```text
Intervention till 8 Jul'26.xlsx
Malaysia Intervention till 8 Jul'26.xlsx
Myanmar Intervention till 8 Jul'26.xlsx
Nepal Intervention till 8 Jul'26.xlsx
Oman Intervention till 8 jul'26.xlsx
Sri lanka intervention till 8 jul'26.xlsx
```

Observed useful fields from `Intervention till 8 Jul'26.xlsx`:

```text
BU
Contract _D
REQ_ID
INTERVENTIONID
PCODE
AMOUNT
HCP_NAME
CONTRACT_TYPE_CODE
CONTRACT_TYPE
Status from consolidate
CON_AMOUNT
FMVROLE
FMVROLE_NAME
TYPE
SUBTYPE
```

Rules:

- [ ] Use for comparison only.
- [ ] Do not build ingestion source of truth from cleaned workbooks.
- [ ] Document any derived fields that do not exist in raw reports.

### Point 5A: Historical Smart Contract / ERS

| Field | Value |
|---|---|
| Path | `files/Historical Smart Contracts-Point 5/ERS.xlsx` |
| File type | `.xlsx` |
| Canonical use | historical ERS / international conference engagement evidence |

Observed fields:

```text
Event Code
BU
Month
Therapy
Therapy Detailed
Type of Event
Name of the Event
Doctor Name
HCP Speciality
Count
Honorarium
USD
```

Rules:

- [ ] ERS is part of International.
- [ ] ERS is not a separate sponsorship root category.
- [ ] This workbook is not a substitute for historical RCPA.

### Point 5B: Historical RCPA Backfill

| Field | Value |
|---|---|
| Paths | root-level historical RCPA `.xlsb` files under `files/` |
| File type | `.xlsb` |
| Canonical use | historical prescription context and pre/post engagement movement |

Files:

```text
Nepal & Myanmar Apr'24-Mar'25 RCPA report.xlsb
Nepal & Myanmar RCPA Report Apr'25-mar'26.xlsb
Sri Lanka RCPA Report Apr'25 - Mar'26.xlsb
```

Rules:

- [ ] Anything before 1 Nov is manual P-code mapping.
- [ ] Store compact summaries online; keep raw/detail evidence local.
- [ ] Profile storage impact before persistence.
- [ ] Document competitor-filter assumptions from source fields or notes.

### Point 6: Monthly Cumulative RCPA

| Field | Value |
|---|---|
| Path | `files/RCPA Report All Bu's Apr'26 - 03 Jul'26.xlsx` |
| File type | `.xlsx` |
| Cadence | monthly, around 3rd of each month |
| Format | unified all-BU workbook for convenience |
| Load mode | cumulative replacement/upsert, not blind append |

Observed sheets:

```text
Malaysia
Myanmar
Nepal
Oman
Sri Lanka
UAE
```

Observed required fields:

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

Rules:

- [ ] Headers are expected to stay stable.
- [ ] P-code is expected to be present.
- [ ] Detect covered month range.
- [ ] Rerunning the same cumulative file must not duplicate doctor-month summaries.

### Point 7: MSL Doctor Master

| Field | Value |
|---|---|
| Path | `files/MSL Doctor Master File Point 7/MSL.xlsx` |
| File type | `.xlsx` |
| Canonical use | territory/patch enrichment if report-level fields are insufficient |

Observed required fields:

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

Rules:

- [ ] Use only if Smart Contract and RCPA territory fields are insufficient.
- [ ] Preserve country/P-code identity boundary.
- [ ] Do not infer territory hierarchy from names without profiling distributions.

## Business Semantics

| Raw Label / Concept | Canonical Meaning |
|---|---|
| National Conference | sponsorship |
| International Conference | sponsorship |
| ERS | international conference evidence |
| No Fee Agreement | no-fee engagement evidence |
| Speaker | paid/service engagement evidence |
| Consultancy | paid/service engagement evidence |
| Advisory Board | paid/service engagement evidence |
| FMV amount | fair-market-value economics field |
| Contracted Amount | actual contracted economics field |
| BTC/BTU | expense components |
| FS HQ | territory/HQ field |
| Location / PATCHNAME | RCPA territory/patch fields |

## Gate Status

| Gate | Status |
|---|---|
| File package received | passed |
| Business semantics clarified | passed |
| Official FX provided | passed |
| Profiles complete | pending |
| Synthetic fixtures created | pending |
| Source-specific tests written | pending |
| Storage impact estimated | pending |
| Implementation-ready | blocked until profile/test gates pass |

## Review Checklist

- [ ] Profile every received file family.
- [ ] Create source fingerprints for XLSX, XLSB, and HTML-XLS exports.
- [ ] Compare raw reports to cleaned reports.
- [ ] Create synthetic fixtures.
- [ ] Write tests before source-specific loaders.
- [ ] Keep real workbooks out of committed fixtures.
