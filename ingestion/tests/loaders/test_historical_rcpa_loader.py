from pathlib import Path

from ingestion.loaders.historical_rcpa import load_historical_rcpa
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_historical_rcpa_loader_captures_prescription_identity_and_provenance() -> None:
    build()
    result = load_historical_rcpa(
        profile_path(Path("ingestion/tests/fixtures/xlsx/historical_rcpa_observed.xlsx"))
    )

    assert result.rows_seen == 3
    assert result.rows_loaded > 0
    doctor_month = sorted(result.records, key=lambda row: str(row["pcode_normalized"]))
    assert doctor_month[0]["country"] == "Nepal"
    assert doctor_month[0]["pcode_normalized"] == "NP001"
    assert doctor_month[0]["patch_name"] == "Patch C"
    assert doctor_month[0]["mapping_provenance"] == "source_supplied"
    assert doctor_month[1]["pcode_normalized"] == "SL001"
    assert doctor_month[1]["mapping_provenance"] == "manual_legacy"
    assert doctor_month[2]["pcode_normalized"] == "SL002"
    assert doctor_month[2]["mapping_provenance"] == "system_supplied"
    assert result.summaries["mapping_provenance_counts"] == {
        "source_supplied": 1,
        "manual_legacy": 1,
        "system_supplied": 1,
    }


def test_historical_rcpa_loader_preserves_brand_and_competitor_metadata() -> None:
    build()
    result = load_historical_rcpa(
        profile_path(Path("ingestion/tests/fixtures/xlsx/historical_rcpa_observed.xlsx"))
    )

    brand_rows = result.summaries["rcpa_doctor_brand_summary"]
    assert {row["brand_group"] for row in brand_rows} == {"Cipla Brand", "Competitor Brand"}
    assert {row["own_or_competitor"] for row in brand_rows} == {"own", "competitor"}
    assert any(
        row["competitor_filter_note"] == "Competitor prescription row retained from source."
        for row in result.records
    )
