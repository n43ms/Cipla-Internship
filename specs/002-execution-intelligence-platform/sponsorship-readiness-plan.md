# Sponsorship And Territory Implementation Readiness Plan

**Feature Context**: Extension of `002-execution-intelligence-platform`

**Created**: 2026-07-04

**Primary Inputs**:

- `specs/002-execution-intelligence-platform/spec.md`
- `specs/002-execution-intelligence-platform/plan.md`
- `specs/002-execution-intelligence-platform/tasks.md`
- `ingestion_sponsorship.md`
- `files/transcript3.txt`
- `files/transcript4.txt`
- current repository architecture
- current Supabase database footprint

**Purpose**:

This is a supplemental implementation plan for the sponsorship, repeated-ingestion, historical RCPA, territory, accommodation, and AI-extension work discussed after the original execution-intelligence scope was implemented.

It does not replace the original `plan.md`. It exists because the original `tasks.md` is mostly complete for the current product surface, while the new sponsorship/territory work depends on data that has not arrived yet. The correct engineering approach is to prepare the architecture and intake process now, then implement each source-specific slice only after real source files prove the schema.

## Executive Decision

Build the next phase as an evidence-gated vertical-slice program.

Do not build a full set of fake sponsorship, accommodation, doctor-contract, and territory modules before the data arrives. That would create speculative schema, unused APIs, brittle placeholder UI, and rework when the real files differ.

Do build the data-agnostic readiness layer now:

```text
source intake checklist
schema drift profiling
raw-vs-cleaned comparison workflow
storage budget checks
source contract templates
synthetic fixture pattern
implementation gates
feature-flag boundaries
```

Then, when each real data source arrives:

```text
profile source
record actual schema
write tiny synthetic fixture
implement loader
persist compact canonical facts
build or extend materialized view
expose typed backend service/API
render frontend surface
add grounded AI context only after deterministic service output is stable
```

This minimizes credit burn, prevents architectural drift, and keeps the system understandable.

## Current System Baseline

### Existing Runtime Boundaries

The repo already has the right high-level architecture:

```text
local raw workbooks
  -> ingestion CLI
  -> workbook profiling
  -> deterministic normalization
  -> canonical Supabase Postgres tables
  -> materialized KPI/data-quality views
  -> FastAPI repositories/services/routers
  -> React dashboard
  -> backend-grounded AI assistant
```

Existing critical layers:

```text
ingestion/
  main.py
  orchestrator.py
  file_registry.py
  profiler.py
  workbook_reader.py
  schema_maps.py
  loaders/
  normalizers/
  validators/
  repositories/

database/
  migrations/
  views/

backend/app/
  repositories/
  services/
  routers/
  schemas/
  services/ai/

frontend/src/
  api/
  pages/
  components/
  types/
```

This is the right base. The next phase should extend these boundaries, not bypass them.

### Completed Product Capabilities

Based on `tasks.md`, the existing platform already has:

```text
planner ingestion
execution snapshot ingestion
consolidation ingestion
request doctor splitting
RCPA compact summary ingestion
event reconciliation
budget utilization
workflow governance
intervention mix
doctor ROI and quadrant logic
data quality page
backend services and routers
frontend dashboard pages
grounded AI panel
Gemini/test/null provider abstraction
AI redaction and deterministic fallback
```

Therefore the next plan should not duplicate these foundations. It should add sponsorship and territory support through the same architectural pattern.

### Current Database Constraint

Current Supabase database size was checked through Postgres:

```text
current database size: 321 MB
Supabase Free database limit: 500 MB
remaining budget: ~179 MB
```

The largest current objects are RCPA summaries:

```text
rcpa_doctor_month_summary   ~190 MB
rcpa_doctor_brand_summary    ~73 MB
doctors                      ~13 MB
mv_doctor_roi                ~9 MB
```

This means the sponsorship plan is feasible on the current architecture only if Supabase remains a compact dashboard-serving database.

The next phase must not store:

```text
raw workbooks
full raw RCPA rows
unbounded SKU-level detail
large per-row source JSON blobs
duplicated RCPA snapshots across many materialized views
unbounded AI/query/audit history
```

