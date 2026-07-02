# Cipla EMEU Execution Intelligence Platform

## Final Architecture and Implementation Plan

Prepared as the definitive architecture for the Cipla internship project.

This plan replaces the earlier `plan1.md` and `plan2.md` as the implementation source of truth. It keeps the strongest parts of both documents, incorporates the actual workbook structures inspected from the supplied Excel and XLSB files, and removes design choices that would create unnecessary risk, cost, or fragility during deployment.

---

## 1. Executive Summary

The application is a production-quality marketing execution intelligence platform for Cipla's EMEU/PBP team. It converts disconnected Excel and XLSB files into a trusted dashboard that answers:

1. Which planned marketing activities were executed, delayed, or missed?
2. Where is sanctioned budget underused or spent inefficiently?
3. Which doctors were engaged through Cipla activities?
4. Are engaged doctors actually prescribing Cipla brands?
5. Which high-prescribing doctors are not being engaged?
6. What data quality issues prevent confident decision-making?
7. Where are requests stuck in approval, confirmation, or post-event reporting?
8. Which intervention types consume effort and budget, and which generate the strongest business return?

The system must not behave like a fragile spreadsheet clone. It must behave like a serious data product: auditable ingestion, deterministic business logic, explicit reconciliation, typed APIs, polished dashboard UX, and AI summaries grounded only in trusted query results.

The final architecture is:

```text
Source Excel / XLSB files
  -> Workbook profiling
  -> Ingestion run tracking
  -> Validation and normalization
  -> Canonical business tables
  -> Explicit event reconciliation
  -> Materialized KPI views
  -> FastAPI read services
  -> React dashboard
  -> Grounded AI assistant
```

The most important architectural decision is this: the app should not treat the monthly execution planner as the only source of truth. The yearly planner, consolidation report, execution planner, and RCPA files each describe part of the business reality. The system must reconcile them transparently.

---

## 2. Source Files and Structural Findings

The architecture is based on the actual supplied files, not assumptions.

### 2.1 RCPA Files

Files:

- `Nepal & Myanmar Apr'24-Mar'25 RCPA report.xlsb`
- `Nepal & Myanmar RCPA Report Apr'25-mar'26.xlsb`
- `Sri Lanka RCPA Report Apr'25 - Mar'26.xlsb`

Observed characteristics:

- All three are XLSB files with large prescription-level row counts.
- They share the same business grain: country/BU, territory hierarchy, employee, month, doctor, Pcode, brand, SKU, own-or-competitor, quantity, value, status.
- Column names differ across files:
  - Historical Nepal/Myanmar uses `Month(formated)`, `O & C`, `Status Doctor (Mar'25)`.
  - Current Nepal/Myanmar uses `Own/Competitor`, `Status Doctor (Mar'26)`.
  - Sri Lanka uses `Active Status` and does not include the same month-formatted column.
- Month formats differ:
  - `Apr-24`
  - `25-Apr`
  - `Oct-25`
- Current-year Nepal/Myanmar and Sri Lanka RCPA month cells can also appear as Excel serial numbers such as `45772`.
- Pcodes appear numeric in the files, but must be stored as text to avoid future ID corruption.
- RCPA values are in local currencies and must not be compared across countries without currency normalization.

Implication: RCPA ingestion must use column alias maps, robust month normalization including Excel serial-number dates, text Pcode normalization, and local currency handling.

### 2.2 Yearly Planner Files

Files:

- `FY27 - Yearly Planner Template Nepal vf.xlsx`
- `FY27 - Yearly Planner Template Sri Lanka vf1 NEW.xlsx`

Observed characteristics:

- Nepal file contains both `YP FY27` and `Yearly Planner FY27 v2`.
- Nepal `Yearly Planner FY27 v2` has additional planning fields such as HO finalized information and should be treated as canonical when present.
- Sri Lanka file uses `YP FY27` as the canonical planning sheet.
- Both contain planned country, therapy, month, event type, event name, central/local, brands, honorarium HCPs, delegate HCPs, planned patients, pharmacies, operational cost, and total cost.
- Sri Lanka includes extra planning/comment fields such as `Comments`, `Country comment`, and `Total cost proposed`.
- Both contain promotional expense sheets that are useful for budget context but should be modeled separately from event-level planned activities.

Implication: planner ingestion must choose the correct canonical sheet per country and preserve country-specific extra fields without breaking the common model.

### 2.3 Consolidation Report

File:

- `Consolidation report Nov'25 - 01 Jun'26 - AJ.xlsx`

Observed characteristics:

- `Working` is the canonical operational sheet.
- It includes request IDs, country/division, intervention dates, months, venue, intervention name/type/subtype, topic, estimated budget, confirmed budget, actual expenses, expected doctors, attended doctors, expected Pcodes, actual Pcodes, approval statuses, cancellation reason, city/state, and up to six approval levels.
- It includes transcript-critical financial and workflow fields: `ESTIMATED INTERVENTION`, `APPROVE/CONFIRMED TOTAL INTERVENTION`, `TOTAL ACTUAL EXPENSES FOR INTERVENTION`, `ACTUAL EXPENSE AGAINST BTU`, `TOTAL ACTUAL BTC EXPENSE`, `Association Amount`, request approval/confirmation status, post-event report approval/confirmation status, expense submitted/confirmed dates, and approval chain columns.
- This is the richest source for actual execution and spend.
- Doctor fields are semi-structured and may contain multiple names/Pcodes per row.

Implication: this file should populate execution requests, request-doctor attendance facts, financial spend split, workflow governance, intervention mix, and post-event reporting status. It should not be reduced to a flat dashboard summary during ingestion.

