# Sponsorship ROI And Batch Upload Implementation Plan

**Feature Context**: Extension of `002-execution-intelligence-platform`

**Created**: 2026-07-04

**Last Updated**: 2026-07-10

**Primary Inputs**:

- `specs/002-execution-intelligence-platform/spec.md`
- `specs/002-execution-intelligence-platform/plan.md`
- `specs/002-execution-intelligence-platform/tasks.md`
- `ingestion_sponsorship.md`
- `files/transcript3.txt`
- `files/transcript4.txt`
- `files/transcript5.txt`
- Abhijeet email response from 2026-07-10
- received workbook package under `files/`
- current repository architecture
- current Supabase database footprint

## Purpose

This plan updates the sponsorship, RCPA, territory, expense, and AI-extension roadmap after the July 9, 2026 clarification call with Abhijeet.

The key change is that the next phase is no longer a broad speculative discovery effort. The business objective and source strategy are now clear:

```text
North Star: keep Doctor ROI quadranting as the core product.
Method: refresh the system through manual batch upload of known raw Excel reports.
Business value: explain why a doctor belongs in a quadrant using sponsorship history, paid engagement economics, RCPA trend, spend, contract evidence, and territory context.
```

The clarification files have now arrived under `files/`. Source-specific code still should not be finalized until the actual workbooks are profiled and synthetic fixtures are created from observed schemas. The correct engineering approach is to register the received package, profile it, then build vertical slices from observed columns rather than from transcript assumptions.

## Executive Decision

Build the next phase as a manual-batch, evidence-gated vertical slice.

Do not pursue live SFTP, SharePoint folder polling, or data-lake automation in this project phase. Abhijeet clarified that the current CRM/data-lake environment contains roughly 128 reports across departments, many with similar names and different cadences. A direct automated connector would be brittle, hard to validate, and not worth the complexity for the remaining internship timeline.

Do build a robust manual upload pipeline:

```text
business user exports exact raw reports
  -> user uploads workbook batch
  -> ingestion profiler validates source type and schema
  -> deterministic loaders normalize known fields
  -> compact canonical facts and KPI views refresh
  -> dashboard preserves Doctor ROI quadrant workflow
  -> ExecAI summarizes only deterministic backend context
```

This gives the business control over the exact files being refreshed while still making the application reusable.

## Final Deliverable Contract

The final deliverable is not just file upload, profiling, or a separate sponsorship page. The final deliverable is a complete refreshable Doctor ROI evidence workflow:

```text
1. Business user uploads the latest Excel/XLSB/CRM HTML-XLS files from the dashboard.
2. The system validates the batch and clearly rejects wrong, duplicate, unreadable, or unknown files.
3. Accepted files are ingested through deterministic loaders into Supabase compact canonical facts.
4. Materialized views refresh from Supabase.
5. Existing dashboard pages reload API data and reflect the new source package.
6. Doctor ROI calculations include source-backed sponsorship and engagement investment where available.
7. Doctor detail views explain sponsorship, paid engagement, no-fee, FMV, contracted value, expense, RCPA, and caveat evidence.
8. Data Quality explains any weak joins, missing P-codes, missing economics, manual RCPA mapping periods, or upload issues.
9. ExecAI answers only from the refreshed backend evidence, never directly from raw workbook rows.
```

The deliverable is complete only when a non-technical business user can upload the agreed file package, run or trigger the accepted-batch refresh, and see Doctor ROI evidence updated in the dashboard after the Supabase write and view refresh.

### Required User-Visible Outcomes

After the final refresh workflow is implemented:

```text
Doctor ROI table:
  shows current ROI plus sponsorship/engagement summary signals.

Doctor ROI detail drawer:
  shows full doctor-level sponsorship, paid engagement, no-fee, FMV, contracted value, expense, RCPA, and caveat history.

Data Quality page:
  shows upload/ingestion status, rejected files, weak joins, missing P-codes, missing FMV/contracted value, missing spend, and manual mapping caveats.

ExecAI:
  can explain why a doctor is in a quadrant using deterministic sponsorship, engagement, spend, and RCPA evidence.
```

### Doctor ROI Calculation Contract

Doctor ROI must not treat missing sponsorship history as true zero investment.

The investment side of Doctor ROI must include, when source-backed and linked to the doctor:

```text
current execution spend
sponsorship spend
paid engagement spend
contracted amount
FMV amount
doctor-attributable BTU/BTC/actual expenses
```

The return/context side must include:

```text
RCPA prescription quantity
RCPA prescription value if available
Cipla versus competitor share
pre/post or historical trend windows where coverage is sufficient
```

Required zero-spend behavior:

```text
If no spend and no sponsorship/engagement evidence exists:
  show zero spend with normal caveat rules.

If sponsorship/engagement evidence exists and amount is known:
  include the known amount in investment metrics and show source evidence.

If sponsorship/engagement evidence exists but amount is missing:
  do not show a misleading plain zero; show "prior sponsorship/engagement found, amount unavailable" and exclude the missing amount from numeric spend totals.

If linkage is weak:
  show evidence with confidence/caveat and do not overstate ROI precision.
```

The system may describe association between sponsorship/engagement and prescription movement, but must not claim causal uplift unless a future validated methodology explicitly supports it.

### Non-Ambiguous Product Decisions

These decisions are final for this phase unless Abhijeet provides a new written correction:

```text
Upload is the business-user refresh entry point.
Upload validation alone does not update KPI data.
Dashboard data changes only after accepted-batch ingestion writes Supabase facts and refreshes views.
Raw reports are source of truth.
Cleaned/presentable reports are comparison and validation evidence only.
Historical RCPA supplies prescription baseline and trend context, not sponsorship spend.
Sponsorship/engagement spend comes from consolidated intervention, doctor-wise contract, ERS/conference, FMV, contracted amount, and expense fields.
National Conference and International Conference are sponsorship.
ERS is international-conference evidence, not a separate sponsorship root.
No Fee Agreement is engagement/no-fee evidence, not sponsorship by default.
Missing sponsorship amount is not numeric zero.
Known sponsorship amount is credited into Doctor ROI investment.
Weak doctor/P-code joins must be visible as caveats.
```

### Batch Refresh State Machine

Accepted uploaded batches must move through explicit states:

```text
uploaded
validated
accepted_for_ingestion
quarantined
ingestion_running
ingestion_failed
supabase_written
views_refreshed
dashboard_refreshed
```

Every user-facing upload result should map to one of these states. Ambiguous labels such as "done" or "processed" are not sufficient.

### Source-To-Dashboard Traceability

Every displayed sponsorship/engagement/RCPA fact must retain enough provenance to answer:

```text
which source file supplied it
which source sheet supplied it
which source row or row group supplied it where practical
which doctor/P-code it joined to
which intervention/request/contract it joined to
which caveats affect it
```

This provenance does not require storing unbounded raw rows in Supabase. Compact source references, file hashes, row numbers, aggregate counts, and local generated extracts are acceptable where storage budget requires them.

## Received Package Status

The July 10 package is now sufficient to start the profiling and source-contract finalization phase.

Received folders and files:

```text
files/Raw Reports -Point 1/
  Consolidated Raw Report/
    Consolidate report All Bu's Nov'25 - 9 Jul'26.xlsx
  Doctor Raw Report/
    Doctor Wise Intervention Report - Nepal.xls
    Doctor Wise Intervention Report - Oman.xls
    Doctor Wise Intervention Report - UAE.xls
    Doctor Wise Intervention Report -Malaysia.xls
    Doctor Wise Intervention Report -Sri Lanka.xls
    Consolidated Intervention Report - Myanmar.xls

files/Cleaned Presentable Version - Point 2/
  Intervention till 8 Jul'26.xlsx
  Malaysia Intervention till 8 Jul'26.xlsx
  Myanmar Intervention till 8 Jul'26.xlsx
  Nepal Intervention till 8 Jul'26.xlsx
  Oman Intervention till 8 jul'26.xlsx
  Sri lanka intervention till 8 jul'26.xlsx

files/Historical Smart Contracts-Point 5/
  ERS.xlsx

files/MSL Doctor Master File Point 7/
  MSL.xlsx

files/RCPA Report All Bu's Apr'26 - 03 Jul'26.xlsx
```

Confirmed historical RCPA backfill workbooks also exist under `files/`:

```text
Nepal & Myanmar Apr'24-Mar'25 RCPA report.xlsb
Nepal & Myanmar RCPA Report Apr'25-mar'26.xlsb
Sri Lanka RCPA Report Apr'25 - Mar'26.xlsb
```

These are part of the intended historical RCPA backfill package.

Confirmed business answers:

```text
National Conference and International Conference are sponsored by Cipla.
ERS is not a separate sponsorship category; it is part of International.
No Fee Agreement usually means free work after prior sponsorship/agreement, but charity/philanthropy or other reasons can exist.
Accommodation and travel are under expenses.
BTC / BTU = total expense basis for accommodation/travel handling.
Doctor-level contract report is part of Point 1, so no separate doctor-contract file is expected.
Territory is in the consolidated report as the highlighted HQ column and in MSL as Location.
MSL Doctor Master has been provided, though it remains optional unless report-level territory is insufficient.
Monthly RCPA has a standard format, headers stay the same, P-code is always present, and files are cumulative.
Monthly RCPA arrives around the 3rd of each month.
Daily extracts are saved in SharePoint, but this app phase still uses manual batch upload.
```

Official FX rates versus 1 USD:

```text
Sri Lanka: 368.90
Nepal: 89
Oman: 0.46
UAE: 1.00
Myanmar: 4300
Malaysia: 4.39
```

Resolved clarifications:

```text
root-level historical RCPA XLSB files are in scope for the historical backfill.
RCPA Report All Bu's Apr'26 - 03 Jul'26.xlsx is the unified all-BU monthly workbook provided for convenience.
No external Varad validation output is required for this implementation phase.
FQ HQ in the transcript/email is equivalent to the observed FS HQ field; it was a transcription/reference mismatch.
FX conversion must use only the company-provided official values listed above, with no internet-rate fallback.
```

## Clarified Product Scope

### Core Objective

The core product remains the four-quadrant Doctor ROI model:

```text
identify doctors worth more attention
identify doctors receiving spend without enough value
identify transactional doctors
identify dark-horse or underserved opportunities
```

Sponsorship, contracts, RCPA, spend, and territory data are supporting evidence for the quadrant, not separate replacement products.

### Primary Next-Phase User Questions

The next phase should answer:

```text
Which doctors were sponsored for National or International conferences?
Which doctors later performed no-fee, speaker, consultancy, advisory, or other services?
How much did Cipla spend on the doctor across fees and expenses?
What was the fair-market-value amount versus contracted amount?
Did prescriptions move before or after the engagement window?
Is the doctor a high-value relationship, a transactional paid relationship, or a poor ROI case?
Are there territory-level underserved or overserved patterns?
What evidence explains why the doctor is in a given quadrant?
```

The UI priority is:

```text
Doctor ROI detail enrichment first
Sponsorship/engagement economics next
Territory intelligence later as bonus or second page
ExecAI context last, after deterministic services exist
```

## Clarified Source Strategy

### Source 1: Raw Consolidated Intervention Report

Status:

```text
received
raw export from CRM / Smart Contract reporting
one of the two primary recurring reports
manual batch upload source
path: files/Raw Reports -Point 1/Consolidated Raw Report/Consolidate report All Bu's Nov'25 - 9 Jul'26.xlsx
observed shape: one sheet, 3,568 rows, 87 columns
```

Purpose:

```text
intervention/event spine
event name
intervention number or request identifier
intervention type and subtype
approval and execution metadata where useful
expense headers
travel/accommodation expense evidence
BTU/BTC and billed-to-company or billed-to-user expense breakdowns if present
total expenses if present
local currency amounts
country and period scope
```

Observed priority fields:

```text
DIVISION
FS HQ
REQ_ID
Intervention Start Date
Intervention End Date
INTERVENTION DATE
Month
Venue
INTERVENTION NAME
INTERVENTION TYPE
INTERVENTION SUB TYPE
ME LOCATION
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

Known caveats:

```text
may not contain all doctor-level contract economics
may lack contract ID
type and subtype can look repetitive
some fields are good-to-know but not insight-driving
BTU/build-to-user values may be test or rare in real business flow
```

### Source 2: Raw Doctor-Wise Intervention Report

Status:

```text
received
raw export from CRM / Smart Contract reporting
preferred source for doctor-level ROI economics
one of the two primary recurring reports
manual batch upload source
path: files/Raw Reports -Point 1/Doctor Raw Report/
format: CRM HTML exports saved with .xls extension
real header row begins after title/filter preamble
```

Purpose:

```text
doctor name
P-code
doctor segment
intervention/request identifier
intervention/event name
contract type or agreement type
amount paid
fair market value amount
contracted value amount
local currency
doctor-level fee or honorarium evidence
```

Observed priority fields from the Sri Lanka doctor-wise report:

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
FMV Speciality
FMV Tier
FMV Role
FMV amount
Contract ID
Contracted Amount
Status
```

Critical business decision:

```text
FMV amount and contracted value amount are the holy-grail fields for ROI economics.
```

The system should compute:

```text
contract_saving_local = fair_market_value_amount - contracted_value_amount
contract_saving_usd after official FX conversion
paid engagement ROI using contracted value, expenses, and RCPA movement
```

Do not treat FMV saving as prescription ROI. It is negotiation or contracting efficiency. It can become a useful secondary KPI after the core Doctor ROI path is stable.

### Source 3: Clean Business Report

Status:

```text
received
single cleaned/presentable report used for business reporting
comparison source only
path: files/Cleaned Presentable Version - Point 2/
```

Purpose:

```text
compare business-facing reporting against raw source exports
identify manually removed, renamed, grouped, or highlighted fields
validate that raw ingestion reproduces business-visible totals
```

Rule:

```text
Cleaned reports are not the recurring source of truth unless Abhijeet explicitly confirms a cleaned report is the only maintained source.
```

### Source 4: Historical RCPA Backfill

Status:

