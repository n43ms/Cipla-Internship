# Feature Specification: Cipla EMEU Execution Intelligence Platform

**Feature Branch**: `002-execution-intelligence-platform`

**Created**: 2026-06-14

**Status**: Draft

**Input**: User description: "Use constitution.md and finalplan.md to fully plan the architecture of the project flawlessly. Do not miss a single component of finalplan.md and explicitly mention any errors found in the planned architecture."

## Clarifications

### Session 2026-06-14

- Q: Who can access the deployed dashboard during MVP? -> A: Protected deployed demo.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trust the Ingested Data (Priority: P1)

As the project owner and dashboard builder, I need every supplied workbook to be profiled, validated, normalized, and tracked by ingestion run so that dashboard metrics are traceable back to source files and data quality issues are visible.

**Why this priority**: No dashboard or AI feature is credible until the source files are loaded reproducibly and data defects are reported rather than hidden.

**Independent Test**: Run a full profiling and ingestion validation over the supplied planner, consolidation, execution, and RCPA files; verify that the system reports file identities, sheet usage, row counts, skipped rows, validation errors, normalized months, normalized Pcodes, and currency labels.

**Acceptance Scenarios**:

1. **Given** all supplied source files are available, **When** a profiling run is executed, **Then** each file is classified by source type, canonical sheet choices are identified, row counts are reported, and source-specific column differences are detected.
2. **Given** malformed rows or missing fields exist in a workbook, **When** ingestion validates the file, **Then** the affected rows are reported with field-level errors and valid rows continue through the pipeline where safe.
3. **Given** RCPA files contain over one million prescription-level rows, **When** ingestion processes them, **Then** the system aggregates prescription facts before persistence and still reports row counts and validation summaries.

---

### User Story 2 - Compare Planned vs Actual Execution (Priority: P2)

As a Cipla EMEU/PBP manager, I need to compare yearly planned activities with monthly execution snapshots and smart-contract requests so that I can see which events were executed, delayed, unmatched, or missed.

**Why this priority**: This is the central business problem: planned marketing activities, request approvals, and actual execution currently live in disconnected files.

**Independent Test**: Load planner, monthly execution, and consolidation data for Nepal, Sri Lanka, and Myanmar where available; verify that event-level execution status, match status, match confidence, planned HCPs, engaged HCPs, and unmatched records are visible.

**Acceptance Scenarios**:

1. **Given** a planned event appears with a month suffix in an execution file, **When** event reconciliation runs, **Then** the system links the records using explicit match metadata rather than silently mutating the names.
2. **Given** a planned event has no confident execution or consolidation match, **When** the execution dashboard is viewed, **Then** the event appears as unmatched or action due with a data quality explanation.
3. **Given** Sri Lanka has no May country tab in the monthly execution planner, **When** Sri Lanka May execution is analyzed, **Then** the system derives execution evidence from consolidation requests and exposes any limitation.

---

### User Story 3 - Understand Budget Utilization (Priority: P3)

As a business stakeholder, I need to see planned budget, confirmed budget, actual spend, unused budget, and overruns so that I can identify where sanctioned spend is underused or inefficiently deployed.

**Why this priority**: Budget underuse is a governance risk and one of the strongest executive use cases for the dashboard.

**Independent Test**: For a selected country and month, compare planner costs with consolidation confirmed and actual spend; verify event-level budget gaps and unmatched spend records are shown with currency labels.

**Acceptance Scenarios**:

1. **Given** planned cost exists for an event but no matching actual spend exists, **When** budget utilization is viewed, **Then** the unspent gap is visible and tied to the unmatched/missed event.
2. **Given** actual spend exists without a confident planner match, **When** budget utilization is viewed, **Then** the spend is shown as unmatched actual activity rather than being forced into an unrelated plan event.
3. **Given** monetary values come from different countries, **When** they are displayed together, **Then** the system either uses normalized values or clearly warns that local-currency values are not directly comparable.

---

### User Story 4 - Evaluate Doctor ROI and Missed Opportunities (Priority: P4)

As a marketing manager, I need to connect doctor engagement and spend with RCPA prescription behavior so that I can identify high-value engaged doctors, high-prescribing unengaged doctors, and low-prescription high-spend doctors.

**Why this priority**: This turns the dashboard from execution tracking into business intelligence by linking marketing effort to prescription behavior.

**Independent Test**: Load consolidation doctor attendance and RCPA prescription facts; verify doctor-level segments, engagement counts, prescription quantities, own-vs-competitor split, and Pcode coverage flags.

**Acceptance Scenarios**:

1. **Given** an attended doctor has a valid Pcode and RCPA records, **When** Doctor ROI is viewed, **Then** the doctor appears with engagement history, prescription trend, brand mix, and segment.
2. **Given** a high-prescribing doctor has no engagement record, **When** missed opportunity analysis is viewed, **Then** the doctor appears as a high-value unengaged opportunity.
3. **Given** a request doctor field contains multiple names or Pcodes, **When** consolidation ingestion runs, **Then** each doctor participation record is split, validated, and traceable to its source position.

---

### User Story 5 - See Data Quality Before Acting (Priority: P5)

As any dashboard user, I need data freshness, match coverage, Pcode coverage, RCPA coverage, validation errors, and unmatched records to be visible so that I know when a metric is reliable enough to act on.

**Why this priority**: This prevents the dashboard from presenting uncertain data as fact and supports credible stakeholder reviews.

**Independent Test**: Load a dataset with unmatched events, missing Pcodes, stale ingestion, and incomplete RCPA coverage; verify that warnings and drilldowns appear before users rely on affected KPIs.

**Acceptance Scenarios**:

1. **Given** match coverage falls below an acceptable threshold, **When** a KPI depends on event matching, **Then** the UI displays a warning and links to unmatched records.
2. **Given** Pcode coverage is weak, **When** Doctor ROI is viewed, **Then** the UI distinguishes valid doctor ROI rows from insufficient-data rows.
3. **Given** ingestion has not completed or completed with warnings, **When** the dashboard loads, **Then** users see a data freshness and quality status before interpreting the results.

---

### User Story 6 - Ask Grounded Business Questions (Priority: P6)

As a manager or project owner, I need to ask concise natural-language questions about execution, budget, doctor ROI, and data quality so that I can quickly summarize trusted metrics for stakeholders.

**Why this priority**: AI creates demo value only after deterministic data services exist; it must not become a source of unverified metrics.

**Independent Test**: Ask questions about execution risk, budget gaps, top prescribers, and unsupported topics; verify answers cite supporting metrics or state that the available data cannot answer.

**Acceptance Scenarios**:

1. **Given** a user asks "What is at risk this month?", **When** the assistant answers, **Then** it summarizes deterministic execution and budget facts with limitations.
2. **Given** a user asks for a metric not available in the data, **When** the assistant answers, **Then** it refuses to invent the metric and explains what data is missing.
3. **Given** data quality is weak for a selected country/month, **When** the assistant summarizes the result, **Then** it includes the limitation in the answer.

### Edge Cases

