from __future__ import annotations

from pydantic import Field

from backend.app.schemas.meta import ApiModel


class UploadFileResult(ApiModel):
    original_filename: str
    saved_filename: str | None = None
    status: str
    source_type: str
    file_format: str
    confidence: float = 0
    rows_seen: int = 0
    sheet_count: int = 0
    canonical_sheets: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class UploadBatchResponse(ApiModel):
    batch_id: str
    refresh_state: str = "validated"
    total_files: int
    accepted_count: int
    quarantined_count: int
    manifest_path: str | None = None
    summary_path: str | None = None
    files: list[UploadFileResult] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class BatchIngestionStatusResponse(ApiModel):
    batch_id: str
    refresh_state: str
    accepted_count: int = 0
    quarantined_count: int = 0
    ingestion_run_id: str | None = None
    rows_seen: int = 0
    rows_loaded: int = 0
    rows_skipped: int = 0
    warning_count: int = 0
    error_count: int = 0
    manifest_path: str | None = None
    summary_path: str | None = None
    message: str
    next_steps: list[str] = Field(default_factory=list)
