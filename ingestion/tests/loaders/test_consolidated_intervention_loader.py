from pathlib import Path

from ingestion.loaders.consolidated_intervention import load_consolidated_intervention
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_consolidated_intervention_loader_extracts_observed_fields() -> None:
    build()
    result = load_consolidated_intervention(
        profile_path(Path("ingestion/tests/fixtures/xlsx/consolidated_intervention_observed.xlsx"))
    )

    assert result.rows_loaded == 2
    first = result.records[0]
    assert first["req_id"] == "REQ-SP-1"
    assert first["fs_hq"] == "Colombo HQ"
    assert first["intervention_type"] == "International Conference"
    assert first["intervention_sub_type"] == "ERS"
    assert first["actual_total_expense_local"] == 2200
    assert first["actual_btu_expense_local"] == 1000
    assert first["actual_btc_expense_local"] == 1200
    assert first["total_btc_local"] == 1200
    assert first["expected_btu_local"] == 800
    assert first["association_contract_id"] == "C-001"
    assert result.summaries["request_doctors"][0]["pcode_normalized"] == "P001"
