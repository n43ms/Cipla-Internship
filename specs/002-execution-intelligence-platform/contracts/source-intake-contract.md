# Source Intake Contract

Use this contract for every sponsorship/readiness source before implementation. It records what was requested, what actually arrived, and whether the file is safe to use as recurring ingestion evidence.

## Intake Summary

| Field | Value |
|---|---|
| Source name | TBD |
| Business owner | TBD |
| Technical owner | TBD |
| Source system | TBD |
| File received date | TBD |
| File cadence | one-time / daily / weekly / monthly / annual / unknown |
| File type | xlsx / xlsb / csv / other |
| Raw recurring source? | yes / no / unknown |
| Cleaned/presentation copy? | yes / no / unknown |
| Safe for implementation? | blocked / profile-only / implementation-ready |

## Minimum Viable Intake

The team can start profiling with any one of these:

- one raw recurring consolidation or smart-contract extract,
- one cleaned/presentable version of the same or similar file,
- one small RCPA sample with P-codes,
- one doctor/MSL/territory mapping sample,
- three to five known validation examples.

## Source Shape

| Item | Observed Value |
|---|---|
| Workbook sheets | TBD |
| Canonical sheet candidate | TBD |
| Header row | TBD |
| Row count | TBD |
| Date/month fields | TBD |
| Money fields | TBD |
| Doctor identity fields | TBD |
| Contract/request identity fields | TBD |
| Territory fields | TBD |
| Label/classification fields | TBD |

## Schema Mapping Review

| Canonical concept | Source column | Required? | Status | Notes |
|---|---|---:|---|---|
| country/division | TBD | yes | unknown |  |
| month/date | TBD | yes | unknown |  |
| request/intervention ID | TBD | conditional | unknown |  |
| intervention name/type | TBD | conditional | unknown |  |
| P-code | TBD | conditional | unknown |  |
| doctor name | TBD | conditional | unknown |  |
| contract ID | TBD | conditional | unknown |  |
| sponsorship/no-fee label | TBD | conditional | unknown |  |
| territory/patch | TBD | conditional | unknown |  |

## Gate Status

| Gate | Required Evidence | Status |
|---|---|---|
| Real recurring source | Raw exported file, not manually cleaned | blocked |
| Profile complete | Profile markdown/json reviewed | blocked |
| Raw-vs-cleaned comparison | Required only if both variants exist | blocked |
| Stable keys identified | Request ID, contract ID, country+P-code, month grain | blocked |
| Business labels confirmed | Exact observed labels, not meeting-memory labels | blocked |
| Storage impact estimated | DB size before load and expected row count | blocked |

## Review Checklist

- [ ] The file is stored outside git.
- [ ] The source owner and cadence are known or explicitly marked unknown.
- [ ] The profile report exists.
- [ ] Unknown columns have been reviewed.
- [ ] Missing required fields are documented.
- [ ] Empty columns are documented.
- [ ] Sample values are bounded and non-sensitive.
- [ ] No loader, migration, dashboard, or AI context is planned without passing gates.

## Open Questions

- TBD
