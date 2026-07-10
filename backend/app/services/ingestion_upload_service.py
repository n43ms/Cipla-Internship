from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email import policy
from email.parser import BytesParser
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, Request

from backend.app.config import get_settings
from backend.app.schemas.ingestion_upload import (
    BatchIngestionStatusResponse,
    UploadBatchResponse,
    UploadFileResult,
)
from ingestion.file_registry import calculate_file_hash
from ingestion.models import SourceFile
from ingestion.orchestrator import ingest_manifest_batch
from ingestion.profiler import profile_source_file
from ingestion.source_fingerprints import detect_file_format, fingerprint_path

SUPPORTED_UPLOAD_EXTENSIONS = {".xlsx", ".xlsb", ".xls"}
MAX_UPLOAD_BYTES = 80 * 1024 * 1024


@dataclass(frozen=True)
class UploadedFilePart:
    filename: str
    content: bytes


async def validate_uploaded_batch(request: Request) -> UploadBatchResponse:
    files = await _parse_multipart_files(request)
    if not files:
        raise HTTPException(status_code=400, detail="Select at least one Excel file to upload.")

    batch_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + f"-{uuid4().hex[:8]}"
    batch_dir = Path(get_settings().upload_data_dir) / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    seen_hashes: dict[str, str] = {}
    results: list[UploadFileResult] = []
    manifest_files: list[dict[str, object]] = []

    for file_part in files:
        result, manifest_entry = _validate_file_part(file_part, batch_dir, seen_hashes)
        results.append(result)
        if manifest_entry is not None:
            manifest_files.append(manifest_entry)

    manifest_path = batch_dir / "source-manifest.json"
    if manifest_files:
        manifest_path.write_text(
            json.dumps(
                {
                    "received_package_path": ".",
                    "owner": "dashboard_upload",
                    "files": manifest_files,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    accepted_count = sum(1 for result in results if result.status == "accepted")
    response = UploadBatchResponse(
        batch_id=batch_id,
        refresh_state="validated" if accepted_count else "quarantined",
        total_files=len(results),
        accepted_count=accepted_count,
        quarantined_count=len(results) - accepted_count,
        manifest_path=str(manifest_path) if manifest_files else None,
        files=results,
        next_steps=_next_steps(accepted_count, len(results) - accepted_count),
    )
    summary_path = batch_dir / "batch-upload-summary.json"
    summary_path.write_text(response.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
    _write_batch_status(
        batch_dir,
        BatchIngestionStatusResponse(
            batch_id=batch_id,
            refresh_state="accepted_for_ingestion" if accepted_count else "quarantined",
            accepted_count=accepted_count,
            quarantined_count=len(results) - accepted_count,
            manifest_path=str(manifest_path) if manifest_files else None,
            summary_path=str(summary_path),
            message=(
                "Batch passed intake validation and is ready for ingestion."
                if accepted_count
                else "Batch has no accepted files and cannot be ingested."
            ),
            next_steps=_next_steps(accepted_count, len(results) - accepted_count),
        ),
    )
    return response.model_copy(update={"summary_path": str(summary_path)})


def get_batch_ingestion_status(batch_id: str) -> BatchIngestionStatusResponse:
    batch_dir = _batch_dir(batch_id)
    status_path = _batch_status_path(batch_dir)
    if not status_path.exists():
        raise HTTPException(status_code=404, detail="Upload batch was not found.")
    return BatchIngestionStatusResponse.model_validate_json(status_path.read_text(encoding="utf-8"))


def run_batch_ingestion(batch_id: str) -> BatchIngestionStatusResponse:
    batch_dir = _batch_dir(batch_id)
    status = get_batch_ingestion_status(batch_id)
    if status.accepted_count == 0 or not status.manifest_path:
        raise HTTPException(status_code=409, detail="Batch has no accepted files to ingest.")
    if status.refresh_state in {"ingestion_running"}:
        raise HTTPException(status_code=409, detail="Batch ingestion is already running.")
    if status.refresh_state in {"supabase_written", "views_refreshed", "dashboard_refreshed"}:
        return status

    running_status = status.model_copy(
        update={
            "refresh_state": "ingestion_running",
            "message": "Ingestion is running. Accepted files are being loaded into Supabase.",
            "next_steps": ["Wait for Supabase write and materialized-view refresh to finish."],
        }
    )
    _write_batch_status(batch_dir, running_status)
    try:
        summary = ingest_manifest_batch(Path(status.manifest_path))
    except Exception as exc:
        failed = running_status.model_copy(
            update={
                "refresh_state": "ingestion_failed",
                "message": "Ingestion failed before the dashboard could refresh.",
                "next_steps": [str(exc)],
            }
        )
        _write_batch_status(batch_dir, failed)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    completed = running_status.model_copy(
        update={
            "refresh_state": "views_refreshed",
            "ingestion_run_id": summary.ingestion_run_id,
            "rows_seen": summary.rows_seen,
            "rows_loaded": summary.rows_loaded,
            "rows_skipped": summary.rows_skipped,
            "warning_count": summary.warning_count,
            "error_count": summary.error_count,
            "message": "Supabase facts were written and materialized views were refreshed.",
            "next_steps": [
                "Refresh the dashboard pages to see updated Doctor ROI evidence.",
                "Review Data Quality for join, P-code, missing amount, and RCPA caveats.",
            ],
        }
    )
    _write_batch_status(batch_dir, completed)
    return completed


def _validate_file_part(
    file_part: UploadedFilePart,
    batch_dir: Path,
    seen_hashes: dict[str, str],
) -> tuple[UploadFileResult, dict[str, object] | None]:
    safe_name = _safe_filename(file_part.filename)
    suffix = Path(safe_name).suffix.lower()
    target_path = _unique_target_path(batch_dir, safe_name)
    saved_name = target_path.name
    reasons: list[str] = []
    warnings: list[str] = []

    if suffix not in SUPPORTED_UPLOAD_EXTENSIONS:
        return (
            UploadFileResult(
                original_filename=file_part.filename,
                saved_filename=None,
                status="quarantined",
                source_type="unknown",
                file_format="unsupported",
                reasons=["Only .xlsx, .xlsb, and CRM HTML .xls Excel files are supported."],
            ),
            None,
        )

    target_path.write_bytes(file_part.content)
    file_hash = calculate_file_hash(target_path)
    duplicate_of = seen_hashes.get(file_hash)
    if duplicate_of:
        reasons.append(f"Duplicate of {duplicate_of}. Upload each workbook once.")
    else:
        seen_hashes[file_hash] = file_part.filename

    file_format = detect_file_format(target_path)
    fingerprint = fingerprint_path(target_path)
    warnings.extend(fingerprint.warnings)
    if file_format in {"unsupported", "legacy_xls"}:
        reasons.append("The file format could not be read as a supported Excel workbook.")
    if fingerprint.inferred_source_type == "unknown":
        reasons.append("The system could not recognize this workbook from its name or headers.")

    profile_rows = 0
    sheet_count = 0
    canonical_sheets: list[str] = []
    if not reasons:
        profile = profile_source_file(
            SourceFile(
                path=target_path,
                original_filename=file_part.filename,
                file_hash=file_hash,
                file_type=suffix.lstrip("."),
                source_type=fingerprint.inferred_source_type,
                country_scope=None,
            )
        )
        profile_rows = profile.total_rows_seen
        sheet_count = profile.detected_sheet_count
        canonical_sheets = profile.canonical_sheets
        warnings.extend(profile.warnings)

    status = "quarantined" if reasons else "accepted"
    result = UploadFileResult(
                original_filename=file_part.filename,
                saved_filename=saved_name,
        status=status,
        source_type=fingerprint.inferred_source_type,
        file_format=file_format,
        confidence=fingerprint.confidence,
        rows_seen=profile_rows,
        sheet_count=sheet_count,
        canonical_sheets=canonical_sheets,
        warnings=warnings,
        reasons=reasons,
    )
    manifest_entry = None
    if status == "accepted":
        manifest_entry = {
            "label": Path(saved_name).stem,
            "path": saved_name,
            "source_type": fingerprint.inferred_source_type,
            "raw_or_cleaned": _raw_or_cleaned_for_source(fingerprint.inferred_source_type),
        }
    return result, manifest_entry


async def _parse_multipart_files(request: Request) -> list[UploadedFilePart]:
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type:
        raise HTTPException(status_code=415, detail="Upload must use multipart form data.")
    body = await request.body()
    if len(body) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload is too large for one batch.")
    parser_input = (
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
    )
    message = BytesParser(policy=policy.default).parsebytes(parser_input)
    files: list[UploadedFilePart] = []
    for part in message.iter_parts():
        filename = part.get_filename()
        field_name = part.get_param("name", header="content-disposition")
        if field_name != "files" or not filename:
            continue
        payload = part.get_payload(decode=True) or b""
        if payload:
            files.append(UploadedFilePart(filename=filename, content=payload))
    return files


def _safe_filename(filename: str) -> str:
    stem = Path(filename).stem or "uploaded-file"
    suffix = Path(filename).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem).strip(" ._") or "uploaded-file"
    return f"{safe_stem[:120]}{suffix}"


def _unique_target_path(batch_dir: Path, safe_name: str) -> Path:
    target = batch_dir / safe_name
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    for index in range(2, 1000):
        candidate = batch_dir / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise HTTPException(status_code=400, detail="Too many files with the same filename.")


def _raw_or_cleaned_for_source(source_type: str) -> str:
    if source_type == "cleaned_presentable":
        return "cleaned"
    if source_type in {"msl_doctor_master", "ers_conference"}:
        return "reference"
    return "raw"


def _next_steps(accepted_count: int, quarantined_count: int) -> list[str]:
    if accepted_count == 0:
        return [
            "No files are ready for ingestion. Replace the rejected files and upload again.",
            "Use the original Excel exports without renaming columns or deleting sheets.",
        ]
    steps = [
        "Accepted files are saved for review and profiling.",
        "Review rejected files before running any ingestion refresh.",
    ]
    if quarantined_count == 0:
        steps.append("All files passed the intake check. The batch can move to ingestion review.")
    return steps


def _batch_dir(batch_id: str) -> Path:
    if not re.fullmatch(r"[0-9TZ-]+[a-f0-9]{8}", batch_id):
        raise HTTPException(status_code=400, detail="Invalid upload batch id.")
    batch_dir = Path(get_settings().upload_data_dir) / batch_id
    if not batch_dir.exists() or not batch_dir.is_dir():
        raise HTTPException(status_code=404, detail="Upload batch was not found.")
    return batch_dir


def _batch_status_path(batch_dir: Path) -> Path:
    return batch_dir / "batch-ingestion-status.json"


def _write_batch_status(batch_dir: Path, status: BatchIngestionStatusResponse) -> None:
    _batch_status_path(batch_dir).write_text(
        status.model_dump_json(by_alias=True, indent=2),
        encoding="utf-8",
    )
