from pathlib import Path

from ingestion.loaders.rcpa import load_rcpa
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_rcpa_loader_aggregates_alias_mapped_rows() -> None:
    build()
    result = load_rcpa(profile_path(Path("ingestion/tests/fixtures/xlsx/rcpa_tiny.xlsx")))

    assert result.rows_loaded == 3
    assert result.records[0]["pcode_normalized"] == "00123"
    assert result.records[0]["own_prescription_qty"] == 10
    assert result.records[0]["currency_code"] == "LKR"
    assert result.records[0]["speciality"] == "Cardiology"
    assert result.records[0]["doctor_class"] == "A"
    assert result.records[0]["patch_name"] == "Colombo 1"
    assert result.records[0]["active_status"] == "Active"
    assert result.summaries["rcpa_detail_record_count"] == 1
    assert result.summaries["rcpa_detail_records"][0]["sku_detail"] == "SKU A"
    assert result.summaries["rcpa_doctor_brand_summary"][0]["brand_group"] == "Cipla Brand"
    assert result.summaries["rcpa_country_brand_month_summary"][0]["prescription_qty"] == 10
