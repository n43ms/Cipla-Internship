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

- [ ] Database size was measured again.
- [ ] Largest relations were reviewed.
- [ ] RCPA summary growth was checked.
- [ ] AI log growth was checked.
- [ ] Any generated detailed extract stayed local.

## Compact-Mode Rules

- raw files stay out of Supabase,
- raw files stay out of git,
- large raw RCPA detail stays out of Supabase,
- detailed RCPA evidence stays under `data/processed/`,
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
