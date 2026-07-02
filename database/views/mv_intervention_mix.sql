create materialized view if not exists mv_intervention_mix as
select
    er.country_id,
    c.code as country_code,
    c.name as country_name,
    er.calendar_month_id,
    cm.month_start_date,
    cm.month_label,
    coalesce(er.intervention_type, 'Unknown') as intervention_type,
    er.intervention_sub_type,
    count(distinct er.id)::integer as request_count,
    count(distinct er.id) filter (
        where er.request_approval_status in ('approved', 'confirmed')
           or er.request_confirmation_status = 'confirmed'
    )::integer as approved_count,
    count(distinct er.id) filter (where em.match_status = 'matched')::integer as matched_request_count,
    count(distinct er.id) filter (
        where em.match_status = 'matched'
          and es.normalized_status = 'executed'
    )::integer as executed_count,
    count(distinct er.id) filter (
        where em.match_status = 'matched'
          and es.normalized_status = 'executed'
    )::integer as executed_request_count,
    count(distinct es.id) filter (
        where em.match_status = 'matched'
          and es.normalized_status = 'executed'
    )::integer as executed_snapshot_count,
    count(distinct er.id) filter (
        where em.match_status = 'matched'
          and es.normalized_status = 'action_due'
    )::integer as action_due_count,
    count(distinct er.id) filter (
        where em.match_status = 'matched'
          and es.normalized_status = 'action_due'
    )::integer as action_due_request_count,
    count(distinct es.id) filter (
        where em.match_status = 'matched'
          and es.normalized_status = 'action_due'
    )::integer as action_due_snapshot_count,
    count(distinct er.id) filter (
        where em.match_status = 'matched'
          and em.execution_snapshot_id is null
    )::integer as matched_without_execution_count,
    count(distinct er.id) filter (
        where er.post_approval_status in ('pending_owner', 'pending_confirmation', 'pending', 'draft', 'sent_for_correction')
           or er.post_confirmation_status in ('pending_owner', 'pending_confirmation', 'pending', 'draft', 'sent_for_correction')
    )::integer as report_pending_count,
    sum(er.confirmed_contracted_amount_local) as confirmed_contracted_amount,
    sum(er.direct_hcp_spend_local) as direct_hcp_btu_spend,
    sum(er.overhead_spend_local) as overhead_btc_spend,
    sum(er.actual_total_expense_local) as total_actual_spend,
    coalesce(er.fx_rate_status, 'missing') as fx_rate_status,
    coalesce(p4.in_primary_scope, false) as is_primary_phase4_scope,
    coalesce(p4.scope_status, 'out_of_scope_unknown') as scope_status,
    coalesce(p4.scope_reason, 'This country/month is outside the current Phase 4 analytical scope.') as scope_reason,
    now() as refreshed_at
from execution_requests er
join countries c on c.id = er.country_id
join calendar_months cm on cm.id = er.calendar_month_id
left join phase4_analysis_scope p4 on p4.country_id = er.country_id and p4.calendar_month_id = er.calendar_month_id
left join event_matches em on em.execution_request_id = er.id
left join execution_snapshots es on es.id = em.execution_snapshot_id
group by
    er.country_id, c.code, c.name, er.calendar_month_id, cm.month_start_date, cm.month_label,
    coalesce(er.intervention_type, 'Unknown'), er.intervention_sub_type, coalesce(er.fx_rate_status, 'missing'),
    p4.in_primary_scope, p4.scope_status, p4.scope_reason;
