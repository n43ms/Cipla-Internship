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
- confirmed budget local/USD where available
- actual spend local/USD where available
- unspent gap
- overrun amount
- plan-without-spend count
- spend-without-plan count
- currency code
- missing-FX flag

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
- static FX seed date
- Sri Lanka May derivation note when applicable
