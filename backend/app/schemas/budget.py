from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from backend.app.schemas.meta import ApiModel, ResponseMeta


class BudgetGapRow(ApiModel):
    event_name: str | None = None
    event_type: str | None = None
    country: str
    month: str
    match_status: str
    planned_budget_usd: Decimal | None = None
    estimated_intervention_local: Decimal | None = None
    confirmed_contracted_amount_local: Decimal | None = None
    actual_total_expense_local: Decimal | None = None
    direct_hcp_btu_spend_local: Decimal | None = None
    overhead_btc_spend_local: Decimal | None = None
    actual_total_expense_usd: Decimal | None = None
    unspent_gap_usd: Decimal | None = None
    overrun_amount_usd: Decimal | None = None
    currency_code: str | None = None
    fx_rate_status: str
    btu_btc_reconciliation_status: str
    spend_without_plan: bool
    plan_without_spend: bool
    scope_status: str | None = None


class BudgetSummary(ApiModel):
    meta: ResponseMeta
    planned_budget_usd: Decimal = Decimal("0")
    estimated_intervention_local: Decimal = Decimal("0")
    estimated_intervention_usd: Decimal = Decimal("0")
    confirmed_contracted_amount_local: Decimal = Decimal("0")
    confirmed_contracted_amount_usd: Decimal = Decimal("0")
    confirmed_vs_estimated_variance_local: Decimal = Decimal("0")
    confirmed_vs_estimated_variance_usd: Decimal = Decimal("0")
    direct_hcp_btu_spend_local: Decimal = Decimal("0")
    direct_hcp_btu_spend_usd: Decimal = Decimal("0")
    overhead_btc_spend_local: Decimal = Decimal("0")
    overhead_btc_spend_usd: Decimal = Decimal("0")
    actual_total_spend_local: Decimal = Decimal("0")
    actual_total_spend_usd: Decimal = Decimal("0")
    association_amount_local: Decimal = Decimal("0")
    unspent_gap_usd: Decimal = Decimal("0")
    overrun_amount_usd: Decimal = Decimal("0")
    plan_without_spend_count: int = 0
    spend_without_plan_count: int = 0
    btu_btc_reconciliation_issue_count: int = 0
    missing_fx_count: int = 0
    provisional_fx_count: int = 0
    currency_codes: list[str] = Field(default_factory=list)
    fx_rate_statuses: list[str] = Field(default_factory=list)
    rows: list[BudgetGapRow] = Field(default_factory=list)
