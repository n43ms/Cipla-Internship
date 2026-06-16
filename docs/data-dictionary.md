# Data Dictionary

## Phase 3 Source Workbooks

Real workbooks live locally in `data/raw/` and are not committed.

| Workbook Family | Files | Canonical Sheet Logic | Main Output |
|---|---|---|---|
| RCPA | Nepal/Myanmar historical, Nepal/Myanmar current, Sri Lanka current | Data sheet with RCPA aliases and prescription-level fields | `rcpa_prescriptions` aggregates and doctor seed data |
| Yearly Planner | Nepal FY27, Sri Lanka FY27 | Nepal prefers `Yearly Planner FY27 v2`; Sri Lanka uses `YP FY27` | `plan_events` |
| Consolidation | `Consolidation report Nov'25 - 01 Jun'26 - AJ.xlsx` | `Working` | `execution_requests`, `request_doctors` |
| Monthly Execution Snapshot | April and May Execution YP Planner files | April `YP`; May country tabs plus `YP`, with no Sri Lanka May tab | `execution_snapshots` |

## Source File Audit Tables

### `source_files`

Reusable workbook identity.

- `original_filename`: source workbook file name.
- `file_hash`: SHA-256 hash used for duplicate detection.
- `file_type`: `xlsx` or `xlsb`.
- `source_type`: `planner`, `execution_snapshot`, `consolidation`, or `rcpa`.
- `country_scope`: inferred countries from filename/profile.
- `detected_sheet_count`: number of sheets found by the profiler.

### `ingestion_runs`

One local ingestion attempt.

- `status`: `running`, `completed`, `completed_with_warnings`, or `failed`.
- `source_file_count`: number of files participating in the run.
- `total_rows_seen`: source rows considered by loaders.
- `total_rows_loaded`: canonical records produced.
- `total_rows_skipped`: rows intentionally skipped with validation output.
- `warning_count`, `error_count`: quality signals.
- `summary_json`: bounded run summary.

### `ingestion_run_files`

Per-run file participation.

- `status`: `profiled`, `loaded`, `skipped`, or `failed`.
- `sheets_profiled`: sheet count.
- `profile_json`: workbook profile, sheet profile, canonical sheet choice, and anomalies.

### `validation_errors`

File-level and row-level quality findings.

- `severity`: `info`, `warning`, or `error`.
- `entity_type`: intended canonical entity.
- `field_name`: affected canonical field when known.
- `sheet_name`, `row_number`: source location.
- `raw_value`: bounded raw value or row summary for debugging.

## Canonical Load Rules

### Planner To `plan_events`

Required source concepts:

- country
- month
- event name

Important aliases:

- `Name of the Event`, `Event`, `Intervention Name` -> `event_name`
- `Type of Event`, `Event Type`, `Intervention Type` -> `event_type`
- `Total Cost (USD)`, `Total cost proposed` -> `total_planned_cost_usd`

Normalization:

- event names preserve the raw display name and store `event_name_normalized` for later matching.
- month values are mapped to calendar month start dates and fiscal year labels.
- non-data/footer rows missing required values are skipped as warnings.

### Execution Snapshot To `execution_snapshots`

Required source concepts:

- event name
- country from column or sheet name
- month from column or execution workbook filename

Important aliases:

- `Name`, `Event`, `Name of the Event` -> `event_name`
- `HCP's Engaged count`, `Approved Doctors`, `Engaged HCPs` -> `engaged_hcps`
- `Raised Request Count`, `Raised Requests` -> `raised_request_count`
- `Intervention Status`, `Status` -> `status_source_value`

Status mapping:

- `1`, `Executed`, `Done`, `Completed` -> `executed`
- blank with zero raised requests, `Action due`, `Pending`, `Planned` -> `action_due`
- cancellation text -> `cancelled`
- delay text -> `delayed`
- unknown text -> `unknown`

### Consolidation To `execution_requests`

Canonical sheet:

- `Working`

Required source concepts:

- country/division
- month
- intervention name

Important mappings:

- `REQ_ID` -> `req_id`
- `DIVISION` -> country
- `Months` -> month
- `INTERVENTION NAME` -> `intervention_name`
- `INTERVENTION TYPE` -> `intervention_type`
- `APPROVE/CONFIRMED TOTAL INTERVENTION` -> `confirmed_contracted_amount_local`
- `ESTIMATED INTERVENTION` -> `estimated_intervention_local`
- `TOTAL ACTUAL EXPENSES FOR INTERVENTION` -> `actual_total_expense_local`
- `ACTUAL EXPENSE AGAINST BTU` -> `actual_btu_expense_local`
- `TOTAL ACTUAL BTC EXPENSE` -> `actual_btc_expense_local`
- `Association Amount` -> `association_amount_local`

Currency:

- country default currency is used.
- Sri Lanka uses LKR and official company FX `1 USD = 310 LKR`.
- non-LKR currencies remain local with missing FX status until company rates are provided.

### Consolidation Doctor Fields To `request_doctors`

Semi-structured fields are split into expected and actual attendance rows.

Important mappings:

- `Expected PCODE` -> expected Pcode list
- `Actual PCODE` -> actual Pcode list
- `Dr. NAME EXPECTED` -> expected doctor list
- `Dr.NAME ATTENDED` -> actual doctor list

Rules:

- preserve raw doctor name, class, and Pcode.
- normalize Pcode for joins.
- use `source_position` so duplicate or missing Pcodes do not break uniqueness.
- imperfect splits are kept with parse status instead of silently discarded.

### RCPA To `rcpa_prescriptions`

RCPA is aggregated before persistence.

Important aliases:

- `BU`, `Country` -> country
- `Month`, `Month(formated)` -> month
- `Doctor Name`, `Doctor` -> `doctor_name`
- `Pcode`, `P Code`, `PCODE` -> Pcode
- `Active Status`, `Status Doctor (Mar'25)`, `Status Doctor (Mar'26)` -> active status
- `O & C`, `Own/Competitor` -> own/competitor
- `RCPA Quantity`, `Qty`, `Quantity` -> prescription quantity
- `RCPA Value`, `Value`, `Amount` -> prescription value

Aggregate grain:

```text
source_file_id
country
month
pcode_normalized
brand_group
sku
own_or_competitor
currency_code
```

Pcode rules:

- text IDs with leading zeros are preserved.
- decimal-looking numeric values like `929400.0` become `929400`.
- blank, `nan`, `none`, and zero-like values are rejected.

Month rules:

- supports text months such as `Apr-24`, `25-Apr`, `Oct-25`, `Apr'26`, `May-26`.
- supports Excel serial numbers such as `45772`.