### 2.4 Monthly Execution Planner Files

Files:

- `Executiion YP Planner All BU's Apr Month.xlsx`
- `Execution YP Planner All Bu's May Month.xlsx`

Observed characteristics:

- April has `Summary` and `YP`.
- May has `Summary`, country tabs, and `YP`.
- April status is represented as `1` or blank.
- May status is represented as `Executed` or `Action due`.
- May includes Nepal and Myanmar tabs, but no Sri Lanka tab.
- `YP` sheets include planned totals, raised totals, approved totals, request totals, and event-created flags.

Implication: these files are useful monthly snapshots, but they are derived artifacts. They should be stored and reconciled, not treated as the entire source of execution truth.

---

## 3. Product Scope

### 3.1 MVP Scope

The MVP should support:

- Nepal and Sri Lanka as primary countries.
- Myanmar retained in the data model because RCPA and execution files include Myanmar and because Nepal/Myanmar RCPA is bundled.
- Time period from November 2025 onward for core execution analysis.
- Historical RCPA from April 2024 to March 2025 for baseline and trend comparison.
- Execution tracking by country, month, event type, event, and therapy.
- Budget utilization by planned cost, confirmed cost, actual spend, and unspent gap.
- Budget utilization by estimated/FMV-like reference, confirmed/contracted amount, direct HCP/BTU spend, overhead/BTC spend, total actual spend, and variance.
- Doctor ROI by engagement history and RCPA prescription behavior.
- Leadership ROI quadrant showing low effort/high reward, high effort/high reward, low effort/low reward, and high effort/low reward doctors or opportunities.
- Workflow governance showing request approval location, request confirmation, post-event reporting/proof status, and pending owner/stage.
- Intervention-type mix by count, spend, execution, and workflow status.
- Data quality visibility.
- AI summaries grounded in dashboard query results.

### 3.2 Non-Goals for MVP

The MVP should not include:

- User-authored ingestion from the browser.
- Manual event-match editing UI.
- Full role-based enterprise permissions.
- Automated scheduled ingestion.
- Direct Power BI embedding.
- AI-based matching or AI-based KPI calculation.
- Proof image/agenda content inspection; the supplied workbook supports reporting/proof status, not actual proof-file analysis.

These can be added later after the core data path is trusted.

---

## 4. System Architecture

### 4.1 Layer Responsibilities

#### Ingestion Layer

Python CLI responsible for:

- File discovery.
- File hashing.
- Workbook profiling.
- Source type detection.
- Header detection.
- Row validation.
- Column alias mapping.
- Date/month normalization.
- Pcode normalization.
- Currency annotation.
- Financial mapping for estimated, confirmed/contracted, BTU, BTC, total actual, and association amounts.
- Workflow lifecycle parsing for request approval, request confirmation, report approval, and report confirmation statuses.
- Upserts into canonical tables.
- Event reconciliation.
- Materialized view refresh.
- Ingestion report generation.

The ingestion layer is the only layer allowed to write source-derived business data.

#### Database Layer

Supabase PostgreSQL responsible for:

- Persistent canonical business facts.
- Referential integrity.
- Unique constraints.
- Reconciliation tables.
- Data quality records.
- Materialized KPI views.
- Query performance.

The database is the analytical source of truth.

#### Backend Layer

FastAPI responsible for:

- Read-only dashboard APIs.
- Typed request/response schemas.
- Filter validation.
- Querying materialized views and canonical detail tables.
- AI orchestration.
- Error handling.
- API-level observability.

Route handlers stay thin. Business logic lives in services.

#### Frontend Layer

React + TypeScript responsible for:

- Dashboard layout.
- Filters.
- Tables.
- Charts.
- Drilldowns.
- Data quality warnings.
- Workflow governance views.
- Intervention mix views.
- ROI quadrant views.
- Loading, empty, error, and stale states.
- AI panel UI.

The frontend must not query Supabase directly and must not call the AI provider directly.

#### AI Layer

Backend service responsible for:

- Accepting plain-English questions.
- Fetching deterministic context from KPI/detail services.
- Sending compact structured context to the model.
- Returning concise, source-grounded responses.

AI never calculates KPIs and never invents missing facts.

---

## 5. Technology Stack

### 5.1 Backend and Ingestion

- Python 3.11 or 3.12.
- FastAPI.
- Pydantic v2.
- Pydantic Settings.
- SQLAlchemy 2.0 with PostgreSQL driver as the primary data layer.
- Alembic for migrations.
- Pandas for lightweight transformations where useful.
- `openpyxl` for XLSX files.
- `python-calamine` as the primary XLSB reader.
- `pyxlsb` as a fallback for workbook-specific reader issues.
- `pytest` for ingestion and service tests.
- `ruff` for linting and formatting.

### 5.2 Frontend

- React.
- TypeScript.
- Vite.
- Tailwind CSS.
- React Query.
- Zustand for global filter state.
- Recharts for charts.
- Lucide React for icons.

### 5.3 Database

- Supabase PostgreSQL.
- SQL migrations committed to the repo.
- Materialized views for dashboard KPIs.
- Indexes on country, month, event, Pcode, request ID, and match status.

### 5.4 AI Provider

Use one backend-only LLM provider key through environment variables. The provider can be Anthropic or OpenAI, but the interface should be wrapped in an internal `AIService` so the vendor is replaceable.

---

## 6. Repository Structure

Use a single repository with clear boundaries:

```text
cipla-internship/
  backend/
    app/
      main.py
      config.py
      database.py
      routers/
      services/
      schemas/
      utils/
    tests/

  ingestion/
    main.py
    config.py
    profiler.py
    validators.py
    normalizers.py
    report.py
    loaders/
      planner.py
      execution_snapshot.py
      consolidation.py
      rcpa.py
    reconciliation/
      event_matcher.py
    tests/

  frontend/
    src/
      api/
      components/
      charts/
      pages/
      hooks/
      store/
      types/
      utils/

  database/
    migrations/
    views/
    seeds/

  data/
    raw/
    processed/
    reports/

  docs/
    data-dictionary.md
    ingestion-runbook.md
    deployment.md

  .env.example
  .gitignore
  README.md
```

Source workbooks remain in `data/raw/` locally and must not be committed.

---

## 7. Database Design

### 7.1 Audit Tables

#### `ingestion_runs`

Tracks each ingestion attempt.

Fields:

- `id`
- `started_at`
- `completed_at`
- `status`: `running`, `completed`, `failed`, `completed_with_warnings`
- `triggered_by`
- `source_file_count`
- `total_rows_seen`
- `total_rows_loaded`
- `total_rows_skipped`
- `error_count`
- `warning_count`
- `summary_json`

#### `source_files`

Tracks reusable file identity. It does not represent run participation because the same workbook hash may be profiled or ingested in multiple runs.

Fields:

- `id`
- `original_filename`
- `file_hash`
- `file_type`: `xlsx`, `xlsb`
- `source_type`: `planner`, `execution_snapshot`, `consolidation`, `rcpa`
- `country_scope`
- `period_start`
- `period_end`
- `detected_sheet_count`
- `created_at`

Unique constraint:

- `file_hash`

#### `ingestion_run_files`

Connects a reusable source file to a specific ingestion run and stores run-specific profiling and load results.

Fields:

- `id`
- `ingestion_run_id`
- `source_file_id`
- `local_path_snapshot`
- `status`: `pending`, `profiled`, `loaded`, `skipped`, `failed`
- `sheets_profiled`
- `rows_seen`
- `rows_loaded`
- `rows_skipped`
- `warnings`
- `errors`
- `profile_json`

Unique constraint:

- `ingestion_run_id`, `source_file_id`

#### `validation_errors`

Stores row-level and file-level issues.

Fields:

- `id`
- `ingestion_run_id`
- `source_file_id`
- `sheet_name`
- `row_number`
- `severity`: `info`, `warning`, `error`
- `entity_type`
- `field_name`
- `error_code`
- `message`
- `raw_value`

### 7.2 Reference Tables

#### `countries`

Fields:

- `id`
- `name`
- `code`
- `default_currency_code`

Seed:

- Sri Lanka: `LKR`
- Nepal: `NPR`
- Myanmar: `MMK`
- Oman: `OMR`
- UAE: `AED`
- Malaysia: `MYR`

#### `calendar_months`

Fields:

- `id`
- `month_start_date`
- `month_label`
- `fiscal_year`
- `fiscal_month_number`
- `calendar_year`
- `calendar_month_number`

Fiscal year starts in April.

Examples:

- `Apr'26` -> `2026-04-01`, `FY27`, fiscal month 1.
- `Nov-25` -> `2025-11-01`, `FY26`, fiscal month 8.

#### `exchange_rates`

Fields:

- `id`
- `currency_code`
- `rate_to_usd`
- `rate_date`
- `source`

MVP behavior:

- Store local amounts reliably.
- Seed LKR with the official company exchange rate `1 USD = 310 LKR` (`rate_to_usd = 1/310`, `source = company`, `rate_status = official`). Seed other currencies only when a documented company or provisional rate exists.
- Use USD amounts only where a seeded exchange rate exists; Sri Lanka/LKR USD values must use the official `1 USD = 310 LKR` rate.
- Temporary manual rates are allowed only for currencies without company-approved rates and must be marked `provisional`; LKR is already official at `1 USD = 310 LKR`.
- Do not compare local-currency values across countries without normalization.

### 7.3 Canonical Business Tables

#### `plan_events`

Canonical planned activities from yearly planners.

Fields:

- `id`
- `source_file_id`
- `country_id`
- `calendar_month_id`
- `fiscal_year`
- `therapy`
- `event_type`
- `event_name`
- `event_name_normalized`
- `central_or_local`
- `brand_name_1`
- `brand_name_2`
- `planned_honorarium_hcps`
- `honorarium_cost_per_hcp_usd`
- `total_honorarium_cost_usd`
- `planned_delegate_hcps`
- `planned_patients`
- `planned_total_hcps`
- `planned_pharmacies`
- `operational_cost_per_unit_usd`
- `total_operational_cost_usd`
- `total_planned_cost_usd`
- `comments`
- `country_comment`
- `ho_finalized`
- `source_sheet_name`
- `source_row_number`

Unique key:

- `country_id`, `calendar_month_id`, `event_type`, `event_name_normalized`, `source_file_id`

#### `execution_snapshots`

Rows from monthly Execution YP Planner files.

Fields:

- `id`
- `source_file_id`
- `country_id`
- `calendar_month_id`
- `therapy`
- `event_type`
- `event_name`
- `event_name_normalized`
- `planned_hcps`
- `engaged_hcps`
- `raised_request_count`
- `intervention_status`
- `status_source_value`
- `yp_total_doctors`
- `yp_total_chemist`
- `raised_total_doctors`
- `approved_total_doctors`
- `request_total_doctors`
- `event_created_count`
- `source_sheet_name`
- `source_row_number`

Status normalization:

- `Executed` -> `executed`
- `Action due` -> `action_due`
- `1` -> `executed`
- blank with zero raised requests -> `action_due`
- unknown/unparseable -> `unknown` and validation warning