```text
received and confirmed
one-time backfill
approximately two years if available
manual batch upload
confirmed files: root-level historical RCPA XLSB files
related historical smart-contract file: files/Historical Smart Contracts-Point 5/ERS.xlsx
```

Purpose:

```text
historical prescription quantity
doctor P-code where available
date/month
patch
territory
therapy/brand/product dimensions if available
pre/post sponsorship and engagement movement
```

Known caveats:

```text
records before the system cutoff around November may be manual or legacy-mapped.
records after system rollout are expected to have stronger P-code support.
Abhijeet clarified anything before 1st Nov is manual for P-code mapping.
ERS.xlsx is received as historical smart-contract / ERS conference data, not a full RCPA replacement by itself.
competitor-filtering assumptions must come from the delivered source files and documented business fields, not external validation output.
```

Implementation implication:

```text
RCPA mapping provenance must be stored or derived as system_supplied, manual_legacy, source_supplied, or unknown.
```

### Source 5: Future Monthly RCPA Refresh

Status:

```text
received standard raw report sample
manual batch upload
generated around the 3rd of every month
cumulative, not a one-month delta
headers expected to remain the same
path: files/RCPA Report All Bu's Apr'26 - 03 Jul'26.xlsx
observed sheets: Malaysia, Myanmar, Nepal, Oman, Sri Lanka, UAE
this unified all-BU workbook represents the monthly sample set for convenience
```

Purpose:

```text
refresh RCPA coverage with the added latest month
update Doctor ROI baselines and sponsorship movement
support idempotent reruns
```

Observed priority fields:

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

Critical implementation rule:

```text
Monthly RCPA loads must be replacement/upsert by source grain, not blind append.
```

The loader must detect the covered month range and avoid duplicate summaries when a cumulative file is uploaded again.

### Source 6: Territory Fields

Status:

```text
received in multiple places
consolidated/doctor-wise reports expose HQ fields such as FS HQ
monthly RCPA exposes Location and PATCHNAME
MSL Doctor Master is received and exposes Location, Territory Id, Patch, and Patchsname
```

Purpose:

```text
patch
territory
country
possibly region, cluster, rep, or task force if present
self-serving territory candidates
underserved or overserved territory candidates
untapped opportunity analysis
```

Priority:

```text
territory intelligence is valuable but secondary.
finish core Doctor ROI and sponsorship evidence first.
```

### Source 7: Accommodation And Travel

Status:

```text
not a separate source unless real files prove otherwise
confirmed under expenses in the consolidated and doctor-wise reports
BTC / BTU are the expense basis
```

Purpose:

```text
travel, taxi, venue, accommodation, and related expenses
total cost of engagement
full doctor/activity investment view
```

Do not design an accommodation entity before profiling the expense columns.

### Source 8: Official FX Rates

Status:

```text
received for all six markets in Abhijeet's July 10 email
```

Purpose:

```text
convert local FMV, contracted value, honorarium, and expenses to USD or reporting currency
make country comparisons defensible
remove internet-sourced FX assumptions
```

## Sponsorship And Engagement Semantics

### Sponsorship Definition

Abhijeet clarified that true sponsorship means:

```text
National Conference
International Conference
```

These are the only categories that should be classified as sponsorship by default.

ERS and other large respiratory congresses should not become separate hard-coded source categories until observed in the files. Treat them as possible subtypes or named events under International Conference if the raw data supports that mapping.

### Non-Sponsorship Engagements

Other activities are not sponsorship by default. They may still be important ROI evidence:

```text
No Fee Agreement
Speaker Agreement
Consultancy Agreement
Advisory Board
video, podcast, editorial, or other business-requested services
paid honorarium engagements
```

These should be modeled as engagement/service evidence, not sponsorship events.

### No-Fee Interpretation

No-fee activity often indicates prior value exchange, such as an earlier sponsorship, but it is not proof by itself.

The system must avoid causal overclaiming:

```text
good: "Doctor completed no-fee activity after prior sponsorship."
good: "No-fee activity may indicate a prior engagement relationship."
bad: "The sponsorship caused this prescription uplift."
bad: "All no-fee activity is caused by prior sponsorship."
```

Outliers such as charity, philanthropy, or unrelated business reasons must remain possible data-quality caveats.

### Paid Engagement Interpretation

Abhijeet introduced a second ROI theory:

```text
Some doctors may not want conference sponsorship.
They may instead prefer paid, transactional engagements such as advisory boards or speaker agreements.
Those paid engagements may still correlate with strong prescription behavior.
```

Therefore the model must support both:

```text
sponsorship ROI
paid engagement ROI
```

Do not collapse everything into a sponsorship bucket.

## Architecture Decisions

### Runtime Boundary

The architecture remains a controlled batch-refresh pipeline:

