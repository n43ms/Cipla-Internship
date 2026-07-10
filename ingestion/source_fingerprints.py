from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ingestion.models import SheetData, SourceFingerprint
from ingestion.schema_maps import normalize_header
from ingestion.workbook_reader import read_html_workbook, read_workbook


@dataclass(frozen=True)
class FingerprintRule:
    source_type: str
    required_headers: tuple[str, ...]
    filename_tokens: tuple[str, ...] = ()


FINGERPRINT_RULES = (
    FingerprintRule(
        source_type="consolidation",
        required_headers=(
            "division",
            "req id",
            "intervention name",
            "total actual expenses for intervention",
        ),
        filename_tokens=("consolidate", "consolidated", "consolidation"),
    ),
    FingerprintRule(
        source_type="doctor_contract",
        required_headers=(
            "division name",
            "intervention no.",
            "dr code",
            "fmv amount",
            "contracted amount",
        ),
        filename_tokens=("doctor", "dr wise"),
    ),
    FingerprintRule(
        source_type="rcpa",
        required_headers=("bu", "month", "pcode", "brand", "quantity"),
        filename_tokens=("rcpa",),
    ),
    FingerprintRule(
        source_type="msl_doctor_master",
        required_headers=("pcode", "doctor name", "bu", "location", "territory id"),
        filename_tokens=("msl", "doctor master"),
    ),
    FingerprintRule(
        source_type="ers_conference",
        required_headers=("conference",),
        filename_tokens=("ers",),
    ),
    FingerprintRule(
        source_type="cleaned_presentable",
        required_headers=("division", "intervention name"),
        filename_tokens=("cleaned", "presentable"),
    ),
)


def fingerprint_path(path: Path) -> SourceFingerprint:
    file_format = detect_file_format(path)
    warnings: list[str] = []
    try:
        sheets = _read_fingerprint_sheets(path, file_format)
    except Exception as exc:
        source_type, confidence, evidence = _score_source_type(path.name, set())
        return SourceFingerprint(
            path=path,
            file_format=file_format,
            inferred_source_type=source_type,
            confidence=confidence,
            evidence=evidence,
            warnings=[f"could not read workbook headers: {exc}"],
        )

    headers = _normalized_headers(sheets)
    source_type, confidence, evidence = _score_source_type(path.name, headers)
    if file_format == "legacy_xls":
        warnings.append("legacy .xls file is not HTML-XLS; ingestion support is not enabled")
    return SourceFingerprint(
        path=path,
        file_format=file_format,
        inferred_source_type=source_type,
        confidence=confidence,
        evidence=evidence,
        warnings=warnings,
    )


def detect_file_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return "xlsx"
    if suffix == ".xlsb":
        return "xlsb"
    if suffix == ".xls":
        with path.open("rb") as file:
            prefix = file.read(128).lstrip().lower()
        return "crm_html_xls" if prefix.startswith(b"<html") else "legacy_xls"
    return "unsupported"


def _read_fingerprint_sheets(path: Path, file_format: str) -> list[SheetData]:
    if file_format in {"xlsx", "xlsb"}:
        return read_workbook(path).sheets
    if file_format == "crm_html_xls":
        return read_html_workbook(path).sheets
    raise ValueError(f"Unsupported fingerprint format: {path.suffix}")


def _normalized_headers(sheets: list[SheetData], max_scan_rows: int = 30) -> set[str]:
    headers: set[str] = set()
    for sheet in sheets:
        for row in sheet.rows[:max_scan_rows]:
            for value in row:
                normalized = normalize_header(value)
                if normalized:
                    headers.add(normalized)
    return headers


def _score_source_type(filename: str, headers: set[str]) -> tuple[str, float, list[str]]:
    filename_normalized = normalize_header(filename)
    best_source = "unknown"
    best_score = 0.0
    best_evidence: list[str] = []
    for rule in FINGERPRINT_RULES:
        header_hits = [
            header for header in rule.required_headers if normalize_header(header) in headers
        ]
        token_hits = [
            token
            for token in rule.filename_tokens
            if normalize_header(token) in filename_normalized
        ]
        header_score = len(header_hits) / len(rule.required_headers) if rule.required_headers else 0
        token_score = min(len(token_hits), 2) * 0.4
        score = header_score + token_score
        if score > best_score:
            best_source = rule.source_type
            best_score = score
            best_evidence = [
                *(f"header:{header}" for header in header_hits),
                *(f"filename:{token}" for token in token_hits),
            ]
    if best_score < 0.4:
        return "unknown", min(best_score, 1.0), best_evidence
    return best_source, min(best_score, 1.0), best_evidence
