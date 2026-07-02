from pathlib import Path


def test_budget_view_flags_btu_btc_reconciliation_states() -> None:
    sql = Path("database/views/mv_budget_utilization.sql").read_text(encoding="utf-8")

    for fragment in [
        "btu_btc_reconciliation_status",
        "missing_total_actual",
        "missing_btu_btc_split",
        "reconciled",
        "mismatch",
        "btu_btc_delta_local",
        "btu_btc_delta_usd",
    ]:
        assert fragment in sql

    assert "actual_btu_expense_local" in sql
    assert "actual_btc_expense_local" in sql
    assert "actual_total_expense_local" in sql
