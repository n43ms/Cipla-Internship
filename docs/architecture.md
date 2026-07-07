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

## Sponsorship Readiness MVP

The sponsorship readiness work is a pre-data inspection layer, not a product feature surface.

It extends only the safe front of the architecture:

```text
local source files
  -> ingestion CLI
  -> workbook profiling
  -> raw-vs-cleaned comparison
  -> markdown/json decision reports
```

The following remain blocked until real source files are profiled and a separate post-data task file exists:

- sponsorship and territory database tables,
- source-specific sponsorship/contract/territory loaders,
- sponsorship and territory backend routers,
- sponsorship and territory frontend pages,
- sponsorship and territory AI context.

Primary references:

- `specs/002-execution-intelligence-platform/sponsorship-readiness-plan.md`
- `specs/002-execution-intelligence-platform/sponsorship-readiness-tasks.md`
- `ingestion_sponsorship.md`
- `docs/source-onboarding-playbook.md`
- `docs/feature-gate-policy.md`
