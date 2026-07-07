from pathlib import Path

from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build
from ingestion.workbook_compare import compare_workbook_profiles


def test_compare_reports_shared_raw_only_cleaned_only_and_normalized_matches() -> None:
    build()
    raw_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    cleaned_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_cleaned.xlsx"))

    comparison = compare_workbook_profiles(raw_profile, cleaned_profile)

    assert "DIVISION" in comparison.shared_columns
    assert "Raw Only Field" in comparison.raw_only_columns
    assert "Cleaned Only Field" in comparison.cleaned_only_columns
    assert {
        "normalized_header": "division",
        "raw_column": "DIVISION",
        "cleaned_column": "Division",
    } in comparison.normalized_header_matches


def test_compare_reports_rename_candidates_and_action_required_columns() -> None:
    build()
    raw_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    cleaned_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_cleaned.xlsx"))

    comparison = compare_workbook_profiles(raw_profile, cleaned_profile)

    assert any(
        candidate.raw_column == "Doctor Sponsorship Remark"
        and candidate.cleaned_column == "Doctor Sponsorship Notes"
        for candidate in comparison.rename_candidates
    )
    assert "Raw Only Field" in comparison.action_required_columns
    assert "Cleaned Only Field" in comparison.action_required_columns
    assert comparison.mapped_canonical_fields["req_id"]["raw_column"] == "REQ_ID"
    assert comparison.mapped_canonical_fields["req_id"]["cleaned_column"] == "Request ID"