#### `execution_requests`

Canonical smart-contract request records from consolidation report.

Fields:

- `id`
- `source_file_id`
- `req_id`
- `country_id`
- `calendar_month_id`
- `rep_code`
- `rep_name`
- `intervention_date`
- `actual_intervention_date`
- `venue`
- `intervention_name`
- `intervention_name_normalized`
- `intervention_type`
- `intervention_sub_type`
- `topic_remarks`
- `estimated_intervention_local`
- `confirmed_contracted_amount_local`
- `confirmed_vs_estimated_variance_local`
- `actual_total_expense_local`
- `actual_btu_expense_local`
- `actual_btc_expense_local`
- `association_amount_local`
- `association_contract_id`
- `association_deliverables`
- `currency_code`
- `fx_rate_to_usd`
- `fx_rate_source`
- `fx_rate_date`
- `fx_rate_status`: `official`, `provisional`, `missing`
- `estimated_intervention_usd`
- `confirmed_contracted_amount_usd`
- `confirmed_vs_estimated_variance_usd`
- `actual_total_expense_usd`
- `actual_btu_expense_usd`
- `actual_btc_expense_usd`
- `direct_hcp_spend_local`
- `direct_hcp_spend_usd`
- `overhead_spend_local`
- `overhead_spend_usd`
- `total_roi_spend_local`
- `total_roi_spend_usd`
- `expected_customer_count`
- `attended_customer_count`
- `expected_category_raw`
- `attended_category_raw`
- `approval_status`
- `confirmation_status`
- `request_approval_status`
- `request_confirmation_status`
- `post_approval_status`
- `post_confirmation_status`
- `expense_submitted_date`
- `expense_confirmed_date`
- `current_owner_stage`
- `cancellation_reason`
- `city`
- `state`
- `approval_chain_json`
- `source_row_number`

Unique key:

- `source_file_id`, `req_id` when `req_id` is present and valid.
- fallback `request_uid` generated from source system, country, source row, intervention date, intervention name, and rep code when `req_id` is missing or invalid.

Validation:

- duplicate `req_id` values within a source file are blocking validation errors unless the rows are byte-identical retries.
- cross-file duplicate `req_id` values are flagged for review but not assumed invalid until source-system scope is confirmed.

Transcript-verified financial mapping:

- `APPROVE/CONFIRMED TOTAL INTERVENTION` -> confirmed/contracted amount.
- `ESTIMATED INTERVENTION` -> estimated/FMV-like reference only.
- `ACTUAL EXPENSE AGAINST BTU` -> direct HCP/BTU spend.
- `TOTAL ACTUAL BTC EXPENSE` -> overhead/BTC spend.
- `TOTAL ACTUAL EXPENSES FOR INTERVENTION` -> total actual spend and default ROI spend.
- `Association Amount` -> separate association/event amount, not default contracted HCP spend.

#### `request_doctors`

Normalized expected and actual doctor participation per request.

Fields:

- `id`
- `execution_request_id`
- `attendance_type`: `expected`, `actual`
- `doctor_name_raw`
- `doctor_class_raw`
- `pcode_raw`
- `pcode_normalized`
- `parse_status`
- `source_position`

Unique key:

- `execution_request_id`, `attendance_type`, `source_position`

Do not use `pcode` alone in the unique key because some records may lack Pcode or contain duplicate malformed entries.

#### `doctors`

Doctor master data, primarily seeded from RCPA.

Fields:

- `id`
- `pcode_normalized`
- `latest_doctor_name`
- `country_id`
- `speciality`
- `doctor_class`
- `patch_name`
- `active_status`
- `first_seen_month_id`
- `last_seen_month_id`
- `source_count`
- `updated_at`

Unique key:

- `country_id`, `pcode_normalized`

Validation:

- cross-country Pcode reuse is allowed and reported as a data-quality observation.
- same-country duplicate Pcodes with conflicting doctor names/classes are validation warnings requiring review.

#### `rcpa_doctor_month_summary`

Compact online doctor/month prescription summary.

Fields:

- `id`
- `source_file_id`
- `country_id`
- `calendar_month_id`
- `pcode_raw`
- `pcode_normalized`
- `doctor_name`
- `speciality`
- `doctor_class`
- `patch_name`
- `active_status`
- `own_prescription_qty`
- `own_prescription_value_local`
- `competitor_prescription_qty`
- `competitor_prescription_value_local`
- `total_prescription_qty`
- `total_prescription_value_local`
- `currency_code`
- `row_count_aggregated`

Unique key:

- `source_file_id`, `country_id`, `calendar_month_id`, `pcode_normalized`, `currency_code`

This table drives Doctor ROI trend, Cipla-vs-competitor split, no-RCPA flags, and ROI quadrant reward metrics.

#### `rcpa_doctor_brand_summary`

Compact online all-period doctor brand mix.

Fields:

- `id`
- `source_file_id`
- `country_id`
- `first_calendar_month_id`
- `last_calendar_month_id`
- `pcode_normalized`
- `doctor_name`
- `brand_group`
- `own_or_competitor`
- `prescription_qty`
- `prescription_value_local`
- `currency_code`
- `row_count_aggregated`

Unique key:

- `source_file_id`, `country_id`, `pcode_normalized`, `brand_group`, `own_or_competitor`, `currency_code`

This table supports doctor detail brand mix without storing every monthly SKU row online.

#### `rcpa_country_brand_month_summary`

Compact online country/month/brand trend.

Fields:

- `id`
- `source_file_id`
- `country_id`
- `calendar_month_id`
- `brand_group`
- `own_or_competitor`
- `prescription_qty`
- `prescription_value_local`
- `currency_code`
- `row_count_aggregated`

Unique key:

- `source_file_id`, `country_id`, `calendar_month_id`, `brand_group`, `own_or_competitor`, `currency_code`

This table supports aggregate brand trend analysis.

Detailed SKU-level RCPA aggregate evidence is stored locally under `data/processed/*.csv.gz` and is not loaded into Supabase. Do not store every raw or SKU-level RCPA row in Postgres for MVP.

### 7.4 Reconciliation Tables

#### `event_matches`

Explicit mapping between planner events, execution snapshots, and consolidation requests.

Fields:

- `id`
- `country_id`
- `calendar_month_id`
- `plan_event_id`
- `execution_snapshot_id`
- `execution_request_id`
- `match_method`: `exact`, `normalized`, `fuzzy`, `manual`
- `match_confidence`
- `match_status`: `matched`, `weak_match`, `unmatched`, `ignored`
- `matched_on`
- `notes`
- `created_at`
- `updated_at`

Matching rules:

1. Exact country, month, event type, normalized name.
2. Normalized name after removing suffixes like `- Apr`, `- May`, `(New)`.
3. Conservative fuzzy match only above a defined confidence threshold.
4. Leave weak or missing matches visible in the data quality dashboard.
5. Add manual overrides later, not in MVP.

### 7.5 AI Tables

#### `ai_query_logs`

Fields:

- `id`
- `created_at`
- `country_id`
- `calendar_month_id`
- `question_redacted`
- `context_summary_json`
- `answer`
- `model`
- `latency_ms`
- `error_message`

Do not log secrets, raw oversized prompts, source row payloads, or raw workbook excerpts. Redact Pcode-like identifiers, monetary values, and likely doctor-name spans before persistence.

---

## 8. Materialized Views

### `mv_execution_kpis`

Purpose:

- Fast dashboard summary for execution.

Includes:

- country
- month
- total planned events
- matched events
- unmatched events
- executed events
- action due events
- planned HCPs
- engaged HCPs
- HCP execution rate
- event execution rate
- match coverage rate

### `mv_budget_utilization`

Purpose:

- Budget planned vs confirmed vs actual.

Includes:

- planned budget USD
- estimated/FMV-like intervention reference
- confirmed/contracted amount
- confirmed-vs-estimated variance
- direct HCP/BTU spend
- overhead/BTC spend
- confirmed budget local/USD
- actual spend local/USD
- unspent gap
- overrun amount
- events with spend but no plan match
- events with plan but no actual spend
- FX source/date/status including provisional manual rates

### `mv_workflow_governance`

Purpose:

- Show where requests and post-event reports are stuck.

Includes:

- country
- month
- rep
- intervention type/subtype
- request approval status
- request confirmation status
- post/report approval status
- post/report confirmation status
- current owner/stage
- pending request count
- pending report count
- reports sent for correction
- reports approved
- expense submitted/confirmed date coverage

### `mv_intervention_mix`

Purpose:

- Show activity mix by intervention type and subtype.

Includes:

- intervention type
- intervention subtype
- request count
- approved/executed count
- report pending count
- confirmed/contracted amount
- direct HCP/BTU spend
- overhead/BTC spend
- total actual spend
- FX status

### `mv_doctor_roi`

Purpose:

- Doctor engagement vs prescription behavior.

Includes:

- pcode
- doctor name
- country
- speciality
- doctor class
- engagement count
- last engagement date
- total actual spend associated with doctor
- Cipla prescription quantity
- competitor prescription quantity
- Cipla prescription value
- competitor prescription value
- Cipla share by quantity
- spend per Cipla prescription
- ROI quadrant x/y values
- ROI quadrant label
- dark-horse flag
- segment:
  - high_value_engaged
  - high_value_unengaged
  - low_rx_high_spend
  - insufficient_data

Quadrants:

- low effort / high reward
- high effort / high reward
- low effort / low reward
- high effort / low reward

Dark-horse doctors are low effort / high reward opportunities.

### `mv_data_quality`

Purpose:

- Leadership-visible ingestion and reconciliation quality.

Includes:

- latest ingestion status
- files loaded
- rows seen
- rows skipped
- validation errors
- planner events
- execution snapshot rows
- consolidation requests
- RCPA rows aggregated
- event match coverage
- Pcode coverage
- RCPA doctor coverage

### `mv_unmatched_events`

Purpose:

- Operational list of records requiring review.

Includes:

- country
- month
- source type
- event name
- event type
- reason
- candidate match if available
- confidence

---

## 9. Ingestion Design

### 9.1 Ingestion CLI Commands

Use a Python CLI with commands:

```bash
python -m ingestion.main profile
python -m ingestion.main ingest --source all
python -m ingestion.main ingest --source planner
python -m ingestion.main ingest --source consolidation
python -m ingestion.main ingest --source execution
python -m ingestion.main ingest --source rcpa
python -m ingestion.main reconcile
python -m ingestion.main refresh-views
python -m ingestion.main report
```

### 9.2 Ingestion Run Order

Full run:

1. Create `ingestion_runs` row.
2. Register source files with file hashes.
3. Profile workbooks and sheets.
4. Load countries and calendar months.
5. Ingest planner events.
6. Ingest consolidation requests.
7. Ingest monthly execution snapshots.
8. Ingest RCPA aggregates and doctors.
9. Run event reconciliation.
10. Refresh materialized views.
11. Persist validation and quality summary.
12. Mark ingestion run complete or complete with warnings.

### 9.3 Workbook Profiling

