from pathlib import Path

import pytest


@pytest.fixture
def temp_workbook_dir(tmp_path: Path) -> Path:
    workbook_dir = tmp_path / "workbooks"
    workbook_dir.mkdir()
    return workbook_dir


@pytest.fixture
def fixture_root() -> Path:
    return Path(__file__).parent / "fixtures"
