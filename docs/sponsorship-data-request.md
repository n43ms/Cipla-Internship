# Sponsorship Readiness Data Request

## Short Teams Message

Hi Abhijeet, even if the full package is not ready, please send any one raw recurring smart-contract/consolidation extract exactly as exported, plus one cleaned/presentable version if available. A small sample is enough to profile the structure and avoid building on assumptions. I will send a detailed email with the exact priority list and fields.

## Email Outline

Subject: Minimum data needed to start sponsorship ingestion safely

Hi Abhijeet,

To start the next phase without waiting for a perfect package, please share whatever is available in this priority order. Even one raw file is useful as long as it is exactly as exported from the source system.

## Priority 1: Minimum Viable Data

1. One raw recurring smart-contract or consolidation extract exactly as exported.
2. One cleaned/presentable version of the same or similar file, if available.
3. One small RCPA sample with P-codes, if available.
4. One doctor/MSL/territory mapping sample, if available.
5. Three to five known business examples:
   - sponsored doctor/event,
   - no-fee or free-service case,
   - international or national conference case,
   - messy or unmatched doctor case,
   - known correct output example.

## Priority 2: Full Desired Package

| Source | Needed Details |
|---|---|
| Raw consolidation/smart-contract extracts | 3-5 files exactly as exported, file cadence, source owner, sheet names, request IDs, intervention fields, spend fields, doctor/P-code fields, status fields |
| Cleaned consolidation file | The manually cleaned/presentable version used for business discussion, preferably matching one raw extract |
| Doctor-level contract report | Contract ID, request ID, country, P-code, doctor name, agreement/service type, dates, amount if present |
| Historical RCPA | Country, month, P-code, doctor name, brand, own/competitor, quantity, value, patch/territory if present |
| Monthly RCPA samples | 2-3 monthly refresh files, with confirmation whether each file is one month or rolling history |
| MSL doctor master | Country, P-code, doctor name, speciality, class, active status, MSL/rep, patch/territory |
| Territory mapping | Territory, patch, region, cluster, task force, effective date if assignments change |
| Accommodation/travel | Only if it exists as a separate source; include doctor/event/request IDs and cost fields |
| Label definitions | Exact source labels for National Conference, International Conference, ERS, no-fee/free service, accommodation/travel, sponsorship/consultancy/speaker/advisory |
| Validation examples | Known correct cases and known problematic cases for reconciliation |

## Non-Negotiable File Rules

- Send raw recurring exports before or alongside cleaned files.
- Do not delete columns before sharing the raw sample.
- Preserve original sheet names and headers.
- Preserve P-codes as shown in source, including leading zeros.
- Share files through approved business storage, not git.
- If only cleaned files are available, mark them as presentation sources.

## Received-Data Checklist

- [ ] At least one raw recurring file received.
- [ ] Cleaned version received or explicitly unavailable.
- [ ] RCPA sample received or explicitly unavailable.
- [ ] Doctor/MSL/territory sample received or explicitly unavailable.
- [ ] Known validation examples received or explicitly unavailable.
- [ ] Source owner and cadence known.
- [ ] Confidentiality constraints confirmed.
- [ ] Files stored outside git.

## Engineering Use

The first action after receiving data is profiling, not coding. The implementation sequence is:

```text
profile -> compare raw vs cleaned -> update source contract -> create synthetic fixture -> write tests -> update loader/schema only for proven fields
```
