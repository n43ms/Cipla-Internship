# Research: Cipla EMEU Execution Intelligence Platform

## Decision: Python 3.11 for Backend and Ingestion

**Rationale**: Python 3.11 has strong compatibility with FastAPI, pandas, SQLAlchemy, openpyxl, python-calamine, pyxlsb, pytest, and deployment hosts. It is modern enough for performance and typing while avoiding occasional dependency friction on newer runtimes.

**Alternatives considered**: Python 3.12 is acceptable later, but Python 3.11 is the safer default for a data-heavy internship build. Node-only ingestion was rejected because XLSB parsing, dataframe transformations, and analytical testing are more mature in Python.

## Decision: SQLAlchemy 2.0 + Alembic Over Supabase Client as Data Layer

**Rationale**: Supabase is the hosted PostgreSQL platform, but SQLAlchemy and Alembic give explicit schema ownership, migrations, constraints, transactions, and typed repositories. This matters because ingestion has to be idempotent, auditable, and testable.

**Alternatives considered**: Supabase Python client is useful for narrow platform operations, but it is too weak as the primary data access layer for migrations, materialized views, joins, and transactional ingestion. Direct psycopg everywhere would be explicit but more repetitive.

## Decision: Local Ingestion CLI for MVP

**Rationale**: Source workbooks are confidential, large, and messy. Local ingestion avoids browser upload security issues, serverless timeouts, deployment storage complexity, and accidental exposure. The deployed app remains demoable because it reads from the database after ingestion.

**Alternatives considered**: Browser upload was rejected for MVP due to security and timeout risk. Scheduled ingestion is deferred because files are manually received and the first priority is correctness.

## Decision: python-calamine Primary XLSB Reader With Fallback

**Rationale**: RCPA files are XLSB and large. `python-calamine` is a pragmatic high-performance reader for Excel formats, while `pyxlsb` can be retained as a fallback if a workbook-specific issue appears. `openpyxl` remains the default for `.xlsx`.

**Alternatives considered**: openpyxl cannot read XLSB. Converting XLSB to XLSX manually was rejected because it breaks reproducibility and adds manual steps.

## Decision: Excel Serial Dates Are First-Class Month Inputs

**Rationale**: Current-year Nepal/Myanmar and Sri Lanka RCPA files can store month cells as Excel serial numbers such as `45772`. Treating these as malformed strings would silently drop or misclassify prescription rows. The month normalizer must detect numeric serials, convert them using Excel's date system, and map the result to `calendar_months`.

**Alternatives considered**: Pre-converting the workbook in Excel was rejected because it adds manual, non-reproducible cleanup. Rejecting numeric months was rejected because it would create false data-quality errors and data loss.

## Decision: Static Exchange-Rate Seeds for MVP

**Rationale**: Currency normalization is needed for cross-country comparison, but live FX integration is not necessary for the MVP. The July 10 company-provided official rates must be used for all six scoped markets: LKR 368.90, NPR 89, OMR 0.46, AED 1.00, MMK 4300, and MYR 4.39 per USD. Internet-rate fallback is not allowed.

**Alternatives considered**: Live FX API integration was rejected as a deployment and reliability distraction. Ignoring FX entirely was rejected because it would make cross-country money charts misleading.

## Decision: Official Company FX Rates

**Rationale**: The user has now provided the company-approved rates for every scoped market. Conversions must use the July 10 official values everywhere, stored with `source = company` and `rate_status = official`.

**Alternatives considered**: Keeping public/provisional rates was rejected because official company values are now available. Live internet rates remain rejected because they create moving business numbers.

## Decision: Confirmed + BTU/BTC Financial Mapping

**Rationale**: The consolidation workbook contains enough fields to support the transcript's financial ask. `APPROVE/CONFIRMED TOTAL INTERVENTION` is the confirmed/contracted amount. `ESTIMATED INTERVENTION` is retained as the estimated/FMV-like reference. `ACTUAL EXPENSE AGAINST BTU` represents direct HCP/BTU spend, `TOTAL ACTUAL BTC EXPENSE` represents overhead/BTC spend, and `TOTAL ACTUAL EXPENSES FOR INTERVENTION` represents total actual spend for ROI.

**Alternatives considered**: `Association Amount` was rejected as the default contracted amount because coverage is sparse and it appears to represent association/event rows. It remains preserved as a separate association amount. Waiting for further mapping was rejected because the user confirmed the confirmed + BTU/BTC mapping.

## Decision: Workflow Governance From Consolidation Lifecycle Columns

**Rationale**: The consolidation workbook directly contains request approval, request confirmation, report/post approval, report/post confirmation, submitted date, confirmed date, and Level 1-6 approver columns. These fields are sufficient to build the transcript-requested three-part execution governance view: current request location, request overview, and reporting/proof status.

**Alternatives considered**: Inferring lifecycle from execution status alone was rejected because it would hide the actual workflow bottleneck fields. Inspecting actual proof images/agendas is out of scope because those files are not in the supplied data.

## Decision: Dual-Tier Authentication & Strict Single-Node Replacement Policy

**Rationale**: To prevent any UI regression or layout disruption, the authentication feature strictly enforces a **Zero Frontend Layout Alteration Policy**. 