Supabase should store:

```text
canonical compact facts
doctor/month and doctor/brand summaries
sponsorship facts
doctor-sponsorship bridges
territory summaries
materialized dashboard views
ingestion audit metadata
```

## Constitution Check

This plan is checked against `.specify/memory/constitution.md`.

### I. Trusted Data Before Dashboards

**Status**: PASS

No dashboard implementation is allowed before source files are profiled, source contracts are recorded, and quality gates exist. Raw-vs-cleaned schema drift is treated as a first-class risk.

### II. Explicit Reconciliation, Not Hidden Guesswork

**Status**: PASS

Doctor sponsorship, doctor contract, no-fee service, RCPA movement, and territory joins must be queryable and auditable. Name-based matching is not allowed as a silent primary join.

### III. Deterministic Business Logic And Grounded AI

**Status**: PASS

Sponsorship classification, pre/post RCPA windows, territory segments, and free-service counts must be deterministic SQL/Python/service logic. AI may summarize these outputs only after they exist as backend service context.

### IV. Testable Ingestion, APIs, And User Journeys

**Status**: PASS

Every source-specific implementation requires synthetic fixtures based on actual observed schemas, plus ingestion, database, API, frontend, and AI tests where applicable.

### V. Deployable, Secure, And Product-Grade UX

**Status**: PASS

Raw data remains local or in approved business storage. Secrets stay server-side. New UI must include loading, empty, error, partial-data, stale-data, and low-confidence states.

## Planning Principle: Evidence-Gated Vertical Slices

The core rule for this phase:

```text
No real source-specific schema, migration, loader, dashboard, or AI context is final until at least one real source sample has been profiled.
```

This prevents bad assumptions around:

```text
actual column names
contract ID availability
sponsorship labels
no-fee labels
accommodation structure
territory hierarchy
monthly RCPA shape
manual P-code mapping columns
file cadence
file naming
duplicate keys
```

## What To Build Before Data Arrives

Only build durable, data-agnostic infrastructure.

### 1. Source Intake Contract Template

Create a machine-readable and human-readable source contract template, but do not lock final contracts.

Recommended file:

```text
specs/002-execution-intelligence-platform/contracts/source-intake-contract.md
```

Purpose:

```text
document expected source name
business owner
source system
cadence
file naming pattern
sheet names
required fields
optional fields
identity fields
date fields
money fields
doctor fields
known labels
quality risks
```

This is safe to build now because it documents questions rather than assuming answers.

### 2. Schema Drift Profiling Plan

Enhance or plan enhancements to the existing profiler so every incoming file can produce:

```text
detected source type
sheet names
detected header row
raw columns
mapped canonical fields
required fields present/missing
known optional fields present/missing
unknown extra columns
empty columns
data type samples
row count
source period
source country
file hash
profile timestamp
```

This belongs near:

```text
ingestion/profiler.py
ingestion/schema_maps.py
ingestion/report.py
ingestion/tests/test_profiler.py
```

Important boundary:

```text
Do not add sponsorship-specific required fields until real files confirm them.
```

### 3. Raw-Vs-Cleaned Comparison Workflow

The transcript revealed that the business shared cleaned/presentable files, while recurring extracts may include extra columns.

Build or plan a comparison report:

```text
raw file columns
cleaned file columns
columns removed by business cleanup
columns renamed
columns newly present
columns absent from recurring raw extract
columns that map to existing schema
columns requiring business decision
```

This can be implemented generically against two workbook profiles without knowing sponsorship schema.

### 4. Storage Budget Report

Because the database is already 321 MB, add a repeatable database-size check before and after large ingestion runs.

Recommended output:

```text
database size
largest tables
largest materialized views
estimated free-tier headroom
RCPA summary row counts
AI log size
source/audit table size
```

This can be a docs/runbook task or a small script.

Potential location:

```text
docs/storage-budget.md
scripts/db_size_report.ps1
```

Do not build paid-infra assumptions into the app. Keep compact mode as the default.

### 5. Feature Flags / Disabled Navigation Strategy

