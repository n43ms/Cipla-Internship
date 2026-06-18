create or replace view mv_latest_file_ingestion_status as
select distinct on (sf.id)
    sf.id as source_file_id,
    sf.original_filename,
    sf.source_type,
    sf.country_scope,
    sf.period_start,
    sf.period_end,
    ir.id as ingestion_run_id,
    ir.started_at,
    ir.completed_at,
    ir.status as ingestion_status,
    irf.status as file_status,
    irf.rows_seen,
    irf.rows_loaded,
    irf.rows_skipped,
    irf.warnings,
    irf.errors,
    irf.sheets_profiled
from source_files sf
join ingestion_run_files irf on irf.source_file_id = sf.id
join ingestion_runs ir on ir.id = irf.ingestion_run_id
where ir.status in ('completed', 'completed_with_warnings')
order by sf.id, ir.started_at desc;
