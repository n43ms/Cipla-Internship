create materialized view if not exists mv_execution_kpis as
with scope as (
    select country_id, calendar_month_id from plan_events
    union
    select country_id, calendar_month_id from execution_snapshots
    union
    select country_id, calendar_month_id from execution_requests
),
plan_counts as (
    select
        country_id,
        calendar_month_id,
        count(distinct id) as planned_events,
        coalesce(sum(planned_total_hcps), 0)::integer as planned_hcps
    from plan_events
    group by country_id, calendar_month_id
),
snapshot_metrics as (
    select
        country_id,
        calendar_month_id,
        count(distinct id) filter (where normalized_status = 'executed') as executed_snapshot_count,
        count(distinct id) filter (where normalized_status = 'action_due') as action_due_snapshot_count,
        coalesce(sum(engaged_hcps), 0)::integer as raw_engaged_hcps
    from execution_snapshots
    group by country_id, calendar_month_id
),
matched_snapshot_evidence as (
    select distinct
        em.country_id,
        em.calendar_month_id,
        em.plan_event_id,
        em.execution_snapshot_id,
        es.normalized_status,
        es.engaged_hcps
    from event_matches em
    join execution_snapshots es on es.id = em.execution_snapshot_id
    where em.match_status = 'matched'
      and em.plan_event_id is not null
      and em.execution_snapshot_id is not null
),
matched_execution_metrics as (
    select
        country_id,
        calendar_month_id,
        count(distinct plan_event_id) filter (where normalized_status = 'executed') as planned_events_with_executed_evidence,
        count(distinct plan_event_id) filter (where normalized_status = 'action_due') as planned_events_with_action_due_evidence,
        coalesce(sum(engaged_hcps) filter (where normalized_status = 'executed'), 0)::integer as matched_engaged_hcps
    from matched_snapshot_evidence
    group by country_id, calendar_month_id
),
snapshot_counts as (
    select country_id, calendar_month_id, jsonb_object_agg(snapshot_source, source_count) as snapshot_source_counts
    from (
        select country_id, calendar_month_id, snapshot_source, count(distinct id) as source_count
        from execution_snapshots
        group by country_id, calendar_month_id, snapshot_source
    ) counts
    group by country_id, calendar_month_id
),
match_counts as (
    select
        country_id,
        calendar_month_id,
        count(distinct plan_event_id) filter (where match_status = 'matched' and plan_event_id is not null) as matched_events,
        count(distinct plan_event_id) filter (where match_status = 'weak_match' and plan_event_id is not null) as weak_match_events,
        count(*) filter (where match_status in ('unmatched_plan', 'unmatched_snapshot', 'unmatched_request')) as unmatched_events,
        count(*) filter (where match_status = 'ignored') as ignored_events
    from event_matches
    group by country_id, calendar_month_id
)
select
    s.country_id,
    c.code as country_code,
    c.name as country_name,
    s.calendar_month_id,
    cm.month_start_date,
    cm.month_label,
    coalesce(pc.planned_events, 0) as planned_events,
    coalesce(m.matched_events, 0) as matched_events,
    coalesce(m.weak_match_events, 0) + coalesce(m.unmatched_events, 0) as weak_or_unmatched_events,
    coalesce(mem.planned_events_with_executed_evidence, 0) as executed_events,
    coalesce(mem.planned_events_with_action_due_evidence, 0) as action_due_events,
    coalesce(mem.planned_events_with_executed_evidence, 0) as planned_events_with_executed_evidence,
    coalesce(mem.planned_events_with_action_due_evidence, 0) as planned_events_with_action_due_evidence,
    coalesce(sm.executed_snapshot_count, 0) as executed_snapshot_count,
    coalesce(sm.action_due_snapshot_count, 0) as action_due_snapshot_count,
    coalesce(pc.planned_hcps, 0) as planned_hcps,
    coalesce(mem.matched_engaged_hcps, 0) as engaged_hcps,
    coalesce(mem.matched_engaged_hcps, 0) as matched_engaged_hcps,
    coalesce(sm.raw_engaged_hcps, 0) as raw_engaged_hcps,
    case when coalesce(pc.planned_hcps, 0) > 0
        then round(coalesce(mem.matched_engaged_hcps, 0)::numeric / nullif(pc.planned_hcps, 0), 4)
        else 0 end as hcp_execution_rate,
    case when coalesce(pc.planned_events, 0) > 0
        then round(coalesce(mem.planned_events_with_executed_evidence, 0)::numeric / nullif(pc.planned_events, 0), 4)
        else 0 end as event_execution_rate,
    case when coalesce(pc.planned_events, 0) > 0
        then round(coalesce(m.matched_events, 0)::numeric / nullif(pc.planned_events, 0), 4)
        else 0 end as match_coverage,
    coalesce(m.ignored_events, 0) as ignored_events,
    coalesce(sc.snapshot_source_counts, '{}'::jsonb) as snapshot_source_counts,
    coalesce(p4.in_primary_scope, false) as is_primary_phase4_scope,
    coalesce(p4.scope_status, 'out_of_scope_unknown') as scope_status,
    coalesce(p4.scope_reason, 'This country/month is outside the current Phase 4 analytical scope.') as scope_reason,
    now() as refreshed_at
from scope s
join countries c on c.id = s.country_id
join calendar_months cm on cm.id = s.calendar_month_id
left join phase4_analysis_scope p4 on p4.country_id = s.country_id and p4.calendar_month_id = s.calendar_month_id
left join plan_counts pc on pc.country_id = s.country_id and pc.calendar_month_id = s.calendar_month_id
left join snapshot_metrics sm on sm.country_id = s.country_id and sm.calendar_month_id = s.calendar_month_id
left join matched_execution_metrics mem on mem.country_id = s.country_id and mem.calendar_month_id = s.calendar_month_id
left join match_counts m on m.country_id = s.country_id and m.calendar_month_id = s.calendar_month_id
left join snapshot_counts sc on sc.country_id = s.country_id and sc.calendar_month_id = s.calendar_month_id;
