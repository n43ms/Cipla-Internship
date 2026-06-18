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
    count(*)::integer as request_count,
    count(*) filter (
        where er.request_approval_status in ('approved', 'confirmed')
           or er.request_confirmation_status = 'confirmed'
    )::integer as approved_count,
    count(distinct em.id) filter (where em.match_status = 'matched')::integer as executed_count,
    count(*) filter (
        where er.post_approval_status in ('pending_owner', 'pending_confirmation', 'pending', 'draft', 'sent_for_correction')
           or er.post_confirmation_status in ('pending_owner', 'pending_confirmation', 'pending', 'draft', 'sent_for_correction')
    )::integer as report_pending_count,
    sum(er.confirmed_contracted_amount_local) as confirmed_contracted_amount,
    sum(er.direct_hcp_spend_local) as direct_hcp_btu_spend,
    sum(er.overhead_spend_local) as overhead_btc_spend,
    sum(er.actual_total_expense_local) as total_actual_spend,
    coalesce(er.fx_rate_status, 'missing') as fx_rate_status,
    now() as refreshed_at
from execution_requests er
join countries c on c.id = er.country_id
join calendar_months cm on cm.id = er.calendar_month_id
left join event_matches em on em.execution_request_id = er.id
group by
    er.country_id, c.code, c.name, er.calendar_month_id, cm.month_start_date, cm.month_label,
    coalesce(er.intervention_type, 'Unknown'), er.intervention_sub_type, coalesce(er.fx_rate_status, 'missing');