```text
business user opens React dashboard
  -> user clicks "Upload new data/files"
  -> user uploads Excel/XLSB/CRM HTML-XLS workbook batch
  -> FastAPI stores the batch in gitignored local upload storage
  -> source fingerprinting accepts or quarantines each file
  -> profiler records schema, row counts, sheets, and warnings
  -> approved batch is ingested by deterministic loaders
  -> Supabase receives compact canonical facts and summaries
  -> materialized KPI views refresh
  -> FastAPI read services expose updated Doctor ROI evidence
  -> React dashboard reflects the refreshed data
  -> ExecAI explains only deterministic backend context after refresh
```

The upload step is not the final business-data mutation by itself. It is the business-user entry
point for a refresh. The dashboard should make the next state explicit:

```text
uploaded and rejected
uploaded and accepted for ingestion review
ingestion running
Supabase updated
views refreshed
dashboard data refreshed
```

When the loader phases are complete, accepted uploaded files must be able to drive the same
canonical update path as CLI-based ingestion. The source of truth after ingestion is Supabase,
not the uploaded workbook folder.

### Out Of Scope For This Phase

The following are explicitly out of scope:

```text
SFTP automation
SharePoint folder polling
automatic discovery across 128 CRM/data-lake reports
direct Power BI productionization
fake sponsorship pages before data
AI answers over raw workbook rows
unbounded storage of raw RCPA detail in Supabase
```

Power BI may become the later mass-production environment with Anil, but this repo should focus on a correct, reusable prototype and batch-refresh pipeline.

## Database And Storage Strategy

Current known database constraint:

```text
current database size: 321 MB
Supabase Free database limit: 500 MB
remaining budget: about 179 MB
```

Hard storage rules:

```text
raw workbooks remain local and gitignored
RCPA detailed rows stay local unless explicit storage budget is approved
Supabase stores compact canonical facts and KPI-ready summaries
materialized views must not duplicate full RCPA summaries unnecessarily
source-row JSON must be bounded or avoided
database size must be measured before and after historical RCPA loads
```

Preferred canonical facts after source profiling:

```text
source_file_batches
source_file_profiles
intervention_events
doctor_engagements
doctor_contract_economics
doctor_expense_facts
doctor_sponsorship_facts
rcpa_doctor_month_summary
rcpa_doctor_brand_summary
doctor_territory_observations
```

These names are planning-level only. Final migrations must follow the actual observed schema and existing database naming conventions.

## Source-To-Model Mapping

The implementation should follow this mapping unless profiling proves a field is unavailable or unsafe:

| Source | Primary Use | Canonical Facts | Dashboard Surface |
|---|---|---|---|
| Raw consolidated intervention report | Event/request spine, intervention type/subtype, dates, FS HQ, BTC/BTU/actual expenses | intervention events, expense facts, workflow/evidence references | Doctor ROI evidence, budget, workflow, data quality |
| Raw doctor-wise intervention reports | Doctor/P-code engagement rows, FMV, contracted amount, contract ID, status | doctor engagements, contract economics, doctor-contract links | Doctor ROI table/detail, sponsorship evidence |
| Cleaned presentable reports | Comparison-only validation and business-readable cross-checks | no source-of-truth facts unless explicitly approved | data-quality/comparison reports only |
| ERS workbook | International conference evidence | sponsorship/engagement facts with ERS as subtype/evidence | Doctor ROI detail, sponsorship history |
| Historical RCPA XLSB files | Two-year prescription baseline/backfill | compact doctor-month and doctor-brand summaries with mapping provenance | Doctor ROI calculation and caveats |
| Monthly cumulative RCPA workbook | Recurring RCPA refresh | replace/upsert compact doctor-month and doctor-brand summaries | Doctor ROI and data freshness |
| MSL doctor master | Doctor/P-code/territory reference if report fields are insufficient | doctor master/reference and territory mapping | Doctor ROI joins, territory caveats |

## Implementation Acceptance Gates

Each implementation phase must close with a runnable acceptance check:

```text
Upload gate:
  at least one valid mixed workbook batch can be uploaded from the dashboard and produces accepted/rejected file results.

Ingestion gate:
  accepted uploaded files can be ingested into Supabase through deterministic loaders without hand-editing the files.

View refresh gate:
  materialized views refresh after ingestion and expose changed evidence through FastAPI.

Doctor ROI gate:
  Doctor ROI calculation includes sponsorship/engagement investment where source-backed and exposes amount-missing caveats where not.

Frontend gate:
  Doctor ROI table/detail and Data Quality page visibly change after refreshed API data is returned.

ExecAI gate:
  ExecAI can explain the refreshed doctor evidence using backend context with no raw-workbook hallucination.
```

Any phase that cannot satisfy its gate must leave a documented blocker in the task file or runbook before moving forward.

## Data Arrival Gates

Every source must pass these gates before implementation.

### Gate A: File Identity Confirmed

Each file must be labeled by Abhijeet or the sender:

