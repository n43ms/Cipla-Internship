# Sponsorship Readiness MVP Plan

**Feature Context**: Minimal pre-data extension for `002-execution-intelligence-platform`

**Created**: 2026-07-04

**Rewritten**: 2026-07-07

**Primary Inputs**:

- `specs/002-execution-intelligence-platform/tasks.md`
- `ingestion_sponsorship.md`
- current ingestion/backend/frontend architecture
- current Supabase storage footprint
- realistic assumption that the requested sponsorship/territory data may arrive late, incomplete, or not at all

## Executive Decision

Build a **pre-data readiness MVP**, not the full sponsorship/territory product.

The immediate objective is to make the repository capable of accepting whatever business sends, inspecting it safely, and producing an implementation decision without guessing schemas, labels, joins, or storage needs.

The MVP must work under the worst-case assumption:

```text
no raw consolidation extract arrives
no cleaned comparison file arrives
no doctor contract report arrives
no territory master arrives
no monthly RCPA sample arrives
no confirmed sponsorship/no-fee labels arrive
```

Under that assumption, the system can still deliver durable value:

```text
data request package
source intake contract
generic workbook profiler improvements
raw-vs-cleaned workbook comparison tool
storage budget report
feature gate policy
source onboarding playbook
synthetic fixtures for tool behavior only
```

The MVP must not create fake sponsorship, accommodation, territory, contract, frontend, or AI features.

## Product Boundary

This plan is not trying to ship a Sponsorship Intelligence dashboard yet.

It is trying to make the next real implementation step safe.

The product workflow for the MVP is:

```text
business sends any file, even incomplete
  -> engineer records it in source intake contract
  -> ingestion profiler inspects file shape
  -> optional raw-vs-cleaned comparison runs if two variants exist
  -> report identifies mapped, missing, unknown, empty, and risky fields
  -> storage budget is checked before any large load
  -> engineer decides which source-specific slice is now unblocked
```

The MVP succeeds if it prevents the two worst outcomes:

```text
building against a manually cleaned file that is not the recurring source
creating tables, loaders, dashboards, or AI context from assumptions
```

## Existing Architecture To Reuse

The current system already has the correct major boundaries:

```text
local source files
  -> ingestion CLI
  -> profiler / loaders / normalizers / validators
  -> canonical Supabase Postgres tables
  -> materialized views
  -> FastAPI repositories / services / routers
  -> React dashboard
  -> backend-grounded AI assistant
```

The MVP only extends the first part of that chain:

```text
local source files
  -> ingestion CLI
  -> workbook profiling
  -> workbook comparison
  -> markdown/json decision reports
```

It deliberately does not extend these layers yet:

```text
database sponsorship schema
database territory schema
backend sponsorship routers
frontend sponsorship pages
AI sponsorship context
```

Those layers require real source evidence.

## MVP Architecture

### 1. Source Intake Contract

Location:

```text
specs/002-execution-intelligence-platform/contracts/source-intake-contract.md
```

Purpose:

```text
record what was requested
record what actually arrived
record source owner and cadence
record whether file is raw recurring source or cleaned presentation copy
record sheet names, expected fields, identity fields, money fields, date fields, doctor fields, and label fields
record open questions and implementation gate status
```

This is a contract and audit artifact, not code. It protects the team from acting on vague meeting memory.

### 2. Business Data Request Package

Location:

```text
docs/sponsorship-data-request.md
```

The request must be written in two levels.

Minimum viable ask:

```text
1 raw recurring consolidation/smart-contract extract
1 cleaned/presentable version if available
1 small RCPA sample with P-codes if available
1 doctor/MSL/territory mapping sample if available
3-5 known business examples for sponsorship/no-fee/conference/messy doctor cases
```

Full desired ask:

```text
raw consolidation extracts
cleaned consolidation file
doctor-level contract report
historical RCPA
monthly RCPA samples
MSL doctor master
territory mapping
accommodation/travel data if separate
confirmed sponsorship/no-fee labels
validation examples
```

The request must make clear that a small imperfect sample is still useful. Waiting for a perfect package is not required.

### 3. Profiler Schema-Drift Upgrade

Existing files to extend:

```text
ingestion/models.py
ingestion/profiler.py
ingestion/report.py
ingestion/main.py
```

The profiler should produce source-neutral metadata:

```text
detected sheet names
detected header row
row count
column count
raw columns
mapped canonical fields
unknown columns
required fields present
required fields missing
empty columns
bounded sample values
source type guess
file hash if already supported or practical
profile timestamp
```

Important boundary:

```text
Do not add sponsorship-specific required fields before real data confirms them.
```

This keeps the profiler generic and reusable for every future source.

### 4. Raw-Vs-Cleaned Workbook Comparison

New file:

```text
ingestion/workbook_compare.py
```

Input:

```text
profile output for raw workbook
profile output for cleaned workbook
```

Output:

```text
shared columns
raw-only columns
cleaned-only columns
normalized-header matches
rename candidates
columns mapped to existing canonical fields
columns requiring business decision
markdown report
json report
```

