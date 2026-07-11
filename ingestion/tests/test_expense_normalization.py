from ingestion.normalizers.expenses import normalize_expenses


def test_expense_normalization_reconciles_btu_btc_to_total() -> None:
    expenses = normalize_expenses(btu_expense=100, btc_expense=40, total_expense=140)

    assert expenses.btu_expense_local == 100
    assert expenses.btc_expense_local == 40
    assert expenses.total_expense_local == 140
    assert expenses.reconciliation_status == "reconciled"


def test_expense_normalization_derives_total_when_missing() -> None:
    expenses = normalize_expenses(btu_expense=100, btc_expense=40)

    assert expenses.total_expense_local == 140
    assert expenses.reconciliation_status == "reconciled"


def test_expense_normalization_flags_mismatch() -> None:
    expenses = normalize_expenses(btu_expense=100, btc_expense=40, total_expense=150)

    assert expenses.reconciliation_status == "mismatch"
