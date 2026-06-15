<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Principle 1 placeholder -> I. Trusted Data Before Dashboards
- Principle 2 placeholder -> II. Explicit Reconciliation, Not Hidden Guesswork
- Principle 3 placeholder -> III. Deterministic Business Logic and Grounded AI
- Principle 4 placeholder -> IV. Testable Ingestion, APIs, and User Journeys
- Principle 5 placeholder -> V. Deployable, Secure, and Product-Grade UX
Added sections:
- Architecture and Data Constraints
- Delivery Workflow and Quality Gates
Removed sections:
- Placeholder template guidance
Templates requiring updates:
- updated: .specify/templates/plan-template.md
- updated: .specify/templates/spec-template.md
- updated: .specify/templates/tasks-template.md
Follow-up TODOs: none
-->

# Cipla EMEU Execution Intelligence Platform Constitution

## Core Principles

### I. Trusted Data Before Dashboards

Every feature MUST preserve trust in the data path from source workbook to dashboard.
Ingestion MUST profile source files, record ingestion runs, validate rows, normalize
months/Pcodes/currencies, and report skipped or malformed data. The system MUST
surface data quality limitations instead of hiding them behind polished charts.

Rationale: this project is valuable only if stakeholders can trust the numbers.
A visually attractive dashboard with silent join failures, damaged Pcodes, or mixed
currencies is worse than a spreadsheet because it creates false confidence.

### II. Explicit Reconciliation, Not Hidden Guesswork

The system MUST reconcile yearly planner events, monthly execution snapshots,
consolidation requests, and RCPA prescription records through explicit, queryable
records. Event matching MUST store match method, confidence, status, and source
references. Weak or missing matches MUST be visible in data-quality views and UI.

Rationale: the core engineering problem is not rendering charts; it is connecting
messy enterprise records whose event names, dates, and doctor identifiers do not
line up cleanly. Hidden string matching is not acceptable for a stakeholder demo.

### III. Deterministic Business Logic and Grounded AI

KPIs, ROI segmentation, budget utilization, filtering, matching rules, and data
quality metrics MUST be computed through deterministic code or SQL. AI MUST only
summarize structured query results produced by backend services. AI MUST include
limitations when data is missing, weakly matched, stale, or below coverage thresholds.

Rationale: calculations and joins are business rules, not language-model tasks.
The AI assistant is a reporting layer, not an autonomous analyst or source of truth.

### IV. Testable Ingestion, APIs, and User Journeys

Changes that affect ingestion, canonical schemas, reconciliation, materialized views,
API contracts, or dashboard behavior MUST include targeted tests. Tests MUST cover
known workbook quirks: XLSB RCPA column aliases, month formats, text Pcodes, April
execution status values, missing Sri Lanka May execution tab, multi-doctor Pcode
fields, and currency handling.

Rationale: this app depends on messy real files. The likely failures are silent data
corruption and misleading metrics, so tests must focus on file-specific edge cases
and cross-layer contracts rather than only happy-path UI rendering.

### V. Deployable, Secure, and Product-Grade UX

The product MUST remain deployable as a real application: React frontend, FastAPI
backend, Supabase PostgreSQL, local ingestion CLI for MVP, and environment-based
secret handling. The frontend MUST include loading, empty, error, stale-data, weak
match, missing FX, and no-RCPA states. Secrets and real source workbooks MUST never
be committed.

Rationale: the goal is a serious internship/portfolio-grade product, not a local
prototype. The app must be demoable, secure, understandable, and resilient when the
data is imperfect.

## Architecture and Data Constraints

- Source workbooks are local input artifacts and MUST remain out of git.
- RCPA rows MUST be aggregated before database write for MVP; raw row JSON storage
  is allowed for smaller planner, execution, and consolidation files only if useful.
- Pcodes MUST be stored and joined as normalized text, with raw values preserved.
- Months MUST resolve to canonical calendar month records with fiscal-year metadata.
- Currency values MUST preserve local amount and currency code; cross-country money
  comparisons require USD normalization or an explicit UI warning.
- Dashboard endpoints SHOULD read from materialized KPI/data-quality views where
  practical to keep API services thin and consistent.
- Browser-triggered ingestion, manual match editing UI, full RBAC, scheduled
  ingestion, and Power BI embedding are non-goals for MVP unless a later amendment
  changes scope.

## Delivery Workflow and Quality Gates

- Specs MUST define user-visible value, source data used, data-quality expectations,
  and measurable success criteria.
- Plans MUST include a Constitution Check covering data provenance, reconciliation,
  deterministic logic, testing, security, deployment, and UX states.
- Tasks MUST be grouped so the product remains demoable at each milestone:
  profiling, schema, ingestion, reconciliation/views, API, frontend, AI, deployment.
- No dashboard milestone is complete unless it handles loading, error, empty, stale,
  and low-confidence data states.
- No AI milestone is complete unless answers cite supporting metrics or clearly say
  the available data cannot answer the question.

## Governance

This constitution supersedes conflicting project guidance. `finalplan.md` is the
current product and architecture agenda, but implementation decisions must satisfy
this constitution when future specs or tasks are generated.

Amendments require:

- a written reason for the change,
- an explicit semantic version bump,
- review of affected Spec Kit templates,
- migration or rollout notes when data contracts change.

Versioning policy:

- MAJOR: principles removed, redefined incompatibly, or MVP architecture replaced.
- MINOR: new principle, section, or mandatory quality gate added.
- PATCH: wording clarifications that do not change obligations.

Compliance review is required during planning and before implementation completion.
Any violation must be documented with the reason, risk, and rejected simpler option.

**Version**: 1.0.0 | **Ratified**: 2026-06-14 | **Last Amended**: 2026-06-14