This tool exists because the meetings imply the business may have cleaned files manually. The ingestion pipeline must target the recurring raw shape, not the presentable copy.

### 5. Storage Budget Guard

Files:

```text
scripts/db_size_report.ps1
docs/storage-budget.md
```

The database is already storage-sensitive. Before large RCPA or future sponsorship loads, the team needs a repeatable report:

```text
database size
largest tables
largest materialized views
RCPA summary sizes
AI log size
estimated headroom
compact-mode rules
```

Rules:

```text
raw files stay out of Supabase
large raw RCPA detail stays out of Supabase
source workbooks stay out of git
Supabase remains the compact serving database
```

### 6. Feature Gate Policy

File:

```text
docs/feature-gate-policy.md
```

This policy should make blocked work explicit:

```text
no sponsorship tables before source profile
no sponsorship loader before confirmed labels and joins
no territory table before official mapping shape
no accommodation model unless a separate source proves it
no frontend pages before backend deterministic service exists
no AI prompts/context before deterministic backend context exists
```

This is not bureaucracy. It prevents expensive rework.

### 7. Source Onboarding Playbook

File:

```text
docs/source-onboarding-playbook.md
```

The playbook defines the procedure when even one file arrives:

```text
1. Do not edit loaders first.
2. Put the real file outside git.
3. Run profile.
4. If raw and cleaned variants exist, run compare.
5. Read report and identify actual schema gaps.
6. Create a tiny synthetic fixture matching observed shape.
7. Write failing tests.
8. Update schema maps/loaders only for proven fields.
9. Estimate storage before persistence changes.
10. Only then consider database/backend/frontend/AI work.
```

## Data Scenarios And What They Unlock

### If No Data Arrives

Allowed:

```text
complete docs
complete generic profiler improvements
complete workbook comparison tool using synthetic fixtures
complete storage budget script/runbook
complete feature gate policy
complete onboarding playbook
```

Blocked:

```text
all source-specific sponsorship, territory, accommodation, contract, frontend, and AI work
```

### If Only One Raw Consolidation File Arrives

Allowed:

```text
profile file shape
check current consolidation schema-map coverage
identify possible sponsorship/no-fee/conference label columns
create synthetic fixture from observed structure
write loader/schema-map change tasks if needed
```

Still blocked:

```text
final classifier rules
sponsorship tables
sponsorship dashboard
AI sponsorship answers
```

### If Only A Cleaned File Arrives

Allowed:

```text
profile it as a presentation source
document business meaning
ask for raw recurring extract
avoid implementing ingestion against it unless business confirms it is the actual recurring source
```

Still blocked:

```text
recurring ingestion assumptions
database migrations based on cleaned-only columns
```

### If Only RCPA Arrives

Allowed:

```text
profile RCPA shape
check P-code/month/brand coverage
estimate storage impact
confirm whether existing RCPA loader supports it
```

Still blocked:

```text
sponsorship outcome views unless sponsorship facts also exist
```

### If Only Doctor/Territory Mapping Arrives

Allowed:

```text
profile identity and hierarchy fields
assess whether patch/territory/region/cluster are explicit
document join keys and missing identifiers
```

Still blocked:

```text
territory opportunity view
territory dashboard
AI territory context
```

## Strict Non-Goals For This MVP

Do not build:

```text
sponsorship_events migration
sponsorship_doctors migration
doctor_contract loader
territory assignment migration
accommodation model
sponsorship materialized views
territory materialized views
sponsorship backend router
territory backend router
SponsorshipIntelligence page
TerritoryIntelligence page
AI sponsorship context
AI territory prompts
hardcoded National/International/ERS/no-fee classifiers
```

These are future post-data implementation slices.

## Minimal Post-Data Implementation Rule

When data arrives, implementation must follow this order:

```text
profile real file
compare raw vs cleaned if both exist
update source contract
create synthetic fixture
write failing test
update schema map or loader
run ingestion locally
check storage impact
only then consider database schema or API work
```

Database, backend, frontend, and AI are downstream layers. They should not lead the design.

## Testing Strategy

MVP tests should cover the readiness machinery, not business assumptions.

Required test families:

```text
profiler schema-drift tests
workbook comparison tests
CLI report generation tests
storage report parsing tests if practical
documentation checklist review for data request and gate policy
```

Do not add tests asserting specific sponsorship labels until those labels are observed in real source files.

## Success Criteria

The MVP is complete when:

```text
business has a short minimum viable data request and a full desired data request
incoming files can be profiled before code changes
raw and cleaned files can be compared generically
reports clearly show mapped, missing, unknown, empty, and risky columns
storage impact can be measured before large loads
future sponsorship/territory work is explicitly gated
no speculative migrations, routers, pages, or AI contexts exist
```

## Engineering Position

This is the sustainable architecture:

```text
prepare the intake and inspection layer now
let real files decide source-specific implementation
keep Supabase compact
keep backend and frontend clean until deterministic data exists
extend AI last, only from tested backend context
```

That is the path that burns the least time, avoids fake product surface area, and keeps the system credible.
