create materialized view if not exists mv_territory_opportunity as
with rcpa_territory as (
    select
        rdms.country_id,
        c.code as country_code,
        c.name as country_name,
        coalesce(nullif(rdms.territory_name, ''), nullif(rdms.patch_name, ''), 'Unknown') as territory_name,
        nullif(rdms.patch_name, '') as patch_name,
        min(cm.month_start_date) as first_month,
        max(cm.month_start_date) as last_month,
        count(distinct rdms.pcode_normalized)::integer as doctor_count,
        coalesce(sum(rdms.own_prescription_qty), 0)::numeric(18, 2) as cipla_prescription_qty,
        coalesce(sum(rdms.competitor_prescription_qty), 0)::numeric(18, 2) as competitor_prescription_qty,
        coalesce(sum(rdms.total_prescription_qty), 0)::numeric(18, 2) as total_prescription_qty,
        count(*) filter (where rdms.mapping_provenance = 'manual_legacy')::integer as manual_mapping_count,
        count(*) filter (where rdms.mapping_provenance = 'unknown')::integer as unknown_mapping_count
    from rcpa_doctor_month_summary rdms
    join countries c on c.id = rdms.country_id
    join calendar_months cm on cm.id = rdms.calendar_month_id
    group by
        rdms.country_id,
        c.code,
        c.name,
        coalesce(nullif(rdms.territory_name, ''), nullif(rdms.patch_name, ''), 'Unknown'),
        nullif(rdms.patch_name, '')
),
engagement_territory as (
    select
        def.country_id,
        c.code as country_code,
        c.name as country_name,
        coalesce(nullif(def.fs_hq, ''), nullif(def.territory_code, ''), nullif(def.region, ''), 'Unknown') as territory_name,
        null::text as patch_name,
        min(cm.month_start_date) as first_month,
        max(cm.month_start_date) as last_month,
        count(distinct def.pcode_normalized) filter (where def.pcode_normalized is not null)::integer as engaged_doctor_count,
        count(*)::integer as engagement_count,
        count(*) filter (where def.is_sponsorship)::integer as sponsorship_count,
        count(*) filter (
            where def.engagement_class in ('paid_speaker', 'paid_consultancy', 'paid_advisory')
        )::integer as paid_engagement_count,
        count(*) filter (where def.engagement_class = 'no_fee')::integer as no_fee_engagement_count,
        coalesce(sum(coalesce(def.contracted_amount_usd, 0)), 0)::numeric(18, 2) as contracted_amount_usd,
        coalesce(sum(coalesce(def.fmv_amount_usd, 0)), 0)::numeric(18, 2) as fmv_amount_usd,
        coalesce(sum(coalesce(def.contract_saving_usd, 0)), 0)::numeric(18, 2) as contract_saving_usd,
        coalesce(sum(coalesce(def.contracted_amount_usd, 0) + coalesce(def.total_actual_intervention_expense_local * def.fx_rate_to_usd, 0)), 0)::numeric(18, 2) as known_investment_usd,
        count(*) filter (
            where def.is_sponsorship or def.engagement_class <> 'unclassified'
        )::integer as classified_evidence_count,
        count(*) filter (
            where (def.is_sponsorship or def.engagement_class <> 'unclassified')
              and coalesce(def.contracted_amount_usd, def.fmv_amount_usd, def.total_actual_intervention_expense_local * def.fx_rate_to_usd) is null
        )::integer as missing_amount_count
    from doctor_engagement_facts def
    join countries c on c.id = def.country_id
    join calendar_months cm on cm.id = def.calendar_month_id
    group by
        def.country_id,
        c.code,
        c.name,
        coalesce(nullif(def.fs_hq, ''), nullif(def.territory_code, ''), nullif(def.region, ''), 'Unknown')
),
combined as (
    select
        coalesce(r.country_id, e.country_id) as country_id,
        coalesce(r.country_code, e.country_code) as country_code,
        coalesce(r.country_name, e.country_name) as country_name,
        coalesce(r.territory_name, e.territory_name) as territory_name,
        r.patch_name,
        least(coalesce(r.first_month, e.first_month), coalesce(e.first_month, r.first_month)) as first_month,
        greatest(coalesce(r.last_month, e.last_month), coalesce(e.last_month, r.last_month)) as last_month,
        coalesce(r.doctor_count, 0) as doctor_count,
        coalesce(e.engaged_doctor_count, 0) as engaged_doctor_count,
        coalesce(r.cipla_prescription_qty, 0) as cipla_prescription_qty,
        coalesce(r.competitor_prescription_qty, 0) as competitor_prescription_qty,
        coalesce(r.total_prescription_qty, 0) as total_prescription_qty,
        coalesce(e.engagement_count, 0) as engagement_count,
        coalesce(e.sponsorship_count, 0) as sponsorship_count,
        coalesce(e.paid_engagement_count, 0) as paid_engagement_count,
        coalesce(e.no_fee_engagement_count, 0) as no_fee_engagement_count,
        coalesce(e.contracted_amount_usd, 0) as contracted_amount_usd,
        coalesce(e.fmv_amount_usd, 0) as fmv_amount_usd,
        coalesce(e.contract_saving_usd, 0) as contract_saving_usd,
        coalesce(e.known_investment_usd, 0) as known_investment_usd,
        coalesce(e.classified_evidence_count, 0) as classified_evidence_count,
        coalesce(e.missing_amount_count, 0) as missing_amount_count,
        coalesce(r.manual_mapping_count, 0) as manual_mapping_count,
        coalesce(r.unknown_mapping_count, 0) as unknown_mapping_count
    from rcpa_territory r
    full outer join engagement_territory e
      on e.country_id = r.country_id
     and lower(e.territory_name) = lower(r.territory_name)
)
select
    country_id,
    country_code,
    country_name,
    territory_name,
    patch_name,
    first_month,
    last_month,
    doctor_count,
    engaged_doctor_count,
    cipla_prescription_qty,
    competitor_prescription_qty,
    total_prescription_qty,
    round(cipla_prescription_qty / nullif(total_prescription_qty, 0), 4) as cipla_share_qty,
    round(total_prescription_qty / nullif(doctor_count, 0), 2) as prescriptions_per_doctor,
    engagement_count,
    sponsorship_count,
    paid_engagement_count,
    no_fee_engagement_count,
    round(engagement_count::numeric / nullif(doctor_count, 0), 4) as engagements_per_doctor,
    contracted_amount_usd,
    fmv_amount_usd,
    contract_saving_usd,
    known_investment_usd,
    manual_mapping_count,
    unknown_mapping_count,
    missing_amount_count,
    case
        when doctor_count = 0 then 'insufficient_data'
        when (total_prescription_qty / nullif(doctor_count, 0)) >= 50 and engagement_count = 0
            then 'underserved'
        when known_investment_usd > 0 and (total_prescription_qty / nullif(doctor_count, 0)) < 10
            then 'overserved'
        when (engagement_count::numeric / nullif(doctor_count, 0)) > 2
             and (total_prescription_qty / nullif(doctor_count, 0)) < 20
            then 'overserved'
        else 'balanced'
    end as opportunity_label,
    case
        when doctor_count = 0 or total_prescription_qty = 0 then 'low'
        when manual_mapping_count > 0 or unknown_mapping_count > 0 or missing_amount_count > 0 then 'medium'
        else 'high'
    end as evidence_confidence,
    array_remove(array[
        case when manual_mapping_count > 0 then 'manual_rcpa_mapping_period' end,
        case when unknown_mapping_count > 0 then 'unknown_rcpa_mapping_period' end,
        case when missing_amount_count > 0 then 'missing_engagement_amount' end,
        case when doctor_count = 0 then 'no_rcpa_doctor_base' end
    ], null) as source_caveats
from combined;