- RCPA files use different column names for the same business field, including `O & C` vs `Own/Competitor`, `Active Status` vs `Status Doctor`, and `Month(formated)` availability.
- Month values appear as `Apr-24`, `25-Apr`, `Oct-25`, `Apr'26`, `May-26`, and Excel serial numbers such as `45772`; RCPA ingestion must treat serial dates as first-class month inputs, not malformed values.
- Pcodes appear numeric, decimal-like, blank, duplicated, missing, or embedded in multi-doctor fields.
- Nepal planner contains multiple plausible planning sheets; only the canonical version should drive plan events.
- Monthly execution files use incompatible status values across months: April uses `1` or blank; May uses `Executed` or `Action due`.
- Sri Lanka May execution lacks a dedicated country tab in the monthly execution planner.
- Event names differ across planner, monthly execution, and consolidation files by suffix, punctuation, casing, or labels such as `(New)`.
- Consolidation doctor fields may contain multiple expected or actual doctors in one row.
- Actual spend may exist without a matching plan event; plan events may exist without actual spend.
- Currency values are local by country and cannot be compared across countries unless normalized.
- RCPA coverage may be absent for a doctor, country, month, or brand.
- Ingestion may be stale, partially successful, or completed with warnings.
- AI questions may request unsupported facts, causal claims, or calculations not present in trusted data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST profile all supplied workbook types before ingestion and report workbook type, sheet names, used ranges, detected headers, required columns, row counts, and source-specific anomalies.
- **FR-002**: System MUST track ingestion attempts with status, source file count, row counts, skipped rows, warning count, error count, and a summary suitable for display.
- **FR-003**: System MUST track each source file by filename, file type, source type, country scope, period scope, and file identity.
- **FR-004**: System MUST validate source rows and record file-level or row-level validation issues without silently dropping business-relevant records.
- **FR-005**: System MUST ingest the three RCPA files using column aliases for observed schema differences and aggregate rows by doctor, month, brand, SKU, and own-vs-competitor before persistence.
- **FR-006**: System MUST ingest Nepal and Sri Lanka yearly planners while selecting the canonical planning sheet for each country and preserving country-specific planning fields.
- **FR-007**: System MUST ingest consolidation `Working` records as actual execution request facts including request ID, country, dates, venue, intervention details, budgets, spend, doctor counts, doctor fields, approval statuses, cancellation reason, location, and approval chain.
- **FR-008**: System MUST split semi-structured expected and actual doctor fields from consolidation into normalized doctor participation records with raw values, normalized Pcodes, parse status, and source position.
- **FR-009**: System MUST ingest April and May monthly execution planner files as execution snapshots, including summary rows, country-tab rows where present, `YP` totals, status source values, and normalized status.
- **FR-010**: System MUST normalize all observed month formats into canonical calendar-month records with fiscal-year context.
- **FR-010a**: System MUST support Excel serial-number dates in month normalization, including RCPA files where the month cell is numeric rather than a formatted string.
- **FR-011**: System MUST store Pcodes as raw and normalized text, never as business identifiers that depend on numeric precision.
- **FR-012**: System MUST preserve local currency values and currency codes, and MUST distinguish local-currency metrics from normalized monetary metrics.
- **FR-012a**: MVP exchange rates MUST be loaded from a documented static seed file with one representative rate per supported currency; live FX feeds are out of MVP scope.
- **FR-013**: System MUST reconcile plan events, execution snapshots, and consolidation requests using explicit match records that include match method, confidence, status, source references, and notes.
- **FR-014**: System MUST expose weak and unmatched event records as first-class data quality outputs rather than hiding them from dashboard metrics.
- **FR-015**: System MUST provide execution KPIs covering planned events, matched events, unmatched events, executed events, action-due events, planned HCPs, engaged HCPs, HCP execution rate, event execution rate, and match coverage.
- **FR-016**: System MUST provide budget KPIs covering planned budget, confirmed budget, actual spend, unspent gap, overrun amount, planned events without spend, and spend without plan match.
- **FR-017**: System MUST provide doctor ROI outputs covering engagement count, last engagement, associated spend, Cipla prescription quantity/value, competitor prescription quantity/value, Cipla share, spend per Cipla prescription, and ROI segment.
- **FR-018**: System MUST provide data quality outputs covering latest ingestion status, rows seen, rows skipped, validation errors, event match coverage, Pcode coverage, RCPA coverage, and unmatched records.
- **FR-019**: System MUST provide filters for country, month, therapy, event type, brand, speciality, doctor class, and ROI segment where relevant.
- **FR-020**: System MUST support drilldown from dashboard summaries into event, budget, doctor, and data-quality details.
- **FR-021**: System MUST expose read-only dashboard data to the frontend through typed backend contracts and MUST prevent frontend access to database secrets or AI provider secrets.
- **FR-022**: System MUST support an AI assistant that only summarizes deterministic query results and includes supporting metrics, limitations, and confidence.
- **FR-023**: System MUST reject or qualify AI answers when data is missing, stale, weakly matched, or outside available source coverage.
- **FR-023a**: System MUST redact AI query logs before persistence by masking Pcode-like identifiers, monetary amounts, and likely doctor-name spans; full raw questions may be processed in memory but must not be stored.
- **FR-024**: System MUST provide loading, empty, error, stale-ingestion, weak-match, missing-FX, and no-RCPA states for dashboard experiences.
- **FR-025**: System MUST keep source workbooks, secrets, generated data extracts, and real report artifacts out of version control.
- **FR-026**: System MUST support a local ingestion workflow for MVP and a deployed dashboard/backend that can be demonstrated without requiring browser-based file upload.
- **FR-027**: System MUST include targeted tests for ingestion quirks, database constraints, reconciliation, KPI outputs, API contracts, frontend states, and AI grounding.
- **FR-027a**: System MUST use synthetic fixtures under `ingestion/tests/fixtures/` with tiny workbook samples that cover the known source quirks without committing real Cipla files.
- **FR-028**: System MUST document a data dictionary, ingestion runbook, deployment guide, and demo validation flow.
- **FR-029**: MVP deployment MUST be protected from public access through a simple demo-appropriate access control such as deployment-provider protection, a shared password, or an allowlist; full user accounts and role-based access remain out of MVP.

### Architecture Corrections and Clarifications

