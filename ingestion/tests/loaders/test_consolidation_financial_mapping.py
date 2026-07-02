from decimal import Decimal
from pathlib import Path

from ingestion.loaders.consolidation import load_consolidation
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_consolidation_financial_mapping_preserves_local_and_usd_fields() -> None:
    build()

    result = load_consolidation(profile_path(Path("ingestion/tests/fixtures/xlsx/consolidation_tiny.xlsx")))

    assert result.rows_loaded == 1
    row = result.records[0]
    assert row["estimated_intervention_local"] is not None
    assert row["confirmed_contracted_amount_local"] is not None
    assert row["confirmed_vs_estimated_variance_local"] == (
        row["confirmed_contracted_amount_local"] - row["estimated_intervention_local"]
    )
    assert row["actual_btu_expense_local"] == row["direct_hcp_spend_local"]
    assert row["actual_btc_expense_local"] == row["overhead_spend_local"]
    assert row["actual_total_expense_local"] == row["total_roi_spend_local"]
    assert "association_amount_local" in row
    assert "association_contract_id" in row
    assert row["currency_code"] == "LKR"
    assert row["fx_rate_status"] == "official"
    assert row["fx_rate_source"] == "company"
    assert row["fx_rate_to_usd"] == Decimal("1") / Decimal("310")
    assert row["confirmed_contracted_amount_usd"] == (row["confirmed_contracted_amount_local"] * row["fx_rate_to_usd"]).quantize(Decimal("0.01"))


def test_consolidation_financial_mapping_uses_btu_plus_btc_when_actual_total_missing() -> None:
    # The loader's expected semantic is explicit: if source total actual is absent but
    # BTU/BTC components exist, total actual should be calculated from the components.
    build()
    result = load_consolidation(profile_path(Path("ingestion/tests/fixtures/xlsx/consolidation_tiny.xlsx")))
    row = dict(result.records[0])

    assert row["actual_total_expense_local"] == row["actual_btu_expense_local"] + row["actual_btc_expense_local"]
