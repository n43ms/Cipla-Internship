create materialized view if not exists mv_budget_utilization as
with matched_pairs as (
    select distinct
        em.country_id,
        em.calendar_month_id,
        em.plan_event_id,
        em.execution_request_id,
        em.match_status
    from event_matches em
    where em.match_status in ('matched', 'weak_match')
      and (em.plan_event_id is not null or em.execution_request_id is not null)
),
plan_only as (
    select
        pe.country_id,
        pe.calendar_month_id,
        pe.id as plan_event_id,
        null::uuid as execution_request_id,
        'unmatched_plan'::text as match_status
    from plan_events pe
    where not exists (
        select 1
        from matched_pairs mp
        where mp.plan_event_id = pe.id
    )
),
request_only as (
    select
        er.country_id,
        er.calendar_month_id,
        null::uuid as plan_event_id,
        er.id as execution_request_id,
        'unmatched_request'::text as match_status
    from execution_requests er
    where not exists (
        select 1
        from matched_pairs mp
        where mp.execution_request_id = er.id
    )
),
budget_rows as (
    select * from matched_pairs
    union all
    select * from plan_only
    union all
    select * from request_only
)
select
    br.country_id,
    c.code as country_code,
    c.name as country_name,
    br.calendar_month_id,
    cm.month_start_date,
    cm.month_label,
    br.plan_event_id,
    br.execution_request_id,
    br.match_status,
    coalesce(pe.event_name, er.intervention_name) as event_name,
    coalesce(pe.event_type, er.intervention_type) as event_type,
    pe.therapy,
    er.intervention_sub_type,
    pe.total_planned_cost_usd as planned_budget_usd,
    er.estimated_intervention_local,
    er.estimated_intervention_usd,
    er.confirmed_contracted_amount_local,
    er.confirmed_contracted_amount_usd,
    er.confirmed_vs_estimated_variance_local,
    case
        when er.fx_rate_to_usd is not null and er.confirmed_vs_estimated_variance_local is not null
        then round(er.confirmed_vs_estimated_variance_local * er.fx_rate_to_usd, 4)
        else null
    end as confirmed_vs_estimated_variance_usd,
    er.actual_btu_expense_local as direct_hcp_btu_spend_local,
    er.actual_btu_expense_usd as direct_hcp_btu_spend_usd,
    er.actual_btc_expense_local as overhead_btc_spend_local,
    er.actual_btc_expense_usd as overhead_btc_spend_usd,
    er.actual_total_expense_local,
    er.actual_total_expense_usd,
    er.association_amount_local,
    er.currency_code,
    er.fx_rate_to_usd,
    er.fx_rate_source,
    er.fx_rate_date,
    coalesce(er.fx_rate_status, case when er.id is null then 'not_applicable' else 'missing' end) as fx_rate_status,
    (er.id is not null and (er.fx_rate_status is null or er.fx_rate_status = 'missing')) as missing_fx,
    (er.fx_rate_status = 'provisional') as provisional_fx,
    case
        when er.actual_total_expense_local is null then 'missing_total_actual'
        when er.actual_btu_expense_local is null and er.actual_btc_expense_local is null then 'missing_btu_btc_split'
        when abs(coalesce(er.actual_btu_expense_local, 0) + coalesce(er.actual_btc_expense_local, 0) - er.actual_total_expense_local) <= 1 then 'reconciled'
        else 'mismatch'
    end as btu_btc_reconciliation_status,
    case
        when er.actual_total_expense_local is null then null
        else round(coalesce(er.actual_btu_expense_local, 0) + coalesce(er.actual_btc_expense_local, 0) - er.actual_total_expense_local, 4)
    end as btu_btc_delta_local,
    case
        when er.actual_total_expense_usd is null then null
        else round(coalesce(er.actual_btu_expense_usd, 0) + coalesce(er.actual_btc_expense_usd, 0) - er.actual_total_expense_usd, 4)
    end as btu_btc_delta_usd,
    case
        when pe.id is not null and er.id is null then pe.total_planned_cost_usd
        when pe.total_planned_cost_usd is not null and er.actual_total_expense_usd is not null
        then greatest(pe.total_planned_cost_usd - er.actual_total_expense_usd, 0)
        else null
    end as unspent_gap_usd,
    case
        when pe.total_planned_cost_usd is not null and er.actual_total_expense_usd is not null
        then greatest(er.actual_total_expense_usd - pe.total_planned_cost_usd, 0)
        else null
    end as overrun_amount_usd,
    (pe.id is not null and er.id is null) as plan_without_spend,
    (pe.id is null and er.id is not null) as spend_without_plan,
    coalesce(p4.in_primary_scope, false) as is_primary_phase4_scope,
    coalesce(p4.scope_status, 'out_of_scope_unknown') as scope_status,
    coalesce(p4.scope_reason, 'This country/month is outside the current analytical scope.') as scope_reason,
    now() as refreshed_at
from budget_rows br
join countries c on c.id = br.country_id
join calendar_months cm on cm.id = br.calendar_month_id
left join plan_events pe on pe.id = br.plan_event_id
left join execution_requests er on er.id = br.execution_request_id
left join phase4_analysis_scope p4 on p4.country_id = br.country_id and p4.calendar_month_id = br.calendar_month_id;
