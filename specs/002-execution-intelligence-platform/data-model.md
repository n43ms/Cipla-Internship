# Data Model: Cipla EMEU Execution Intelligence Platform

## Modeling Principles

- Keep raw source identity separate from ingestion run participation.
- Preserve raw source values when they are useful for audit, but expose normalized fields for joins and filters.
- Use explicit reconciliation records instead of hidden joins.
- Store local currency and nullable normalized currency separately.
- Treat weak coverage as data, not as an exception.

## Audit and Source Entities

### ingestion_runs

Tracks each complete profiling/ingestion/reconciliation attempt.

Fields:

- `id` UUID primary key
- `started_at`, `completed_at`
- `status`: `running`, `completed`, `completed_with_warnings`, `failed`
- `triggered_by`
- `source_file_count`
- `total_rows_seen`, `total_rows_loaded`, `total_rows_skipped`
- `warning_count`, `error_count`
- `summary_json`

Validation:

- exactly one terminal status per run,
- failed runs retain partial validation/report information,
- completed runs require source file participation records.

### source_files

Represents a reusable file identity.

Fields:

- `id` UUID primary key
- `original_filename`
- `file_hash`
- `file_type`: `xlsx`, `xlsb`
- `source_type`: `planner`, `execution_snapshot`, `consolidation`, `rcpa`
- `country_scope`
- `period_start`, `period_end`
- `detected_sheet_count`
- `created_at`

Validation:

- unique `file_hash`,
- source type must be classified before ingestion.

### ingestion_run_files

Connects a source file to a specific ingestion run.

Fields:

- `id` UUID primary key
- `ingestion_run_id`
- `source_file_id`
- `local_path_snapshot`
- `status`
- `sheets_profiled`
- `rows_seen`, `rows_loaded`, `rows_skipped`
- `warnings`, `errors`
- `profile_json`

Validation:

- unique `(ingestion_run_id, source_file_id)`,
- allows the same file hash to participate in multiple runs.

### validation_errors

Stores file-level and row-level issues.

Fields:

- `id` UUID primary key
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

Validation:

- row number may be null for file/sheet-level issues,
- severity controls whether a row can continue through ingestion.

## Reference Entities

### countries

Fields:

- `id`
- `name`
- `code`
- `default_currency_code`

Seed values:

- Nepal / `NP` / `NPR`
- Sri Lanka / `LK` / `LKR`
- Myanmar / `MM` / `MMK`
- Oman / `OM` / `OMR`
- UAE / `AE` / `AED`
- Malaysia / `MY` / `MYR`

### calendar_months

Fields:

- `id`
- `month_start_date`
- `month_label`
- `fiscal_year`
- `fiscal_month_number`
- `calendar_year`
- `calendar_month_number`

Validation:

- fiscal year starts in April,
- all observed source formats must resolve to a canonical month,
- supported inputs include `Apr-24`, `25-Apr`, `Oct-25`, `Apr'26`, `May-26`, date objects, and Excel serial numbers such as `45772`.

### exchange_rates

Fields:

- `id`
- `currency_code`
- `rate_to_usd`
- `rate_date`
- `source`
- `rate_status`: `official`, `provisional`, `missing`

Validation:

- MVP uses static seed rows only, not a live FX integration,
- seed all six scoped currencies from the July 10 company-provided official rates: LKR 368.90, NPR 89, OMR 0.46, AED 1.00, MMK 4300, and MYR 4.39 per USD,
- internet/public FX fallback is not allowed for this phase; currencies outside the company-provided list remain `missing`,
- USD fields stay null when FX is unavailable,
- cross-country views must expose missing-FX warnings.

## Canonical Business Entities

### plan_events

Canonical planned activity from yearly planner files.

Fields:

- `id`
- `source_file_id`, `ingestion_run_id`
- `country_id`, `calendar_month_id`
- `fiscal_year`
- `therapy`
- `event_type`
- `event_name`, `event_name_normalized`
- `central_or_local`
- `brand_name_1`, `brand_name_2`
- `planned_honorarium_hcps`
- `planned_delegate_hcps`
- `planned_total_hcps`
- `planned_patients`
- `planned_pharmacies`
- `honorarium_cost_per_hcp_usd`
- `total_honorarium_cost_usd`
- `operational_cost_per_unit_usd`
- `total_operational_cost_usd`
- `total_planned_cost_usd`
- `comments`, `country_comment`
- `ho_finalized`
- `source_sheet_name`, `source_row_number`

