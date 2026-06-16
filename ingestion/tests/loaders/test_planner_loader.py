from pathlib import Path

from ingestion.loaders.planner import load_planner
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_planner_loader_selects_nepal_canonical_sheet() -> None:
    build()
    result = load_planner(profile_path(Path("ingestion/tests/fixtures/xlsx/planner_nepal_tiny.xlsx")))

    assert result.rows_loaded == 1
    assert result.records[0]["country"] == "Nepal"
    assert result.records[0]["event_name_normalized"] == "diabetes cme"
    assert result.records[0]["planned_honorarium_hcps"] == 10
    assert result.records[0]["planned_delegate_hcps"] == 2
    assert result.records[0]["comments"] == "priority"
