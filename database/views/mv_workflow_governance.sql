create materialized view if not exists mv_workflow_governance as
select
    er.country_id,
    c.code as country_code,
    c.name as country_name,
    er.calendar_month_id,
    cm.month_start_date,
    cm.month_label,
    er.req_id,
    er.request_uid,
    er.rep_name,
    er.intervention_type,
    er.intervention_sub_type,
    coalesce(er.request_approval_status, 'unknown') as request_approval_status,
    coalesce(er.request_confirmation_status, 'unknown') as request_confirmation_status,
    coalesce(er.post_approval_status, 'unknown') as post_approval_status,
    coalesce(er.post_confirmation_status, 'unknown') as post_confirmation_status,
    coalesce(
        er.current_owner_stage,
        case
            when er.request_approval_status in ('pending_owner', 'pending_confirmation', 'pending') then 'request approval pending'
            when er.request_confirmation_status in ('pending_owner', 'pending_confirmation', 'pending') then 'request confirmation pending'
            when er.post_approval_status in ('pending_owner', 'pending_confirmation', 'pending', 'sent_for_correction') then 'post report approval pending'
            when er.post_confirmation_status in ('pending_owner', 'pending_confirmation', 'pending', 'sent_for_correction') then 'post report confirmation pending'
            when er.post_approval_status = 'draft' or er.post_confirmation_status = 'draft' then 'post report not submitted'
            when er.request_approval_status in ('deleted', 'rejected') then concat('request ', er.request_approval_status)
            when er.post_approval_status = 'approved' or er.post_confirmation_status in ('approved', 'confirmed') then 'post report approved'
            when er.request_approval_status in ('approved', 'confirmed') or er.request_confirmation_status in ('approved', 'confirmed') then 'request approved; report pending'
            else 'unknown'
        end
    ) as current_owner_stage,
    er.expense_submitted_date,
    er.expense_confirmed_date,
    case when er.request_approval_status in ('pending_owner', 'pending_confirmation', 'pending') then 1 else 0 end as pending_request_count,
    case when er.post_approval_status in ('pending_owner', 'pending_confirmation', 'pending', 'draft', 'sent_for_correction')
        or er.post_confirmation_status in ('pending_owner', 'pending_confirmation', 'pending', 'draft', 'sent_for_correction')
        then 1 else 0 end as pending_report_count,
    case when er.post_approval_status = 'sent_for_correction' or er.post_confirmation_status = 'sent_for_correction' then 1 else 0 end as reports_sent_for_correction,
    case when er.post_approval_status = 'approved' or er.post_confirmation_status = 'confirmed' then 1 else 0 end as reports_approved,
    case when er.expense_submitted_date is not null then 1 else 0 end as expense_submitted_flag,
    case when er.expense_confirmed_date is not null then 1 else 0 end as expense_confirmed_flag,
    er.source_row_number,
    now() as refreshed_at
from execution_requests er
join countries c on c.id = er.country_id
join calendar_months cm on cm.id = er.calendar_month_id;
