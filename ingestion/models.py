from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


CellValue = str | int | float | bool | date | None


@dataclass(frozen=True)
class SourceFile:
    path: Path
    original_filename: str
    file_hash: str
    file_type: str
    source_type: str
    country_scope: str | None = None
    period_start: date | None = None
    period_end: date | None = None


@dataclass(frozen=True)
class SheetData:
    name: str
    rows: list[list[CellValue]]


@dataclass(frozen=True)
class WorkbookData:
    path: Path
    sheets: list[SheetData]
    reader_engine: str


@dataclass(frozen=True)
class HeaderMatch:
    row_index: int | None
    headers: list[str]
    canonical_columns: dict[str, int]
    required_coverage: float
    score: int


@dataclass(frozen=True)
class SheetProfile:
    sheet_name: str
    row_count: int
    column_count: int
    used_range: str
    likely_header_row: int | None
    likely_data_start_row: int | None
    column_names: list[str]
    required_column_coverage: float
    sample_rows: list[list[str | None]]
    anomalies: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WorkbookProfile:
    path: Path
    original_filename: str
    file_hash: str
    file_type: str
    source_type: str
    country_scope: str | None
    detected_sheet_count: int
    canonical_sheets: list[str]
    sheets: list[SheetProfile]
    warnings: list[str] = field(default_factory=list)

    @property
    def total_rows_seen(self) -> int:
        return sum(sheet.row_count for sheet in self.sheets)

    def to_json(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "original_filename": self.original_filename,
            "file_hash": self.file_hash,
            "file_type": self.file_type,
            "source_type": self.source_type,
            "country_scope": self.country_scope,
            "detected_sheet_count": self.detected_sheet_count,
            "canonical_sheets": self.canonical_sheets,
            "warnings": self.warnings,
            "sheets": [
                {
                    "sheet_name": sheet.sheet_name,
                    "row_count": sheet.row_count,
                    "column_count": sheet.column_count,
                    "used_range": sheet.used_range,
                    "likely_header_row": sheet.likely_header_row,
                    "likely_data_start_row": sheet.likely_data_start_row,
                    "column_names": sheet.column_names,
                    "required_column_coverage": sheet.required_column_coverage,
                    "sample_rows": sheet.sample_rows,
                    "anomalies": sheet.anomalies,
                }
                for sheet in self.sheets
            ],
        }


@dataclass(frozen=True)
class ParseResult:
    value: Any
    raw_value: Any
    status: str
    message: str | None = None


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    error_code: str
    message: str
    entity_type: str | None = None
    field_name: str | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    raw_value: str | None = None


@dataclass(frozen=True)
class LoadResult:
    source_type: str
    rows_seen: int
    rows_loaded: int
    rows_skipped: int
    records: list[dict[str, Any]]
    issues: list[ValidationIssue]
    summaries: dict[str, Any] = field(default_factory=dict)


def to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        return None
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"nan", "none", "null", "-"}:
        return None
    try:
        return Decimal(text)
    except Exception:
        return None


def to_int(value: Any) -> int | None:
    decimal_value = to_decimal(value)
    if decimal_value is None:
        return None
    return int(decimal_value)

