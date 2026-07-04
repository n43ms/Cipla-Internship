# Ingestion And Sponsorship Intelligence Plan

This document converts the discussions in `files/transcript3.txt` and `files/transcript4.txt` into an implementation-ready product and architecture plan.

It is intentionally written as a staff-level engineering document: first the business conversation, then the exact data implications, then the system changes required to build the next version of the platform without turning the ingestion layer into fragile Excel glue.

## 1. Broad Meeting Overview

Two connected themes came out of the meetings:

1. The platform must become reusable and refreshable.
   The current dashboard was built from the structured files already provided. The business now wants the software to accept new extracts repeatedly, refresh the database, and show updated dashboard metrics without manual rework each time.

2. Sponsorship intelligence must become a first-class analytical layer.
   The team wants to understand whether sponsored doctors are producing business value, whether sponsored doctors later provide free/no-fee services, whether RCPA prescription behavior improves after sponsorship, and which doctors or territories deserve more attention.

The meetings also clarified that there are multiple data streams with different refresh cadences:

| Data stream | Business meaning | Expected cadence | Current state |
|---|---|---:|---|
| Yearly planner | Planned events, expected doctors, planned budget | Annual/static with updates | Considered consistent |
| Execution/smart-contract extracts | Contracts, activities, workflow, approvals, spend, actual attendance | Daily or near-daily extract | Report shape must be confirmed from raw exports |
| Consolidation report | Main activity/consolidation report used for execution, budget, and sponsorship | Extracted regularly; possibly daily/weekly depending source | Presentable version differs from raw version |
| Doctor-contract report | Doctor-level file that may contain contract IDs missing from the main consolidation file | Daily or periodic | Needs to be obtained and reconciled |
| RCPA | Doctor prescription behavior by month, brand, quantity, value | Historical backfill plus monthly refresh | Being cleaned manually with P-code assignment |
| MSL/doctor master | Doctor identity, specialty, class, task force, territory/patch | Periodic/reference | Exists in Varad's Power BI model |
| Territory mapping | Territory/patch-level grouping for field deployment insights | Expected alongside RCPA/doctor data | Required for next analytical layer |

The most important technical conclusion is that the system should not require users to manually delete columns, reshape files, or create a "presentation version" before ingestion. The future ingestion pipeline must understand raw exported report shapes, validate them, map aliases, ignore irrelevant columns safely, and fail loudly when required columns are missing or semantically changed.

## 2. Detailed Meeting Interpretation

### 2.1 Reusable Ingestion Was The Starting Concern

Aditya asked whether the software should expect one normalized Excel template or multiple messy real-world files. The concern was correct: if the new files differ from the sample files used to build the dashboard, a hard-coded loader can silently corrupt the database.

Abhijeet confirmed that real data exists and is generated regularly. It is not just a hypothetical template-fill exercise. Some data arrives every day through a shared internal location described in the transcript as `SethMKTGBCTHO` or similar. Anil has access to some of these daily reports.

Decision implied by the discussion:

```text
Do not depend only on a manually cleaned template.
Build ingestion around raw exported report classes, with schema profiling and controlled normalization.
```

The correct engineering response is to support a "canonical input contract" per source type:

```text
Raw Excel extract
  -> file registry identifies source type
  -> profiler detects sheets/header rows/columns
  -> loader maps aliases to canonical fields
  -> validators report missing, extra, or semantically changed fields
  -> canonical tables are upserted idempotently
```

This is already the broad shape of the current repo, but the meetings require stronger coverage for raw report drift, sponsorship classification, contract-ID joins, and territory enrichment.

### 2.2 The Main Data Sources Are Smart Contract Tool Data And RCPA

Abhijeet said the relevant data is primarily from two sources:

1. Smart contract tool extracts.
2. RCPA prescription data.

The smart contract/consolidation side tells us:

```text
which activity was planned or requested
which doctor was expected/attended
what type of contract/activity it was
what spend was approved/confirmed/actual
what workflow stage it is in
whether it is a paid, no-fee, sponsored, conference, speaker, consultant, advisory, or related activity
```

The RCPA side tells us:

```text
which doctor prescribed what
which brands/SKUs were prescribed
how prescription quantity/value moved over time
which doctor belongs to which class/speciality/territory
whether a doctor has Cipla prescription behavior even without recent engagement
```

The platform's analytical value comes from joining these sources at doctor and time grains:

```text
P-code + country + month
P-code + country + event/activity date
P-code + country + contract/sponsorship event
P-code + country + territory
```

### 2.3 P-code Is The Core Doctor Identity

Both meetings repeatedly converged on P-code as the reliable doctor identifier.

The business problem:

```text
Doctor names are manually entered.
The same doctor may appear with spelling variations.
Different MRs may write the same doctor differently.
A doctor may work across therapies or task forces.
Two different doctors can have similar names.
Historical records may lack P-codes.
```

Varad's Power BI model avoided name matching by joining RCPA and doctor-wise contract data through P-code. That is the right principle.

Architecture decision:

```text
P-code should remain the primary join key for doctor-level analytics.
Name matching should only be used as a fallback, warning path, or manual mapping workflow.
```

Current repo already reflects this:

```text
doctors unique key:
  country_id + pcode_normalized

request_doctors:
  pcode_raw
  pcode_normalized
  parse_status

RCPA summaries:
  country_id
  pcode_normalized
```

Required addition:

```text
Track doctor identity confidence and historical P-code assignment provenance.
```

For historical RCPA files where P-code is being added manually, we need to know:

```text
was P-code present in the source?
was it manually assigned?
who/what file supplied the mapping?
was the mapping high confidence?
does the same old doctor name map to multiple P-codes?
does the same P-code appear under multiple names?
```

Without this, sponsorship ROI may look precise while relying on manually repaired identity data.

### 2.4 Historical RCPA Is A Rate Limiter

Abhijeet stated that the team is cleaning roughly 1,200 doctors. Around 800 had been reviewed and P-coded at one point; roughly 400 remained. Later transcript context suggests another deficit around 450 records during an in-progress sheet cleanup.

The goal is to provide around two years of RCPA history, with the same structure and P-code present, so the dashboard can avoid recency bias.

Why this matters:

```text
Six months of RCPA may overstate or understate a doctor's true value.
Two years of RCPA gives a better baseline for doctor quadrants and sponsorship outcomes.
```

The business explicitly wants to test whether current top performers remain top performers after the larger historical RCPA backfill. They want to challenge the hypothesis that the current short-window leaderboard is stable.

Engineering implication:

```text
The system must support backfills and re-runs.
RCPA ingestion must be idempotent by country + month + P-code + brand/SKU/own-competitor grain.
Historical files must not duplicate current rows.
Dashboards need data-window indicators so users know whether conclusions are based on 6 months, 12 months, or 24 months.
```

