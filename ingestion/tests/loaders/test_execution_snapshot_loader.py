from pathlib import Path

from ingestion.loaders.execution_snapshot import load_execution_snapshot
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_execution_loader_maps_may_status_values() -> None:
    build()
    result = load_execution_snapshot(profile_path(Path("ingestion/tests/fixtures/xlsx/execution_may_tiny.xlsx")))

    assert result.rows_loaded == 1
    assert result.records[0]["normalized_status"] == "executed"
    assert result.records[0]["country"] == "Nepal"