- **AC-001**: `source_files.file_hash` alone is not sufficient to model repeated ingestion runs. The architecture must distinguish a reusable file identity from the fact that a file participated in a specific ingestion run, or otherwise allow the same file hash to be associated with later runs without losing run history.
- **AC-002**: `doctors.pcode_normalized` as a globally unique key may be unsafe if different countries can reuse the same Pcode. The architecture must validate global uniqueness in the supplied data and be prepared to use country plus normalized Pcode as the uniqueness boundary.
- **AC-003**: Planner files with multiple candidate plan sheets must not double-count events. Nepal must use `Yearly Planner FY27 v2` when present; older or alternate sheets may be profiled but must not contribute duplicate canonical plan events unless explicitly selected.
- **AC-004**: Smart-contract `REQ_ID` should be validated for global uniqueness before treating it as the only unique execution request key. If duplicates appear, the uniqueness boundary must include source system or country context.
- **AC-005**: Monetary comparisons across countries must not assume all RCPA values are USD. Local amounts must remain visible, and cross-country comparisons require normalized values or explicit warnings.
- **AC-006**: AI query logs must avoid storing secrets, raw oversized prompts, or unnecessary sensitive source data.
- **AC-007**: Manual event-match editing is intentionally out of MVP, so unmatched and weak matches must be visible enough for operational review without requiring a write-back UI.
- **AC-008**: Sri Lanka May execution evidence must be derived from consolidation requests by filtering Sri Lanka requests to May 2026, grouping by normalized intervention/event fields, and marking the resulting execution snapshot rows as `derived_from_consolidation` so they are never confused with monthly planner tab rows.
- **AC-009**: `rcpa_prescriptions` must have an explicit idempotency constraint at the aggregate grain: source file, country, month, normalized Pcode, brand group, SKU, own-vs-competitor, and currency. Re-ingesting the same file must update the existing aggregate row, not duplicate it.

### Key Entities *(include if feature involves data)*

- **Ingestion Run**: A single attempt to profile, validate, load, reconcile, and summarize source data.
- **Source File**: A supplied workbook with file identity, source type, period scope, country scope, and ingestion status.
- **Validation Error**: A file-level or row-level issue affecting trust, parsing, matching, coverage, or metric interpretation.
- **Country**: A market such as Nepal, Sri Lanka, Myanmar, Oman, UAE, or Malaysia, including default local currency.
- **Calendar Month**: Canonical month record with fiscal-year metadata used to normalize all source date labels.
- **Exchange Rate**: Currency conversion reference used only when normalized monetary comparison is required.
- **Plan Event**: A planned marketing activity from a yearly planner.
- **Execution Snapshot**: A monthly planner-derived view of planned vs raised/engaged/approved execution.
- **Execution Request**: A smart-contract request from the consolidation report with actual execution and spend details.
- **Request Doctor**: An expected or actual doctor participation record extracted from an execution request.
- **Doctor**: A doctor profile primarily seeded from RCPA and linked by normalized Pcode plus country validation.
- **RCPA Prescription**: Aggregated prescription behavior by doctor, month, brand, SKU, and own-vs-competitor.
- **Event Match**: Explicit reconciliation record linking planner, execution snapshot, and consolidation evidence.
- **KPI View**: Prepared execution, budget, doctor ROI, data quality, or unmatched-event output used by the dashboard.
- **AI Query Log**: Record of a user question, structured context summary, answer, model metadata, latency, and error state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All eight supplied source files are profiled and classified without manual workbook inspection.
- **SC-002**: At least 99% of structurally valid rows from planner, execution, and consolidation sources are loaded or reported with explicit validation reasons.
- **SC-003**: RCPA ingestion aggregates prescription records without storing every prescription-level row as raw database JSON.
- **SC-004**: Every dashboard KPI displays the latest ingestion status and indicates when match, Pcode, currency, or RCPA coverage limits interpretation.
- **SC-005**: Users can identify missed or action-due events for a selected country/month in under two minutes.
- **SC-006**: Users can identify planned budget, actual spend, unspent gap, and unmatched spend for a selected country/month in under two minutes.
- **SC-007**: Users can identify high-value engaged doctors, high-value unengaged doctors, and low-prescription high-spend doctors from a single Doctor ROI view.
- **SC-008**: No AI answer presents a metric unless that metric is present in structured system context or the answer states that the data is unavailable.
- **SC-009**: Known file quirks from finalplan.md are covered by automated tests before implementation is considered complete.
- **SC-010**: The deployed dashboard remains demoable even when ingestion completed with warnings, by showing data quality and limitation states instead of blank screens.

## Assumptions

- MVP users are project stakeholders and internal reviewers, not a broad authenticated enterprise user base.
- MVP access is a protected deployed demo, not a public app and not a full enterprise login system.
- Nepal and Sri Lanka are the primary business markets for the MVP; Myanmar remains in scope for data modeling and RCPA/execution coverage because source files include it.
- Core execution analysis starts from November 2025, while historical Nepal/Myanmar RCPA from April 2024 through March 2025 is retained for baseline comparison.
- Source workbooks are received manually and placed in a local raw-data folder for MVP ingestion.
- Browser-based ingestion, role-based permissions, scheduled ingestion, manual match editing, and Power BI embedding are intentionally deferred.
- The product must be deployable as a dashboard and backend service while ingestion remains a local controlled operation for MVP.
- Real Cipla source workbooks are confidential project inputs and must not be committed; test fixtures should be synthetic and small.
- The final technology choices and contracts will be detailed in the planning phase, but this specification defines the complete user value, data behavior, constraints, and quality obligations.