Prepare a clean way to hide incomplete pages without placeholder UI.

Recommended principle:

```text
Do not show Sponsorship or Territory pages until API data exists.
Do not add dummy cards or fake empty tables.
```

If feature flags are needed:

```text
VITE_ENABLE_SPONSORSHIP=false
VITE_ENABLE_TERRITORY=false
```

But do not add these until there is a concrete frontend route to guard.

### 6. Synthetic Fixture Strategy

Define the fixture policy now:

```text
Every real source sample produces a tiny synthetic fixture.
No real Cipla data enters git.
Fixtures must cover the exact observed edge case.
```

Examples once data arrives:

```text
national conference row
international conference row
no-fee agreement row
doctor contract row with contract ID
doctor contract row missing P-code
RCPA monthly row with manual P-code
territory row with patch/cluster
accommodation row if present
```

Do not create fake fixtures for labels that have not been confirmed.

## What Not To Build Before Data Arrives

Avoid these until source samples are profiled:

```text
final sponsorship_events migration
final sponsorship_doctors migration
doctor_contracts loader
territory_mapping loader
accommodation loader
sponsorship materialized views
territory materialized views
sponsorship backend router
territory backend router
sponsorship frontend page
territory frontend page
AI sponsorship context
AI territory context
hard-coded National/International/ERS/no-fee rules beyond documented draft
```

Rationale:

These depend on exact real-world labels, columns, identifiers, and cardinality. Guessing them now creates rework.

## Data Arrival Gates

Each source must pass these gates before implementation.

### Gate A: File Is Real Recurring Source

Acceptable:

```text
raw exported Excel/XLSB/CSV exactly as generated by the system
not manually deleted columns
not renamed headers
not Power BI-only transformed data
```

If only cleaned data is available, mark it as:

```text
presentation source, not recurring source of truth
```

### Gate B: Source Profile Complete

The file must have:

```text
profile report
sheet names
headers
row counts
mapped fields
unknown fields
required/missing fields
sample values for labels
source period and country scope
```

### Gate C: Business Labels Confirmed

Required before classifier logic:

```text
exact National Conference label
exact International Conference label
exact ERS label if present
exact No Fee Agreement label
exact accommodation/travel labels
exact sponsorship/consultancy/speaker/advisory labels
```

### Gate D: Stable Keys Identified

Required before persistence:

```text
request/intervention ID behavior known
contract ID availability known
country + P-code uniqueness confirmed
doctor contract join key confirmed
monthly RCPA replacement grain confirmed
territory effective-date behavior known
```

### Gate E: Storage Impact Estimated

Before loading into Supabase:

```text
expected row count
expected table size
materialized view size estimate
retention policy
compact-vs-detail decision
```

If projected storage exceeds free-tier headroom, keep detail local and store only compact summaries.

## Full Implementation Roadmap

### Phase 0: Readiness Work Before Data Arrives

**Goal**: Prepare intake, profiling, and decision gates without assuming source details.

Allowed work:

```text
write source intake contract template
write storage budget runbook or script
define raw-vs-cleaned comparison workflow
define feature flag policy
document vertical-slice implementation rules
review current data dictionary for extension points
prepare task backlog, but do not mark source-specific tasks as implementation-ready
```

Blocked work:

```text
source-specific migrations
source-specific loaders
source-specific API endpoints
source-specific dashboards
source-specific AI contexts
```

Exit criteria:

```text
business knows exactly what data to send
engineer has an intake checklist
incoming files can be profiled before code decisions
storage budget can be measured before and after loads
```

### Phase 1: Raw Consolidation / Smart-Contract Intake

**Trigger**: Abhijeet/Anil provides 3-5 raw recurring extracts plus a cleaned comparison file.

**Goal**: Determine whether current consolidation ingestion can support daily refresh and sponsorship classification.

Steps:

```text
1. Profile each raw extract.
2. Profile matching cleaned/presentable file.
3. Generate raw-vs-cleaned diff.
4. Map raw columns to existing CONSOLIDATION_SCHEMA.
5. Identify columns currently ignored but business-relevant.
6. Identify sponsorship/no-fee/conference labels in actual data.
7. Identify whether contract ID is present in this source.
8. Create tiny synthetic fixture matching observed raw shape.
9. Add tests for newly observed aliases or required fields.
10. Only then extend loader/schema maps if needed.
```

