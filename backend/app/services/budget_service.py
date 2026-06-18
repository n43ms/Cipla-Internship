from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.repositories.budget_repository import BudgetRepository
from backend.app.schemas.budget import BudgetGapRow, BudgetSummary
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
    ) -> BudgetSummary:
        validate_country_month_filters(self.session, country=country, month=month)
        data = self.repository.summary(country, month, include_out_of_scope)
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
                scope_status=item.get("scope_status"),
            )
            for item in data["rows"]
        ]
        return BudgetSummary(
            meta=build_meta(
                self.session,
                filters_applied=_filters(country=country, month=month, includeOutOfScope=include_out_of_scope),
                flags=flags,
                limitations=limitations,
            ),
            planned_budget_usd=_decimal(row.get("planned_budget_usd")),
            estimated_intervention_local=_decimal(row.get("estimated_intervention_local")),
            estimated_intervention_usd=_decimal(row.get("estimated_intervention_usd")),
            confirmed_contracted_amount_local=_decimal(row.get("confirmed_contracted_amount_local")),
            confirmed_contracted_amount_usd=_decimal(row.get("confirmed_contracted_amount_usd")),
            confirmed_vs_estimated_variance_local=_decimal(row.get("confirmed_vs_estimated_variance_local")),
            confirmed_vs_estimated_variance_usd=_decimal(row.get("confirmed_vs_estimated_variance_usd")),
            direct_hcp_btu_spend_local=_decimal(row.get("direct_hcp_btu_spend_local")),
            direct_hcp_btu_spend_usd=_decimal(row.get("direct_hcp_btu_spend_usd")),
            overhead_btc_spend_local=_decimal(row.get("overhead_btc_spend_local")),
            overhead_btc_spend_usd=_decimal(row.get("overhead_btc_spend_usd")),
            actual_total_spend_local=_decimal(row.get("actual_total_spend_local")),
            actual_total_spend_usd=_decimal(row.get("actual_total_spend_usd")),
            association_amount_local=_decimal(row.get("association_amount_local")),
            unspent_gap_usd=_decimal(row.get("unspent_gap_usd")),
            overrun_amount_usd=_decimal(row.get("overrun_amount_usd")),
            plan_without_spend_count=int(row.get("plan_without_spend_count") or 0),
            spend_without_plan_count=int(row.get("spend_without_plan_count") or 0),
            btu_btc_reconciliation_issue_count=int(row.get("btu_btc_reconciliation_issue_count") or 0),
            missing_fx_count=int(row.get("missing_fx_count") or 0),
            provisional_fx_count=int(row.get("provisional_fx_count") or 0),
            currency_codes=list(row.get("currency_codes") or []),
            fx_rate_statuses=list(row.get("fx_rate_statuses") or []),
            rows=mapped_rows,
        )


def _decimal(value: object) -> Decimal:
    return Decimal(str(value or 0))


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}