```text
point number from request
business source name
raw or cleaned
country or market scope
period coverage
export date
owner
```

This is required because several reports can look similar at the surface level.

### Gate B: Raw Export Preserved

Accepted source files must be:

```text
exactly downloaded from the system
not manually filtered
not manually renamed
not manually deleted
not converted into a presentation-only format
```

If top blank/comment rows exist, the profiler should detect and report the header row rather than requiring manual deletion.

### Gate C: Profile Complete

Each file must produce:

```text
sheet names
header row
raw columns
mapped canonical fields
unknown columns
empty columns
sample values for label columns
row count
country scope
period scope
file hash
profile timestamp
```

### Gate D: Business Semantics Confirmed

Before classification logic is finalized, confirm:

```text
exact National Conference label
exact International Conference label
ERS is part of International; still confirm how ERS appears in raw fields
exact no-fee label
exact speaker, consultancy, advisory, and paid-service labels
FMV amount column
contracted value amount column
expense amount columns
official FX rate by market already provided; use only the company-provided values during implementation
no internet or market-rate fallback is allowed
```

### Gate E: Join Keys Confirmed

Before persistence and views:

```text
request/intervention ID behavior
country + P-code behavior
contract ID availability
event name stability
doctor-wise to consolidated join grain
RCPA doctor/month replacement grain
territory/patch grain
```

### Gate F: Storage Impact Estimated

Before loading historical RCPA or broad sponsorship history:

```text
expected row count
expected summary row count
expected table size
expected materialized-view size
free-tier headroom
retention and compact-mode decision
```

## Implementation Roadmap

### Phase 0: Source Intake And Batch Upload Readiness

**Trigger**: Received package exists under `files/`.

**Goal**: Prepare the intake path without assuming final source schemas.

Work:

```text
source intake contract
batch upload source manifest format
schema profiling
raw-vs-cleaned comparison
storage budget report
official FX intake slot
synthetic fixture policy
feature gate policy
```

Exit criteria:

```text
incoming files can be registered, profiled, and rejected safely
no real workbook enters git
no source-specific loader runs before profile approval
```

### Phase 1: Profile The Expected File Package

**Trigger**: Start immediately from the July 10 received package.

**Goal**: Convert the transcript clarifications into observed source contracts.

Received package to profile:

```text
raw consolidated intervention report
raw doctor-wise intervention report
clean business report
historical smart-contract ERS file
confirmed historical RCPA backfill files
monthly cumulative RCPA sample
official FX rate list
MSL/doctor master
```

Work:

```text
profile each file
compare raw consolidated and raw doctor-wise fields
compare raw reports to cleaned business report
identify National and International labels
identify paid engagement labels
identify FMV and contracted value fields
identify expense fields
identify P-code coverage
identify territory/patch coverage
identify RCPA competitor-filtering caveat from delivered columns or documented source notes
record that the unified all-BU workbook is the monthly sample package
write source-specific profile summary
```

Exit criteria:

```text
actual schemas are documented
implementation blockers are known
synthetic fixtures can be created from observed shapes
```

### Phase 2: Manual Batch Upload Pipeline

**Trigger**: File profiles are complete.

**Goal**: Make repeatable upload practical without SFTP.

Work:

```text
upload or CLI batch manifest
source type detection
file hash and duplicate detection
batch audit summary
per-file validation result
safe rerun behavior
failure report with missing required fields
```

Exit criteria:

```text
same file cannot silently duplicate facts
wrong report type is rejected or quarantined
business user can refresh by uploading the known file set
```

### Phase 3: Intervention And Doctor Engagement Spine

**Trigger**: Consolidated and doctor-wise schemas are confirmed.

**Goal**: Normalize interventions, doctors, and engagement economics.

Work:

```text
load consolidated intervention event facts
load doctor-wise engagement facts
join doctor-wise rows to intervention spine
preserve P-code and doctor name evidence
persist contract type or agreement type
persist FMV amount and contracted value amount
persist paid amount or honorarium if present
persist expense categories from consolidated report
convert local currency using official FX
```

Exit criteria:

```text
doctor-level spend and contract economics are queryable
FMV-vs-contracted saving can be calculated
unjoined doctor/event rows are visible as data-quality output
```

### Phase 4: Sponsorship And Engagement Classification

**Trigger**: Label columns and sample values are confirmed.

**Goal**: Classify source rows without over-broad sponsorship logic.

Rules:

```text
National Conference -> sponsorship
International Conference -> sponsorship
ERS or similar congress -> subtype or named international conference only if observed
No Fee Agreement -> no-fee engagement, not sponsorship
Speaker Agreement -> paid or service engagement, not sponsorship
Consultancy Agreement -> paid or service engagement, not sponsorship
Advisory Board -> paid engagement, not sponsorship
```

Work:

