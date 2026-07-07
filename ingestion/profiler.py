from __future__ import annotations

from pathlib import Path

from ingestion.file_registry import (
    SourceFile,
    calculate_file_hash,
    infer_country_scope,
    infer_source_type,
)
from ingestion.models import HeaderMatch, SheetData, SheetProfile, WorkbookProfile
from ingestion.schema_maps import SCHEMAS, SourceSchema, normalize_header
from ingestion.workbook_reader import read_workbook

MAX_SAMPLE_VALUES_PER_COLUMN = 3
MAX_SAMPLE_VALUE_LENGTH = 80


def _cell_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _used_range(rows: list[list[object]]) -> tuple[int, int, str]:
    non_empty_rows = [row for row in rows if any(_cell_text(value) for value in row)]
    row_count = len(non_empty_rows)
    column_count = max((len(row) for row in non_empty_rows), default=0)
    range_label = (
        f"A1:{_excel_column_name(column_count)}{row_count}"
        if row_count and column_count
        else "empty"
    )
    return row_count, column_count, range_label


def _excel_column_name(index: int) -> str:
    if index <= 0:
        return "A"
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def detect_header(sheet: SheetData, schema: SourceSchema, max_scan_rows: int = 30) -> HeaderMatch:
    lookup = schema.alias_lookup()
    best = HeaderMatch(
        row_index=None, headers=[], canonical_columns={}, required_coverage=0, score=0
    )
    for idx, row in enumerate(sheet.rows[:max_scan_rows]):
        canonical_columns: dict[str, int] = {}
        headers = [_cell_text(value) for value in row]
        for column_index, header in enumerate(headers):
            canonical = lookup.get(normalize_header(header))
            if canonical and canonical not in canonical_columns:
                canonical_columns[canonical] = column_index
        required_hits = schema.required.intersection(canonical_columns)
        score = len(canonical_columns) + (len(required_hits) * 3)
        coverage = len(required_hits) / len(schema.required) if schema.required else 1.0
        if score > best.score:
            best = HeaderMatch(
                row_index=idx,
                headers=headers,
                canonical_columns=canonical_columns,
                required_coverage=coverage,
                score=score,
            )
    return best


def classify_workbook(path: Path, sheets: list[SheetData]) -> str:
    filename_guess = infer_source_type(path.name)
    scores = {source_type: 0 for source_type in SCHEMAS}
    if filename_guess in scores:
        scores[filename_guess] += 8
    for sheet in sheets:
        for source_type, schema in SCHEMAS.items():
            if any(
                sheet.name.lower() == expected.lower() for expected in schema.canonical_sheet_names
            ):
                scores[source_type] += 4
            header = detect_header(sheet, schema)
            scores[source_type] += header.score
    return max(scores.items(), key=lambda item: item[1])[0] if any(scores.values()) else "unknown"


def _schema_drift_metadata(
    sheet: SheetData,
    header: HeaderMatch,
    schema: SourceSchema | None,
) -> tuple[dict[str, str], list[str], list[str], list[str], dict[str, list[str]]]:
    headers = header.headers
    lookup = schema.alias_lookup() if schema else {}
    mapped_columns: dict[str, str] = {}
    mapped_indexes: set[int] = set()
    unknown_columns: list[str] = []
    empty_columns: list[str] = []
    sample_values: dict[str, list[str]] = {}

    for canonical, column_index in sorted(header.canonical_columns.items()):
        mapped_indexes.add(column_index)
        mapped_columns[canonical] = (
            headers[column_index] if column_index < len(headers) else canonical
        )

    for column_index, column_name in enumerate(headers):
        if not column_name:
            continue
        normalized = normalize_header(column_name)
        if column_index not in mapped_indexes and normalized not in lookup:
            unknown_columns.append(column_name)

        values = _column_values_after_header(sheet.rows, header.row_index, column_index)
        non_empty_values = [_cell_text(value) for value in values if _cell_text(value)]
        if not non_empty_values:
            empty_columns.append(column_name)

        bounded = _bounded_sample_values(non_empty_values)
        if bounded:
            sample_key = _sample_key(column_name, column_index, header)
            sample_values[sample_key] = bounded

    missing_required_columns = (
        sorted(schema.required.difference(header.canonical_columns)) if schema else []
    )
    return mapped_columns, unknown_columns, missing_required_columns, empty_columns, sample_values


def _column_values_after_header(
    rows: list[list[object]],
    header_row_index: int | None,
    column_index: int,
) -> list[object]:
    start = (header_row_index + 1) if header_row_index is not None else 0
    values: list[object] = []
    for row in rows[start:]:
        values.append(row[column_index] if column_index < len(row) else None)
    return values