**Key Design & Security Rules**:
1. **Zero Menu / Header / UI Component Alterations**: The top navbar, `CiplaLogoPlaceholder`, `PRIMARY_PAGES` dropdowns, `OPERATIONS_PAGES` dropdowns, `UtilityMenu`, background visual effects, grid cards, and page layout components are 100% IMMUTABLE and PROHIBITED from modification.
2. **Single-Node Landing Screen Substitution**: ONLY replace the static "Click to continue" button node (lines 230-238 in `App.tsx`) with an inline glassmorphic Email + Passcode input form.
3. **Master Admin Immutability**: `adityaxnema@gmail.com` is hardcoded to `"Guddan@1205"`. Password change requests targeting this account are explicitly rejected by backend logic (`400 Bad Request` / `403 Forbidden`).
4. **Cipla Corporate Gate**: Only `@cipla.com` emails (and master admin `adityaxnema@gmail.com`) are allowed access. All other domains return `403 Forbidden`.
5. **Shared Corporate Passcode**: Default initial shared password for `@cipla.com` users is `"AdityaIntern@2026"`. Designated admins (`pralhad.gujar@cipla.com`, `abhijeet.mudila@cipla.com`, `aditya.emmanual@cipla.com`, `adityaxnema@gmail.com`) can update this passcode via backend API `POST /api/auth/change-password`.

**Alternatives considered**: AI-based quadrant classification was rejected because segmentation is business logic. Fixed global thresholds were rejected because market/currency/therapy differences would make them brittle before official thresholds are provided.

## Decision: Synthetic Fixture Structure Before Tests

**Rationale**: Tests need tiny reproducible workbooks, not the confidential real files. Fixtures live under `ingestion/tests/fixtures/` with `xlsx/`, `xlsb/`, and `expected/` subfolders. Each fixture should contain three to five rows and target one known edge case.

**Alternatives considered**: Testing against real Cipla files was rejected for confidentiality and repo hygiene. CSV-only fixtures were rejected because they do not exercise workbook/sheet/header/XLSB behavior.

## Decision: Deterministic Sri Lanka May Execution Derivation

**Rationale**: The May execution workbook has no Sri Lanka country tab. For Sri Lanka May, execution evidence must come from consolidation `Working` records filtered to Sri Lanka and May 2026, grouped by normalized intervention fields, and marked as `derived_from_consolidation`.

**Alternatives considered**: Leaving Sri Lanka May blank was rejected because consolidation contains usable actual execution evidence. Inventing monthly planner rows was rejected because it would blur source provenance.

## Decision: Explicit AI Log Redaction

**Rationale**: The `question_redacted` field must correspond to real behavior. AI logging will mask Pcode-like identifiers, monetary values, and likely doctor-name spans before persistence while using the raw question only in request memory.

**Alternatives considered**: Storing raw questions was rejected because users may include sensitive doctor or financial details. Dropping question logs entirely was rejected because sanitized logs are useful for debugging and demo analytics.

## Decision: Aggregate RCPA Before Persistence

**Rationale**: RCPA source rows can exceed one million rows. The dashboard needs doctor/month/brand/SKU/own-vs-competitor facts, not raw row-level storage. Aggregation keeps Supabase storage, query cost, and view refresh time under control while preserving row counts and validation summaries.

**Alternatives considered**: Raw RCPA JSON in PostgreSQL was rejected for MVP because it bloats storage and slows development without improving dashboard trust. A separate warehouse is overbuilt for this solo MVP.

## Decision: Explicit Reconciliation Table

**Rationale**: Planner, monthly execution, and consolidation data use inconsistent event names, statuses, dates, and source semantics. A first-class `event_matches` table makes matching auditable and allows weak/unmatched records to drive data-quality warnings.

**Alternatives considered**: Joining directly in views was rejected because it hides match assumptions. AI-based matching was rejected because matching is a deterministic business rule that needs tests and traceability.

## Decision: Materialized KPI Views

**Rationale**: Dashboard KPIs should be consistent across API endpoints, AI summaries, and UI drilldowns. Materialized views centralize calculations and keep the API thin and fast enough for demo usage.

**Alternatives considered**: Calculating KPIs in the frontend was rejected because it duplicates business logic and risks inconsistent metrics. Calculating everything in FastAPI services was possible but would make SQL lineage and performance less transparent.

## Decision: Provider-Neutral AI Adapter, Provider Chosen Later

**Rationale**: AI is the last layer and should not affect ingestion, database, KPI, or dashboard architecture. The backend will expose an `AIProvider` interface and a deterministic context builder. OpenAI or Anthropic can be selected later through `AI_PROVIDER` and `AI_API_KEY`.

**Alternatives considered**: Choosing a provider now adds no architectural value and risks distracting from the core data path. Frontend-direct AI calls are rejected because they would expose secrets and bypass grounded context.

## Decision: Protected Demo Access, Not Full RBAC

**Rationale**: The MVP needs to be demoable without being public. Deployment-provider protection, a shared demo password, or a simple allowlist satisfies the current requirement while avoiding role models, user lifecycle, and enterprise auth overhead.

**Alternatives considered**: Full enterprise RBAC is out of scope for MVP. A public dashboard was rejected because the data and project context are sensitive.
