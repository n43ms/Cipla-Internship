# Architecture Notes

## Runtime Boundaries

The platform has three runtime boundaries:

- `ingestion`: local Python CLI that reads confidential workbooks and writes canonical data.
- `backend`: FastAPI service that reads dashboard data and mediates AI calls.
- `frontend`: React dashboard that calls only FastAPI.

Supabase PostgreSQL is the shared persistence layer. The frontend must not connect
directly to Supabase or any AI provider.

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
- official LKR company FX seed at `1 USD = 310 LKR`,
- shared constants and error schemas,
- test harnesses and fixture structure.

## Sponsorship ROI Batch Upload Phase

The sponsorship ROI phase now has a received source package and should be implemented as a manual-batch, evidence-gated extension of the existing Doctor ROI platform.

It extends the architecture through this path:

```text
business user uploads known workbook package through React "Upload new data/files"
  -> FastAPI stores accepted local batch under data/uploads/<batch-id>/
  -> source manifest and fingerprinting
  -> workbook/HTML-XLS profiling
  -> raw-vs-cleaned comparison
  -> synthetic fixtures
  -> deterministic loaders
  -> compact canonical facts written to Supabase
  -> materialized Doctor ROI and sponsorship evidence views refreshed
  -> FastAPI read services
  -> React dashboard reflects refreshed Doctor ROI/detail/data-quality evidence
  -> ExecAI context only after deterministic services exist
```

The following remain blocked until profiles, fixtures, tests, and storage checks pass:

- production source-specific loaders,
- canonical migrations for sponsorship/engagement/economics facts,
- sponsorship/engagement outcome materialized views,
- Doctor ROI detail API/UI enrichment,
- standalone territory page,
- ExecAI sponsorship/territory context.

Manual dashboard upload is the target refresh mechanism for this project phase. SFTP, SharePoint polling, and CRM/data-lake auto-discovery are out of scope. Upload validation alone does not update live KPI data; the dashboard reflects new files only after accepted-batch ingestion writes Supabase facts and refreshes the materialized views.

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