Potential implementation files:

```text
ingestion/schema_maps.py
ingestion/loaders/consolidation.py
ingestion/normalizers/sponsorship.py
ingestion/tests/loaders/test_consolidation_loader.py
ingestion/tests/loaders/test_sponsorship_classification.py
```

Do not create sponsorship database tables in this phase unless the real raw data proves classification fields and doctor linkage are usable.

Exit criteria:

```text
raw recurring consolidation file can be ingested or rejected with explicit validation
known schema drift is documented
sponsorship/no-fee candidate labels are known
contract ID availability is known
```

### Phase 2: Sponsorship Classification Slice

**Trigger**: Phase 1 confirms sponsorship labels and doctor linkage.

**Goal**: Create deterministic sponsorship facts from actual observed source rows.

Implementation sequence:

```text
1. Add sponsorship normalizer rules from confirmed labels.
2. Add synthetic fixtures for each confirmed label.
3. Add ingestion tests first.
4. Add minimal database migration for sponsorship facts.
5. Extend canonical persistence.
6. Add data-quality warnings for missing P-code, missing date, missing contract ID.
7. Create compact sponsorship summary view.
8. Add backend read service only after view compiles and tests pass.
```

Recommended first schema should be minimal:

```text
sponsorship_events
  execution_request_id
  country_id
  calendar_month_id
  request_uid
  req_id
  contract_id nullable
  association_contract_id nullable
  sponsorship_category
  sponsorship_reason
  sponsorship_confidence
  event_date
  intervention_name/type/subtype
  amount fields already available from execution_requests or copied only if needed
  source references

sponsorship_doctors
  sponsorship_event_id
  request_doctor_id nullable
  country_id
  pcode_raw
  pcode_normalized
  doctor_name_raw
  doctor_role nullable
  link_status
  source_position
```

Keep the first migration compact. Do not add accommodation, territory, or outcome columns until those sources are confirmed.

Exit criteria:

```text
National/International/other confirmed sponsorship rows are stored deterministically
doctor links are visible and auditable
missing P-code rows are preserved as low-confidence/unlinked
no dashboard claims causal prescription impact yet
```

### Phase 3: Doctor-Level Contract Report Slice

**Trigger**: Separate doctor-level contract report is provided.

**Goal**: Attach contract IDs and doctor-level agreement evidence to sponsorship/activity facts.

Steps:

```text
1. Profile doctor contract report.
2. Confirm join keys: request ID, contract ID, P-code, country, date.
3. Decide whether this is a new source type.
4. Create synthetic fixture.
5. Implement loader only after schema is known.
6. Add reconciliation table or extend sponsorship_doctors with contract references.
7. Add unmatched-contract data-quality output.
```

Preferred join order:

```text
request_id + country + pcode
contract_id + pcode
country + pcode + month + event name similarity only as explicit weak match
```

Name-only matching is not allowed as an automatic confident join.

Exit criteria:

```text
contract ID coverage is measurable
unmatched contract rows are visible
doctor-level agreement evidence can enrich detail views
```

### Phase 4: Historical RCPA Backfill Hardening

**Trigger**: Historical RCPA files with P-codes arrive.

**Goal**: Load historical RCPA without breaking free-tier storage or corrupting doctor identity.

Steps:

```text
1. Profile historical RCPA file 1.
2. Profile historical RCPA file 2.
3. Compare against current RCPA_SCHEMA.
4. Confirm monthly replacement grain.
5. Confirm manual P-code mapping fields, if any.
6. Estimate storage before load.
7. Load to compact summaries only.
8. Keep detailed evidence local under data/processed.
9. Refresh doctor ROI view.
10. Report coverage window and P-code coverage.
```

Storage rules:

```text
Do not store raw RCPA detail online.
Do not store detailed SKU-level rows online unless storage budget is explicitly approved.
Prefer compact doctor-month, doctor-brand, and country-brand-month summaries.
Track database size before and after load.
```