Current repo already supports compact RCPA summary persistence and local detailed exports. The new requirement is to expose historical coverage and manual-mapping confidence more visibly, especially on Doctor ROI and sponsorship views.

### 2.5 RCPA Refresh Cadence Is Monthly

Abhijeet clarified that after the historical backfill, RCPA does not need recurring "previous batch" loads except monthly updates. A new RCPA month is expected near the end/start of each month; for example, June data may arrive today or tomorrow after the month closes.

Required behavior:

```text
RCPA backfill:
  one-time or occasional large load

RCPA ongoing refresh:
  monthly append/replace for latest month
```

The system should show:

```text
latest RCPA month available
RCPA coverage window
countries covered
doctor count covered
P-code coverage
manual mapping coverage
missing or partial RCPA warning
```

### 2.6 Smart Contract / Execution Data Refresh Cadence Is Daily

For contract/activity data, Abhijeet described a daily extraction path. The data can be real-time in the system, but an extract is saved once a day, around 10:30 according to the transcript.

This applies especially to:

```text
contracts created
activities booked
money spent
pending activities
workflow approvals
sponsorship/consultancy activities
```

Required behavior:

```text
Daily refresh should update execution, budget, workflow, and sponsorship facts.
Monthly RCPA refresh should update prescription outcomes.
```

This means the platform needs two separate freshness clocks:

```text
Operational freshness:
  daily smart contract/consolidation extract age

RCPA freshness:
  latest prescription month available
```

The current `DataFreshnessBanner` and data-quality views should be extended to display both.

### 2.7 Raw Reports Differ From Presentable Reports

The discussion around the consolidation report is critical.

Abhijeet showed/mentioned that the raw report has more columns than the cleaner version already shared. The current dashboard was built against presentable/cleaned files, not necessarily the exact raw extract. Some columns may have been deleted, such as GST or other fields considered nonessential.

This is a risk:

```text
If ingestion is hard-coded to the cleaned report,
then the daily raw report may not ingest correctly.
```

Agreed path:

```text
Abhijeet/Anil will highlight fields removed from the raw report.
The engineering side will decide whether to ignore them or add provisions.
The team will standardize a machine-friendly ingestion format.
```

Engineering decision:

```text
Ingestion should accept the raw report directly.
Irrelevant columns can be ignored.
Potentially useful columns should be preserved in raw/source metadata or added to canonical tables.
Required columns should be validated with explicit error messages.
```

Do not require humans to manually delete columns before upload. That is operationally brittle.

### 2.8 Sponsorship Must Be Identified From National/International Conferences

The most concrete sponsorship rule from the meeting:

```text
National Conference and International Conference are sponsorship cues.
These are always sponsored by Cipla.
```

Business explanation:

```text
Cipla sponsors a doctor for a national/international conference.
After that, the doctor may do free/no-fee services for Cipla.
Separately, the doctor may show stronger prescription behavior after being sponsored.
```

Abhijeet described two narratives:

1. Sponsorship leads to free services:

```text
Doctor was sponsored for conference ABC.
After that, the doctor performed 6 no-fee/free services in the year.
Expected might have been only 2.
This is valuable even if not directly measured as prescriptions.
```

2. Sponsorship leads to prescription impact:

```text
Doctor was sponsored or paid.
After that, RCPA shows a jump, slump, or no change in Cipla prescriptions.
```

Architecture implication:

```text
Sponsorship cannot just be a text label in intervention_type.
It needs a modeled timeline:
  sponsorship event date
  sponsored doctor
  sponsorship category
  spend/contract evidence
  no-fee services after sponsorship
  RCPA before/after windows
```

### 2.9 No-Fee Agreement Is Related But Not Identical To Sponsorship

Varad and Abhijeet discussed "no fee agreement" in the smart contract system. The key point:

```text
No-fee agreement indicates work done without a new payment/agreement because it may already be aligned under a prior agreement or sponsorship.
```

For the product:

```text
No-fee/free-service activity should be counted as an outcome after sponsorship, not automatically treated as the sponsorship itself.
```

Correct model:

```text
sponsorship event:
  conference/travel/accommodation/consultancy sponsorship

free-service event:
  later no-fee activity performed by the same doctor

relationship:
  same doctor, after sponsorship date, within configurable time window
```

### 2.10 Doctor Detail Must Show Sponsorship Background

Near the end of transcript3, Abhijeet confirmed a specific UX behavior:

```text
When the user clicks a doctor/quadrant,
show background like:
  "we sponsored him for international conference ABC"
```

This should appear in the doctor detail drawer or equivalent drilldown. It should not be hidden behind an obscure export.

Current Doctor ROI detail already shows:

```text
engagement history
prescription trend
brand mix
```

Required addition:

```text
sponsorship timeline
free/no-fee service timeline
pre/post RCPA movement
confidence/data-quality notes
```

### 2.11 Leadership View Is Different From Brand Manager View

Varad's Power BI tool is brand-manager oriented:

```text
brand filters
therapy-level view
top five prescribed brands
which doctors prescribe a brand
brand trend over time
```

Abhijeet clarified that Aditya's platform is more leadership-facing:

```text
overall best doctors
top-line summaries
execution governance
budget discipline
doctor ROI
territory/resource deployment
data quality and confidence
```

Engineering implication:

```text
Do not clone the Power BI dashboard blindly.
Borrow the useful data relationships and metrics,
but design the product around leadership decisions.
```

Leadership questions include:

```text
Which doctors are high value but under-engaged?
Which sponsored doctors are giving free services back?
Which sponsored doctors show prescription uplift?
Which doctors have high spend but weak RCPA?
Which territories are self-serving loyalist territories?
Which territories are underserved and should get more field attention?
Where is data incomplete enough that decisions should be delayed?
```

### 2.12 Territory-Level Intelligence Is A New Direction

The second part of transcript4 introduced territory segmentation.

The business wants to identify:

```text
self-serving territories:
  doctors keep writing Cipla even without frequent visits

underserved territories:
  doctors may prescribe more if resources are deployed there

territories doing exceedingly well:
  top clusters by RCPA or growth

territories needing engagement:
  high potential but low current service/engagement
```

Kiran/leadership specifically asked for territory-level data because it helps deploy field resources.

Important nuance:

```text
Doctor rankings may not change dramatically every month.
Territory insights can change more often because field deployment changes territory behavior.
```

Required data:

```text
P-code
territory/patch
possibly region/cluster/task force
MR/rep alignment if available
monthly RCPA by territory
engagement/service frequency by territory
```

Current repo has `patch_name` in RCPA aliases and doctors. That can be the starting point, but it should be formalized into a territory dimension if the business expects territory analytics to be reliable.

### 2.13 File Size And Performance Matter

