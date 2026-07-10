create materialized view if not exists mv_doctor_roi as
with actual_attendance_raw as (
    select
        rd.id as request_doctor_id,
        rd.execution_request_id,
        er.country_id,
        er.calendar_month_id,
        er.actual_intervention_date,
        er.intervention_date,
        rd.pcode_normalized,
        rd.doctor_name_raw,
        rd.doctor_class_raw,
        er.actual_btu_expense_local,
        er.actual_btc_expense_local,
        er.actual_total_expense_local,
        er.actual_btu_expense_usd,
        er.actual_btc_expense_usd,
        er.actual_total_expense_usd,
        er.currency_code,
        er.fx_rate_status
    from request_doctors rd
    join execution_requests er on er.id = rd.execution_request_id
    where rd.attendance_type = 'actual'
      and rd.pcode_normalized is not null
      and rd.parse_status = 'parsed'
),
actual_attendance as (
    select
        min(request_doctor_id::text)::uuid as request_doctor_id,
        execution_request_id,
        country_id,
        calendar_month_id,
        max(actual_intervention_date) as actual_intervention_date,
        max(intervention_date) as intervention_date,
        pcode_normalized,
        max(doctor_name_raw) filter (where doctor_name_raw is not null) as doctor_name_raw,
        max(doctor_class_raw) filter (where doctor_class_raw is not null) as doctor_class_raw,
        max(actual_btu_expense_local) as actual_btu_expense_local,
        max(actual_btc_expense_local) as actual_btc_expense_local,
        max(actual_total_expense_local) as actual_total_expense_local,
        max(actual_btu_expense_usd) as actual_btu_expense_usd,
        max(actual_btc_expense_usd) as actual_btc_expense_usd,
        max(actual_total_expense_usd) as actual_total_expense_usd,
        max(currency_code) as currency_code,
        max(fx_rate_status) as fx_rate_status
    from actual_attendance_raw
    group by execution_request_id, country_id, calendar_month_id, pcode_normalized
),
request_actual_counts as (
    select execution_request_id, count(distinct pcode_normalized)::numeric as doctor_count
    from actual_attendance
    group by execution_request_id
),
engagement as (
    select
        aa.country_id,
        aa.pcode_normalized,
        max(aa.doctor_name_raw) filter (where aa.doctor_name_raw is not null) as attended_doctor_name,
        max(aa.doctor_class_raw) filter (where aa.doctor_class_raw is not null) as attended_doctor_class,
        count(distinct aa.execution_request_id)::integer as engagement_count,
        min(coalesce(aa.actual_intervention_date, aa.intervention_date)) as first_engagement_date,
        max(coalesce(aa.actual_intervention_date, aa.intervention_date)) as last_engagement_date,
        sum(aa.actual_btu_expense_local / nullif(rac.doctor_count, 0)) as direct_hcp_btu_spend_local,
        sum(aa.actual_btc_expense_local / nullif(rac.doctor_count, 0)) as overhead_btc_spend_local,
        sum(aa.actual_total_expense_local / nullif(rac.doctor_count, 0)) as total_roi_spend_local,
        sum(aa.actual_btu_expense_usd / nullif(rac.doctor_count, 0)) as direct_hcp_btu_spend_usd,
        sum(aa.actual_btc_expense_usd / nullif(rac.doctor_count, 0)) as overhead_btc_spend_usd,
        sum(aa.actual_total_expense_usd / nullif(rac.doctor_count, 0)) as total_roi_spend_usd,
        bool_or(aa.fx_rate_status = 'missing') as has_missing_fx,
        bool_or(aa.fx_rate_status = 'provisional') as has_provisional_fx
    from actual_attendance aa
    join request_actual_counts rac on rac.execution_request_id = aa.execution_request_id
    group by aa.country_id, aa.pcode_normalized
),
doctor_contract_economics as (
    select
        country_id,
        pcode_normalized,
        max(doctor_name) filter (where doctor_name is not null) as doctor_contract_doctor_name,
        max(doctor_segment) filter (where doctor_segment is not null) as doctor_contract_segment,
        count(*)::integer as doctor_contract_engagement_count,
        count(*) filter (where is_sponsorship)::integer as sponsorship_count,
        count(*) filter (where engagement_class = 'no_fee')::integer as no_fee_engagement_count,
        count(*) filter (where engagement_class like 'paid_%')::integer as paid_engagement_count,
        min(expected_intervention_date) as first_doctor_contract_date,
        max(expected_intervention_date) as last_doctor_contract_date,
        sum(contracted_amount_local) as contracted_engagement_amount_local,
        sum(contracted_amount_usd) as contracted_engagement_amount_usd,
        sum(fmv_amount_local) as fmv_engagement_amount_local,
        sum(fmv_amount_usd) as fmv_engagement_amount_usd,
        sum(contract_saving_local) as contract_saving_local,
        sum(contract_saving_usd) as contract_saving_usd,
        count(*) filter (where contracted_amount_local is null and fmv_amount_local is null)::integer as amount_missing_count,
        bool_or(fx_rate_status = 'missing') as has_missing_fx,
        bool_or(fx_rate_status = 'provisional') as has_provisional_fx
    from doctor_engagement_facts
    where pcode_normalized is not null
    group by country_id, pcode_normalized
),
rx as (
    select
        country_id,
        pcode_normalized,
        max(doctor_name) filter (where doctor_name is not null) as rcpa_doctor_name,
        max(speciality) filter (where speciality is not null) as speciality,
        max(doctor_class) filter (where doctor_class is not null) as doctor_class,
        max(active_status) filter (where active_status is not null) as active_status,
        min(cm.month_start_date) as rcpa_first_month,
        max(cm.month_start_date) as rcpa_last_month,
        sum(own_prescription_qty) as cipla_prescription_qty,
        sum(own_prescription_value_local) as cipla_prescription_value_local,
        sum(competitor_prescription_qty) as competitor_prescription_qty,
        sum(competitor_prescription_value_local) as competitor_prescription_value_local,
        sum(total_prescription_qty) as total_prescription_qty,
        sum(total_prescription_value_local) as total_prescription_value_local,
        count(*)::integer as rcpa_month_count
    from rcpa_doctor_month_summary
    join calendar_months cm on cm.id = rcpa_doctor_month_summary.calendar_month_id
    where pcode_normalized is not null
    group by country_id, pcode_normalized
),
doctor_universe as (
    select country_id, pcode_normalized from doctors where pcode_normalized is not null
    union
    select country_id, pcode_normalized from engagement
    union
    select country_id, pcode_normalized from doctor_contract_economics
    union
    select country_id, pcode_normalized from rx
),
metrics as (
    select
        du.country_id,
        c.code as country_code,
        c.name as country_name,
        du.pcode_normalized,
        coalesce(d.latest_doctor_name, rx.rcpa_doctor_name, e.attended_doctor_name, de.doctor_contract_doctor_name) as doctor_name,
        coalesce(d.speciality, rx.speciality) as speciality,
        coalesce(d.doctor_class, rx.doctor_class, e.attended_doctor_class, de.doctor_contract_segment) as doctor_class,
        coalesce(d.active_status, rx.active_status) as active_status,
        coalesce(e.engagement_count, 0) + coalesce(de.doctor_contract_engagement_count, 0) as engagement_count,
        coalesce(de.sponsorship_count, 0) as sponsorship_count,
        coalesce(de.no_fee_engagement_count, 0) as no_fee_engagement_count,
        coalesce(de.paid_engagement_count, 0) as paid_engagement_count,
        case
            when e.first_engagement_date is null then de.first_doctor_contract_date
            when de.first_doctor_contract_date is null then e.first_engagement_date
            else least(e.first_engagement_date, de.first_doctor_contract_date)
        end as first_engagement_date,
        case
            when e.last_engagement_date is null then de.last_doctor_contract_date
            when de.last_doctor_contract_date is null then e.last_engagement_date
            else greatest(e.last_engagement_date, de.last_doctor_contract_date)
        end as last_engagement_date,
        coalesce(e.direct_hcp_btu_spend_local, 0) as direct_hcp_btu_spend_local,
        coalesce(e.overhead_btc_spend_local, 0) as overhead_btc_spend_local,
        coalesce(e.total_roi_spend_local, 0) + coalesce(de.contracted_engagement_amount_local, 0) as total_roi_spend_local,
        coalesce(e.direct_hcp_btu_spend_usd, 0) as direct_hcp_btu_spend_usd,
        coalesce(e.overhead_btc_spend_usd, 0) as overhead_btc_spend_usd,
        coalesce(e.total_roi_spend_usd, 0) + coalesce(de.contracted_engagement_amount_usd, 0) as total_roi_spend_usd,
        coalesce(de.contracted_engagement_amount_local, 0) as contracted_engagement_amount_local,
        coalesce(de.contracted_engagement_amount_usd, 0) as contracted_engagement_amount_usd,
        coalesce(de.fmv_engagement_amount_local, 0) as fmv_engagement_amount_local,
        coalesce(de.fmv_engagement_amount_usd, 0) as fmv_engagement_amount_usd,
        coalesce(de.contract_saving_local, 0) as contract_saving_local,
        coalesce(de.contract_saving_usd, 0) as contract_saving_usd,
        coalesce(de.amount_missing_count, 0) as sponsorship_engagement_amount_missing_count,
        coalesce(rx.cipla_prescription_qty, 0) as cipla_prescription_qty,
        coalesce(rx.cipla_prescription_value_local, 0) as cipla_prescription_value_local,
        coalesce(rx.competitor_prescription_qty, 0) as competitor_prescription_qty,
        coalesce(rx.competitor_prescription_value_local, 0) as competitor_prescription_value_local,
        coalesce(rx.total_prescription_qty, 0) as total_prescription_qty,
        coalesce(rx.total_prescription_value_local, 0) as total_prescription_value_local,
        rx.rcpa_month_count,
        rx.rcpa_first_month,
        rx.rcpa_last_month,
        (rx.pcode_normalized is not null) as has_rcpa,
        coalesce(e.has_missing_fx, false) or coalesce(de.has_missing_fx, false) as has_missing_fx,
        coalesce(e.has_provisional_fx, false) or coalesce(de.has_provisional_fx, false) as has_provisional_fx
    from doctor_universe du
    join countries c on c.id = du.country_id
    left join doctors d on d.country_id = du.country_id and d.pcode_normalized = du.pcode_normalized
    left join engagement e on e.country_id = du.country_id and e.pcode_normalized = du.pcode_normalized
    left join doctor_contract_economics de on de.country_id = du.country_id and de.pcode_normalized = du.pcode_normalized
    left join rx on rx.country_id = du.country_id and rx.pcode_normalized = du.pcode_normalized
),
thresholds as (
    select
        country_id,
        percentile_cont(0.5) within group (order by nullif(total_roi_spend_usd, 0)) as median_spend_usd,
        percentile_cont(0.5) within group (order by nullif(cipla_prescription_qty, 0)) as median_cipla_qty,
        percentile_cont(0.5) within group (order by nullif(engagement_count, 0)) as median_engagement_count
    from metrics
    group by country_id
)
select
    m.*,
    case when m.total_prescription_qty > 0
        then round(m.cipla_prescription_qty / nullif(m.total_prescription_qty, 0), 4)
        else null end as cipla_share_qty,
    case when m.cipla_prescription_qty > 0
        then round(m.total_roi_spend_usd / nullif(m.cipla_prescription_qty, 0), 4)
        else null end as spend_per_cipla_prescription_usd,
    coalesce(t.median_spend_usd, 0) as country_median_spend_usd,
    coalesce(t.median_cipla_qty, 0) as country_median_cipla_qty,
    coalesce(t.median_engagement_count, 0) as country_median_engagement_count,
    coalesce(m.total_roi_spend_usd, 0) as quadrant_x,
    coalesce(m.cipla_prescription_qty, 0) as quadrant_y,
    case
        when not m.has_rcpa then 'no_rcpa'
        when m.engagement_count = 0 and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0) and m.cipla_prescription_qty > 0 then 'high_value_unengaged'
        when m.engagement_count > 0 and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0) then 'high_value_engaged'
        when m.total_roi_spend_usd > coalesce(t.median_spend_usd, 0) and m.cipla_prescription_qty < coalesce(t.median_cipla_qty, 0) then 'low_rx_high_spend'
        else 'insufficient_data'
    end as roi_segment,
    case
        when not m.has_rcpa then 'insufficient data'
        when m.total_roi_spend_usd <= coalesce(t.median_spend_usd, 0) and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0) then 'low effort / high reward'
        when m.total_roi_spend_usd > coalesce(t.median_spend_usd, 0) and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0) then 'high effort / high reward'
        when m.total_roi_spend_usd <= coalesce(t.median_spend_usd, 0) and m.cipla_prescription_qty < coalesce(t.median_cipla_qty, 0) then 'low effort / low reward'
        else 'high effort / low reward'
    end as quadrant_label,
    (
        m.has_rcpa
        and m.engagement_count = 0
        and m.total_roi_spend_usd <= coalesce(t.median_spend_usd, 0)
        and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0)
        and m.cipla_prescription_qty > 0
    ) as dark_horse_flag,
    (
        m.has_rcpa
        and m.engagement_count = 0
        and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0)
        and m.cipla_prescription_qty > 0
    ) as dark_horse_unengaged_flag,
    (
        m.has_rcpa
        and m.engagement_count > 0
        and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0)
    ) as high_value_engaged_flag,
    now() as refreshed_at
from metrics m
left join thresholds t on t.country_id = m.country_id;
