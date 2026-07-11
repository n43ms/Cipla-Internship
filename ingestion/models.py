from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
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
class SourceManifestEntry:
    label: str
    path: Path
    source_type: str
    raw_or_cleaned: str
    country_scope: tuple[str, ...] = ()
    period_start: date | None = None
    period_end: date | None = None
    owner: str | None = None
    export_timestamp: datetime | None = None
    received_package_path: Path | None = None


@dataclass(frozen=True)
class SourceManifest:
    path: Path
    received_package_path: Path
    files: list[SourceManifestEntry]
    owner: str | None = None


@dataclass(frozen=True)
class SourceFingerprint:
    path: Path
    file_format: str
    inferred_source_type: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BatchFileValidation:
    entry: SourceManifestEntry
    file_hash: str | None
    fingerprint: SourceFingerprint | None
    accepted: bool
    issues: list[ValidationIssue] = field(default_factory=list)


@dataclass(frozen=True)
class BatchValidationResult:
    manifest: SourceManifest
    files: list[BatchFileValidation]

    @property
    def issues(self) -> list[ValidationIssue]:
        return [issue for file_result in self.files for issue in file_result.issues]

    @property
    def accepted_files(self) -> list[BatchFileValidation]:
        return [file_result for file_result in self.files if file_result.accepted]

    @property
    def quarantined_files(self) -> list[BatchFileValidation]:
        return [file_result for file_result in self.files if not file_result.accepted]


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
    mapped_columns: dict[str, str] = field(default_factory=dict)
    unknown_columns: list[str] = field(default_factory=list)
    missing_required_columns: list[str] = field(default_factory=list)
    empty_columns: list[str] = field(default_factory=list)
    sample_values: dict[str, list[str]] = field(default_factory=dict)
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
    period_start: date | None = None
    period_end: date | None = None
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
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
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
                    "mapped_columns": sheet.mapped_columns,
                    "unknown_columns": sheet.unknown_columns,
                    "missing_required_columns": sheet.missing_required_columns,
                    "empty_columns": sheet.empty_columns,
                    "sample_values": sheet.sample_values,
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


def to_date(value: Any) -> date | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    serial = to_decimal(value)
    if serial is not None and serial == serial.to_integral_value() and serial > 0:
        return date(1899, 12, 30) + timedelta(days=int(serial))
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "-"}:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d %b %Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def to_usd(value: Decimal | None, rate_to_usd: Decimal | None) -> Decimal | None:
    if value is None or rate_to_usd is None:
        return None
    return (value * rate_to_usd).quantize(Decimal("0.01"))
