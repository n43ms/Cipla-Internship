from pathlib import Path

from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_profiler_reports_mapped_and_unknown_columns() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    sheet = profile.sheets[0]

    assert profile.source_type == "consolidation"
    assert sheet.mapped_columns["country"] == "DIVISION"
    assert sheet.mapped_columns["month"] == "Months"
    assert sheet.mapped_columns["intervention_name"] == "INTERVENTION NAME"
    assert "Raw Only Field" in sheet.unknown_columns
    assert "Doctor Sponsorship Remark" in sheet.unknown_columns


def test_profiler_reports_missing_required_and_empty_columns() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    sheet = profile.sheets[0]

    assert sheet.missing_required_columns == []
    assert "Unused Empty Field" in sheet.empty_columns


def test_profiler_reports_bounded_sample_values() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    sheet = profile.sheets[0]

    assert sheet.sample_values["country"] == ["Sri Lanka"]
    assert sheet.sample_values["Raw Only Field"] == ["raw value", "raw value 2"]
    assert len(sheet.sample_values["Doctor Sponsorship Remark"]) == 2