The RCPA/Power BI data files are large. Varad mentioned files around 150 MB, possibly 130 MB even as XLSB.

This validates existing repo choices:

```text
Do not persist detailed SKU-level RCPA online if it explodes storage.
Aggregate compact RCPA summaries for Supabase.
Keep detailed extracts local if needed.
Use efficient readers for XLSX/XLSB.
Paginate doctor details.
```

Required addition:

```text
Large RCPA ingestion should report progress and produce clear row-count summaries.
Failed large-file runs should be restartable without duplicate database rows.
```

## 3. Broad Overview Of Required Product Additions

The required build can be grouped into five product areas.

### 3.1 Autonomous Ingestion Standardization

Build a stronger ingestion contract so the platform can refresh from raw recurring extracts.

Required capabilities:

```text
profile raw files
detect source type
compare raw vs expected schema
map known column aliases
ignore irrelevant columns safely
flag missing required columns
store unknown/new columns in profiling reports
support idempotent re-runs
separate daily operational refresh from monthly RCPA refresh
show ingestion/data freshness in dashboard
```

### 3.2 Sponsorship Intelligence

Build a new analytics layer that identifies sponsored doctors and connects sponsorships to later business outcomes.

Required capabilities:

```text
classify sponsorship events from smart-contract/consolidation rows
especially National Conference and International Conference
link sponsorship rows to doctors through P-code
store contract ID where available
store request/intervention ID where contract ID is unavailable
track spend and dates
identify no-fee/free-service events after sponsorship
compare RCPA before and after sponsorship
show sponsorship background inside doctor detail
show portfolio-level sponsorship KPIs
```

### 3.3 Historical RCPA Backfill And Monthly RCPA Refresh

Support large historical RCPA files and ongoing monthly updates.

Required capabilities:

```text
ingest 2 years of historical RCPA with P-codes
support files around 150 MB
handle manually assigned P-codes with quality/provenance
aggregate online summaries by doctor/month/brand
preserve detailed extracts locally if needed
replace/update monthly RCPA without duplicates
show latest RCPA month and coverage window
```

### 3.4 Territory Intelligence

Add territory/patch-level analytical rollups for leadership and field resource deployment.

Required capabilities:

```text
load territory/patch/task-force attributes from RCPA/MSL/doctor master
roll up prescriptions and engagement by territory
classify self-serving loyalist territories
classify underserved/high-potential territories
expose top/bottom territory lists
allow AI questions about territory performance
```

### 3.5 AI Extension For Sponsorship And Territory Questions

The AI layer should summarize deterministic sponsorship and territory service outputs, not invent its own logic.

Required capabilities:

```text
query planner recognizes sponsorship, conference, no-fee, territory questions
context builder fetches compact sponsorship/territory service output
answer policy supports sponsorship and territory topics
response contract validates evidence references
redaction masks P-codes, doctor names, monetary amounts, contract IDs if needed
frontend suggested prompts include sponsorship/territory questions
```

## 4. Required Data To Build This Correctly

### 4.1 Minimum Data Needed From Business

The next implementation should not begin with blind coding. The minimum required data package is:

1. Two or three raw daily smart-contract/consolidation extracts.
   Needed to confirm whether the raw recurring report shape is stable.

2. The cleaned/presentable consolidation file already used.
   Needed for schema diffing against raw extracts.

3. The doctor-level contract report.
   Abhijeet mentioned one report may contain only doctor data with contract ID, while another contains the other activity details. We need both to reconcile contract IDs.

4. Historical RCPA file 1.
   Most recent year or current historical sheet, with manually assigned P-codes.

5. Historical RCPA file 2.
   Prior year, same format after cleanup.

6. One monthly RCPA update file.
   Needed to confirm ongoing monthly refresh shape after the historical backfill.

7. MSL/doctor master or equivalent.
   Needed for doctor identity, speciality, class, territory/patch, task force, active status.

8. Territory mapping.
   If not already fully present in RCPA `Patch`/`Territory`, provide explicit territory hierarchy.

9. Sponsorship taxonomy confirmation.
   At minimum:

```text
National Conference = sponsored
International Conference = sponsored
ERS = priority conference focus
No Fee Agreement = free/no-fee service outcome, not automatically sponsorship
```

10. Accommodation data definition.
    The transcript mentions "sponsorship, accommodation" as remaining work but does not define fields. We need to confirm whether accommodation is:

```text
part of sponsorship spend
separate travel/hotel record
included in conference sponsorship
or another smart-contract intervention subtype
```

### 4.2 Required Fields By Source

#### Smart Contract / Consolidation Activity Data

Required canonical fields:

```text
country
month
request ID / intervention ID
contract ID if available
association contract ID if available
intervention name
intervention type
intervention subtype
topic/remarks
intervention date
actual intervention date
venue
city
state
rep code
rep name
expected doctors
expected P-codes
actual doctors
actual P-codes
expected category
attended category
estimated intervention amount
approved/confirmed amount
actual BTU expense
actual BTC expense
total actual expense
association amount
association deliverables
request approval status
request confirmation status
post approval status
post confirmation status
expense submitted date
expense confirmed date
current owner stage
cancellation/rejection reason
source row number
source file/sheet
```

Existing repo support:

```text
ingestion/schema_maps.py already maps most of these fields in CONSOLIDATION_SCHEMA.
ingestion/loaders/consolidation.py already loads many of these into execution_requests.
ingestion/loaders/request_doctors.py already splits doctor/P-code lists into request_doctors.
```

Missing or needs hardening:

```text
contract ID may be missing from main report
must join with separate doctor-level contract report if supplied
sponsorship category is not modeled explicitly
accommodation fields are not modeled explicitly
national/international conference logic is not formalized
free/no-fee agreement classification is not formalized
```

#### RCPA Data

Required canonical fields:

```text
country
month
doctor name
P-code
legacy code if provided
active status
brand group
SKU
SKU detail
own_or_competitor
prescription quantity
prescription value
speciality
doctor class
patch/territory
task force if available
MR/rep if available
manual P-code mapping flag if available
source row number
source file/sheet
```

Existing repo support:

```text
RCPA_SCHEMA already maps country, month, doctor name, P-code, active status, brand, SKU, own/competitor, quantity, value, speciality, doctor class, and patch/territory.
Current RCPA repository stores compact summaries and doctor master data.
```

Missing or needs hardening:

```text
legacy code handling is not visibly first-class
manual P-code assignment provenance is not visibly modeled
territory should be promoted from a loose patch string to a usable analytic dimension
RCPA historical coverage and completeness need dashboard exposure
```

#### Doctor / MSL Master Data

Required canonical fields:

```text
country
P-code
doctor name
legacy code
speciality
doctor class
active status
territory/patch
region/cluster if available
task force
facility/account if available
source system
effective date or source month
```

