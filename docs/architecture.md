# Architecture Notes

## Runtime Boundaries

The platform has three runtime boundaries:

- `ingestion`: local Python CLI that reads confidential workbooks and writes canonical data.
- `backend`: FastAPI service that reads dashboard data and mediates AI calls.
- `frontend`: React dashboard that calls only FastAPI.

Supabase PostgreSQL is the shared persistence layer. The frontend must not connect
directly to Supabase or any AI provider.

Supabase is the compact serving database, not the raw workbook archive. Large source rows remain
outside Supabase; PostgreSQL keeps canonical facts, KPI-ready summaries, materialized views, file
hashes, provenance, and caveats required by the dashboard.

## Data Ownership

- Raw workbook evidence belongs to local storage under `data/raw/`.
- Canonical business facts belong in PostgreSQL tables.
- KPI math belongs in SQL materialized views or typed backend services.
- AI may summarize backend service results but must not calculate source-of-truth metrics.

## Phase 2 Foundation

Phase 2 establishes:

- Alembic migration wiring,
- audit/source tables,
- reference tables,
- canonical table shells,
- reconciliation and AI log tables,
- uniqueness/index constraints,
- official company FX seeds for all six scoped markets dated 2026-07-10,
- shared constants and error schemas,
- test harnesses and fixture structure.

## Sponsorship ROI Batch Upload Phase

The sponsorship ROI phase now has a received source package and should be implemented as a manual-batch, evidence-gated extension of the existing Doctor ROI platform.

It extends the architecture through this path:

```text
already received files/ package
  -> engineering-controlled CLI/backend preload
  -> source manifest and fingerprinting
  -> workbook/HTML-XLS profiling
  -> deterministic loaders
  -> compact canonical facts written to Supabase
  -> materialized Doctor ROI, data-quality, sponsorship, and territory views refreshed

future business-user refresh
  -> business user uploads known workbook package through React "Upload new data/files"
  -> FastAPI stores accepted local batch under data/uploads/<batch-id>/
  -> source manifest and fingerprinting
  -> workbook/HTML-XLS profiling
  -> raw-vs-cleaned comparison
  -> synthetic fixtures
  -> deterministic loaders
  -> compact canonical facts written to Supabase
  -> materialized Doctor ROI, sponsorship, RCPA, data-quality, and territory views refreshed
  -> FastAPI read services
  -> React dashboard reflects refreshed Doctor ROI/detail/data-quality evidence
  -> ExecAI context only after deterministic services exist
```

The following require real Supabase preload or business spot checks before being marked fully accepted:

- current-package preload verification against Supabase,
- held-out dashboard upload verification against Supabase,
- selected doctor and territory business validation examples,
- before/after database storage-size measurement for the real historical RCPA load.

Manual dashboard upload is the target refresh mechanism for this project phase. SFTP, SharePoint polling, and CRM/data-lake auto-discovery are out of scope. Upload validation alone does not update live KPI data; the dashboard reflects new files only after accepted-batch ingestion writes Supabase facts and refreshes the materialized views.

Territory intelligence remains source-backed and caveated. It uses RCPA `Location`/`PATCHNAME`,
Smart Contract `FS HQ`/territory fields, and the ingested MSL doctor master. MSL is reference
enrichment only: it adds doctor-master coverage and territory metadata, and it fills missing
engagement P-codes only when country plus normalized doctor name maps to exactly one P-code.
Raw MSL mapping rows are temporary ingestion staging, not retained in Supabase after enrichment.

RCPA storage is compact by design. Doctor-month summaries remain online because they drive ROI
math, RCPA credit, territory opportunity, and caveats. Doctor-brand summaries are retained only as
a slim serving table for detail-drawer brand mix and brand filters.

ExecAI uses deterministic FastAPI service responses for Doctor ROI, sponsorship/engagement outcome evidence, RCPA trend, data-quality caveats, and territory rows. It must use association-only language for pre/post movement and must not claim causal uplift.

Source semantics:

- National Conference and International Conference are sponsorship.
- ERS is International evidence, not a separate sponsorship category.
- No-fee, speaker, consultancy, advisory, and honorarium are engagement evidence.
- FMV and contracted amount support economics/contracting efficiency.
- RCPA files are cumulative and must be loaded idempotently.
- FX uses only company-provided rates.

Primary references:

- `specs/002-execution-intelligence-platform/sponsorship-readiness-plan.md`
- `specs/002-execution-intelligence-platform/sponsorship-readiness-tasks.md`
- `ingestion_sponsorship.md`
- `docs/source-onboarding-playbook.md`
- `docs/feature-gate-policy.md`