Profiler must detect:

- workbook type
- sheet names
- used ranges
- likely header row
- column names
- row count
- sample rows
- required column presence
- source-specific anomalies

Profiler output should be printable as a table and persisted in the ingestion run summary.

### 9.4 Column Alias Strategy

Each loader must define a source-specific alias map.

RCPA aliases:

```text
country: BU
month: Month, Month(formated)
doctor_name: Doctor Name
pcode: Pcode
active_status: Active Status, Status Doctor (Mar'25), Status Doctor (Mar'26)
own_or_competitor: O & C, Own/Competitor
quantity: RCPA Quantity
value: RCPA Value
```

Planner aliases:

```text
country: Country
therapy: Therapy
month: Month
event_type: Type of Event
event_name: Name of the Event
central_or_local: Central/Local
brand_name_1: Brand Name 1
brand_name_2: Brand Name 2
planned_honorarium_hcps: # No. of Doctors as Speakers...
planned_delegate_hcps: # No. of Doctors as Delegates...
planned_total_hcps: # Total Planned Docs
planned_pharmacies: # Total Planned Pharmacy
total_planned_cost_usd: Total Cost (USD)
```

Consolidation aliases:

```text
country: DIVISION
req_id: REQ_ID
month: Months
intervention_name: INTERVENTION NAME
intervention_type: INTERVENTION TYPE
estimated_intervention: ESTIMATED INTERVENTION
confirmed_contracted_amount: APPROVE/CONFIRMED TOTAL INTERVENTION
actual_total_expense: TOTAL ACTUAL EXPENSES FOR INTERVENTION
actual_btu_expense: ACTUAL EXPENSE AGAINST BTU
actual_btc_expense: TOTAL ACTUAL BTC EXPENSE
association_amount: Association Amount
expected_pcodes: Expected PCODE
actual_pcodes: Actual PCODE
expected_doctors: Dr. NAME EXPECTED
actual_doctors: Dr.NAME ATTENDED
```

### 9.5 Normalization Rules

#### Event Name Normalization

Normalize for matching only; preserve raw names.

Rules:

- lowercase
- trim whitespace
- collapse repeated spaces
- normalize punctuation
- remove trailing month suffixes like `- Apr`, `- May`, `- Apr 2026`
- remove harmless labels like `(New)` only for matching
- preserve original display name

#### Month Normalization

Map all observed source month formats to `calendar_months`.

Supported examples:

- `Apr-24`
- `25-Apr`
- `Oct-25`
- `Apr'26`
- `May-26`
- Excel serial dates

Excel serial numbers such as `45772` are expected in current RCPA files and must be parsed as valid month inputs, not validation failures.

#### Pcode Normalization

Rules:

- read as string
- trim whitespace
- convert numeric-looking decimals such as `929400.0` to `929400`
- reject empty, `nan`, `none`, and zero-like values
- preserve `pcode_raw`
- use `pcode_normalized` for joins

#### Currency Handling

Rules:

- preserve local value and currency code
- compute USD only when a static seeded exchange rate exists in MVP
- label manual temporary rates as provisional until official company rates are provided; LKR uses official company FX at `1 USD = 310 LKR`
- label metrics clearly when local currency is used
- avoid cross-country monetary comparisons without USD normalization

#### Sri Lanka May Execution Derivation

Because the May monthly execution planner has no Sri Lanka country tab, Sri Lanka May execution evidence must be derived deterministically from consolidation `Working` rows:

1. Filter consolidation requests to Sri Lanka and May 2026.
2. Group by normalized intervention name, intervention type/subtype, country, and calendar month.
3. Compute raised request count, approved/confirmed evidence, attended HCPs, actual spend, and status from consolidation fields.
4. Insert execution snapshot rows with `snapshot_source = derived_from_consolidation`.
5. Expose a data-quality limitation explaining that these rows were derived from consolidation, not from a monthly execution tab.

---

## 10. Backend API Design

All backend APIs are read-only for MVP except AI query logging.

### 10.1 Endpoints

#### `GET /api/health`

Returns service status.

#### `GET /api/filters`

Returns available countries, months, therapies, event types, brands, and latest ingestion metadata.

#### `GET /api/ingestion/latest`

Returns latest ingestion run summary.

#### `GET /api/data-quality`

Returns data quality summary from `mv_data_quality` and unmatched event counts.

#### `GET /api/workflow/summary`

Returns request approval, request confirmation, report approval, report confirmation, and owner/stage counts.

#### `GET /api/workflow/requests`

Returns request-level workflow governance rows with pagination.

#### `GET /api/interventions/mix`

Returns intervention type/subtype counts, spend, execution, reporting, and FX status.

#### `GET /api/execution/summary`

Query params:

- `country`
- `month`
- `therapy`
- `event_type`

Returns KPI summary from `mv_execution_kpis`.

#### `GET /api/execution/events`

Returns event-level execution matrix with match status.

#### `GET /api/budget/summary`

Returns budget utilization summary and event-level budget gaps.

#### `GET /api/doctors/roi`

Returns doctor ROI table/scatter data.

Filters:

- country
- month range
- brand
- speciality
- doctor class
- ROI segment

#### `GET /api/doctors/{pcode}`

Returns doctor detail:

- profile
- engagement history
- prescription trend
- brand mix
- spend association
- data quality flags

#### `POST /api/ai/query`

Request:

- `question`
- `country`
- `month`
- `page_context`
- optional filters

Response:

- `answer`
- `supporting_metrics`
- `limitations`
- `confidence`

### 10.2 Backend Service Rules