Current repo has a `doctors` table but does not yet expose a full MSL import path as a distinct source class. It currently builds doctor master mostly from RCPA/attendance aggregates.

Recommendation:

```text
Add a doctor master/MSL loader if MSL data becomes available as a stable file.
Until then, keep deriving doctor attributes from RCPA and request attendance, but mark lower confidence.
```

#### Sponsorship And Accommodation Data

Required canonical fields:

```text
sponsorship event ID
request/intervention ID
contract ID
association contract ID
country
month
event/conference name
sponsorship category
conference type: national / international / ERS / other
doctor P-code
doctor name
doctor role: delegate / speaker / consultant / advisor / attendee
sponsored date or event date
approval/confirmation status
approved amount
actual amount
BTU/BTC split
association amount
currency
venue/city/country
accommodation/travel fields if available
source evidence and row number
```

Important:

```text
Do not infer sponsorship solely from spend amount.
Use explicit intervention type/subtype/name rules first.
National Conference and International Conference are confirmed sponsorship cues.
```

### 4.3 Required Business Rules To Confirm

Before implementation, confirm these:

| Rule | Recommended default | Needs business confirmation |
|---|---|---|
| Sponsorship classifier | `intervention_type/sub_type/name` contains National Conference or International Conference | Exact labels in raw report |
| ERS priority | Treat ERS as priority conference focus if present in event name/topic | Whether ERS should be separate category |
| Free/no-fee outcome | No-fee agreement after sponsorship is counted as free service outcome | Exact smart-contract field/value |
| RCPA pre/post window | 6 months before and 6 months after sponsorship | Business may prefer 3/6/12 months |
| Prescription uplift | Post-window Cipla quantity minus pre-window Cipla quantity, plus percent change | Whether to normalize by months available |
| Sponsorship ROI | Use actual total spend if available, otherwise confirmed amount, otherwise association amount | Finance owner must approve |
| Doctor identity | P-code required for confident doctor-level attribution | How to handle missing P-code historical rows |
| Territory | Use patch/territory from RCPA/MSL | Whether territory hierarchy has region/cluster |
| Causality language | Say "associated with", not "caused by" | Important for compliance and credibility |

## 5. Current Architecture Fit

The repo is already close to the right high-level architecture:

```text
ingestion CLI
  -> loaders and normalizers
  -> canonical repositories
  -> Supabase Postgres canonical tables
  -> materialized views
  -> FastAPI repositories/services/routers
  -> React dashboard
  -> backend-grounded AI
```

Current load-bearing pieces:

```text
ingestion/main.py
ingestion/orchestrator.py
ingestion/file_registry.py
ingestion/profiler.py
ingestion/schema_maps.py
ingestion/loaders/consolidation.py
ingestion/loaders/rcpa.py
ingestion/loaders/request_doctors.py
ingestion/repositories/canonical_repository.py
ingestion/repositories/rcpa_repository.py
database/views/mv_doctor_roi.sql
backend/app/repositories/doctor_repository.py
backend/app/services/doctor_service.py
frontend/src/pages/DoctorRoi.tsx
backend/app/services/ai/context_builder.py
```

The key gap is that sponsorship is currently implicit inside existing activity/intervention fields. The system can show doctor engagement and spend, but it cannot yet answer:

```text
Which doctors were sponsored for national/international conferences?
Which sponsored doctors later did no-fee services?
How did their RCPA move after sponsorship?
Which sponsorships have weak or missing P-code/contract evidence?
Which territories are self-serving or underserved?
```

Those answers require new modeled data and new materialized views.

## 6. Proposed Architecture Changes

### 6.1 Ingestion Layer Changes

#### 6.1.1 Add Raw Report Schema Audit

Add or extend profiling output so each run produces:

```text
source file
detected source type
sheet names
header row
canonical fields detected
required fields missing
known optional fields detected
unknown columns
columns ignored
columns present in raw but not in cleaned template
row counts
sample values for risky fields
```

This should be visible in ingestion reports and eventually Data Quality.

Implementation targets:

```text
ingestion/profiler.py
ingestion/file_registry.py
ingestion/schema_maps.py
ingestion/report.py
ingestion/tests/test_profiler.py
```

Why:

```text
The meeting explicitly identified raw-vs-presentable report drift as a risk.
The software should tell us what changed instead of failing silently.
```

#### 6.1.2 Extend Source Types

Current source types should remain:

```text
planner
execution_snapshot
consolidation
rcpa
```

Add source types if distinct files are provided:

```text
doctor_contracts
doctor_master_msl
territory_mapping
sponsorship_override
```

Do not add these blindly until sample files are available. If the data lives inside existing consolidation/RCPA files, derive from those instead.

#### 6.1.3 Add Sponsorship Classifier

Create deterministic classification logic:

```text
input:
  intervention_name
  intervention_type
  intervention_sub_type
  topic_remarks
  association_deliverables

output:
  sponsorship_category
  sponsorship_confidence
  sponsorship_reason
```

Initial rules:

```text
if intervention_type/sub_type/name contains "International Conference":
  category = international_conference
  confidence = high

if intervention_type/sub_type/name contains "National Conference":
  category = national_conference
  confidence = high

if event/name/topic contains "ERS":
  category = ers_conference
  confidence = medium/high depending exact field

if intervention type indicates no-fee agreement:
  category = no_fee_service
  confidence = high
  note = outcome candidate, not sponsorship source

if association deliverables mention travel/accommodation/sponsor:
  category = sponsored_support
  confidence = medium unless business confirms exact labels
```

Implementation target:

```text
ingestion/normalizers/sponsorship.py
ingestion/tests/test_sponsorship_normalizer.py
```

This must be deterministic. AI must not classify sponsorship from raw text.

#### 6.1.4 Extend Consolidation Loader Output

`ingestion/loaders/consolidation.py` already loads the activity-level facts. Extend it to emit derived sponsorship records in `LoadResult.extra`.

Possible output:

```python
LoadResult(
    records=execution_request_records,
    issues=issues,
    extra={
        "request_doctors": request_doctors,
        "sponsorship_events": sponsorship_events,
        "sponsorship_doctors": sponsorship_doctors,
    },
)
```

Important:

```text
Do not duplicate all execution request fields into sponsorship tables unless needed.
Prefer referencing execution_requests.id where possible.
```

#### 6.1.5 Add Doctor Contract Report Loader If Needed

The transcript says one report may contain only doctor's data with contract ID, while another has the rest of the information.

If that separate file exists, add:

```text
ingestion/loaders/doctor_contracts.py
```

Canonical output:

```text
source_file_id
country
request_id / intervention_id
contract_id
association_contract_id
pcode
doctor_name
contract_type
contract_date
contract_amount
source_row_number
```

