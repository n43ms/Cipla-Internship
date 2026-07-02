from pathlib import Path


def test_budget_view_exposes_phase5_financial_contract() -> None:
    sql = Path("database/views/mv_budget_utilization.sql").read_text(encoding="utf-8")

    required_fragments = [
        "planned_budget_usd",
        "estimated_intervention_local",
        "estimated_intervention_usd",
        "confirmed_contracted_amount_local",
        "confirmed_contracted_amount_usd",
        "confirmed_vs_estimated_variance_local",
        "confirmed_vs_estimated_variance_usd",
        "direct_hcp_btu_spend_local",
        "overhead_btc_spend_local",
        "actual_total_expense_local",
        "actual_total_expense_usd",
        "association_amount_local",
        "unspent_gap_usd",
        "overrun_amount_usd",
        "missing_fx",
        "provisional_fx",
        "spend_without_plan",
        "plan_without_spend",
    ]

    for fragment in required_fragments:
        assert fragment in sql


def test_budget_view_does_not_treat_estimated_intervention_as_actual_spend() -> None:
    sql = Path("database/views/mv_budget_utilization.sql").read_text(encoding="utf-8")

    assert "er.estimated_intervention_local" in sql
    assert "er.actual_total_expense_local" in sql
    assert "er.actual_btu_expense_local" in sql
    assert "er.actual_btc_expense_local" in sql
    assert "unspent_gap_usd" in sql
    assert "er.actual_total_expense_usd" in sql
