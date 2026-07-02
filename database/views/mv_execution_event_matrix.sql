create materialized view if not exists mv_execution_event_matrix as
with decorated as (
    select
        em.*,
        count(*) filter (where em.match_status in ('matched', 'weak_match') and em.plan_event_id is not null)
            over (partition by em.plan_event_id) as plan_match_count,
        count(*) filter (where em.match_status in ('matched', 'weak_match') and em.execution_snapshot_id is not null)
            over (partition by em.execution_snapshot_id) as snapshot_match_count
    from event_matches em
)
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
        when em.plan_event_id is not null and em.execution_snapshot_id is not null and em.execution_request_id is not null then 'planner_execution_consolidation'
        when em.plan_event_id is not null and em.execution_snapshot_id is not null then 'planner_execution'
        when em.plan_event_id is not null and em.execution_request_id is not null then 'planner_consolidation'
        when em.execution_snapshot_id is not null and em.execution_request_id is not null then 'execution_consolidation'
        else 'reconciliation'
    end as source_type,
    coalesce(pe.event_name, es.event_name, er.intervention_name) as event_name,
    coalesce(pe.event_type, es.event_type, er.intervention_type) as event_type,
    pe.event_name as planned_event_name,
    es.event_name as snapshot_event_name,
    er.intervention_name as request_event_name,
    em.match_status,
    em.match_method,
    em.match_confidence as confidence,
    case
        when em.match_status = 'unmatched_plan' then null
        else coalesce(es.event_name, er.intervention_name, pe.event_name)
    end as candidate_match,
    pe.planned_total_hcps as planned_hcps,
    es.engaged_hcps,
    es.normalized_status as execution_status,
    es.snapshot_source,
    er.req_id,
    er.request_uid,
    er.intervention_type,
    er.intervention_sub_type,
    er.request_approval_status,
    er.request_confirmation_status,
    er.post_approval_status,
    er.post_confirmation_status,
    er.current_owner_stage,
    case
        when em.match_status in ('weak_match', 'unmatched_plan', 'unmatched_snapshot', 'unmatched_request')
            then coalesce(em.unmatched_reason_code, p4.scope_status)
        else null
    end as unmatched_reason_code,
    case
        when em.match_status in ('weak_match', 'unmatched_plan', 'unmatched_snapshot', 'unmatched_request')
            then coalesce(em.unmatched_reason_detail, p4.scope_reason)
        else null
    end as unmatched_reason_detail,
    coalesce(p4.in_primary_scope, false) as is_primary_phase4_scope,
    coalesce(p4.scope_status, 'out_of_scope_unknown') as scope_status,
    coalesce(p4.scope_reason, 'This country/month is outside the current Phase 4 analytical scope.') as scope_reason,
    case
        when em.match_status in ('unmatched_plan', 'unmatched_snapshot', 'unmatched_request') then 'unmatched'
        when em.plan_event_id is not null and em.plan_match_count > 1 then 'one_plan_many_requests'
        when em.execution_snapshot_id is not null and em.snapshot_match_count > 1 then 'one_snapshot_many_requests'
        else 'single_match'
    end as match_grain,
    jsonb_build_object(
        'planEventId', em.plan_event_id,
        'executionSnapshotId', em.execution_snapshot_id,
        'executionRequestId', em.execution_request_id,
        'matchedOn', em.matched_on,
        'notes', em.notes,
        'planSourceRow', pe.source_row_number,
        'snapshotSourceRow', es.source_row_number,
        'requestSourceRow', er.source_row_number,
        'snapshotDerivation', es.source_derivation_json
    ) as source_references,
    case
        when es.snapshot_source = 'derived_from_consolidation'
            then 'Derived from consolidation because the monthly execution country tab was missing.'
        else null
    end as source_derivation_note,
    em.created_at
from decorated em
join countries c on c.id = em.country_id
join calendar_months cm on cm.id = em.calendar_month_id
left join phase4_analysis_scope p4 on p4.country_id = em.country_id and p4.calendar_month_id = em.calendar_month_id
left join plan_events pe on pe.id = em.plan_event_id
left join execution_snapshots es on es.id = em.execution_snapshot_id
left join execution_requests er on er.id = em.execution_request_id;
