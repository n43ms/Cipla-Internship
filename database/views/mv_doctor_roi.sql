create materialized view if not exists mv_doctor_roi as
with actual_attendance as (
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
rx as (
    select
        country_id,
        pcode_normalized,
        max(doctor_name) filter (where doctor_name is not null) as rcpa_doctor_name,
        max(speciality) filter (where speciality is not null) as speciality,
        max(doctor_class) filter (where doctor_class is not null) as doctor_class,
        max(active_status) filter (where active_status is not null) as active_status,
        sum(own_prescription_qty) as cipla_prescription_qty,
        sum(own_prescription_value_local) as cipla_prescription_value_local,
        sum(competitor_prescription_qty) as competitor_prescription_qty,
        sum(competitor_prescription_value_local) as competitor_prescription_value_local,
        sum(total_prescription_qty) as total_prescription_qty,
        sum(total_prescription_value_local) as total_prescription_value_local,
        count(*)::integer as rcpa_month_count
    from rcpa_doctor_month_summary
    where pcode_normalized is not null
    group by country_id, pcode_normalized
),
doctor_universe as (
    select country_id, pcode_normalized from doctors where pcode_normalized is not null
    union
    select country_id, pcode_normalized from engagement
    union
    select country_id, pcode_normalized from rx
),
metrics as (
    select
        du.country_id,
        c.code as country_code,
        c.name as country_name,
        du.pcode_normalized,
        coalesce(d.latest_doctor_name, rx.rcpa_doctor_name, e.attended_doctor_name) as doctor_name,
        coalesce(d.speciality, rx.speciality) as speciality,
        coalesce(d.doctor_class, rx.doctor_class, e.attended_doctor_class) as doctor_class,
        coalesce(d.active_status, rx.active_status) as active_status,
        coalesce(e.engagement_count, 0) as engagement_count,
        e.last_engagement_date,
        coalesce(e.direct_hcp_btu_spend_local, 0) as direct_hcp_btu_spend_local,
        coalesce(e.overhead_btc_spend_local, 0) as overhead_btc_spend_local,
        coalesce(e.total_roi_spend_local, 0) as total_roi_spend_local,
        coalesce(e.direct_hcp_btu_spend_usd, 0) as direct_hcp_btu_spend_usd,
        coalesce(e.overhead_btc_spend_usd, 0) as overhead_btc_spend_usd,
        coalesce(e.total_roi_spend_usd, 0) as total_roi_spend_usd,
        coalesce(rx.cipla_prescription_qty, 0) as cipla_prescription_qty,
        coalesce(rx.cipla_prescription_value_local, 0) as cipla_prescription_value_local,
        coalesce(rx.competitor_prescription_qty, 0) as competitor_prescription_qty,
        coalesce(rx.competitor_prescription_value_local, 0) as competitor_prescription_value_local,
        coalesce(rx.total_prescription_qty, 0) as total_prescription_qty,
        coalesce(rx.total_prescription_value_local, 0) as total_prescription_value_local,
        rx.rcpa_month_count,
        (rx.pcode_normalized is not null) as has_rcpa,
        coalesce(e.has_missing_fx, false) as has_missing_fx,
        coalesce(e.has_provisional_fx, false) as has_provisional_fx
    from doctor_universe du
    join countries c on c.id = du.country_id
    left join doctors d on d.country_id = du.country_id and d.pcode_normalized = du.pcode_normalized
    left join engagement e on e.country_id = du.country_id and e.pcode_normalized = du.pcode_normalized
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
        and m.total_roi_spend_usd <= coalesce(t.median_spend_usd, 0)
        and m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0)
        and m.cipla_prescription_qty > 0
    ) as dark_horse_flag,
    now() as refreshed_at
from metrics m
left join thresholds t on t.country_id = m.country_id;
