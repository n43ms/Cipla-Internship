create or replace view phase4_analysis_scope as
with all_scopes as (
    select country_id, calendar_month_id from plan_events
    union
    select country_id, calendar_month_id from execution_snapshots
    union
    select country_id, calendar_month_id from execution_requests
),
availability as (
    select
        s.country_id,
        s.calendar_month_id,
        exists (
            select 1 from plan_events pe
            where pe.country_id = s.country_id
              and pe.calendar_month_id = s.calendar_month_id
        ) as planner_available,
        exists (
            select 1 from execution_snapshots es
            where es.country_id = s.country_id
              and es.calendar_month_id = s.calendar_month_id
        ) as snapshot_available,
        exists (
            select 1 from execution_requests er
            where er.country_id = s.country_id
              and er.calendar_month_id = s.calendar_month_id
        ) as consolidation_available
    from all_scopes s
)
select
    a.country_id,
    c.code as country_code,
    c.name as country_name,
    a.calendar_month_id,
    cm.month_start_date,
    cm.month_label,
    a.planner_available,
    a.snapshot_available,
    a.consolidation_available,
    (
        c.name in ('Nepal', 'Sri Lanka')
        and cm.month_label in ('2026-04', '2026-05')
        and a.planner_available
        and a.snapshot_available
        and a.consolidation_available
    ) as in_primary_scope,
    case
        when c.name not in ('Nepal', 'Sri Lanka') then 'out_of_scope_no_fy27_planner_country'
        when cm.month_label < '2026-04' then 'historical_consolidation_no_fy27_plan'
        when cm.month_label > '2026-05' then 'future_or_later_period_no_execution_snapshot'
        when not a.planner_available then 'no_planner_for_country_month'
        when not a.snapshot_available then 'no_execution_snapshot_for_month'
        when not a.consolidation_available then 'no_consolidation_requests_for_month'
        else 'primary_phase4_scope'
    end as scope_status,
    case
        when c.name not in ('Nepal', 'Sri Lanka')
            then 'Phase 4 plan-vs-actual KPIs are scoped to Nepal and Sri Lanka because those are the only markets with FY27 planner coverage.'
        when cm.month_label < '2026-04'
            then 'This period is before FY27 planner coverage and is retained as historical consolidation evidence only.'
        when cm.month_label > '2026-05'
            then 'This period is outside the available April-May 2026 execution snapshot window and is retained for future analysis.'
        when not a.planner_available
            then 'No planner row exists for this country/month, so plan-vs-actual execution cannot be computed without inventing a plan.'
        when not a.snapshot_available
            then 'No monthly execution snapshot exists for this country/month, so execution evidence is incomplete.'
        when not a.consolidation_available
            then 'No consolidation requests exist for this country/month, so request/workflow evidence is incomplete.'
        else 'Primary Phase 4 scope: planner, execution snapshot, and consolidation evidence are all available.'
    end as scope_reason
from availability a
join countries c on c.id = a.country_id
join calendar_months cm on cm.id = a.calendar_month_id;
