from pathlib import Path

import pytest

from ingestion.file_registry import calculate_file_hash, discover_source_files, validate_data_path
from ingestion.tests.fixtures.build_fixtures import build


def test_file_discovery_hashes_and_deduplicates_fixture_workbooks() -> None:
    build()
    root = Path("ingestion/tests/fixtures/xlsx")

    files = discover_source_files(root, require_gitignored_path=False)

    assert {file.source_type for file in files} >= {"planner", "execution_snapshot", "consolidation", "rcpa"}
    assert all(file.file_hash == calculate_file_hash(file.path) for file in files)
    assert len({file.file_hash for file in files}) == len(files)


def test_data_path_validation_rejects_non_raw_paths() -> None:
    with pytest.raises(ValueError):
        validate_data_path(Path("files/not-raw.xlsx"))