If manual P-code mapping fields exist, add them to audit/provenance. If they do not exist, do not invent precision; mark mapping provenance as unknown/source_supplied.

Exit criteria:

```text
historical RCPA extends doctor ROI baseline
latest RCPA coverage window is visible
manual/unknown P-code mapping limitations are visible
database remains below storage budget
```

### Phase 5: Monthly RCPA Refresh Slice

**Trigger**: 2-3 monthly RCPA refresh samples arrive.

**Goal**: Support repeatable monthly updates safely.

Steps:

```text
1. Profile each monthly sample.
2. Compare monthly sample shape to historical backfill shape.
3. Confirm whether files contain one month or rolling history.
4. Confirm whether monthly load should replace month or append new month.
5. Add idempotency tests for rerun behavior.
6. Add clear ingestion summary for replaced/inserted rows.
```

Exit criteria:

```text
same monthly RCPA file can be re-run without duplicates
new month updates doctor ROI and RCPA freshness
partial month/missing P-code issues are visible
```

### Phase 6: Sponsorship Outcome Views

**Trigger**: Sponsorship facts and sufficient RCPA history are loaded.

**Goal**: Create deterministic outcomes without causal overclaiming.

Views should be built only after source coverage is strong enough:

```text
mv_doctor_sponsorship_outcomes
mv_sponsorship_kpis
extensions to mv_doctor_roi
extensions to mv_data_quality
```

Metrics:

```text
sponsorship count
first/last sponsorship date
conference type counts
sponsorship spend
free/no-fee services after sponsorship
pre-window Cipla Rx
post-window Cipla Rx
Rx delta
Rx delta percentage
months observed before/after
outcome confidence
data-quality flags
```

Default comparison window should not be hard-coded as final until business confirms it. Initial implementation can support configurable windows:

```text
SPONSORSHIP_PRE_WINDOW_MONTHS=6
SPONSORSHIP_POST_WINDOW_MONTHS=6
```

But labels must say:

```text
post-sponsorship movement
associated movement
not causal uplift
```

Exit criteria:

```text
doctor-level sponsorship outcomes are deterministic and explainable
insufficient RCPA windows lower confidence
causal language is avoided
```

### Phase 7: Doctor ROI Detail Extension

**Trigger**: Sponsorship outcome service exists.

**Goal**: Add sponsorship background to existing doctor detail drawer.

This directly satisfies the transcript requirement:

```text
when clicking a quadrant/doctor, show background like sponsored for international conference ABC
```

Implementation sequence:

```text
1. Extend backend doctor detail schema.
2. Add repository query for sponsorship timeline.
3. Add service limitations.
4. Add frontend detail section.
5. Add tests for populated, empty, and low-confidence states.
```

UI sections:

```text
Sponsorship background
Free/no-fee services after sponsorship
RCPA movement after sponsorship
Data caveats
```

Do not create a separate Sponsorship page before this extension unless leadership explicitly wants a separate workflow first. Doctor detail is the lowest-risk visible integration because it reuses the existing Doctor ROI page.

Exit criteria:

```text
doctor drawer shows sponsorship evidence when available
no-sponsorship and missing-link states are clear
existing Doctor ROI page remains stable
```

### Phase 8: Sponsorship Intelligence Page

**Trigger**: Doctor detail extension is stable and portfolio-level KPIs are validated.

**Goal**: Add a leadership sponsorship workflow.

Recommended route:

```text
frontend/src/pages/SponsorshipIntelligence.tsx
```

Recommended backend:

```text
backend/app/schemas/sponsorship.py
backend/app/repositories/sponsorship_repository.py
backend/app/services/sponsorship_service.py
backend/app/routers/sponsorship.py
```

Dashboard sections:

```text
summary cards
sponsored doctor table
sponsorship event table
outcome matrix
data-quality warnings
doctor drilldown link
```

Exit criteria:

```text
leadership can answer who was sponsored, what evidence exists, what happened after, and where data is weak
```

### Phase 9: Territory Intelligence Slice

