# Data Dictionary

## Phase 3 Source Workbooks

Real workbooks live locally in `data/raw/` and are not committed.

| Workbook Family | Files | Canonical Sheet Logic | Main Output |
|---|---|---|---|
| RCPA | Nepal/Myanmar historical, Nepal/Myanmar current, Sri Lanka current | Data sheet with RCPA aliases and prescription-level fields | `rcpa_doctor_month_summary`, `rcpa_doctor_brand_summary`, `rcpa_country_brand_month_summary`, local detail extracts, and doctor seed data |
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

## Phase 4 Production Analytical Scope

Phase 4 plan-vs-actual execution KPIs default to the only country/month combinations where
planner, execution snapshot, and consolidation evidence can be reconciled fairly:

```text
Countries: Nepal, Sri Lanka
Months: 2026-04, 2026-05
```

Out-of-scope source data is not deleted. It remains in canonical/audit tables and can be inspected
with `includeOutOfScope=true`, but it is excluded from default dashboard KPI numerators and
denominators. This prevents Malaysia, Myanmar, Oman, UAE, historical consolidation, and future
planner rows from polluting Phase 4 performance metrics.

Scope fields exposed by Phase 4 views:

- `is_primary_phase4_scope`: true only for Nepal/Sri Lanka Apr-May 2026 with planner, snapshot, and consolidation evidence.
- `scope_status`: machine-readable scope classification.
- `scope_reason`: user-facing explanation for why a country/month is in or outside scope.
- `unmatched_reason_code`: reason an individual reconciliation row is unmatched or weak.
- `unmatched_reason_detail`: user-facing detail for review.
- `match_grain`: explains whether a row is a single match or a one-planned-event/one-snapshot-to-many-request case.

`mv_intervention_mix.executed_count` means true executed snapshot evidence. It does not count
generic matched requests or action-due snapshots.

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

### RCPA To Compact Summary Tables

RCPA is parsed completely, validated, and aggregated before persistence. Supabase stores compact
app-ready summaries so the project stays under the free-tier database limit. The detailed
SKU-level aggregate evidence is written locally to compressed CSV extracts under `data/processed/`
and is not committed.

Important aliases:

- `BU`, `Country` -> country
- `Month`, `Month(formated)` -> month
- `Doctor Name`, `Doctor` -> `doctor_name`
- `Pcode`, `P Code`, `PCODE` -> Pcode
- `Active Status`, `Status Doctor (Mar'25)`, `Status Doctor (Mar'26)` -> active status
- `O & C`, `Own/Competitor` -> own/competitor
- `RCPA Quantity`, `Qty`, `Quantity` -> prescription quantity
- `RCPA Value`, `Value`, `Amount` -> prescription value

Detailed local extract grain:

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

Supabase online grains:

```text
rcpa_doctor_month_summary:
source_file_id + country + month + pcode_normalized + currency_code

rcpa_doctor_brand_summary:
source_file_id + country + pcode_normalized + brand_group + own_or_competitor + currency_code

rcpa_country_brand_month_summary:
source_file_id + country + month + brand_group + own_or_competitor + currency_code
```

Summary usage:

- `rcpa_doctor_month_summary` drives Doctor ROI trend, Cipla vs competitor split, no-RCPA flags, and ROI quadrants.
- `rcpa_doctor_brand_summary` drives doctor detail brand mix without storing monthly SKU detail online.
- `rcpa_country_brand_month_summary` drives country/month/brand market trend summaries.
- `doctors` is seeded from RCPA doctor-month summaries using country-scoped Pcode uniqueness.

Pcode rules:

- text IDs with leading zeros are preserved.
- decimal-looking numeric values like `929400.0` become `929400`.
- blank, `nan`, `none`, and zero-like values are rejected.

Month rules:

- supports text months such as `Apr-24`, `25-Apr`, `Oct-25`, `Apr'26`, `May-26`.
- supports Excel serial numbers such as `45772`.

## Phase 5 Budget Utilization

`mv_budget_utilization` is the dashboard-ready budget view. It does not treat estimated values as actual spend.

Financial source semantics:

- `total_planned_cost_usd` from `plan_events` -> planned budget.
- `ESTIMATED INTERVENTION` -> `estimated_intervention_local`; reference/FMV-like value only.
- `APPROVE/CONFIRMED TOTAL INTERVENTION` -> `confirmed_contracted_amount_local`; contracted governance amount.
- `ACTUAL EXPENSE AGAINST BTU` -> direct HCP/BTU spend.
- `TOTAL ACTUAL BTC EXPENSE` -> overhead/BTC spend.
- `TOTAL ACTUAL EXPENSES FOR INTERVENTION` -> total actual spend and default ROI spend.
- `Association Amount` remains separate and is not used as default HCP spend.

FX rules:

- Sri Lanka LKR uses official company FX: `1 USD = 310 LKR`.
- Non-LKR currencies keep local values when no company FX exists and are flagged as `missing`.
- `provisional` FX is allowed only when a documented non-official rate exists.

Budget quality flags:

- `plan_without_spend`: planned event has no matched consolidation spend.
- `spend_without_plan`: consolidation spend has no matched planner row.
- `btu_btc_reconciliation_status`: `reconciled`, `mismatch`, `missing_total_actual`, or `missing_btu_btc_split`.

## Phase 6 Doctor ROI

`mv_doctor_roi` is the doctor opportunity view.

Join grain:

- doctor identity is country-scoped by `(country_id, pcode_normalized)`;
- actual attendance is read only from `request_doctors.attendance_type = 'actual'`;
- request spend is allocated evenly across parsed actual-attendance Pcodes for that request;
- RCPA prescription behavior comes from compact doctor-month summaries.

ROI fields:

- engagement count and last engagement date;
- direct HCP/BTU spend, overhead/BTC spend, and total ROI spend;
- Cipla prescription quantity/value and competitor prescription quantity/value;
- Cipla share by quantity;
- spend per Cipla prescription;
- deterministic `roi_segment`, `quadrant_label`, and `dark_horse_flag`.

Segment rules:

- `high_value_engaged`: engaged doctor with above-threshold Cipla prescription quantity.
- `high_value_unengaged`: no engagement but above-threshold Cipla prescription quantity.
- `low_rx_high_spend`: above-threshold spend with below-threshold Cipla prescription quantity.
- `no_rcpa`: engagement/doctor row without RCPA coverage.
- `insufficient_data`: available data does not justify a stronger segment.

Quadrants use country-level medians for spend and Cipla prescription quantity.

## Phase 7 Data Quality

`mv_data_quality` is the shared trust layer for dashboard pages and AI context.

It exposes:

- latest ingestion run status and file counts;
- rows seen, loaded, and skipped;
- latest validation errors/warnings;
- event match coverage;
- request-doctor Pcode coverage;
- doctor ROI RCPA coverage;
- missing/provisional FX counts;
- BTU/BTC reconciliation issues;
- missing confirmed amount counts;
- spend-without-plan and plan-without-spend counts;
- request/post workflow coverage;
- intervention type coverage;
- unmatched event count;
- Sri Lanka May consolidation-derived snapshot count.