Reconciliation strategy:

```text
primary join:
  request_id + pcode

secondary join:
  country + pcode + intervention_date/month + intervention_name similarity

fallback:
  store unmatched contract rows and show in data quality
```

#### 6.1.6 Add Territory Loader Or Formalize Patch

If territory is only in RCPA `Patch`, start by promoting `patch_name` to territory analytics.

If a separate territory file arrives, add:

```text
ingestion/loaders/territory_mapping.py
```

Canonical output:

```text
country
pcode
territory
region
cluster
task_force
rep_code
rep_name
effective_month
source_row_number
```

#### 6.1.7 Preserve Manual P-code Mapping Provenance

For historical RCPA cleanup, add optional fields:

```text
pcode_mapping_source
pcode_mapping_method
pcode_mapping_confidence
legacy_code
doctor_name_raw
doctor_name_cleaned
```

If the source files do not provide these columns, default them:

```text
pcode_mapping_method = source_supplied
pcode_mapping_confidence = unknown
```

For files built manually by Varad/Abhijeet:

```text
pcode_mapping_method = manual_backfill
```

This protects dashboard trust.

### 6.2 Database Schema Changes

#### 6.2.1 New Table: `sponsorship_events`

Purpose:

```text
One row per sponsorship-relevant activity/conference/support event.
```

Recommended columns:

```text
id uuid primary key
execution_request_id uuid null references execution_requests(id)
source_file_id uuid references source_files(id)
country_id uuid references countries(id)
calendar_month_id uuid references calendar_months(id)
request_uid text
req_id text
contract_id text null
association_contract_id text null
sponsorship_category text not null
sponsorship_confidence text not null
sponsorship_reason text not null
conference_name text null
conference_type text null
intervention_name text not null
intervention_type text null
intervention_sub_type text null
topic_remarks text null
event_date date null
actual_event_date date null
venue text null
city text null
state text null
confirmed_amount_local numeric null
actual_total_expense_local numeric null
actual_btu_expense_local numeric null
actual_btc_expense_local numeric null
association_amount_local numeric null
confirmed_amount_usd numeric null
actual_total_expense_usd numeric null
currency_code text null
fx_rate_status text null
workflow_status text null
source_row_number integer
source_references jsonb not null default '{}'
created_at timestamptz not null default now()
updated_at timestamptz not null default now()
```

Suggested unique key:

```text
unique(source_file_id, source_row_number, sponsorship_category)
```

Better stable key if request UID is reliable:

```text
unique(request_uid, sponsorship_category, conference_type)
```

#### 6.2.2 New Table: `sponsorship_doctors`

Purpose:

```text
One row per doctor attached to a sponsorship event.
```

Recommended columns:

```text
id uuid primary key
sponsorship_event_id uuid references sponsorship_events(id)
execution_request_id uuid null references execution_requests(id)
request_doctor_id uuid null references request_doctors(id)
country_id uuid references countries(id)
pcode_raw text null
pcode_normalized text null
doctor_name_raw text null
doctor_class_raw text null
doctor_role text null
attendance_type text null
link_status text not null
link_confidence numeric not null default 1
source_position integer null
source_references jsonb not null default '{}'
created_at timestamptz not null default now()
```

Suggested unique key:

```text
unique(sponsorship_event_id, pcode_normalized, doctor_role, source_position)
```

Data-quality rules:

```text
if P-code missing:
  keep row but link_status = missing_pcode

if doctor name present but P-code missing:
  do not join to RCPA automatically

if multiple P-codes found for one doctor name:
  flag conflict
```

#### 6.2.3 New Table: `doctor_identity_observations`

Purpose:

```text
Audit doctor names, P-codes, legacy codes, and mapping confidence across source files.
```

Recommended columns:

```text
id uuid primary key
source_file_id uuid references source_files(id)
country_id uuid references countries(id)
pcode_raw text null
pcode_normalized text null
legacy_code text null
doctor_name_raw text null
doctor_name_cleaned text null
speciality text null
doctor_class text null
territory text null
task_force text null
mapping_method text not null
mapping_confidence text not null
source_type text not null
source_row_number integer null
source_references jsonb not null default '{}'
created_at timestamptz not null default now()
```

This table is not a replacement for `doctors`. It is an audit trail behind doctor master resolution.

#### 6.2.4 New Table: `doctor_territory_assignments`

Purpose:

```text
Track doctor-to-territory mapping over time.
```

Recommended columns:

```text
id uuid primary key
country_id uuid references countries(id)
pcode_normalized text not null
territory text not null
region text null
cluster text null
task_force text null
rep_code text null
rep_name text null
effective_month_id uuid null references calendar_months(id)
source_file_id uuid references source_files(id)
source_row_number integer null
created_at timestamptz not null default now()
```

Suggested unique key:

```text
unique(country_id, pcode_normalized, territory, effective_month_id, source_file_id)
```

If territory changes over time, preserve history rather than overwriting blindly.

#### 6.2.5 Optional Table: `accommodation_records`

Only add this if the business supplies distinct accommodation/travel data.

Purpose:

```text
Store travel/hotel/accommodation support tied to sponsorship.
```

Recommended columns:

```text
id uuid primary key
sponsorship_event_id uuid null references sponsorship_events(id)
country_id uuid references countries(id)
pcode_normalized text null
doctor_name_raw text null
request_uid text null
contract_id text null
accommodation_type text null
city text null
hotel_or_vendor text null
start_date date null
end_date date null
amount_local numeric null
amount_usd numeric null
currency_code text null
source_file_id uuid references source_files(id)
source_row_number integer null
source_references jsonb not null default '{}'
```

If no distinct data exists, keep accommodation as:

```text
sponsorship_events.sponsorship_category = accommodation_support
```

### 6.3 Materialized View Changes

#### 6.3.1 `mv_doctor_sponsorship_outcomes`

Purpose:

```text
Doctor-level sponsorship outcome summary.
```

Grain:

```text
country_id + pcode_normalized
```

Metrics:

```text
sponsorship_count
first_sponsorship_date
last_sponsorship_date
national_conference_count
international_conference_count
ers_conference_count
sponsored_spend_usd
free_service_count_after_sponsorship
no_fee_service_count_after_sponsorship
latest_free_service_date
pre_sponsorship_cipla_rx_qty
post_sponsorship_cipla_rx_qty
rx_qty_delta
rx_qty_delta_pct
pre_sponsorship_cipla_share
post_sponsorship_cipla_share
cipla_share_delta
months_pre_observed
months_post_observed
has_sufficient_pre_window
has_sufficient_post_window
outcome_confidence
data_quality_flags
```

Important:

```text
This view should say "post-sponsorship movement", not "causal uplift".
```

