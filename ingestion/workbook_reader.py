from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.models import SheetData, WorkbookData


def _clean_cell(value: Any) -> Any:
    if pd.isna(value):
        return None
    return value


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
    raise ValueError(f"Unsupported workbook extension: {path.suffix}")