Validation:

- Nepal canonical sheet is `Yearly Planner FY27 v2` when present,
- Sri Lanka canonical sheet is `YP FY27`,
- alternate planner sheets are profiled but not double-counted,
- event names are normalized for matching only.

### execution_snapshots

Monthly execution planner-derived status evidence.

Fields:

- `id`
- `source_file_id`, `ingestion_run_id`
- `country_id`, `calendar_month_id`
- `therapy`
- `event_type`
- `event_name`, `event_name_normalized`
- `planned_hcps`
- `engaged_hcps`
- `raised_request_count`
- `snapshot_source`: `monthly_planner`, `derived_from_consolidation`
- `status_source_value`
- `normalized_status`: `executed`, `action_due`, `unknown`
- `yp_total_doctors`
- `raised_total_doctors`
- `approved_total_doctors`
- `request_total_doctors`
- `event_created_count`
- `source_sheet_name`, `source_row_number`

Validation:

- April `1` maps to `executed`,
- April blank maps to `action_due` when no raised evidence exists,
- May `Executed` and `Action due` map directly,
- missing Sri Lanka May tab is a recorded limitation, not an ingestion failure,
- Sri Lanka May derived rows are built from consolidation requests where country is Sri Lanka and calendar month is May 2026, grouped by normalized intervention/event fields, with `snapshot_source = derived_from_consolidation`.

### execution_requests

Smart-contract request facts from consolidation `Working`.

Fields:

- `id`
- `source_file_id`, `ingestion_run_id`
- `source_system`
- `req_id`
- `request_uid`
- `country_id`, `calendar_month_id`
- `rep_code`, `rep_name`
- `intervention_date`, `actual_intervention_date`
- `venue`
- `intervention_name`, `intervention_name_normalized`
- `intervention_type`, `intervention_sub_type`
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
- `actual_total_expense_usd`
- `actual_btu_expense_usd`
- `actual_btc_expense_usd`
- `direct_hcp_spend_local`
- `overhead_spend_local`
- `total_roi_spend_local`
- `direct_hcp_spend_usd`
- `overhead_spend_usd`
- `total_roi_spend_usd`
- `expected_customer_count`
- `attended_customer_count`
- `expected_category_raw`
- `attended_category_raw`
- `request_approval_status`
- `request_confirmation_status`
- `post_approval_status`
- `post_confirmation_status`
- `expense_submitted_date`
- `expense_confirmed_date`
- `current_owner_stage`
- `approval_status`
- `confirmation_status`
- `cancellation_reason`
- `city`, `state`
- `approval_chain_json`
- `source_row_number`

Validation:

- unique `(source_system, req_id)` when valid,
- duplicate `REQ_ID` values create validation errors and fallback `request_uid`,
- `confirmed_contracted_amount_local` maps from `APPROVE/CONFIRMED TOTAL INTERVENTION`,
- `estimated_intervention_local` maps from `ESTIMATED INTERVENTION` and is reference-only,
- `actual_btu_expense_local` maps from `ACTUAL EXPENSE AGAINST BTU`,
- `actual_btc_expense_local` maps from `TOTAL ACTUAL BTC EXPENSE`,
- `actual_total_expense_local` maps from `TOTAL ACTUAL EXPENSES FOR INTERVENTION`,
- `direct_hcp_spend_local = actual_btu_expense_local`,
- `overhead_spend_local = actual_btc_expense_local`,
- `total_roi_spend_local = actual_total_expense_local`,
- when BTU, BTC, and actual total are populated, `actual_btu_expense_local + actual_btc_expense_local` should reconcile to `actual_total_expense_local`; mismatches create data-quality warnings,
- `association_amount_local` is preserved separately and is not the default contracted HCP spend,
- request and post/report lifecycle statuses map from the four pending approval/confirmation columns,
- actual spend without plan match remains visible.

### request_doctors

Expected and actual doctor participation extracted from consolidation.

Fields:

- `id`
- `execution_request_id`
- `attendance_type`: `expected`, `actual`
- `doctor_name_raw`
- `doctor_class_raw`
- `pcode_raw`
- `pcode_normalized`
- `parse_status`: `parsed`, `missing_pcode`, `ambiguous`, `invalid`
- `source_position`

Validation:

- unique `(execution_request_id, attendance_type, source_position)`,
- Pcode may be null but must be explicitly marked,
- raw values are preserved for audit.

### doctors

Doctor master profile seeded mainly from RCPA and joined to attendance where possible.

Fields:

- `id`
- `country_id`
- `pcode_normalized`
- `latest_doctor_name`
- `speciality`
- `doctor_class`
- `patch_name`
- `active_status`
- `first_seen_month_id`
- `last_seen_month_id`
- `source_count`
- `updated_at`

Validation:

- unique `(country_id, pcode_normalized)`,
- blank/invalid Pcodes do not create doctor master rows,
- cross-country Pcode collisions are reported.

### rcpa_doctor_month_summary

Compact online prescription trend by doctor and month.

Fields:

- `id`
- `source_file_id`, `ingestion_run_id`
- `country_id`, `calendar_month_id`
- `pcode_raw`, `pcode_normalized`
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

Validation:

- unique conflict target: `source_file_id`, `country_id`, `calendar_month_id`, `pcode_normalized`, `currency_code`,
- drives Doctor ROI trend, Cipla vs competitor split, no-RCPA flags, and ROI quadrant reward metrics,
- `ingestion_run_id` records the latest run that wrote or replaced the summary row.

### rcpa_doctor_brand_summary

Compact online all-period brand mix by doctor.

Fields:

- `id`
- `source_file_id`, `ingestion_run_id`
- `country_id`
- `first_calendar_month_id`, `last_calendar_month_id`
- `pcode_normalized`
- `doctor_name`
- `brand_group`
- `own_or_competitor`
- `prescription_qty`
- `prescription_value_local`
- `currency_code`
- `row_count_aggregated`

Validation:

- unique conflict target: `source_file_id`, `country_id`, `pcode_normalized`, `brand_group`, `own_or_competitor`, `currency_code`,
- supports doctor detail brand mix without storing every monthly SKU row online,
- detailed SKU-level aggregate evidence is retained in local compressed extracts under `data/processed/`.

### rcpa_country_brand_month_summary

Compact online country/month/brand market trend.

Fields:

- `id`
- `source_file_id`, `ingestion_run_id`
- `country_id`, `calendar_month_id`
- `brand_group`
- `own_or_competitor`
- `prescription_qty`
- `prescription_value_local`
- `currency_code`
- `row_count_aggregated`

Validation:

- unique conflict target: `source_file_id`, `country_id`, `calendar_month_id`, `brand_group`, `own_or_competitor`, `currency_code`,
- supports aggregate brand and market-trend summaries without loading SKU-level RCPA detail into Supabase.

### Local RCPA Detail Extracts

Detailed RCPA aggregate evidence is generated under `data/processed/` as compressed CSV files.

Fields:

- country, month, Pcode, doctor metadata
- brand group, SKU, SKU detail
- own-vs-competitor label
- prescription quantity and local value
- currency and source row aggregate count

Validation:

- local extracts are gitignored and are not part of the deployed database,
- they preserve the previous SKU-level aggregate grain for audit/debugging/reruns,
- no raw prescription-level RCPA table is stored in Supabase for MVP.

## Reconciliation Entity

### event_matches

Explicit links between planned, snapshot, and request evidence.

Fields:

- `id`
- `ingestion_run_id`
- `country_id`, `calendar_month_id`
- `plan_event_id`
- `execution_snapshot_id`
- `execution_request_id`
- `match_method`: `exact`, `normalized`, `fuzzy`
- `match_confidence`
- `match_status`: `matched`, `weak_match`, `unmatched_plan`, `unmatched_snapshot`, `unmatched_request`, `ignored`
- `matched_on`
- `notes`
- `created_at`, `updated_at`

Rules:

- exact country/month/type/name match first,
- normalized event name match second,
- conservative fuzzy match only above configured threshold,
- weak matches are excluded from confident KPI numerators unless explicitly labeled,
- manual overrides are out of MVP.

## KPI and Reporting Views

### mv_execution_kpis