- Routers handle HTTP concerns only.
- Services query database views and canonical tables.
- Pydantic schemas define all request and response contracts.
- Never return raw database exceptions to the client.
- Log internal errors with enough detail for debugging.
- Use pagination for event and doctor tables.
- Use deterministic SQL/Python calculations for all KPIs.

---

## 11. Frontend UX Architecture

### 11.1 Pages

#### Executive Overview

Purpose:

- First screen for leadership.

Includes:

- data freshness banner
- execution rate card
- HCP engagement rate card
- budget utilization card
- doctor ROI opportunity card
- data quality warning card
- monthly trend chart
- top risks list

#### Execution Matrix

Purpose:

- Show plan vs actual execution by event.

Includes:

- country/month filters
- KPI cards
- planned vs engaged HCP chart
- event table
- match confidence badge
- status badge
- drilldown side panel

#### Budget Utilization

Purpose:

- Show budget approved, spent, underused, and overrun.

Includes:

- budget summary cards
- estimated vs confirmed/contracted amount
- direct HCP/BTU spend
- overhead/BTC spend
- total actual spend
- planned vs actual spend chart
- event-level gap table
- country/local currency labels
- warnings for missing or provisional FX

#### Workflow Governance

Purpose:

- Show where requests and post-event reporting are stuck.

Includes:

- request approval location
- request confirmation status
- request approved/rejected/corrected/deleted/draft counts
- post-event report draft/pending/approved/sent-for-correction counts
- owner/stage drilldown
- rep-level pending count where available

#### Intervention Mix

Purpose:

- Show what activity types each market is executing.

Includes:

- intervention type/subtype breakdown
- request count
- approved/executed count
- spend by intervention type
- report pending status by intervention type

#### Doctor ROI

Purpose:

- Connect doctor engagement to prescription behavior.

Includes:

- scatter plot: engagement/spend vs prescriptions
- ROI quadrant matrix
- segments
- top prescribing unengaged doctors
- high spend low prescription doctors
- low effort/high reward dark-horse doctors
- doctor detail drawer

#### Data Quality

Purpose:

- Make uncertainty visible instead of hiding it.

Includes:

- latest ingestion run
- file-level row counts
- validation errors
- event match coverage
- Pcode coverage
- BTU/BTC reconciliation issues
- missing confirmed/contracted amount count
- provisional FX count
- workflow status coverage
- intervention type coverage
- unmatched events table
- RCPA coverage summary

#### AI Assistant

Purpose:

- Provide concise summaries and guided exploration.

Includes:

- fixed right-side panel
- suggested prompts
- grounded answers
- cited metrics
- limitations

### 11.2 Frontend State

Use React Query for server state.

Use Zustand only for UI/global filters:

- selected country
- selected month
- selected therapy
- selected event type
- selected brand

### 11.3 Required UI States

Every page must handle:

- loading
- error
- empty data
- stale ingestion
- weak match coverage
- missing FX
- no RCPA coverage

No blank screens.

---

## 12. AI Design

The AI assistant is a reporting assistant, not an autonomous analyst.

### 12.1 Allowed AI Behavior

AI may:

- summarize current KPI state
- explain high-risk events
- list budget gaps
- summarize top doctor ROI opportunities
- explain data quality limitations
- turn deterministic query results into readable language

### 12.2 Forbidden AI Behavior

AI must not:

- invent metrics
- infer missing rows
- calculate ROI from raw text
- decide event matches
- classify doctors without structured data
- hide data quality limitations

### 12.3 AI Context Construction

Before calling the model, backend must:

1. Determine page context and filters.
2. Query relevant KPI/detail services.
3. Build compact structured context.
4. Include data quality flags.
5. Ask the model for concise output only.

Every answer should include either:

- supporting metrics, or
- a clear statement that the available data cannot answer the question.

---

## 13. Deployment Architecture

### 13.1 MVP Deployment

Recommended:

- Frontend: Vercel.
- Backend: Render, Railway, Fly.io, or similar Python-friendly host.
- Database: Supabase Postgres.
- Ingestion: local CLI run from developer machine.

Reason:

- Keeps ingestion simple and controllable.
- Avoids browser-upload security and timeout issues.
- Lets the dashboard be deployed and demoable quickly.

### 13.2 Environment Variables

Required:

```text
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ANON_KEY=
DATABASE_URL=
AI_PROVIDER=
AI_API_KEY=
DATA_DIR=
ENVIRONMENT=
```

Rules:

- service role key only in ingestion/backend server environment
- never expose service role key to frontend
- frontend uses only backend API URL

### 13.3 Git Ignore Rules

The repo must ignore:

```text
.env
.venv/
node_modules/
data/raw/
data/processed/
data/reports/
outputs/
*.xlsb
*.xlsx
```

If sample files are needed for tests, use tiny synthetic fixtures, not real Cipla files. Fixture files live under `ingestion/tests/fixtures/xlsx/`, `ingestion/tests/fixtures/xlsb/`, and expected outputs under `ingestion/tests/fixtures/expected/`. Each fixture should contain three to five rows and target a specific edge case.

---

## 14. Testing Strategy

### 14.1 Ingestion Tests

Required tests:

- workbook profiler recognizes all eight supplied file types
- Nepal planner selects `Yearly Planner FY27 v2`
- Sri Lanka planner selects `YP FY27`
- April execution status maps `1` to executed
- April blank status maps correctly
- May execution status maps `Executed` and `Action due`
- Sri Lanka missing May execution tab derives labeled execution evidence from consolidation
- consolidation parses request ID, dates, spend, approval statuses
- consolidation maps estimated, confirmed/contracted, BTU, BTC, total actual, association amount, and variance fields
- consolidation maps request approval, request confirmation, post/report approval, and post/report confirmation statuses
- consolidation parses multi-doctor expected and actual Pcode fields
- RCPA parser handles `O & C` and `Own/Competitor`
- RCPA parser handles `Active Status` and `Status Doctor`
- month parser handles all observed formats, including Excel serial-number month values
- Pcode parser preserves normalized text IDs
- validation errors are recorded for malformed rows

