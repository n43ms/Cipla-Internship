from __future__ import annotations

import hashlib
from pathlib import Path

from ingestion.models import SourceFile


SUPPORTED_EXTENSIONS = {".xlsx", ".xlsb"}


def calculate_file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_data_path(path: Path) -> None:
    normalized = {part.lower() for part in path.parts}
    if "data" not in normalized or "raw" not in normalized:
        raise ValueError(f"Raw workbook path must be under data/raw: {path}")


def infer_country_scope(filename: str) -> str | None:
    lower = filename.lower()
    countries: list[str] = []
    if "nepal" in lower:
        countries.append("Nepal")
    if "sri lanka" in lower or "srilanka" in lower:
        countries.append("Sri Lanka")
    if "myanmar" in lower:
        countries.append("Myanmar")
    if "oman" in lower:
        countries.append("Oman")
    if "uae" in lower:
        countries.append("UAE")
    if "malaysia" in lower:
        countries.append("Malaysia")
    return ", ".join(countries) if countries else None


def infer_source_type(filename: str) -> str:
    lower = filename.lower()
    if "rcpa" in lower:
        return "rcpa"
    if "consolidation" in lower:
        return "consolidation"
    if "execution" in lower or "executiion" in lower or "yp planner" in lower:
        return "execution_snapshot"
    if "yearly planner" in lower or "planner" in lower or "fy27" in lower:
        return "planner"
    return "unknown"


def discover_source_files(data_dir: Path, *, require_gitignored_path: bool = True) -> list[SourceFile]:
    if not data_dir.exists():
        return []
    discovered: list[SourceFile] = []
    seen_hashes: set[str] = set()
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if path.name.startswith("~$"):
            continue
        if require_gitignored_path:
            validate_data_path(path)
        file_hash = calculate_file_hash(path)
        if file_hash in seen_hashes:
            continue
        seen_hashes.add(file_hash)
        discovered.append(
            SourceFile(
                path=path,
                original_filename=path.name,
                file_hash=file_hash,
                file_type=path.suffix.lower().lstrip("."),
                source_type=infer_source_type(path.name),
                country_scope=infer_country_scope(path.name),
            )
        )
    return discovered