#### 6.3.2 `mv_sponsorship_kpis`

Purpose:

```text
Portfolio-level sponsorship summary for dashboard cards.
```

Metrics:

```text
total_sponsorship_events
total_sponsored_doctors
events_missing_pcode
events_missing_contract_id
confirmed_sponsorship_spend_usd
actual_sponsorship_spend_usd
national_conference_events
international_conference_events
no_fee_services_after_sponsorship
doctors_with_positive_post_rx_movement
doctors_with_negative_post_rx_movement
doctors_with_insufficient_rcpa_window
```

Filters:

```text
country
month range
conference type
territory
sponsorship category
```

#### 6.3.3 Extend `mv_doctor_roi`

Add columns from sponsorship outcomes:

```text
sponsorship_count
last_sponsorship_date
sponsored_spend_usd
free_service_count_after_sponsorship
post_sponsorship_rx_delta
post_sponsorship_rx_delta_pct
sponsorship_outcome_label
territory
region
cluster
```

Potential labels:

```text
high_rx_no_sponsorship
sponsored_positive_movement
sponsored_no_movement
sponsored_negative_movement
sponsored_free_service_return
insufficient_post_window
missing_pcode_or_rcpa
```

#### 6.3.4 `mv_territory_opportunity`

Purpose:

```text
Territory-level resource deployment insight.
```

Grain:

```text
country_id + territory + month or rolling period
```

Metrics:

```text
doctor_count
active_doctor_count
cipla_rx_qty
competitor_rx_qty
total_rx_qty
cipla_share_qty
engagement_count
sponsored_doctor_count
spend_usd
rx_per_engagement
rx_per_spend_usd
high_value_unengaged_doctor_count
self_serving_doctor_count
underserved_doctor_count
latest_rcpa_month
```

Classification:

```text
self_serving_loyalist:
  high Cipla Rx/share with low recent engagement/spend

underserved_high_potential:
  strong total Rx or competitor opportunity with low Cipla share and low engagement

resource_intensive:
  high engagement/spend with weak Rx return

stable_core:
  strong Rx and adequate engagement
```

This view will power both dashboard and AI territory questions.

#### 6.3.5 Extend `mv_data_quality`

Add sponsorship/territory quality metrics:

```text
sponsorship_event_count
sponsorship_doctor_count
sponsorship_missing_pcode_count
sponsorship_missing_contract_id_count
sponsorship_unclassified_count
doctor_contract_unmatched_count
territory_coverage_pct
manual_pcode_mapping_count
manual_pcode_mapping_conflict_count
rcpa_pre_post_window_insufficient_count
```

### 6.4 Backend API Changes

Add a sponsorship module parallel to existing doctor/budget/data-quality services.

#### 6.4.1 New Files

```text
backend/app/schemas/sponsorship.py
backend/app/repositories/sponsorship_repository.py
backend/app/services/sponsorship_service.py
backend/app/routers/sponsorship.py
```

Register the router in:

```text
backend/app/routers/__init__.py
```

#### 6.4.2 API Endpoints

Recommended endpoints:

```text
GET /api/sponsorship/summary
GET /api/sponsorship/events
GET /api/sponsorship/doctors
GET /api/sponsorship/doctors/{countryCode}/{pcode}
GET /api/territories/opportunities
```

If keeping territory under sponsorship is too broad, use:

```text
backend/app/routers/territories.py
backend/app/services/territory_service.py
backend/app/repositories/territory_repository.py
```

#### 6.4.3 Response Contracts

`SponsorshipSummaryResponse`:

```text
meta
totalSponsorshipEvents
totalSponsoredDoctors
confirmedSpendUsd
actualSpendUsd
nationalConferenceCount
internationalConferenceCount
ersConferenceCount
freeServiceReturnCount
positiveRxMovementDoctorCount
insufficientRcpaWindowCount
missingPcodeCount
missingContractIdCount
rows
```

`SponsorshipDoctorRow`:

```text
countryCode
pcodeNormalized
doctorName
speciality
doctorClass
territory
sponsorshipCount
lastSponsorshipDate
sponsoredSpendUsd
conferenceTypes
freeServiceCountAfterSponsorship
preSponsorshipCiplaRxQty
postSponsorshipCiplaRxQty
rxQtyDelta
rxQtyDeltaPct
outcomeLabel
confidence
dataQualityFlags
```

`SponsorshipEventRow`:

```text
countryCode
month
requestId
contractId
interventionName
sponsorshipCategory
conferenceType
eventDate
doctorCount
confirmedAmountUsd
actualAmountUsd
workflowStatus
missingPcodeCount
sourceReferences
```

`DoctorSponsorshipDetailResponse`:

```text
profile
sponsorshipTimeline
freeServiceTimeline
prePostRcpaSummary
relatedEngagements
dataQualityFlags
limitations
```

#### 6.4.4 Extend Existing Doctor Detail

Current endpoint:

```text
GET /api/doctors/{countryCode}/{pcode}
```

Add:

```text
sponsorshipTimeline
freeServiceTimeline
sponsorshipOutcomeSummary
territoryContext
```

This directly satisfies the meeting requirement:

```text
When clicking a quadrant/doctor, show background like sponsored for International Conference ABC.
```

### 6.5 Frontend Changes

#### 6.5.1 Add Sponsorship Intelligence Page

Add a new page:

```text
frontend/src/pages/SponsorshipIntelligence.tsx
```

Add API client:

```text
frontend/src/api/sponsorship.ts
```

Add components:

```text
frontend/src/components/sponsorship/SponsorshipCards.tsx
frontend/src/components/sponsorship/SponsorshipDoctorTable.tsx
frontend/src/components/sponsorship/SponsorshipTimeline.tsx
frontend/src/components/sponsorship/SponsorshipOutcomeMatrix.tsx
```

Primary UI sections:

```text
KPI cards:
  sponsored doctors
  sponsorship spend
  free-service returns
  positive RCPA movement
  insufficient evidence

Filters:
  country
  month range
  conference type
  territory
  outcome label
  data-quality flag

Doctor outcome table:
  doctor
  P-code
  territory
  sponsorship count
  spend
  free-service count
  RCPA pre/post movement
  confidence

Event table:
  conference/event
  request ID
  contract ID
  date
  doctor count
  amount
  workflow status

Outcome matrix:
  sponsored positive movement
  sponsored no movement
  sponsored negative movement
  no RCPA / insufficient window
```

#### 6.5.2 Extend Doctor ROI Page

Modify:

```text
frontend/src/pages/DoctorRoi.tsx
frontend/src/components/doctors/DoctorRoiComponents.tsx
frontend/src/types/api.ts
```

Add filters:

```text
territory
sponsorship status
conference type
post-sponsorship outcome
```

Add columns/badges:

```text
sponsorship count
last sponsorship
free service return
post-sponsorship RCPA delta
territory
```

Add detail drawer sections:

```text
Sponsorship background
  conference name/type/date/amount

Free/no-fee services after sponsorship
  request/event/date/status

RCPA movement after sponsorship
  pre-window quantity
  post-window quantity
  delta
  confidence

Data caveats
  missing P-code
  missing contract ID
  insufficient RCPA window
```

#### 6.5.3 Add Territory View

This can be either:

```text
new page: Territory Intelligence
```

or a section inside Sponsorship Intelligence.

Recommended: add it as its own page if data quality is strong enough, because territory is a separate leadership workflow.

Primary UI:

```text
territory leaderboard
self-serving territories
underserved territories
resource-intensive territories
top doctors inside selected territory
RCPA trend by territory
engagement/spend by territory
```

#### 6.5.4 Extend AI Panel Suggested Prompts

Add prompts:

```text
Which sponsored doctors gave the strongest free-service return?
Which sponsored doctors improved after conference support?
Which sponsored doctors have weak RCPA evidence?
Which territories are underserved?
Which territories are self-serving loyalist territories?
```

### 6.6 AI Layer Changes

#### 6.6.1 `query_planner.py`

Add topics:

```text
sponsorship:
  sponsor, sponsored, sponsorship, conference, international, national, ERS, no-fee, free service, accommodation

territory:
  territory, patch, region, cluster, underserved, self-serving, field resource, deploy, mobilize
```

Map sections:

```text
sponsorship -> sponsorshipSummary, sponsoredDoctorRows, sponsorshipEvents
territory -> territoryOpportunityRows, territorySummary
```

#### 6.6.2 `context_builder.py`

Add service calls:

```text
SponsorshipService(session).summary(...)
SponsorshipService(session).doctors(...)
SponsorshipService(session).events(...)
TerritoryService(session).opportunities(...)
```

Keep context compact:

```text
top 10 sponsored doctors
top 10 weak-evidence sponsored doctors
top 10 territory opportunities
summary cards
limitations
```

Do not send:

```text
full doctor lists
raw workbook rows
unbounded event histories
unredacted contract IDs if considered sensitive
```

#### 6.6.3 `answer_policy.py`

Add supported topic routing for:

```text
sponsorship
territory
accommodation if data exists
```

Fallback answers should be useful without Gemini:

```text
"I found X sponsored doctors, Y with positive post-sponsorship RCPA movement, and Z with insufficient RCPA coverage..."
```

#### 6.6.4 `response_contract.py`

Allow evidence references to sponsorship and territory paths:

```text
sponsorship.summary
sponsorship.topDoctorRows
sponsorship.eventRows
territory.opportunityRows
```

#### 6.6.5 `redaction.py`

Extend if needed:

```text
contract IDs
association contract IDs
doctor names
P-codes
monetary amounts
raw source snippets
```

### 6.7 Data Quality Changes

New dashboard warnings:

```text
Some sponsorship events are missing P-code, so they cannot be joined to RCPA.
Some sponsorship events are missing contract ID; request ID was used instead.
Some historical RCPA P-codes were manually assigned; validate before executive decisions.
Some doctors have insufficient pre/post RCPA months to judge movement.
Territory coverage is incomplete for selected markets.
```

New ingestion validations:

```text
national/international conference row without doctor P-code
sponsorship row without date
sponsorship row without amount
doctor-contract row not matched to execution request
P-code maps to multiple doctor names in same country
doctor name maps to multiple P-codes in same country
territory missing for active RCPA doctor
manual mapping confidence missing for historical RCPA backfill
```

### 6.8 Testing Plan

#### Ingestion Tests

Add:

```text
ingestion/tests/loaders/test_sponsorship_loader.py
ingestion/tests/loaders/test_doctor_contract_loader.py
ingestion/tests/loaders/test_territory_loader.py
ingestion/tests/test_sponsorship_normalizer.py
ingestion/tests/test_schema_drift_report.py
```

Cases:

```text
National Conference classified as sponsorship
International Conference classified as sponsorship
ERS recognized as priority conference
No Fee Agreement classified as free-service outcome
missing P-code creates warning but preserves row
contract ID from separate doctor report joins by request ID + P-code
unmatched contract rows are reported
manual historical P-code mapping provenance is stored
territory/patch is loaded and normalized
large RCPA sample aggregates without duplicate rows
```

#### Database Tests

Add:

```text
backend/tests/database/test_sponsorship_views.py
backend/tests/database/test_territory_opportunity_view.py
backend/tests/database/test_sponsorship_data_quality.py
```

Cases:

```text
pre/post RCPA windows calculate correctly
free-service count after sponsorship is date-bounded
missing post-window lowers confidence
same doctor with multiple sponsorships aggregates correctly
territory classifications are deterministic
high Rx / low engagement territory becomes self-serving
high potential / low engagement territory becomes underserved
```

#### API Tests

Add:

```text
backend/tests/api/test_sponsorship_api.py
backend/tests/api/test_territory_api.py
```

Cases:

```text
pagination
filters
sorts
response aliases camelCase
limitations included
data-quality flags included
doctor sponsorship detail includes timeline
```

#### Frontend Tests

Add:

```text
frontend/tests/sponsorship-intelligence.test.tsx
frontend/tests/territory-intelligence.test.tsx
frontend/tests/doctor-sponsorship-detail.test.tsx
frontend/tests/ai-sponsorship-prompts.test.tsx
```

Cases:

```text
loading/error/empty states
summary cards render
filters update API calls
doctor detail shows sponsorship background
missing-data warnings render
AI prompt sends pageContext sponsorship or territory
```

## 7. Recommended Implementation Sequence

### Phase 1: Data Contract And Schema Drift Audit

Goal:

```text
Know exactly what the raw recurring reports look like.
```

Work:

```text
collect 2-3 raw daily smart-contract/consolidation extracts
collect cleaned/presentable file
run profiler
document raw-vs-cleaned differences
update schema aliases
decide ignored vs persisted columns
```

Output:

```text
machine-readable source contract
schema drift report
updated loader tests
```

### Phase 2: Sponsorship Classification In Ingestion

Goal:

```text
Turn national/international conference rows into structured sponsorship facts.
```

Work:

```text
add sponsorship normalizer
add sponsorship tables migration
extend consolidation loader
persist sponsorship_events and sponsorship_doctors
add data-quality warnings
```

Output:

```text
first sponsorship records in Supabase
validated national/international conference classification
doctor P-code coverage report
```

### Phase 3: Contract-ID And Doctor Identity Hardening

Goal:

```text
Connect doctor-level contract IDs and historical P-code mappings.
```

Work:

```text
load doctor contract report if supplied
reconcile contract ID to request + P-code
add doctor identity observations
store manual mapping provenance
surface mapping conflicts
```