```text
deterministic classifier
classification reason
confidence
unclassified candidate bucket
tests for every observed label
```

Exit criteria:

```text
only true sponsorship categories enter sponsorship facts
paid and no-fee engagements remain separately analyzable
classification is auditable from raw labels
```

### Phase 5: Historical RCPA Backfill

**Trigger**: Confirmed historical RCPA files are profiled.

**Goal**: Extend Doctor ROI baselines without corrupting identity or storage.

Work:

```text
profile RCPA shape
capture competitor-drug filtering caveats from source fields or documented file notes
confirm manual/legacy mapping cutoff around November
load compact doctor-month and doctor-brand summaries
store mapping provenance
store territory/patch observations if present
refresh Doctor ROI views
measure database size before and after
```

Exit criteria:

```text
two-year or available RCPA window improves Doctor ROI context
manual mapping caveats are visible
competitor-filter caveat is documented
storage remains within budget
```

### Phase 6: Monthly Cumulative RCPA Refresh

**Trigger**: Standard monthly RCPA sample is received.

**Goal**: Support future refreshes by upload.

Work:

```text
detect covered month range
compare headers to historical backfill
upsert or replace summaries by month grain
make reruns idempotent
show latest RCPA freshness
flag partial or missing months
```

Exit criteria:

```text
cumulative monthly files can be uploaded repeatedly without duplicate summaries
latest month updates Doctor ROI and data-quality metadata
```

### Phase 7: Sponsorship And Engagement Outcome Views

**Trigger**: Engagement facts and sufficient RCPA history are loaded.

**Goal**: Explain doctor quadrant membership with historical evidence.

Views should support:

```text
sponsorship count
first and latest sponsorship date
National and International conference counts
paid engagement count
no-fee engagement count
speaker/consultancy/advisory count
FMV amount
contracted amount
contract saving
fees and honorarium
expenses
total investment
pre-window Cipla Rx
post-window Cipla Rx
Rx movement
months observed before and after
confidence and caveats
```

Labels must use association language:

```text
post-sponsorship movement
post-engagement movement
associated movement
not causal uplift
```

Exit criteria:

```text
Doctor ROI can explain why a doctor is high value, transactional, underinvested, or low ROI
data limitations are explicit
```

### Phase 8: Doctor ROI Detail Extension

**Trigger**: Outcome service exists.

**Goal**: Put sponsorship and engagement evidence where the workflow already exists.

UI sections:

```text
Sponsorship background
Paid engagement economics
No-fee service history
FMV vs contracted value
Expense breakdown
RCPA movement
Territory or patch context if available
Data caveats
```

Exit criteria:

```text
clicking a quadrant doctor shows the history behind the quadrant
one internationally sponsored doctor can be validated manually
low-confidence rows do not overclaim
```

### Phase 9: Territory Intelligence

**Trigger**: Territory/patch fields are confirmed in reports, or MSL/doctor master is provided.

**Goal**: Add territory opportunity only after core Doctor ROI is stable.

Work:

```text
profile territory fields
decide whether report fields are enough or MSL master is required
build territory observations
define underserved, overserved, and self-serving rules from distributions
validate output against source-level reconciliations and selected business spot checks only if available
```

Exit criteria:

```text
territory labels are deterministic
one self-serving or underserved territory can be validated manually
territory page is added only if there is enough reliable data
```

### Phase 10: ExecAI Extension

**Trigger**: Deterministic services exist for sponsorship, paid engagement, RCPA movement, and optionally territory.

**Goal**: Let ExecAI explain evidence, not invent it.

Supported topics:

```text
why this doctor is in this quadrant
what drugs or therapy areas drive the prescription trend
prior sponsorships
paid engagements
no-fee services
FMV vs contracted value
expenses
territory opportunity if available
```

Context rules:

```text
send compact backend summaries only
send evidence references
cap top-N rows
redact sensitive identifiers where configured
fallback deterministically when provider fails
refuse or qualify causal questions
```

Exit criteria:

```text
ExecAI can explain a doctor's quadrant using grounded evidence
unsupported claims are qualified
no raw workbook rows are sent to the model
```

## Testing And Validation Strategy

Every implementation slice follows:

```text
profile real file
record actual schema
write tiny synthetic fixture
write failing tests
implement loader/service/view/UI
run focused tests
compare to source-level reconciliations and selected business spot checks only if available
record caveats
```

Required validation examples:

```text
one doctor sponsored for an international conference
one doctor with no-fee activity after prior sponsorship if present
one paid advisory/speaker/consultancy doctor if present
one FMV greater than contracted value example
one cumulative RCPA refresh rerun
one self-serving or underserved territory if data supports it
Sri Lanka Q1 execution sanity check if the cleaned report includes it
```

Known business benchmark from transcript:

```text
Sri Lanka Q1 planned doctors: 2,126
Sri Lanka Q1 engaged doctors: 2,382
doctor engagement execution: 112%
planned events: 67
raised/executed events: 38
event execution: 57%
```

Use this only as a validation benchmark if the delivered files cover the same period and scope.

## Risk Register

### Risk: Wrong report uploaded

Mitigation:

```text
source manifest
file labels from Abhijeet
source fingerprinting
required-column validation
wrong-source quarantine
```

### Risk: Treating all engagements as sponsorship

Mitigation:

```text
classify only National and International as sponsorship
model paid and no-fee services separately
store classification reason and raw label
```

### Risk: No-fee activity is overinterpreted

Mitigation:

```text
use "possible prior engagement evidence" language
track no-fee separately
show outlier caveats such as charity or philanthropy
```

### Risk: RCPA historical data is partially manual

Mitigation:

```text
store mapping provenance
separate legacy/manual and system-supported periods
profile and document competitor-filtering assumptions from the delivered source files
avoid name-only confident joins
```

### Risk: Cumulative monthly RCPA duplicates data

Mitigation:

```text
detect covered months
replace/upsert by doctor/month/brand grain
idempotency tests
file hash audit
```

### Risk: Local currency comparisons are misleading

Mitigation:

```text
use only the official company FX rates provided for all six markets
store local amount and converted amount
flag missing FX as data quality issue
```

### Risk: Territory data is not complete enough

Mitigation:

```text
derive territory only from confirmed fields
use the received MSL/doctor master only if needed
keep territory page gated until validation examples exist
```

### Risk: AI overclaims causality

Mitigation:

```text
deterministic service context first
evidence references required
answer policy uses association language
causal prompts are refused or qualified
```

## Updated Backlog With Gates

### Ready Now With Received Files

```text
R0. Register the received file inventory and source labels.
R1. Build or document manual batch upload manifest expectations.
R2. Profile the raw consolidated report, doctor-wise HTML exports, cleaned reports, ERS workbook, MSL workbook, and RCPA workbook.
R3. Compare raw reports against cleaned presentable reports.
R4. Build storage budget report before loading historical RCPA.
R5. Record that historical RCPA scope and monthly unified workbook scope are confirmed.
R6. Define source-based validation checks; external Varad output is not required.
```

### Ready After Raw Consolidated And Doctor-Wise Profiles Pass

```text
C1. Profile both raw reports.
C2. Compare raw reports to the clean business report.
C3. Create source-specific synthetic fixtures.
C4. Implement intervention and doctor engagement loaders.
C5. Add FMV, contracted value, expense, and official FX handling.
C6. Add classification tests for observed labels.
```

### Ready After Sponsorship Labels Are Observed

```text
S1. Classify National and International as sponsorship.
S2. Classify no-fee, speaker, consultancy, and advisory as engagement/service evidence.
S3. Persist classification reason and confidence.
S4. Build sponsorship and engagement summary views.
```

### Ready After Historical RCPA Scope Is Confirmed And Profiled

```text
H1. Profile historical RCPA.
H2. Capture competitor-filtering caveats from delivered source fields.
H3. Confirm manual/system mapping provenance.
H4. Estimate storage.
H5. Load compact summaries.
H6. Refresh Doctor ROI baseline.
```

### Ready After Monthly RCPA Sample Profile Passes

```text
M1. Profile cumulative monthly format.
M2. Confirm headers match historical shape or document drift.
M3. Implement cumulative replacement/upsert.
M4. Add idempotency tests.
M5. Add latest RCPA freshness metadata.
```

### Ready After Outcome Views Are Stable

```text
O1. Extend Doctor ROI detail schema and API.
O2. Add sponsorship and engagement evidence to Doctor ROI drawer.
O3. Add validation against one known sponsored doctor.
O4. Extend ExecAI context and answer policy.
```

### Ready After Territory Fields Are Confirmed

```text
T1. Profile territory/patch fields.
T2. Decide whether MSL/doctor master is needed.
T3. Build territory observations.
T4. Define underserved, overserved, and self-serving rules.
T5. Add territory UI only after validation examples pass.
```

## Final Recommendation

The cleanest execution path is:

```text
1. Finish batch-upload readiness and source profiling.
2. Profile Abhijeet's labeled file package as soon as it arrives.
3. Build intervention and doctor engagement spine from the two raw reports.
4. Add sponsorship and paid/no-fee engagement classification.
5. Load historical RCPA compact summaries.
6. Add cumulative monthly RCPA refresh.
7. Extend Doctor ROI detail with sponsorship, engagement, spend, FMV, and RCPA evidence.
8. Add ExecAI evidence summaries.
9. Add territory intelligence only after core Doctor ROI is finalized.
```

This matches the transcript's priority: finalize the core Doctor ROI product before adding territory and other bells and whistles.
