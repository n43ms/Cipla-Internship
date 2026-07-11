from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.models import SheetData, WorkbookData


def _clean_cell(value: Any) -> Any:
    if pd.isna(value):
        return None
    return value


class _HtmlTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._current_table = []
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._current_cell is not None:
            if self._current_row is not None:
                self._current_row.append(" ".join("".join(self._current_cell).split()))
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None:
            if self._current_table is not None:
                self._current_table.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._current_table is not None:
            self.tables.append(self._current_table)
            self._current_table = None


def read_html_workbook(path: Path) -> WorkbookData:
    parser = _HtmlTableParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    sheets = [
        SheetData(name=f"HTML Table {index}", rows=rows)
        for index, rows in enumerate(parser.tables, start=1)
    ]
    return WorkbookData(path=path, sheets=sheets, reader_engine="html_parser")


def _read_with_engine(path: Path, engine: str) -> WorkbookData:
    workbook = pd.ExcelFile(path, engine=engine)
    sheets: list[SheetData] = []
    for sheet_name in workbook.sheet_names:
        frame = pd.read_excel(workbook, sheet_name=sheet_name, header=None, dtype=object)
        rows = [[_clean_cell(value) for value in row] for row in frame.to_numpy().tolist()]
        while rows and all(value is None for value in rows[-1]):
            rows.pop()
        sheets.append(SheetData(name=sheet_name, rows=rows))
    return WorkbookData(path=path, sheets=sheets, reader_engine=engine)


def read_workbook(path: Path) -> WorkbookData:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return _read_with_engine(path, "openpyxl")
    if suffix == ".xlsb":
        try:
            return _read_with_engine(path, "calamine")
        except Exception:
            return _read_with_engine(path, "pyxlsb")
    if suffix == ".xls":
        with path.open("rb") as file:
            prefix = file.read(128).lstrip().lower()
        if prefix.startswith(b"<html"):
            return read_html_workbook(path)
    raise ValueError(f"Unsupported workbook extension: {path.suffix}")

