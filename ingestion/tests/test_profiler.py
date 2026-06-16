from pathlib import Path

from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_profiler_detects_source_type_header_and_canonical_sheet() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/planner_nepal_tiny.xlsx"))

    assert profile.source_type == "planner"
    assert profile.canonical_sheets == ["Yearly Planner FY27 v2"]
    assert profile.sheets[0].likely_header_row == 1
    assert profile.sheets[0].required_column_coverage == 1


def test_profiler_detects_rcpa_aliases() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/rcpa_tiny.xlsx"))

    assert profile.source_type == "rcpa"
    assert profile.canonical_sheets == ["RCPA"]
    assert profile.sheets[0].required_column_coverage >= 0.8