**Trigger**: MSL/doctor master or territory mapping data arrives.

**Goal**: Build territory analytics only after territory hierarchy is real.

Do not infer territory semantics from a loose `patch_name` string if the business expects region/cluster decisions.

Steps:

```text
1. Profile MSL/doctor master or territory mapping.
2. Confirm fields: territory, patch, region, cluster, task force, rep.
3. Confirm whether assignments change over time.
4. Create territory assignment model only after effective-date behavior is known.
5. Build compact territory opportunity view.
6. Add API and frontend surface.
```

Potential view:

```text
mv_territory_opportunity
```

Metrics:

```text
doctor count
active doctor count
Cipla Rx quantity
competitor Rx quantity
Cipla share
engagement count
spend
Rx per engagement
Rx per spend
high-value unengaged doctors
self-serving candidates
underserved candidates
data coverage
```

Territory classification must be deterministic and configurable. Do not hard-code business thresholds until data distribution is reviewed.

Exit criteria:

```text
territory labels are explainable
territory coverage is visible
resource-deployment questions are answerable without AI guessing
```

### Phase 10: AI Extension

**Trigger**: Sponsorship and/or territory services are deterministic and tested.

**Goal**: Let AI explain sponsorship and territory outputs using compact backend context.

Modify:

```text
backend/app/services/ai/query_planner.py
backend/app/services/ai/context_builder.py
backend/app/services/ai/answer_policy.py
backend/app/services/ai/response_contract.py
backend/app/services/ai/redaction.py
frontend/src/components/ai/AiAssistantPanel.tsx
frontend/src/api/ai.ts
```

Supported topic additions:

```text
sponsorship
conference
no-fee/free service
accommodation only if data exists
territory
underserved
self-serving
field resource deployment
```

Context rules:

```text
send summary rows only
send top-N doctors/territories only
send limitations
never send raw workbook rows
never send unbounded doctor lists
redact P-codes, doctor names, money, and contract IDs if enabled
```

Exit criteria:

```text
AI can answer sponsorship/territory questions with evidence refs
unsupported questions are refused or qualified
provider failure falls back deterministically
```

## Data Model Decisions

### Decisions Already Safe

These are stable because existing repo/data already support them:

```text
country + pcode_normalized is the safe doctor identity boundary
request_uid is safer than assuming req_id is globally unique
raw files stay local
RCPA detail stays local/processed, compact summaries go online
dashboard APIs read typed backend services
AI summarizes backend service context only
```

### Decisions Deferred Until Data Arrives

These must not be finalized yet:

```text
whether sponsorship_events needs a separate table or can be derived from execution_requests initially
whether doctor contract report is a new source type
whether contract_id is available in recurring extracts
whether accommodation is a separate entity
whether territory is patch only or a hierarchy
whether legacy code should be first-class in joins
exact no-fee agreement labels
exact national/international/ERS labels
pre/post RCPA comparison window
retention policy for older RCPA summaries
```

### Likely Future Entities

These are likely but still data-gated:

```text
sponsorship_events
sponsorship_doctors
doctor_contract_observations
doctor_identity_observations
doctor_territory_assignments
accommodation_records
```

Do not create them until the source samples prove the fields.

## API Contract Strategy

Do not expose final sponsorship APIs before the backing views exist.

Draft route families:

```text
GET /api/sponsorship/summary
GET /api/sponsorship/events
GET /api/sponsorship/doctors
GET /api/sponsorship/doctors/{countryCode}/{pcode}
GET /api/territories/opportunities
```

Implementation order:

```text
doctor detail sponsorship extension first
sponsorship summary/events next
territory route later
AI context last
```

Rationale:

The existing Doctor ROI page already has the user workflow where sponsorship background is needed. A separate page before the data is stable adds product surface area and test cost too early.

## Frontend Strategy

Frontend should not contain placeholder pages with fake copy.

Allowed before data:

```text
document navigation placement
document component contracts
prepare feature-flag approach if needed
```

Blocked before data:

```text
SponsorshipIntelligence page
TerritoryIntelligence page
fake cards
fake charts
empty routes visible in nav
AI prompts for unavailable data
```

