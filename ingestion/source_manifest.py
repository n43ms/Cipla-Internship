from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ingestion.file_registry import calculate_file_hash
from ingestion.models import (
    BatchFileValidation,
    BatchValidationResult,
    SourceManifest,
    SourceManifestEntry,
    ValidationIssue,
    to_date,
)
from ingestion.source_fingerprints import fingerprint_path

ALLOWED_RAW_OR_CLEANED = {"raw", "cleaned", "reference", "derived"}


def load_source_manifest(path: Path) -> SourceManifest:
    manifest_path = path.resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Source manifest must be a JSON object.")

    package_root = _resolve_package_root(manifest_path, data.get("received_package_path"))
    owner = _optional_text(data.get("owner"))
    files_raw = data.get("files")
    if not isinstance(files_raw, list) or not files_raw:
        raise ValueError("Source manifest must include a non-empty files array.")

    files = [
        _parse_manifest_entry(
            item,
            package_root=package_root,
            default_owner=owner,
        )
        for item in files_raw
    ]
    return SourceManifest(
        path=manifest_path,
        received_package_path=package_root,
        files=files,
        owner=owner,
    )


def validate_source_manifest(manifest: SourceManifest) -> BatchValidationResult:
    results: list[BatchFileValidation] = []
    seen_hashes: dict[str, str] = {}
    for entry in manifest.files:
        issues = _entry_shape_issues(entry)
        file_hash: str | None = None
        fingerprint = None
        if not entry.path.exists():
            issues.append(
                ValidationIssue(
                    severity="error",
                    error_code="source_file_missing",
                    message=f"Manifest file does not exist: {entry.path}",
                    entity_type="source_manifest_file",
                    field_name="path",
                    raw_value=str(entry.path),
                )
            )
        elif not entry.path.is_file():
            issues.append(
                ValidationIssue(
                    severity="error",
                    error_code="source_path_not_file",
                    message=f"Manifest path is not a file: {entry.path}",
                    entity_type="source_manifest_file",
                    field_name="path",
                    raw_value=str(entry.path),
                )
            )
        else:
            file_hash = calculate_file_hash(entry.path)
            duplicate_label = seen_hashes.get(file_hash)
            if duplicate_label:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        error_code="duplicate_file_hash",
                        message=(
                            f"File duplicates manifest label {duplicate_label}; "
                            "remove repeated uploads before profiling."
                        ),
                        entity_type="source_manifest_file",
                        field_name="path",
                        raw_value=str(entry.path),
                    )
                )
            else:
                seen_hashes[file_hash] = entry.label
            fingerprint = fingerprint_path(entry.path)
            if fingerprint.inferred_source_type != entry.source_type:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        error_code="wrong_source_type",
                        message=(
                            f"Manifest label {entry.label} declares {entry.source_type}, "
                            f"but fingerprint detected {fingerprint.inferred_source_type}."
                        ),
                        entity_type="source_manifest_file",
                        field_name="source_type",
                        raw_value=entry.source_type,
                    )
                )
        accepted = not any(issue.severity == "error" for issue in issues)
        results.append(
            BatchFileValidation(
                entry=entry,
                file_hash=file_hash,
                fingerprint=fingerprint,
                accepted=accepted,
                issues=issues,
            )
        )
    return BatchValidationResult(manifest=manifest, files=results)


def _resolve_package_root(manifest_path: Path, value: object) -> Path:
    if value is None:
        return manifest_path.parent
    root = Path(str(value))
    if not root.is_absolute():
        root = manifest_path.parent / root
    return root.resolve()


def _parse_manifest_entry(
    item: object,
    *,
    package_root: Path,
    default_owner: str | None,
) -> SourceManifestEntry:
    if not isinstance(item, dict):
        raise ValueError("Each source manifest file entry must be a JSON object.")
    label = _required_text(item, "label")
    source_type = _required_text(item, "source_type")
    raw_or_cleaned = _required_text(item, "raw_or_cleaned")
    file_path = Path(_required_text(item, "path"))
    if not file_path.is_absolute():
        file_path = package_root / file_path
    country_scope = item.get("country_scope", [])
    if isinstance(country_scope, str):
        country_scope = [country_scope]
    if not isinstance(country_scope, list) or not all(
        isinstance(country, str) for country in country_scope
    ):
        raise ValueError(f"country_scope must be a string array for manifest label {label}.")
    return SourceManifestEntry(
        label=label,
        path=file_path.resolve(),
        source_type=source_type,
        raw_or_cleaned=raw_or_cleaned,
        country_scope=tuple(country_scope),
        period_start=_parse_optional_date(item.get("period_start"), label, "period_start"),
        period_end=_parse_optional_date(item.get("period_end"), label, "period_end"),
        owner=_optional_text(item.get("owner")) or default_owner,
        export_timestamp=_parse_optional_datetime(item.get("export_timestamp"), label),
        received_package_path=package_root,
    )


def _entry_shape_issues(entry: SourceManifestEntry) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if entry.raw_or_cleaned not in ALLOWED_RAW_OR_CLEANED:
        issues.append(
            ValidationIssue(
                severity="error",
                error_code="invalid_raw_or_cleaned",
                message=(
                    "raw_or_cleaned must be one of "
                    f"{', '.join(sorted(ALLOWED_RAW_OR_CLEANED))}."
                ),
                entity_type="source_manifest_file",
                field_name="raw_or_cleaned",
                raw_value=entry.raw_or_cleaned,
            )
        )
    if entry.period_start and entry.period_end and entry.period_start > entry.period_end:
        issues.append(
            ValidationIssue(
                severity="error",
                error_code="invalid_period_scope",
                message="period_start must be on or before period_end.",
                entity_type="source_manifest_file",
                field_name="period_start",
                raw_value=str(entry.period_start),
            )
        )
    return issues


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Source manifest file entry is missing required string field: {key}.")
    return value.strip()


def _optional_text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _parse_optional_date(value: object, label: str, field_name: str):
    if value in (None, ""):
        return None
    parsed = to_date(value)
    if parsed is None:
        raise ValueError(f"Invalid {field_name} for manifest label {label}: {value}")
    return parsed


def _parse_optional_datetime(value: object, label: str) -> datetime | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError(f"Invalid export_timestamp for manifest label {label}: {value}")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid export_timestamp for manifest label {label}: {value}"
        ) from exc
