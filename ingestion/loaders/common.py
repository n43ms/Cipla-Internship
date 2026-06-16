from __future__ import annotations

from typing import Any

from ingestion.models import SheetData, WorkbookProfile
from ingestion.profiler import detect_header
from ingestion.schema_maps import SourceSchema
from ingestion.workbook_reader import read_workbook


def canonical_sheet_data(profile: WorkbookProfile) -> list[SheetData]:
    workbook = read_workbook(profile.path)
    selected = {sheet.lower() for sheet in profile.canonical_sheets}
    return [sheet for sheet in workbook.sheets if sheet.name.lower() in selected]


def iter_mapped_rows(sheet: SheetData, schema: SourceSchema) -> list[tuple[int, dict[str, Any]]]:
    header = detect_header(sheet, schema)
    if header.row_index is None:
        return []
    mapped_rows: list[tuple[int, dict[str, Any]]] = []
    for row_index, row in enumerate(sheet.rows[header.row_index + 1 :], start=header.row_index + 2):
        if not any(value is not None and str(value).strip() for value in row):
            continue
        mapped: dict[str, Any] = {}
        for canonical, column_index in header.canonical_columns.items():
            mapped[canonical] = row[column_index] if column_index < len(row) else None
        mapped_rows.append((row_index, mapped))
    return mapped_rows

