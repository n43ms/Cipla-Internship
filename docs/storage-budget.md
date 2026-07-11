# Storage Budget Runbook

## Purpose

Supabase is the compact serving database. It is not the raw data lake. Check storage before and after large RCPA, sponsorship, contract, or territory experiments.

## Script

Run:

```powershell
.\scripts\db_size_report.ps1
```

Safe dry run without connecting to the database:

```powershell
.\scripts\db_size_report.ps1 -PrintSqlOnly
```

The script reads `DATABASE_URL` from the environment or `.env`, converts SQLAlchemy's `postgresql+psycopg://` prefix for `psql`, and prints the database URL as `[redacted]`.

Sanitized dry-run example:

```text
Database size report
Free-tier reference limit: 500 MB
Database URL: [redacted]

Dry run: SQL only; no database connection attempted.
```

## Pre-Load Checklist

- [ ] Real source file is outside git.
- [ ] Expected row count is known or estimated.
- [ ] Existing database size has been recorded.
- [ ] Largest tables and materialized views have been reviewed.
- [ ] Compact-vs-detail storage decision is documented.

## Post-Load Checklist

- [X] Database size was measured again.
- [X] Largest relations were reviewed.
- [X] RCPA summary growth was checked.
- [ ] AI log growth was checked.
- [X] Any generated detailed extract stayed local.

## July 10 Package Measurement

Measured after the received-package preload. A pre-load measurement was not captured before the
first successful Supabase write, so this is the post-load baseline for future refreshes.

```text
Database size: 425 MB
Free-tier reference limit: 500 MB
RCPA doctor-month summary: 264 MB, 325,535 rows
RCPA doctor-brand summary: 85 MB, 162,770 rows
RCPA country-brand-month summary: 1,352 kB, 2,482 rows
Doctor engagement facts: 4,976 kB, 4,775 rows
Execution requests: 5,160 kB, 3,604 rows
Source file registry: 64 kB
```

Decision:

```text
Keep compact RCPA summaries in Supabase.
Keep detailed RCPA extracts local under data/processed/.
Do not load raw workbook rows into Supabase.
Future RCPA expansion needs storage review before another full historical backfill.
```

## July 11 Storage Cleanup

Measured after the MSL reference enrichment and historical/current RCPA preload pushed the
database close to the Supabase free-tier limit.

```text
Before cleanup database size: 447 MB
After cleanup database size: 347 MB
Storage reclaimed: 100 MB

RCPA doctor-month summary: 264 MB -> 229 MB, 325,535 rows retained
RCPA doctor-brand summary: 85 MB -> 37 MB, 162,770 rows retained
MSL doctor-master staging table: 17 MB -> removed after enrichment
Doctor dimension rows with MSL source: 25,190 retained
Current Alembic head: 0031_brand_grain
```

Decision:

```text
Keep doctor-month RCPA summaries online because they drive Doctor ROI history, quadrant math,
RCPA credit, territory opportunity, and caveats.
Keep doctor-brand RCPA summaries online only as a slim serving table for doctor detail brand mix
and brand filters, with a retained unique source/country/P-code/brand/own-vs-competitor/currency
grain constraint for idempotent future uploads.
Do not keep persistent MSL raw mapping rows in Supabase after they enrich the doctors dimension
and safe engagement P-code links.
Keep raw MSL and RCPA files outside Supabase and outside git.
Future uploads must write compact facts and summaries, not raw workbook rows.
```

## Compact-Mode Rules

- raw files stay out of Supabase,
- raw files stay out of git,
- large raw RCPA detail stays out of Supabase,
- detailed RCPA evidence stays under `data/processed/`,
- RCPA mapping provenance is stored on compact doctor-month summaries, not as raw rows,
- MSL doctor-master files are staging inputs; persistent doctor identity and territory enrichment
  belongs in `doctors`, not in a retained raw MSL mapping table,
- `rcpa_doctor_brand_summary` is a slim serving table with source file, country, P-code, brand,
  own/competitor, quantity, value, currency, and aggregate row count only,
- territory opportunity is a compact materialized view over RCPA doctor-month summaries and doctor engagement facts, not a raw territory table,
- Supabase stores compact canonical facts, summaries, materialized views, and audit metadata,
- avoid duplicating large RCPA summaries into multiple materialized views.

## SQL Snippets

Total database size:

```sql
select pg_size_pretty(pg_database_size(current_database())) as database_size;
```

Largest relations:

```sql
select
  n.nspname as schema_name,
  c.relname as relation_name,
  c.relkind,
  pg_size_pretty(pg_total_relation_size(c.oid)) as total_size,
  pg_total_relation_size(c.oid) as total_bytes
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relkind in ('r', 'm', 'i')
order by pg_total_relation_size(c.oid) desc
limit 25;
```

RCPA summaries:

```sql
select
  relname,
  pg_size_pretty(pg_total_relation_size(oid)) as total_size,
  pg_total_relation_size(oid) as total_bytes
from pg_class
where relname in (
  'rcpa_doctor_month_summary',
  'rcpa_doctor_brand_summary',
  'rcpa_country_brand_month_summary'
)
order by pg_total_relation_size(oid) desc;
```

Materialized views:

```sql
select
  schemaname,
  matviewname,
  pg_size_pretty(pg_total_relation_size((schemaname || '.' || matviewname)::regclass)) as total_size
from pg_matviews
where schemaname = 'public'
order by pg_total_relation_size((schemaname || '.' || matviewname)::regclass) desc;
```

AI logs:

```sql
select
  count(*) as row_count,
  pg_size_pretty(pg_total_relation_size('public.ai_query_logs')) as total_size
from public.ai_query_logs;
```
