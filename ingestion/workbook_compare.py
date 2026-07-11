from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

from ingestion.models import SheetProfile, WorkbookProfile
from ingestion.schema_maps import normalize_header

RENAME_CANDIDATE_THRESHOLD = 0.78


@dataclass(frozen=True)
class RenameCandidate:
    raw_column: str
    cleaned_column: str
    similarity: float

    def to_json(self) -> dict[str, Any]:
        return {
            "raw_column": self.raw_column,
            "cleaned_column": self.cleaned_column,
            "similarity": round(self.similarity, 3),
        }


@dataclass(frozen=True)
class WorkbookComparison:
    raw_filename: str
    cleaned_filename: str
    raw_sheet: str
    cleaned_sheet: str
    shared_columns: list[str]
    raw_only_columns: list[str]
    cleaned_only_columns: list[str]
    normalized_header_matches: list[dict[str, str]]
    rename_candidates: list[RenameCandidate]
    mapped_canonical_fields: dict[str, dict[str, str | None]]
    action_required_columns: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return {
            "raw_filename": self.raw_filename,
            "cleaned_filename": self.cleaned_filename,
            "raw_sheet": self.raw_sheet,
            "cleaned_sheet": self.cleaned_sheet,
            "shared_columns": self.shared_columns,
            "raw_only_columns": self.raw_only_columns,
            "cleaned_only_columns": self.cleaned_only_columns,
            "normalized_header_matches": self.normalized_header_matches,
            "rename_candidates": [candidate.to_json() for candidate in self.rename_candidates],
            "mapped_canonical_fields": self.mapped_canonical_fields,
            "action_required_columns": self.action_required_columns,
        }


def compare_workbook_profiles(
    raw_profile: WorkbookProfile,
    cleaned_profile: WorkbookProfile,
) -> WorkbookComparison:
    raw_sheet = _select_sheet(raw_profile)
    cleaned_sheet = _select_sheet(cleaned_profile)

    raw_columns = _non_empty_columns(raw_sheet)
    cleaned_columns = _non_empty_columns(cleaned_sheet)
    raw_by_normalized = _columns_by_normalized(raw_columns)
    cleaned_by_normalized = _columns_by_normalized(cleaned_columns)

    shared_keys = sorted(set(raw_by_normalized).intersection(cleaned_by_normalized))
    raw_only_keys = sorted(set(raw_by_normalized).difference(cleaned_by_normalized))
    cleaned_only_keys = sorted(set(cleaned_by_normalized).difference(raw_by_normalized))

    raw_only_columns = [raw_by_normalized[key] for key in raw_only_keys]
    cleaned_only_columns = [cleaned_by_normalized[key] for key in cleaned_only_keys]

    normalized_header_matches = [
        {
            "normalized_header": key,
            "raw_column": raw_by_normalized[key],
            "cleaned_column": cleaned_by_normalized[key],
        }
        for key in shared_keys
        if raw_by_normalized[key] != cleaned_by_normalized[key]
    ]

    rename_candidates = _rename_candidates(raw_only_columns, cleaned_only_columns)
    action_required_columns = sorted({*raw_only_columns, *cleaned_only_columns})
    mapped_canonical_fields = _mapped_canonical_fields(raw_sheet, cleaned_sheet)

    return WorkbookComparison(
        raw_filename=raw_profile.original_filename,
        cleaned_filename=cleaned_profile.original_filename,
        raw_sheet=raw_sheet.sheet_name,
        cleaned_sheet=cleaned_sheet.sheet_name,
        shared_columns=[raw_by_normalized[key] for key in shared_keys],
        raw_only_columns=raw_only_columns,
        cleaned_only_columns=cleaned_only_columns,
        normalized_header_matches=normalized_header_matches,
        rename_candidates=rename_candidates,
        mapped_canonical_fields=mapped_canonical_fields,
        action_required_columns=action_required_columns,
    )


def _select_sheet(profile: WorkbookProfile) -> SheetProfile:
    if profile.canonical_sheets:
        canonical = {name.lower() for name in profile.canonical_sheets}
        for sheet in profile.sheets:
            if sheet.sheet_name.lower() in canonical:
                return sheet
    if not profile.sheets:
        raise ValueError(f"Workbook has no sheets: {profile.original_filename}")
    return profile.sheets[0]


def _non_empty_columns(sheet: SheetProfile) -> list[str]:
    return [column for column in sheet.column_names if column and column.strip()]


def _columns_by_normalized(columns: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for column in columns:
        normalized = normalize_header(column)
        if normalized and normalized not in result:
            result[normalized] = column
    return result


def _rename_candidates(
    raw_only_columns: list[str], cleaned_only_columns: list[str]
) -> list[RenameCandidate]:
    candidates: list[RenameCandidate] = []
    for raw_column in raw_only_columns:
        raw_normalized = normalize_header(raw_column)
        for cleaned_column in cleaned_only_columns:
            cleaned_normalized = normalize_header(cleaned_column)
            similarity = SequenceMatcher(None, raw_normalized, cleaned_normalized).ratio()
            if similarity >= RENAME_CANDIDATE_THRESHOLD:
                candidates.append(
                    RenameCandidate(
                        raw_column=raw_column,
                        cleaned_column=cleaned_column,
                        similarity=similarity,
                    )
                )
    return sorted(candidates, key=lambda candidate: (-candidate.similarity, candidate.raw_column))


def _mapped_canonical_fields(
    raw_sheet: SheetProfile,
    cleaned_sheet: SheetProfile,
) -> dict[str, dict[str, str | None]]:
    canonical_fields = sorted(set(raw_sheet.mapped_columns).union(cleaned_sheet.mapped_columns))
    return {
        field: {
            "raw_column": raw_sheet.mapped_columns.get(field),
            "cleaned_column": cleaned_sheet.mapped_columns.get(field),
        }
        for field in canonical_fields
    }