First real frontend change after backend support:

```text
extend Doctor ROI detail drawer with sponsorship background
```

Then:

```text
Sponsorship Intelligence page
Territory Intelligence page
AI suggested prompts
```

## Testing Strategy

Every implementation slice follows this order:

```text
profile real file
write synthetic fixture
write failing test
implement normalizer/loader/repository/view/API/UI
run focused tests
run affected integration tests
record data-quality behavior
```

### Required Test Families

Ingestion:

```text
schema drift report tests
raw-vs-cleaned comparison tests
sponsorship label classification tests
doctor contract report loader tests
RCPA monthly refresh idempotency tests
territory mapping loader tests
accommodation loader tests only if data exists
```

Database:

```text
sponsorship events persistence
sponsorship doctor bridge uniqueness
free-service-after-sponsorship window
pre/post RCPA movement
missing P-code quality flags
contract ID coverage
territory opportunity classification
storage impact smoke checks
```

API:

```text
sponsorship summary
sponsorship doctor rows
sponsorship event rows
doctor detail sponsorship timeline
territory opportunities
invalid filters
pagination and sorting
limitations and data-quality flags
```

Frontend:

```text
doctor detail sponsorship section
sponsorship page loading/error/empty/partial states
territory page loading/error/empty/partial states
quality warnings
AI sponsorship prompt behavior
```

AI:

```text
query planner routes sponsorship questions
context builder caps sponsorship context
answer policy refuses unsupported causal claims
response contract validates sponsorship evidence refs
redaction masks contract IDs if required
```

## Storage And Free-Tier Control Plan

### Current Constraint

```text
Database: 321 MB
Free limit: 500 MB
Headroom: ~179 MB
```

### Storage Rules

Hard rules:

```text
raw files do not enter Supabase
large detailed RCPA does not enter Supabase
RCPA SKU detail stays local under data/processed
only compact sponsorship/territory facts go online
avoid duplicating full RCPA summaries in new materialized views
prune AI query logs if needed
measure table sizes after each large load
```

Preferred env/runtime controls:

```text
INGESTION_STORAGE_MODE=compact
RCPA_ONLINE_MONTHS=24
STORE_RCPA_DETAIL_ONLINE=false
STORE_SOURCE_ROW_JSON=false
AI_LOG_RETENTION_DAYS=30
```

Do not implement these env vars until they are needed, but design new code so this policy is easy to add.

## Risk Register

### Risk: Raw reports differ from cleaned reports

Mitigation:

```text
profile raw files first
compare raw vs cleaned
make loader accept raw shape, not presentation shape
```

### Risk: Contract ID is not in the main consolidation report

Mitigation:

```text
do not require contract_id for first sponsorship fact table
use request_uid as operational spine
add doctor contract report slice when file arrives
show missing contract ID as data quality flag
```

### Risk: Sponsorship labels are inconsistent

Mitigation:

```text
do not hard-code final labels until observed
store classification reason
store confidence
keep unclassified candidate rows visible
```

### Risk: Manual P-code backfill introduces false precision

Mitigation:

```text
track mapping provenance if source provides it
flag unknown/manual mappings
avoid name-only confident joins
show identity limitations
```

### Risk: RCPA backfill exceeds storage

Mitigation:

```text
pre-load size estimate
compact summary only
local detailed extracts
storage report before and after ingestion
avoid redundant materialized views
```

### Risk: Territory hierarchy is unclear

Mitigation:

```text
do not infer hierarchy from patch string alone
ask for official MSL/territory mapping
store source/effective date if available
keep territory page blocked until hierarchy is known
```

### Risk: AI overclaims causality

Mitigation:

```text
answer policy uses association language
system prompt forbids causal claims
evidence refs required
unsupported causality questions are qualified/refused
```

## Implementation Backlog With Gates

### Ready Now

These can be turned into tasks before new data arrives:

```text
R0. Create source intake contract template.
R1. Document raw-vs-cleaned comparison workflow.
R2. Add or document database storage budget report.
R3. Document next-phase feature flag policy.
R4. Add sponsorship/territory implementation notes to data dictionary as "planned, data-gated" definitions.
R5. Prepare email/data request checklist for Abhijeet/Anil/Varad.
```

