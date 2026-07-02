from pathlib import Path

from ingestion.loaders.consolidation import load_consolidation
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_consolidation_loader_extracts_working_sheet_request() -> None:
    build()
    result = load_consolidation(profile_path(Path("ingestion/tests/fixtures/xlsx/consolidation_tiny.xlsx")))

    assert result.rows_loaded == 1
    record = result.records[0]
    assert record["req_id"] == "REQ-1"
    assert record["currency_code"] == "LKR"
    assert record["fx_rate_status"] == "official"
    assert str(record["fx_rate_to_usd"]).startswith("0.003225")
    assert record["confirmed_contracted_amount_usd"].to_eng_string() == "100.00"
    assert record["direct_hcp_spend_local"] == record["actual_btu_expense_local"]
    assert record["overhead_spend_local"] == record["actual_btc_expense_local"]
    assert record["total_roi_spend_local"] == record["actual_total_expense_local"]
    assert record["city"] == "Colombo"