### 14.2 Database Tests

Required checks:

- unique constraints prevent duplicate ingestion
- materialized views refresh successfully
- event match coverage is computed
- Pcode coverage is computed
- unmatched events appear in `mv_unmatched_events`
- doctor ROI view does not divide by zero
- currency fields are not mixed silently
- static FX seed rows exist, including official LKR at `1 USD = 310 LKR`, and missing-FX behavior is visible
- provisional FX rows for non-official currencies are labeled and can be replaced by official company FX
- repeated RCPA ingestion updates existing aggregate rows through the explicit unique key
- BTU plus BTC reconciles to total actual spend where populated, otherwise warning is visible
- workflow governance and intervention mix views refresh successfully
- ROI quadrant labels are deterministic

### 14.3 API Tests

Required tests:

- health endpoint returns OK
- filters endpoint returns available countries and months
- KPI endpoints return typed responses
- invalid country/month returns 400 or 404 cleanly
- event tables paginate
- doctor ROI endpoint handles no RCPA data
- AI endpoint refuses unsupported questions cleanly
- AI logging stores only redacted questions

### 14.4 Frontend Tests

Required checks:

- dashboard renders with loading state
- dashboard renders with empty state
- dashboard renders with API error state
- filters update query keys
- data quality warnings appear when coverage is weak
- doctor ROI chart handles missing values
- AI panel displays limitations

---

## 15. Build Milestones

### Milestone 1: Data Profiling Foundation

Deliver:

- workbook profiler
- file type detection
- schema profile output
- source file hash registration
- initial data dictionary

Success:

- all eight files can be profiled without manual inspection

### Milestone 2: Database Foundation

Deliver:

- migrations for reference, audit, canonical, reconciliation, and view layers
- seed countries and calendar months
- indexes and constraints

Success:

- database can be recreated from migrations

### Milestone 3: Ingestion MVP

Deliver:

- planner loader
- consolidation loader
- execution snapshot loader
- RCPA aggregate loader
- validation errors
- ingestion report

Success:

- all supplied files load into canonical tables
- failed rows are reported, not silently ignored

### Milestone 4: Reconciliation and KPI Views

Deliver:

- event matching service
- materialized views
- data quality view

Success:

- dashboard-ready SQL views produce coherent metrics

### Milestone 5: Backend API

Deliver:

- FastAPI app
- typed schemas
- services for execution, budget, doctor ROI, data quality

Success:

- all endpoints test successfully against loaded data

### Milestone 6: Frontend MVP

Deliver:

- executive overview
- execution matrix
- global filters
- loading/error/empty states
- data freshness banner

Success:

- app is demoable from deployed frontend against backend API

### Milestone 7: Advanced Analytics

Deliver:

- budget utilization tab
- workflow governance tab/section
- intervention mix tab/section
- doctor ROI tab
- ROI quadrant matrix
- doctor drilldown
- unmatched events/data quality tab

Success:

- stakeholder can identify missed events, budget gaps, and doctor ROI opportunities

### Milestone 8: AI Assistant

Deliver:

- grounded AI query endpoint
- AI panel
- suggested prompts
- cited metrics and limitations

Success:

- AI answers are concise, useful, and never unsupported by data

### Milestone 9: Deployment and Polish

Deliver:

- deployed frontend
- deployed backend
- Supabase database
- README
- ingestion runbook
- demo script

Success:

- app can be shown to business stakeholders without local-only dependencies except ingestion

---

## 16. Risk Register

### Risk: Event names do not match across files

Mitigation:

- explicit `event_matches`
- match confidence
- unmatched events dashboard

### Risk: Pcode coverage is weak

Mitigation:

- track expected/actual Pcode coverage
- show doctor ROI only where RCPA join is valid
- expose no-Pcode records in data quality

### Risk: RCPA files are large

Mitigation:

- stream or bounded-read XLSB files
- aggregate before database write
- avoid raw JSON row storage for RCPA

### Risk: Currency values are misinterpreted

Mitigation:

- store currency code
- preserve local amounts
- normalize only with static seeded exchange rates in MVP, with LKR fixed at the official company rate `1 USD = 310 LKR`
- label charts clearly

### Risk: AI hallucination

Mitigation:

- structured context only
- deterministic calculations only
- limitations in every answer
- no raw unrestricted database access by AI

### Risk: Supabase free tier limits

Mitigation:

- avoid raw RCPA storage
- use indexes carefully
- materialized views only for dashboard-ready summaries
- archive or aggregate historical data if needed

---

## 17. Final Engineering Decision

The correct implementation is not the original seven-table dashboard design and not a fully enterprise ETL warehouse. The correct implementation is a pragmatic, audit-aware, reconciliation-driven analytics platform.

Adopt:

- product scope and stack from `plan1.md`
- reconciliation, Pcode, calendar, data quality, and materialized view ideas from `plan2.md`
- workbook-specific rules from actual file profiling
- simplified ingestion that avoids raw RCPA row storage

This architecture is serious enough for a real stakeholder demo, defensible in engineering interviews, and realistic for a solo build. It keeps the MVP deployable while avoiding the data integrity mistakes that would make the dashboard untrustworthy.
