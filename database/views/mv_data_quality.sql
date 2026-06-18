create materialized view if not exists mv_data_quality as
with latest_run as (
    select *
    from ingestion_runs
    order by started_at desc
    limit 1
),
latest_file_runs as (
    select distinct on (irf.source_file_id)
        irf.source_file_id,
        irf.status,
        irf.rows_seen,
        irf.rows_loaded,
        irf.rows_skipped,
        irf.warnings,
        irf.errors
    from ingestion_run_files irf
    join ingestion_runs ir on ir.id = irf.ingestion_run_id
    order by irf.source_file_id, ir.started_at desc
),
validation_latest as (
    select ve.*
    from validation_errors ve
    join latest_file_runs lfr on lfr.source_file_id = ve.source_file_id
),
request_pcode as (
    select
        count(*)::integer as request_doctor_rows,
        count(*) filter (where pcode_normalized is not null)::integer as request_doctor_rows_with_pcode
    from request_doctors
),
workflow as (
    select
        count(*)::integer as workflow_rows,
        count(*) filter (where request_approval_status is not null and request_approval_status <> 'unknown')::integer as request_approval_covered,
        count(*) filter (where post_approval_status is not null and post_approval_status <> 'unknown')::integer as post_approval_covered
    from execution_requests
),
interventions as (
    select
        count(*)::integer as request_rows,
        count(*) filter (where intervention_type is not null and btrim(intervention_type) <> '')::integer as intervention_type_covered
    from execution_requests
),
fx as (
    select
        count(*) filter (where fx_rate_status = 'missing')::integer as missing_fx_count,
        count(*) filter (where fx_rate_status = 'provisional')::integer as provisional_fx_count
    from execution_requests
),
budget_quality as (
    select
        count(*) filter (where btu_btc_reconciliation_status = 'mismatch')::integer as btu_btc_reconciliation_issue_count,
        count(*) filter (where confirmed_contracted_amount_local is null and execution_request_id is not null)::integer as missing_confirmed_amount_count,
        count(*) filter (where spend_without_plan)::integer as spend_without_plan_count,
        count(*) filter (where plan_without_spend)::integer as plan_without_spend_count
    from mv_budget_utilization
),
rcpa as (
    select
        count(distinct country_id || ':' || pcode_normalized)::integer as rcpa_doctor_count,
        coalesce(sum(row_count_aggregated), 0)::integer as rcpa_rows_aggregated
    from rcpa_doctor_month_summary
),
doctor_coverage as (
    select
        count(*)::integer as doctor_roi_rows,
        count(*) filter (where has_rcpa)::integer as doctor_roi_rows_with_rcpa,
        count(*) filter (where roi_segment = 'no_rcpa')::integer as doctor_no_rcpa_count
    from mv_doctor_roi
),
execution_quality as (
    select
        coalesce(sum(planned_events), 0)::integer as planned_events,
        coalesce(sum(matched_events), 0)::integer as matched_events,
        coalesce(sum(weak_or_unmatched_events), 0)::integer as weak_or_unmatched_events,
        coalesce(avg(match_coverage), 0)::numeric as avg_match_coverage
    from mv_execution_kpis
    where is_primary_phase4_scope
),
unmatched as (
    select count(*)::integer as unmatched_event_count
    from mv_unmatched_events
    where is_primary_phase4_scope
),
derived as (
    select count(*)::integer as derived_snapshot_count
    from execution_snapshots
    where snapshot_source = 'derived_from_consolidation'
)
select
    lr.id as latest_ingestion_run_id,
    lr.status as latest_ingestion_status,
    lr.started_at as latest_ingestion_started_at,
    lr.completed_at as latest_ingestion_completed_at,
    coalesce((select count(*) from source_files), 0)::integer as source_file_count,
    coalesce((select count(*) from latest_file_runs where status in ('loaded', 'completed', 'completed_with_warnings')), 0)::integer as loaded_file_count,
    coalesce((select sum(rows_seen) from latest_file_runs), 0)::integer as rows_seen,
    coalesce((select sum(rows_loaded) from latest_file_runs), 0)::integer as rows_loaded,
    coalesce((select sum(rows_skipped) from latest_file_runs), 0)::integer as rows_skipped,
    coalesce((select count(*) from validation_latest where severity = 'error'), 0)::integer as validation_error_count,
    coalesce((select count(*) from validation_latest where severity = 'warning'), 0)::integer as validation_warning_count,
    eq.planned_events,
    eq.matched_events,
    eq.weak_or_unmatched_events,
    eq.avg_match_coverage as match_coverage,
    rp.request_doctor_rows,
    rp.request_doctor_rows_with_pcode,
    case when rp.request_doctor_rows > 0
        then round(rp.request_doctor_rows_with_pcode::numeric / nullif(rp.request_doctor_rows, 0), 4)
        else 0 end as pcode_coverage,
    rcpa.rcpa_doctor_count,
    rcpa.rcpa_rows_aggregated,
    dc.doctor_roi_rows,
    dc.doctor_roi_rows_with_rcpa,
    dc.doctor_no_rcpa_count,
    case when dc.doctor_roi_rows > 0
        then round(dc.doctor_roi_rows_with_rcpa::numeric / nullif(dc.doctor_roi_rows, 0), 4)
        else 0 end as rcpa_coverage,
    fx.missing_fx_count,
    fx.provisional_fx_count,
    bq.btu_btc_reconciliation_issue_count,
    bq.missing_confirmed_amount_count,
    bq.spend_without_plan_count,
    bq.plan_without_spend_count,
    workflow.workflow_rows,
    case when workflow.workflow_rows > 0
        then round(workflow.request_approval_covered::numeric / nullif(workflow.workflow_rows, 0), 4)
        else 0 end as request_workflow_coverage,
    case when workflow.workflow_rows > 0
        then round(workflow.post_approval_covered::numeric / nullif(workflow.workflow_rows, 0), 4)
        else 0 end as post_workflow_coverage,
    case when interventions.request_rows > 0
        then round(interventions.intervention_type_covered::numeric / nullif(interventions.request_rows, 0), 4)
        else 0 end as intervention_type_coverage,
    unmatched.unmatched_event_count,
    derived.derived_snapshot_count,
    (
        lr.completed_at is null
        or lr.completed_at < now() - interval '14 days'
        or lr.status not in ('completed', 'completed_with_warnings')
    ) as stale_ingestion,
    now() as refreshed_at
from latest_run lr
cross join request_pcode rp
cross join workflow
cross join interventions
cross join fx
cross join budget_quality bq
cross join rcpa
cross join doctor_coverage dc
cross join execution_quality eq
cross join unmatched
cross join derived;
