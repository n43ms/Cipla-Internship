from pathlib import Path

from ingestion.tests.fixtures.build_fixtures import build
from ingestion.workbook_reader import read_workbook


def test_xlsx_reader_returns_sheet_rows() -> None:
    build()
    workbook = read_workbook(Path("ingestion/tests/fixtures/xlsx/planner_nepal_tiny.xlsx"))

    assert workbook.reader_engine == "openpyxl"
    assert workbook.sheets[0].name == "Yearly Planner FY27 v2"
    assert workbook.sheets[0].rows[0][0] == "Country"

