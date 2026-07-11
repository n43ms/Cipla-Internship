create materialized view if not exists mv_sponsorship_outcomes as
with engagement as (
    select
        country_id,
        pcode_normalized,
        max(doctor_name) filter (where doctor_name is not null) as doctor_name,
        count(*)::integer as engagement_evidence_count,
        count(*) filter (where is_sponsorship)::integer as sponsorship_count,
        count(*) filter (where engagement_class = 'no_fee')::integer as no_fee_engagement_count,
        count(*) filter (where engagement_class like 'paid_%')::integer as paid_engagement_count,
        count(*) filter (where engagement_class in ('paid_speaker', 'paid_consultancy', 'paid_advisory'))::integer as paid_service_count,
        min(expected_intervention_date) as first_engagement_date,
        max(expected_intervention_date) as latest_engagement_date,
        sum(contracted_amount_local) as contracted_amount_local,
        sum(contracted_amount_usd) as contracted_amount_usd,
        sum(fmv_amount_local) as fmv_amount_local,
        sum(fmv_amount_usd) as fmv_amount_usd,
        sum(contract_saving_local) as contract_saving_local,
        sum(contract_saving_usd) as contract_saving_usd,
        sum(total_actual_intervention_expense_local) as doctor_attributable_expense_local,
        count(*) filter (where contracted_amount_local is null and fmv_amount_local is null)::integer as amount_missing_count,
        bool_or(fx_rate_status = 'missing') as has_missing_fx,
        bool_or(fx_rate_status = 'provisional') as has_provisional_fx
    from doctor_engagement_facts
    where pcode_normalized is not null
    group by country_id, pcode_normalized
),
rcpa_window as (
    select
        e.country_id,
        e.pcode_normalized,
        sum(rdms.own_prescription_qty) filter (
            where cm.month_start_date < date_trunc('month', e.first_engagement_date)::date
              and cm.month_start_date >= (date_trunc('month', e.first_engagement_date)::date - interval '6 months')
        ) as pre_window_cipla_rx_qty,
        sum(rdms.own_prescription_qty) filter (
            where cm.month_start_date > date_trunc('month', e.latest_engagement_date)::date
              and cm.month_start_date <= (date_trunc('month', e.latest_engagement_date)::date + interval '6 months')
        ) as post_window_cipla_rx_qty,
        count(distinct cm.month_start_date) filter (
            where cm.month_start_date < date_trunc('month', e.first_engagement_date)::date
              and cm.month_start_date >= (date_trunc('month', e.first_engagement_date)::date - interval '6 months')
        )::integer as pre_window_month_count,
        count(distinct cm.month_start_date) filter (
            where cm.month_start_date > date_trunc('month', e.latest_engagement_date)::date
              and cm.month_start_date <= (date_trunc('month', e.latest_engagement_date)::date + interval '6 months')
        )::integer as post_window_month_count,
        count(*) filter (where rdms.mapping_provenance = 'manual_legacy')::integer as manual_mapping_count,
        count(*) filter (where rdms.mapping_provenance = 'unknown')::integer as unknown_mapping_count
    from engagement e
    left join rcpa_doctor_month_summary rdms
      on rdms.country_id = e.country_id
     and rdms.pcode_normalized = e.pcode_normalized
    left join calendar_months cm on cm.id = rdms.calendar_month_id
    group by e.country_id, e.pcode_normalized
)
select
    e.country_id,
    c.code as country_code,
    c.name as country_name,
    e.pcode_normalized,
    e.doctor_name,
    e.engagement_evidence_count,
    e.sponsorship_count,
    e.no_fee_engagement_count,
    e.paid_engagement_count,
    e.paid_service_count,
    e.first_engagement_date,
    e.latest_engagement_date,
    e.contracted_amount_local,
    e.contracted_amount_usd,
    e.fmv_amount_local,
    e.fmv_amount_usd,
    e.contract_saving_local,
    e.contract_saving_usd,
    e.doctor_attributable_expense_local,
    e.amount_missing_count,
    coalesce(e.contracted_amount_usd, 0) as known_engagement_investment_usd,
    coalesce(r.pre_window_cipla_rx_qty, 0) as pre_window_cipla_rx_qty,
    coalesce(r.post_window_cipla_rx_qty, 0) as post_window_cipla_rx_qty,
    coalesce(r.post_window_cipla_rx_qty, 0) - coalesce(r.pre_window_cipla_rx_qty, 0) as associated_rx_movement_qty,
    coalesce(r.pre_window_month_count, 0) as pre_window_month_count,
    coalesce(r.post_window_month_count, 0) as post_window_month_count,
    coalesce(r.manual_mapping_count, 0) as manual_mapping_count,
    coalesce(r.unknown_mapping_count, 0) as unknown_mapping_count,
    case
        when coalesce(r.pre_window_month_count, 0) < 3 or coalesce(r.post_window_month_count, 0) < 3 then 'low'
        when coalesce(r.manual_mapping_count, 0) > 0 or coalesce(r.unknown_mapping_count, 0) > 0 then 'medium'
        else 'high'
    end as evidence_confidence,
    array_remove(array[
        case when e.amount_missing_count > 0 then 'amount_unavailable_not_counted_as_zero' end,
        case when coalesce(r.pre_window_month_count, 0) < 3 then 'insufficient_pre_window_rcpa' end,
        case when coalesce(r.post_window_month_count, 0) < 3 then 'insufficient_post_window_rcpa' end,
        case when coalesce(r.manual_mapping_count, 0) > 0 then 'manual_rcpa_mapping_period' end,
        case when coalesce(r.unknown_mapping_count, 0) > 0 then 'unknown_rcpa_mapping_period' end,
        case when e.has_missing_fx then 'missing_fx' end,
        case when e.has_provisional_fx then 'provisional_fx' end
    ], null) as evidence_caveats,
    now() as refreshed_at
from engagement e
join countries c on c.id = e.country_id
left join rcpa_window r on r.country_id = e.country_id and r.pcode_normalized = e.pcode_normalized;
