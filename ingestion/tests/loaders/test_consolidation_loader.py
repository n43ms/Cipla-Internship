from pathlib import Path

from ingestion.loaders.consolidation import load_consolidation
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_consolidation_loader_extracts_working_sheet_request() -> None:
    build()
    result = load_consolidation(profile_path(Path("ingestion/tests/fixtures/xlsx/consolidation_tiny.xlsx")))

    assert result.rows_loaded == 1
    assert result.records[0]["req_id"] == "REQ-1"
    assert result.records[0]["currency_code"] == "LKR"

