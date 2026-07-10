from pathlib import Path

from ingestion.loaders.doctor_wise_intervention import load_doctor_wise_intervention
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_doctor_wise_loader_extracts_engagement_economics() -> None:
    build()
    result = load_doctor_wise_intervention(
        profile_path(Path("ingestion/tests/fixtures/xls/doctor_wise_intervention_observed.xls"))
    )

    assert result.rows_loaded == 2
    first = result.records[0]
    assert first["country"] == "Sri Lanka"
    assert first["intervention_id"] == "REQ-SP-1"
    assert first["doctor_name"] == "Dr Alpha"
    assert first["pcode_normalized"] == "P001"
    assert first["doctor_segment"] == "A"
    assert first["intervention_type"] == "International Conference"
    assert first["fmv_amount_local"] == 3000
    assert first["contracted_amount_local"] == 2400
    assert first["contract_saving_local"] == 600
    assert first["is_sponsorship"] is True
    assert first["sponsorship_class"] == "international_conference"
    assert first["engagement_class"] == "conference"
    assert first["currency_code"] == "LKR"
    assert first["fx_rate_status"] == "official"
    assert first["source_sheet_name"] == "HTML Table 1"


def test_doctor_wise_loader_flags_missing_contracted_value_without_zeroing() -> None:
    build()
    result = load_doctor_wise_intervention(
        profile_path(Path("ingestion/tests/fixtures/xls/doctor_wise_intervention_observed.xls"))
    )

    second = result.records[1]
    assert second["intervention_type"] == "No Fee Agreement"
    assert second["is_sponsorship"] is False
    assert second["engagement_class"] == "no_fee"
    assert second["contracted_amount_local"] is None
    assert second["contract_saving_local"] is None
    assert result.summaries["missing_contracted_value_count"] == 1
