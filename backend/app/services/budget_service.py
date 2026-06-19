from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.repositories.budget_repository import BudgetRepository
from backend.app.schemas.budget import BudgetGapRow, BudgetSummary, LocalCurrencyTotal
from backend.app.services.dashboard_meta import build_meta
from backend.app.services.filter_validation import validate_country_month_filters


class BudgetService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = BudgetRepository(session)

    def summary(
        self,
        country: str | None = None,
        month: str | None = None,
        include_out_of_scope: bool = False,
        page: int = 1,
        page_size: int = 100,
        sort: str = "priority",
        sort_direction: str = "desc",
    ) -> BudgetSummary:
        validate_country_month_filters(self.session, country=country, month=month)
        data = self.repository.summary(country, month, include_out_of_scope, page, page_size, sort, sort_direction)
        row = data["summary"]
        flags: list[str] = []
        limitations: list[str] = []
        if int(row.get("missing_fx_count") or 0):
            flags.append("missing_fx")
            limitations.append("Some non-LKR amounts have no company FX rate, so USD comparisons are incomplete.")
        if int(row.get("provisional_fx_count") or 0):
            flags.append("provisional_fx")
            limitations.append("Some amounts use provisional FX and should not be treated as final finance numbers.")
        if int(row.get("btu_btc_reconciliation_issue_count") or 0):
            flags.append("btu_btc_reconciliation_issue")
            limitations.append("Some BTU + BTC splits do not reconcile to total actual expense.")
        if len(row.get("currency_codes") or []) > 1:
            flags.append("mixed_local_currencies")
            limitations.append("Local currency totals are grouped by currency; only seeded FX rows are comparable in USD.")
        local_totals_are_mixed = len(row.get("currency_codes") or []) > 1
        if not include_out_of_scope:
            limitations.append("Budget rows default to the current Phase 4 analytical scope.")
        mapped_rows = [
            BudgetGapRow(
                event_name=item.get("event_name"),
                event_type=item.get("event_type"),
                country=str(item.get("country_name") or item.get("country_code") or ""),
                month=str(item.get("month_label") or item.get("month_start_date") or ""),
                match_status=str(item.get("match_status") or "unknown"),
                planned_budget_usd=item.get("planned_budget_usd"),
                estimated_intervention_local=item.get("estimated_intervention_local"),
                confirmed_contracted_amount_local=item.get("confirmed_contracted_amount_local"),
                actual_total_expense_local=item.get("actual_total_expense_local"),
                direct_hcp_btu_spend_local=item.get("direct_hcp_btu_spend_local"),
                overhead_btc_spend_local=item.get("overhead_btc_spend_local"),
                actual_total_expense_usd=item.get("actual_total_expense_usd"),
                unspent_gap_usd=item.get("unspent_gap_usd"),
                overrun_amount_usd=item.get("overrun_amount_usd"),
                currency_code=item.get("currency_code"),
                fx_rate_status=str(item.get("fx_rate_status") or "missing"),
                btu_btc_reconciliation_status=str(item.get("btu_btc_reconciliation_status") or "unknown"),
                spend_without_plan=bool(item.get("spend_without_plan")),
                plan_without_spend=bool(item.get("plan_without_spend")),
                row_kind=_row_kind(item),
                scope_status=item.get("scope_status"),
            )
            for item in data["rows"]
        ]
        return BudgetSummary(
            meta=build_meta(
                self.session,
                filters_applied=_filters(
                    country=country,
                    month=month,
                    includeOutOfScope=include_out_of_scope,
                    sort=sort,
                    sortDirection=sort_direction,
                ),
                flags=flags,
                limitations=limitations,
            ),
            planned_budget_usd=_decimal(row.get("planned_budget_usd")),
            estimated_intervention_local=None if local_totals_are_mixed else _decimal(row.get("estimated_intervention_local")),
            estimated_intervention_usd=_decimal(row.get("estimated_intervention_usd")),
            confirmed_contracted_amount_local=None if local_totals_are_mixed else _decimal(row.get("confirmed_contracted_amount_local")),
            confirmed_contracted_amount_usd=_decimal(row.get("confirmed_contracted_amount_usd")),
            confirmed_vs_estimated_variance_local=None if local_totals_are_mixed else _decimal(row.get("confirmed_vs_estimated_variance_local")),
            confirmed_vs_estimated_variance_usd=_decimal(row.get("confirmed_vs_estimated_variance_usd")),
            direct_hcp_btu_spend_local=None if local_totals_are_mixed else _decimal(row.get("direct_hcp_btu_spend_local")),
            direct_hcp_btu_spend_usd=_decimal(row.get("direct_hcp_btu_spend_usd")),
            overhead_btc_spend_local=None if local_totals_are_mixed else _decimal(row.get("overhead_btc_spend_local")),
            overhead_btc_spend_usd=_decimal(row.get("overhead_btc_spend_usd")),
            actual_total_spend_local=None if local_totals_are_mixed else _decimal(row.get("actual_total_spend_local")),
            actual_total_spend_usd=_decimal(row.get("actual_total_spend_usd")),
            association_amount_local=None if local_totals_are_mixed else _decimal(row.get("association_amount_local")),
            unspent_gap_usd=_decimal(row.get("unspent_gap_usd")),
            overrun_amount_usd=_decimal(row.get("overrun_amount_usd")),
            plan_without_spend_count=int(row.get("plan_without_spend_count") or 0),
            spend_without_plan_count=int(row.get("spend_without_plan_count") or 0),
            btu_btc_reconciliation_issue_count=int(row.get("btu_btc_reconciliation_issue_count") or 0),
            missing_fx_count=int(row.get("missing_fx_count") or 0),
            provisional_fx_count=int(row.get("provisional_fx_count") or 0),
            currency_codes=list(row.get("currency_codes") or []),
            fx_rate_statuses=list(row.get("fx_rate_statuses") or []),
            local_totals_by_currency=[LocalCurrencyTotal(**item) for item in data["local_totals_by_currency"]],
            page=page,
            page_size=page_size,
            total=int(data.get("total") or 0),
            sort=sort,
            sort_direction=sort_direction,
            rows=mapped_rows,
        )


def _decimal(value: object) -> Decimal:
    return Decimal(str(value or 0))


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}


def _row_kind(item: dict[str, object]) -> str:
    if item.get("plan_without_spend"):
        return "plan_without_spend"
    if item.get("spend_without_plan"):
        return "spend_without_plan"
    if item.get("execution_request_id") and item.get("plan_event_id"):
        return "matched_request_evidence"
    if item.get("plan_event_id"):
        return "plan_event"
    if item.get("execution_request_id"):
        return "request_evidence"
    return "budget_evidence"
