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
- executed events
- action-due events
- planned HCPs
- engaged HCPs
- HCP execution rate
- event execution rate
- match coverage
- snapshot source counts, including `monthly_planner` and `derived_from_consolidation`

## Budget Summary

Required fields:

- planned budget local/USD where available
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
- currency code
- missing-FX flag
- FX rate date
- FX rate source
- FX rate status: `official`, `provisional`, or `missing`; LKR must be `official` at `1 USD = 310 LKR`

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
- overdue reporting count when due-date logic is available

## Intervention Mix

Required fields:

- intervention type
- intervention subtype
- request count
- matched/executed count
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
- direct HCP/BTU spend
- overhead/BTC spend
- total ROI spend
- coverage flags

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
- missing-FX warning
- Excel serial month parse count
- static FX seed date, including official LKR company rate date
- provisional FX count
- BTU/BTC reconciliation issue count
- missing confirmed/contracted amount count
- workflow status coverage
- intervention type coverage
- Sri Lanka May derivation note when applicable
