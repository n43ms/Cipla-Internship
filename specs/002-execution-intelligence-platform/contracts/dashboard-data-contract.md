# Dashboard Data Contract

All dashboard payloads are returned by FastAPI. The frontend must not compute business KPIs from raw rows.

## Shared Response Metadata

Every dashboard response includes:

- `generatedAt`
- `latestIngestionRunId`
- `latestIngestionStatus`
- `dataQualityFlags`
- `filtersApplied`
- `limitations`
- `sourceDerivationNotes`

## Filter Contract

Supported filters:

- `country`
- `month`
- `includeOutOfScope` for execution, workflow, and intervention endpoints. Default is `false`; default responses must include only Nepal/Sri Lanka Apr-May 2026 Phase 4 production scope.
- Doctor ROI also supports `includeOutOfScope`. When no country is selected and `includeOutOfScope=false`, Doctor ROI defaults to Nepal/Sri Lanka primary markets.
- `monthStart`
- `monthEnd`
- `therapy`
- `eventType`
- `brand`
- `speciality`
- `doctorClass`
- `roiSegment`
- `interventionType`
- `interventionSubType`
- `workflowStatus`
- `fxRateStatus`

Invalid filters return `400` with a typed error body.

## Execution Summary

Required fields:

- planned events
- matched events
- weak/unmatched events
- executed planned events: planned events with matched executed snapshot evidence
- action-due planned events: planned events with matched action-due snapshot evidence
- raw executed snapshot count
- raw action-due snapshot count
- planned HCPs
- matched engaged HCPs
- raw engaged HCPs
- HCP execution rate
- event execution rate
- match coverage
- snapshot source counts, including `monthly_planner` and `derived_from_consolidation`
- `primaryScope`, `scopeStatuses`, and `scopeReasons`

## Budget Summary

Required fields:

- planned budget USD from yearly planner
- estimated intervention local/USD where available
- confirmed/contracted amount local/USD where available
- confirmed-vs-estimated variance
- direct HCP/BTU spend local/USD where available
- overhead/BTC spend local/USD where available
- actual total spend local/USD where available
- unspent gap
- overrun amount
- plan-without-spend count
- spend-without-plan count
- currency codes present in the filtered result
- local totals grouped by currency code; local values must never be summed across currencies
- missing-FX count
- FX rate date
- FX rate source
- FX rate status: `official`, `provisional`, or `missing`; the six scoped currencies must use the July 10 official company rates
- paginated budget evidence rows

Budget grain rules:

- Summary planned budget is deduplicated by `plan_event_id`.
- Matched unspent/overrun is calculated by grouping all matched requests under the matched `plan_event_id` first.
- Request-level rows remain visible as evidence rows but must not be treated as independent planned-budget gaps.
- Spend without plan is reported separately from plan overrun.
- Top-level local totals are nullable when multiple local currencies are present. Consumers must use `localTotalsByCurrency` for local money.
- Public internet FX rates must not fill missing company rates for this phase.

## Workflow Governance

Required fields:

- country
- month
- request approval status counts
- request confirmation status counts
- post/report approval status counts
- post/report confirmation status counts
- current owner/stage counts
- pending request count
- pending report count
- reports sent for correction
- reports approved
- expense submitted date coverage
- expense confirmed date coverage
- `primaryScope`, `scopeStatuses`, and `scopeReasons`
- request-row scope fields: `isPrimaryPhase4Scope`, `scopeStatus`, and `scopeReason`
- overdue reporting count when due-date logic is available

## Intervention Mix

Required fields:

- intervention type
- intervention subtype
- request count
- matched request count
- executed request-link count
- executed distinct snapshot count
- action-due request-link count
- action-due distinct snapshot count
- matched-without-execution count
- approved count
- report pending count
- confirmed/contracted amount
- direct HCP/BTU spend
- overhead/BTC spend
- total actual spend
- FX status

## Doctor ROI

Required fields:

- country
- Pcode
- doctor name
- speciality
- doctor class
- engagement count
- last engagement date
- associated spend
- Cipla prescription quantity/value
- competitor prescription quantity/value
- Cipla share
- spend per Cipla prescription
- ROI segment
- ROI quadrant x value
- ROI quadrant y value
- ROI quadrant label
- dark-horse flag
- unengaged dark-horse flag
- high-value engaged flag
- direct HCP/BTU spend
- overhead/BTC spend
- total ROI spend
- coverage flags
- first/last engagement dates
- first/last RCPA months
- RCPA month count

Doctor ROI rules:

- Month filters apply to engagement evidence.
- RCPA is treated as a historical prescription baseline, not same-period post-event lift.
- Brand filters identify doctors with that brand in the RCPA baseline unless a later endpoint explicitly returns selected-brand ROI metrics.
- Spend allocation must deduplicate actual-attendance rows to request/Pcode grain before allocating request spend.
- Any actual-attendance rows missing usable Pcodes must be surfaced as unallocated doctor spend in Data Quality.

## Data Quality

Required fields:

- latest ingestion run
- file count
- rows seen/loaded/skipped
- validation errors by severity
- event match coverage
- Pcode coverage
- RCPA coverage
- stale ingestion flag
- unmatched records by source
- unmatched record sample with source, country, month, event, reason, candidate match, and confidence
- missing-FX warning
- Excel serial month parse count
- static FX seed date, including official LKR company rate date
- provisional FX count
- BTU/BTC reconciliation issue count
- missing confirmed/contracted amount count
- workflow status coverage
- intervention type coverage
- Sri Lanka May derivation note when applicable
- file-level latest run status and row counts
- actual attendance rows missing Pcodes
- unallocated doctor spend local/USD

Data Quality scoping rules:

- Current validation issue counts and validation drilldowns use the latest ingestion run per source file.
- Historical validation rows remain audit history but must not inflate current warning/error counts.
- File-level participation is shown separately from global latest ingestion status because source families can be refreshed independently.