Output:

```text
contract ID coverage
manual P-code mapping coverage
identity conflict warnings
```

### Phase 4: Sponsorship Outcome Views

Goal:

```text
Answer business questions from deterministic SQL, not ad hoc frontend math.
```

Work:

```text
create mv_doctor_sponsorship_outcomes
create mv_sponsorship_kpis
extend mv_doctor_roi
extend mv_data_quality
add refresh script
```

Output:

```text
doctor-level sponsorship outcomes
portfolio-level sponsorship KPIs
doctor ROI enriched with sponsorship context
```

### Phase 5: Backend APIs

Goal:

```text
Expose sponsorship and territory facts through typed services.
```

Work:

```text
schemas
repository
service
router
filter validation
API tests
```

Output:

```text
/api/sponsorship/*
/api/territories/*
extended /api/doctors/{countryCode}/{pcode}
```

### Phase 6: Frontend Dashboard

Goal:

```text
Make sponsorship insight visible to leadership.
```

Work:

```text
add Sponsorship Intelligence page
extend Doctor ROI detail drawer
add territory section/page
add filters and data-quality states
```

Output:

```text
leadership can inspect sponsored doctors, outcomes, and data caveats
doctor detail shows sponsorship background
territory opportunity becomes visible
```

### Phase 7: AI Sponsorship And Territory Support

Goal:

```text
Let AI explain sponsorship and territory results from trusted service context.
```

Work:

```text
extend query planner
extend context builder
extend answer policy
extend response contract
add frontend prompts
add tests
```

Output:

```text
AI can answer supported sponsorship/territory questions with evidence and limitations.
```

## 8. Key Architecture Principles

### 8.1 Deterministic First, AI Second

Sponsorship classification, RCPA movement, free-service counts, territory labels, and ROI segments must be computed by code/SQL.

AI can explain:

```text
what happened
why a doctor is flagged
where to verify
what limitations apply
```

AI must not decide:

```text
whether a row is sponsorship
whether Rx improved
whether a territory is underserved
how much was spent
which doctor maps to which P-code
```

### 8.2 Do Not Overclaim Causality

The system should avoid wording like:

```text
Sponsorship caused this doctor to increase prescriptions.
```

Use:

```text
Post-sponsorship RCPA movement was positive.
Prescription volume increased after the sponsorship window.
This is an association, not proof of causality.
```

This matters for credibility and compliance.

### 8.3 Raw Source Auditability Is Mandatory

Every sponsorship and RCPA outcome should be traceable to:

```text
source file
sheet
row number
request ID
contract ID if available
P-code
classification reason
```

The user should be able to answer:

```text
Why did the system say this doctor was sponsored?
Which row did it come from?
Was it National Conference or International Conference?
Was P-code source-supplied or manually assigned?
```

### 8.4 Missing Data Must Be Visible

Bad outcome:

```text
doctor appears as no sponsorship because P-code is missing
```

Correct outcome:

```text
doctor has unlinked sponsorship evidence due to missing P-code
dashboard shows warning
data quality page explains unresolved rows
```

### 8.5 Keep Frontend Thin

Frontend should render:

```text
cards
tables
filters
charts
drilldowns
warnings
```

Backend/SQL should compute:

```text
classification
pre/post windows
counts
deltas
segments
territory labels
confidence
limitations
```

## 9. Concrete Product Questions The Built System Should Answer

### Sponsorship Questions

```text
How many doctors were sponsored through national/international conferences?
Which sponsored doctors later performed free/no-fee services?
Which doctors show positive RCPA movement after sponsorship?
Which sponsored doctors show weak or negative RCPA movement?
Which sponsored doctors do not have enough RCPA history to judge yet?
Which sponsorship events are missing P-code or contract ID?
Which conference types have the best post-sponsorship outcomes?
```

### Doctor ROI Questions

```text
Which doctors are high value but have no engagement?
Which doctors receive high spend but have weak prescriptions?
Which doctors have strong RCPA and also provide free services after sponsorship?
Which doctors should be considered for future international conferences?
Which doctors have duplicate/messy identity risk?
```

### Territory Questions

```text
Which territories are self-serving loyalist territories?
Which territories are underserved?
Which territories have high competitor opportunity?
Which territories have high engagement but weak RCPA return?
Which territories should field teams prioritize next month?
```

### Ingestion/Data Quality Questions

```text
Did today's daily extract load successfully?
Did any raw report columns change?
Which required columns were missing?
What is the latest RCPA month?
How complete is P-code coverage?
How many historical P-codes were manually assigned?
How many sponsorship records cannot be joined to RCPA?
```

## 10. Final Engineering Recommendation

Do not build sponsorship as a quick visual add-on inside the existing Doctor ROI page only. That would be fast but strategically weak.

The right design is:

```text
1. Keep execution_requests as the canonical activity spine.
2. Add sponsorship_events as a derived but explicit sponsorship spine.
3. Add sponsorship_doctors as the doctor-level bridge.
4. Join to RCPA through country + P-code + time windows.
5. Join to no-fee/free-service events through same doctor after sponsorship date.
6. Promote territory to a real analytical dimension.
7. Surface all of this through materialized views, typed services, frontend drilldowns, and grounded AI context.
```

This gives the business what was discussed:

```text
reusable ingestion
minimal manual reshaping
daily operational refresh
monthly RCPA refresh
historical RCPA baselines
doctor sponsorship background
free-service return tracking
post-sponsorship RCPA movement
territory-level deployment insights
AI that can explain the above with evidence
```

It also keeps the architecture consistent with the existing repository:

```text
ingestion owns writes
Postgres owns facts and materialized views
backend services own contracts and business response shaping
frontend owns interaction and visualization
AI summarizes deterministic service outputs only
```

## 11. Open Items To Resolve With Business

These should be resolved before coding the final sponsorship implementation:

1. Provide two or three raw daily smart-contract/consolidation extracts.
2. Provide the separate doctor-level contract report if it exists.
3. Confirm exact labels for National Conference, International Conference, ERS, no-fee agreement, accommodation, and sponsorship.
4. Confirm whether accommodation has separate fields or is embedded in sponsorship/conference spend.
5. Confirm preferred pre/post RCPA comparison window: 3, 6, or 12 months.
6. Confirm whether sponsorship ROI should use confirmed amount, actual spend, association amount, or a hierarchy of those values.
7. Confirm whether territory means patch, region, cluster, task force, or a hierarchy of all of them.
8. Confirm whether legacy code must be modeled alongside P-code for brand/task-force aggregation.
9. Confirm how manually assigned historical P-codes should be flagged in the source files.
10. Confirm compliance language for sponsorship and prescription association so dashboard labels do not imply causal claims.