def _bounded_sample_values(values: list[str]) -> list[str]:
    samples: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        samples.append(
            normalized
            if len(normalized) <= MAX_SAMPLE_VALUE_LENGTH
            else f"{normalized[: MAX_SAMPLE_VALUE_LENGTH - 3]}..."
        )
        if len(samples) >= MAX_SAMPLE_VALUES_PER_COLUMN:
            break
    return samples


def _sample_key(column_name: str, column_index: int, header: HeaderMatch) -> str:
    for canonical, mapped_index in header.canonical_columns.items():
        if mapped_index == column_index:
            return canonical
    return column_name


def select_canonical_sheets(source_type: str, sheet_profiles: list[SheetProfile]) -> list[str]:
    names = [sheet.sheet_name for sheet in sheet_profiles]
    lowered = {name.lower(): name for name in names}
    if source_type == "planner":
        if "yearly planner fy27 v2" in lowered:
            return [lowered["yearly planner fy27 v2"]]
        if "yp fy27" in lowered:
            return [lowered["yp fy27"]]
    if source_type == "consolidation" and "working" in lowered:
        return [lowered["working"]]
    if source_type == "execution_snapshot":
        preferred = [
            name for name in names if name.lower() in {"yp", "nepal", "myanmar", "sri lanka"}
        ]
        return preferred or names[:1]
    if source_type == "rcpa":
        return [
            sheet.sheet_name
            for sheet in sheet_profiles
            if sheet.required_column_coverage >= 0.6
            or sheet.sheet_name.lower() in {"rcpa", "data", "sheet1"}
        ][:3]
    return names[:1]


def profile_source_file(source_file: SourceFile) -> WorkbookProfile:
    workbook = read_workbook(source_file.path)
    source_type = (
        source_file.source_type
        if source_file.source_type != "unknown"
        else classify_workbook(source_file.path, workbook.sheets)
    )
    schema = SCHEMAS.get(source_type)
    sheet_profiles: list[SheetProfile] = []
    warnings: list[str] = []
    for sheet in workbook.sheets:
        row_count, column_count, used_range = _used_range(sheet.rows)
        header = detect_header(sheet, schema) if schema else HeaderMatch(None, [], {}, 0, 0)
        anomalies: list[str] = []
        (
            mapped_columns,
            unknown_columns,
            missing_required_columns,
            empty_columns,
            sample_values,
        ) = _schema_drift_metadata(sheet, header, schema)
        if schema and missing_required_columns and header.score > 0:
            anomalies.append(f"missing required aliases: {', '.join(missing_required_columns)}")
        if row_count == 0:
            anomalies.append("empty sheet")
        sample_rows = [
            [_cell_text(value) or None for value in row[: min(len(row), 12)]]
            for row in sheet.rows[(header.row_index or 0) : (header.row_index or 0) + 5]
        ]
        sheet_profiles.append(
            SheetProfile(
                sheet_name=sheet.name,
                row_count=row_count,
                column_count=column_count,
                used_range=used_range,
                likely_header_row=(header.row_index + 1 if header.row_index is not None else None),
                likely_data_start_row=(
                    header.row_index + 2 if header.row_index is not None else None
                ),
                column_names=header.headers,
                required_column_coverage=header.required_coverage,
                sample_rows=sample_rows,
                mapped_columns=mapped_columns,
                unknown_columns=unknown_columns,
                missing_required_columns=missing_required_columns,
                empty_columns=empty_columns,
                sample_values=sample_values,
                anomalies=anomalies,
            )
        )
    canonical_sheets = select_canonical_sheets(source_type, sheet_profiles)
    if not canonical_sheets:
        warnings.append("no canonical sheet selected")
    return WorkbookProfile(
        path=source_file.path,
        original_filename=source_file.original_filename,
        file_hash=source_file.file_hash,
        file_type=source_file.file_type,
        source_type=source_type,
        country_scope=source_file.country_scope
        or infer_country_scope(source_file.original_filename),
        detected_sheet_count=len(workbook.sheets),
        canonical_sheets=canonical_sheets,
        sheets=sheet_profiles,
        warnings=warnings,
    )


def profile_path(path: Path) -> WorkbookProfile:
    source_file = SourceFile(
        path=path,
        original_filename=path.name,
        file_hash=calculate_file_hash(path),
        file_type=path.suffix.lower().lstrip("."),
        source_type=infer_source_type(path.name),
        country_scope=infer_country_scope(path.name),
    )
    return profile_source_file(source_file)
