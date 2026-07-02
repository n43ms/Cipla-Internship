create materialized view if not exists mv_unmatched_events as
select
    em.id as match_id,
    em.country_id,
    c.code as country_code,
    c.name as country_name,
    em.calendar_month_id,
    cm.month_start_date,
    cm.month_label,
    case
        when em.match_status = 'unmatched_plan' then 'planner'
        when em.match_status = 'unmatched_snapshot' then 'execution_snapshot'
        when em.match_status = 'unmatched_request' then 'consolidation'
        else 'weak_match'
    end as source_type,
    coalesce(pe.event_name, es.event_name, er.intervention_name) as event_name,
    coalesce(pe.event_type, es.event_type, er.intervention_type) as event_type,
    em.match_status as reason,
    coalesce(em.unmatched_reason_code, p4.scope_status) as unmatched_reason_code,
    coalesce(em.unmatched_reason_detail, p4.scope_reason) as unmatched_reason_detail,
    coalesce(es.event_name, er.intervention_name, pe.event_name) as candidate_match,
    em.match_confidence as confidence,
    coalesce(p4.in_primary_scope, false) as is_primary_phase4_scope,
    coalesce(p4.scope_status, 'out_of_scope_unknown') as scope_status,
    coalesce(p4.scope_reason, 'This country/month is outside the current Phase 4 analytical scope.') as scope_reason,
    jsonb_build_object(
        'planEventId', em.plan_event_id,
        'executionSnapshotId', em.execution_snapshot_id,
        'executionRequestId', em.execution_request_id,
        'matchedOn', em.matched_on,
        'notes', em.notes
    ) as source_references,
    em.created_at
from event_matches em
join countries c on c.id = em.country_id
join calendar_months cm on cm.id = em.calendar_month_id
left join phase4_analysis_scope p4 on p4.country_id = em.country_id and p4.calendar_month_id = em.calendar_month_id
left join plan_events pe on pe.id = em.plan_event_id
left join execution_snapshots es on es.id = em.execution_snapshot_id
left join execution_requests er on er.id = em.execution_request_id
where em.match_status in ('weak_match', 'unmatched_plan', 'unmatched_snapshot', 'unmatched_request');
