from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class BudgetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def summary(
        self,
        country: str | None,
        month: str | None,
        include_out_of_scope: bool = False,
        page: int = 1,
        page_size: int = 100,
        sort: str = "priority",
        sort_direction: str = "desc",
    ) -> dict[str, Any]:
        offset = max(page - 1, 0) * page_size
        order_by = _budget_order_by(sort, sort_direction)
        params = {
            "country": country,
            "month": month,
            "include_out_of_scope": include_out_of_scope,
            "limit": page_size,
            "offset": offset,
        }
        summary = self.session.execute(
            text(
                """
                with filtered as (
                    select *
                    from mv_budget_utilization
                    where (
                        cast(:country as text) is null
                        or lower(country_code) = lower(cast(:country as text))
                        or lower(country_name) = lower(cast(:country as text))
                    )
                    and (
                        cast(:month as text) is null
                        or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                    )
                    and (cast(:include_out_of_scope as boolean) or is_primary_phase4_scope)
                ),
                plan_totals as (
                    select coalesce(sum(planned_budget_usd), 0) as planned_budget_usd
                    from (
                        select distinct plan_event_id, planned_budget_usd
                        from filtered
                        where plan_event_id is not null
                    ) rows
                ),
                matched_plan_groups as (
                    select
                        plan_event_id,
                        max(planned_budget_usd) as planned_budget_usd,
                        coalesce(sum(actual_total_expense_usd), 0) as actual_total_expense_usd
                    from (
                        select distinct
                            plan_event_id,
                            planned_budget_usd,
                            execution_request_id,
                            actual_total_expense_usd
                        from filtered
                        where plan_event_id is not null
                          and execution_request_id is not null
                    ) rows
                    group by plan_event_id
                ),
                plan_gap_totals as (
                    select
                        coalesce(sum(greatest(planned_budget_usd - actual_total_expense_usd, 0)), 0) as matched_unspent_gap_usd,
                        coalesce(sum(greatest(actual_total_expense_usd - planned_budget_usd, 0)), 0) as matched_overrun_amount_usd
                    from matched_plan_groups
                ),
                plan_only_gap_totals as (
                    select coalesce(sum(planned_budget_usd), 0) as plan_only_unspent_gap_usd
                    from (
                        select distinct plan_event_id, planned_budget_usd
                        from filtered
                        where plan_event_id is not null
                          and execution_request_id is null
                          and plan_without_spend
                    ) rows
                ),
                request_totals as (
                    select
                        coalesce(sum(estimated_intervention_local), 0) as estimated_intervention_local,
                        coalesce(sum(estimated_intervention_usd), 0) as estimated_intervention_usd,
                        coalesce(sum(confirmed_contracted_amount_local), 0) as confirmed_contracted_amount_local,
                        coalesce(sum(confirmed_contracted_amount_usd), 0) as confirmed_contracted_amount_usd,
                        coalesce(sum(confirmed_vs_estimated_variance_local), 0) as confirmed_vs_estimated_variance_local,
                        coalesce(sum(confirmed_vs_estimated_variance_usd), 0) as confirmed_vs_estimated_variance_usd,
                        coalesce(sum(direct_hcp_btu_spend_local), 0) as direct_hcp_btu_spend_local,
                        coalesce(sum(direct_hcp_btu_spend_usd), 0) as direct_hcp_btu_spend_usd,
                        coalesce(sum(overhead_btc_spend_local), 0) as overhead_btc_spend_local,
                        coalesce(sum(overhead_btc_spend_usd), 0) as overhead_btc_spend_usd,
                        coalesce(sum(actual_total_expense_local), 0) as actual_total_spend_local,
                        coalesce(sum(actual_total_expense_usd), 0) as actual_total_spend_usd,
                        coalesce(sum(association_amount_local), 0) as association_amount_local
                    from (
                        select distinct
                            execution_request_id,
                            estimated_intervention_local,
                            estimated_intervention_usd,
                            confirmed_contracted_amount_local,
                            confirmed_contracted_amount_usd,
                            confirmed_vs_estimated_variance_local,
                            confirmed_vs_estimated_variance_usd,
                            direct_hcp_btu_spend_local,
                            direct_hcp_btu_spend_usd,
                            overhead_btc_spend_local,
                            overhead_btc_spend_usd,
                            actual_total_expense_local,
                            actual_total_expense_usd,
                            association_amount_local
                        from filtered
                        where execution_request_id is not null
                    ) rows
                )
                select
                    (select count(*) from filtered)::integer as row_count,
                    plan_totals.planned_budget_usd,
                    request_totals.*,
                    (plan_gap_totals.matched_unspent_gap_usd + plan_only_gap_totals.plan_only_unspent_gap_usd) as unspent_gap_usd,
                    plan_gap_totals.matched_overrun_amount_usd as overrun_amount_usd,
                    count(*) filter (where plan_without_spend)::integer as plan_without_spend_count,
                    count(*) filter (where spend_without_plan)::integer as spend_without_plan_count,
                    count(*) filter (where btu_btc_reconciliation_status = 'mismatch')::integer as btu_btc_reconciliation_issue_count,
                    count(*) filter (where missing_fx)::integer as missing_fx_count,
                    count(*) filter (where provisional_fx)::integer as provisional_fx_count,
                    array_remove(array_agg(distinct currency_code), null) as currency_codes,
                    array_remove(array_agg(distinct fx_rate_status), null) as fx_rate_statuses,
                    max(refreshed_at) as refreshed_at
                from filtered, plan_totals, request_totals, plan_gap_totals, plan_only_gap_totals
                group by
                    plan_totals.planned_budget_usd,
                    plan_gap_totals.matched_unspent_gap_usd,
                    plan_gap_totals.matched_overrun_amount_usd,
                    plan_only_gap_totals.plan_only_unspent_gap_usd,
                    request_totals.estimated_intervention_local,
                    request_totals.estimated_intervention_usd,
                    request_totals.confirmed_contracted_amount_local,
                    request_totals.confirmed_contracted_amount_usd,
                    request_totals.confirmed_vs_estimated_variance_local,
                    request_totals.confirmed_vs_estimated_variance_usd,
                    request_totals.direct_hcp_btu_spend_local,
                    request_totals.direct_hcp_btu_spend_usd,
                    request_totals.overhead_btc_spend_local,
                    request_totals.overhead_btc_spend_usd,
                    request_totals.actual_total_spend_local,
                    request_totals.actual_total_spend_usd,
                    request_totals.association_amount_local
                """
            ),
            params,
        ).mappings().first()
        local_totals = self.session.execute(
            text(
                """
                select
                    currency_code,
                    coalesce(sum(estimated_intervention_local), 0) as estimated_intervention_local,
                    coalesce(sum(confirmed_contracted_amount_local), 0) as confirmed_contracted_amount_local,
                    coalesce(sum(direct_hcp_btu_spend_local), 0) as direct_hcp_btu_spend_local,
                    coalesce(sum(overhead_btc_spend_local), 0) as overhead_btc_spend_local,
                    coalesce(sum(actual_total_expense_local), 0) as actual_total_spend_local,
                    coalesce(sum(association_amount_local), 0) as association_amount_local,
                    count(*)::integer as row_count,
                    count(*) filter (where missing_fx)::integer as missing_fx_count,
                    count(*) filter (where provisional_fx)::integer as provisional_fx_count
                from (
                    select distinct
                        execution_request_id,
                        currency_code,
                        estimated_intervention_local,
                        confirmed_contracted_amount_local,
                        direct_hcp_btu_spend_local,
                        overhead_btc_spend_local,
                        actual_total_expense_local,
                        association_amount_local,
                        missing_fx,
                        provisional_fx
                    from mv_budget_utilization
                    where execution_request_id is not null
                    and (
                        cast(:country as text) is null
                        or lower(country_code) = lower(cast(:country as text))
                        or lower(country_name) = lower(cast(:country as text))
                    )
                    and (
                        cast(:month as text) is null
                        or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                    )
                    and (cast(:include_out_of_scope as boolean) or is_primary_phase4_scope)
                ) rows
                where currency_code is not null
                group by currency_code
                order by currency_code
                """
            ),
            params,
        ).mappings()
        total = self.session.execute(
            text(
                """
                select count(*)::integer
                from mv_budget_utilization
                where (
                    cast(:country as text) is null
                    or lower(country_code) = lower(cast(:country as text))
                    or lower(country_name) = lower(cast(:country as text))
                )
                and (
                    cast(:month as text) is null
                    or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                )
                and (cast(:include_out_of_scope as boolean) or is_primary_phase4_scope)
                """
            ),
            params,
        ).scalar_one()
        rows = self.session.execute(
            text(
                f"""
                select *
                from mv_budget_utilization
                where (
                    cast(:country as text) is null
                    or lower(country_code) = lower(cast(:country as text))
                    or lower(country_name) = lower(cast(:country as text))
                )
                and (
                    cast(:month as text) is null
                    or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                )
                and (cast(:include_out_of_scope as boolean) or is_primary_phase4_scope)
                order by {order_by}
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings()
        return {
            "summary": dict(summary) if summary else {},
            "local_totals_by_currency": [dict(row) for row in local_totals],
            "total": int(total or 0),
            "rows": [dict(row) for row in rows],
        }


def _budget_order_by(sort: str, direction: str) -> str:
    direction_sql = "asc" if direction.lower() == "asc" else "desc"
    columns = {
        "priority": "spend_without_plan desc, plan_without_spend desc, coalesce(unspent_gap_usd, 0) desc, coalesce(overrun_amount_usd, 0) desc, coalesce(actual_total_expense_usd, 0) desc, event_name",
        "eventName": f"event_name {direction_sql} nulls last, country_name, month_start_date desc",
        "unspentGapUsd": f"coalesce(unspent_gap_usd, 0) {direction_sql}, event_name",
        "overrunAmountUsd": f"coalesce(overrun_amount_usd, 0) {direction_sql}, event_name",
        "actualSpendUsd": f"coalesce(actual_total_expense_usd, 0) {direction_sql}, event_name",
        "plannedBudgetUsd": f"coalesce(planned_budget_usd, 0) {direction_sql}, event_name",
        "fxRateStatus": f"fx_rate_status {direction_sql}, event_name",
        "btuBtcReconciliationStatus": f"btu_btc_reconciliation_status {direction_sql}, event_name",
        "matchStatus": f"match_status {direction_sql}, event_name",
    }
    return columns.get(sort, columns["priority"])
