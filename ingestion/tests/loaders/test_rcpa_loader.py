from pathlib import Path

from ingestion.loaders.rcpa import load_rcpa
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_rcpa_loader_aggregates_alias_mapped_rows() -> None:
    build()
    result = load_rcpa(profile_path(Path("ingestion/tests/fixtures/xlsx/rcpa_tiny.xlsx")))

    assert result.rows_loaded == 1
    assert result.records[0]["pcode_normalized"] == "00123"
    assert result.records[0]["own_or_competitor"] == "own"
    assert result.records[0]["currency_code"] == "LKR"
    assert result.records[0]["speciality"] == "Cardiology"
    assert result.records[0]["doctor_class"] == "A"
    assert result.records[0]["patch_name"] == "Colombo 1"
    assert result.records[0]["active_status"] == "Active"
    assert result.records[0]["sku_detail"] == "SKU A"