Includes planned events, matched events, weak/unmatched events, executed events, action-due events, planned HCPs, engaged HCPs, HCP execution rate, event execution rate, and match coverage.

### mv_budget_utilization

Includes planned budget, estimated intervention, confirmed/contracted amount, confirmed-vs-estimated variance, direct HCP/BTU spend, overhead/BTC spend, actual total spend, unspent gap, overrun, plan without spend, spend without plan, currency labels, FX source/date/status, provisional-FX flags, and missing-FX flags.

### mv_workflow_governance

Includes request approval status, request confirmation status, post/report approval status, post/report confirmation status, current owner/stage, market, month, rep, intervention type, pending counts, approved/rejected/corrected/deleted/draft counts, report draft counts, report sent-for-correction counts, report approved counts, expense submitted date coverage, and expense confirmed date coverage.

Status derivation:

- request approval stage from `PENDING FOR APPROVAL Request`,
- request confirmation state from `PENDING FOR CONFIRMATION Request`,
- report/post approval stage from `PENDING FOR APPROVAL POST`,
- report/post confirmation state from `PENDING FOR CONFIRMATION POST`,
- owner/stage parsed from status text such as `Request Submitted Pending With ...` or `Report in Approval Pending With ...`,
- proof/reporting completion inferred from report approval/confirmation and expense submission/confirmation dates; actual proof files are not available in the supplied workbook.

### mv_intervention_mix

Includes intervention type, intervention subtype, country, month, request count, executed count, approved count, report pending count, confirmed/contracted amount, direct HCP/BTU spend, overhead/BTC spend, total actual spend, and FX status.

The view must be data-driven from source values. Current observed types include Patient Benefit Program, Cipla Own CMEs/ Workshop, Pharmacy Benefit Program, National Local Conference, International Conference, Medical Survey, Cipla Digital initiatives, and Cipla International Conference.

### mv_doctor_roi

Includes engagement count, last engagement, associated spend, direct HCP/BTU spend, overhead/BTC spend, total ROI spend, Cipla prescriptions, competitor prescriptions, Cipla share, spend per Cipla prescription, ROI segment, ROI quadrant x/y values, ROI quadrant label, and dark-horse flag.

Segments:

- `high_value_engaged`
- `high_value_unengaged`
- `low_rx_high_spend`
- `insufficient_data`

Quadrants:

- `low_effort_high_reward`
- `high_effort_high_reward`
- `low_effort_low_reward`
- `high_effort_low_reward`

Default quadrant logic:

- x-axis investment/effort uses `total_roi_spend_local` or `total_roi_spend_usd` when official company FX exists,
- y-axis reward/result uses Cipla prescription quantity or value from RCPA,
- thresholds are deterministic medians within the selected country/month/filter cohort unless a later configuration file supplies explicit thresholds,
- `dark_horse = true` when quadrant is `low_effort_high_reward`.

### mv_data_quality

Includes latest ingestion status, files loaded, rows seen/skipped, validation errors, match coverage, Pcode coverage, RCPA coverage, missing FX, provisional FX, stale run state, unmatched counts, BTU/BTC reconciliation issues, missing confirmed amount counts, missing report/proof status counts, and intervention-type coverage.

### mv_unmatched_events

Includes source type, event name, event type, country, month, reason, candidate match, confidence, and source references.

## AI Entity

### ai_query_logs

Fields:

- `id`
- `created_at`
- `country_id`
- `calendar_month_id`
- `question_redacted`
- `context_summary_json`
- `answer`
- `provider`
- `model`
- `latency_ms`
- `error_code`
- `error_message`

Validation:

- no secrets,
- no raw oversized workbook data,
- context summary must reference deterministic API/service outputs,
- persist only `question_redacted`; the raw question may be used in memory for the active request but must not be stored,
- redact Pcode-like numeric identifiers, currency/money amounts, and likely doctor-name spans before insert.

Redaction policy:

- replace 4+ digit numeric identifiers and decimal-looking Pcodes with `[PCODE]`,
- replace currency symbols/codes followed by amounts and large standalone amounts with `[AMOUNT]`,
- replace name-like spans following labels such as `Dr`, `Doctor`, `HCP`, or `Pcode for` with `[NAME]`,
- never store source row payloads or raw workbook excerpts in AI logs.