### Ready After Raw Consolidation Samples

```text
C1. Profile raw extracts.
C2. Compare raw vs cleaned extracts.
C3. Update CONSOLIDATION_SCHEMA aliases if real columns differ.
C4. Add observed sponsorship/no-fee classification tests.
C5. Add sponsorship normalizer from confirmed labels.
C6. Decide whether sponsorship facts need new table immediately.
```

### Ready After Doctor Contract Report

```text
D1. Profile doctor contract report.
D2. Define join key strategy.
D3. Add loader if report is recurring source.
D4. Add unmatched contract quality output.
D5. Enrich sponsorship doctor links with contract evidence.
```

### Ready After Historical RCPA Files

```text
H1. Profile historical RCPA files.
H2. Confirm manual P-code provenance fields.
H3. Estimate storage impact.
H4. Load compact summaries only.
H5. Extend coverage metrics.
H6. Recompute doctor ROI baseline.
```

### Ready After Monthly RCPA Samples

```text
M1. Profile monthly refresh shape.
M2. Confirm replacement grain.
M3. Add monthly refresh idempotency tests.
M4. Add latest RCPA month freshness output.
```

### Ready After Territory/Doctor Master Data

```text
T1. Profile MSL/territory mapping.
T2. Decide patch vs territory vs region/cluster model.
T3. Add territory assignment persistence.
T4. Build territory opportunity view.
T5. Add territory API/UI.
T6. Add AI territory context.
```

### Ready After Sponsorship Outcomes Are Stable

```text
S1. Extend doctor detail endpoint.
S2. Extend Doctor ROI drawer.
S3. Add sponsorship summary API.
S4. Add Sponsorship Intelligence page.
S5. Add AI sponsorship context.
```

## Success Criteria

### Before Data Arrives

Success means:

```text
no speculative migrations
no fake pages
no dead placeholder code
clear data request exists
source intake gates are documented
storage constraint is known
implementation slices are sequenced
```

### After First Raw Consolidation Data

Success means:

```text
raw recurring extract can be profiled
raw-vs-cleaned drift is understood
current loader either supports it or has exact changes needed
sponsorship labels are observed or explicitly absent
```

### After Sponsorship Slice

Success means:

```text
sponsorship facts are deterministic
doctor linkage is P-code-based and auditable
missing P-code/contract evidence is visible
doctor detail can show sponsorship background
```

### After RCPA Backfill

Success means:

```text
doctor ROI baseline improves without breaching storage budget
historical coverage window is visible
manual P-code limitations are visible
monthly refresh remains idempotent
```

### After Territory Slice

Success means:

```text
territory analytics use official or confirmed mapping
self-serving and underserved labels are deterministic
AI can summarize territory outputs without inventing facts
```

## Final Recommendation

The cleanest path is:

```text
Do readiness work now.
Do not build speculative feature surfaces.
When data arrives, implement one source at a time as a vertical slice.
Start with raw consolidation because it unlocks sponsorship classification.
Next do doctor contract linkage if the file exists.
Then harden historical/monthly RCPA.
Then add sponsorship outcomes.
Then add doctor-detail UI.
Then add standalone sponsorship page.
Then add territory intelligence.
Then extend AI.
```

This keeps the product serious:

```text
trusted data first
explicit reconciliation
deterministic calculations
compact Supabase storage
typed APIs
polished frontend
grounded AI only after stable services exist
```

It also protects development time and credits:

```text
no guessing
no fake placeholders
no rework-heavy migrations
no UI before data
no AI context before deterministic service output
```

## Optional Spec Kit Hook

The project has an optional `after_plan` hook:

```text
extension: agent-context
command: /speckit-agent-context-update
description: Refresh agent context after planning
```

This supplemental plan intentionally does not replace `specs/002-execution-intelligence-platform/plan.md`, so the main `AGENTS.md` Spec Kit pointer should remain unchanged unless this plan becomes the primary active feature plan.

