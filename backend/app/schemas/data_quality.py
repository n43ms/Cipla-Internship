from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from backend.app.schemas.meta import ApiModel, ResponseMeta


class IngestionLatestResponse(ApiModel):
    id: str | None = None
    status: str = "unknown"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    source_file_count: int = 0
    total_rows_seen: int = 0
    total_rows_loaded: int = 0
    total_rows_skipped: int = 0
    warning_count: int = 0
    error_count: int = 0


class ValidationIssueRow(ApiModel):
    severity: str
    source_file: str | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    entity_type: str | None = None
    field_name: str | None = None
    error_code: str
    message: str


class SourceFileQualityRow(ApiModel):
    source_file: str | None = None
    source_type: str | None = None
    status: str | None = None
    rows_seen: int = 0
    rows_loaded: int = 0
    rows_skipped: int = 0
    warning_count: int = 0
    error_count: int = 0
    period_start: str | None = None
    period_end: str | None = None
    storage_mode: str = "canonical_rows"
    row_count_note: str | None = None


class UnmatchedQualityRow(ApiModel):
    source_type: str
    reason_code: str
    record_count: int = 0


class UnmatchedRecordRow(ApiModel):
    source_type: str
    country: str
    month: str
    event_name: str | None = None
    event_type: str | None = None
    reason_code: str | None = None
    reason_detail: str | None = None
    candidate_match: str | None = None
    confidence: Decimal = Decimal("0")


class FxQualityRow(ApiModel):
    currency_code: str
    rate_status: str
    rate_to_usd: Decimal | None = None
    rate_date: str | None = None
    source: str | None = None
    row_count: int = 0


class DataQualitySummary(ApiModel):
    meta: ResponseMeta
    latest_ingestion: IngestionLatestResponse
    source_file_count: int = 0
    loaded_file_count: int = 0
    rows_seen: int = 0
    rows_loaded: int = 0
    rows_skipped: int = 0
    validation_error_count: int = 0
    validation_warning_count: int = 0
    match_coverage: Decimal = Decimal("0")
    pcode_coverage: Decimal = Decimal("0")
    rcpa_coverage: Decimal = Decimal("0")
    missing_fx_count: int = 0
    provisional_fx_count: int = 0
    btu_btc_reconciliation_issue_count: int = 0
    missing_confirmed_amount_count: int = 0
    spend_without_plan_count: int = 0
    plan_without_spend_count: int = 0
    request_workflow_coverage: Decimal = Decimal("0")
    post_workflow_coverage: Decimal = Decimal("0")
    intervention_type_coverage: Decimal = Decimal("0")
    unmatched_event_count: int = 0
    derived_snapshot_count: int = 0
    serial_month_parse_count: int = 0
    static_fx_seed_date: str | None = None
    official_lkr_rate_to_usd: Decimal | None = None
    actual_attendance_missing_pcode_count: int = 0
    unallocated_doctor_spend_local: Decimal = Decimal("0")
    unallocated_doctor_spend_usd: Decimal = Decimal("0")
    stale_ingestion: bool = False
    validation_issues: list[ValidationIssueRow] = Field(default_factory=list)
    source_files: list[SourceFileQualityRow] = Field(default_factory=list)
    unmatched_by_source: list[UnmatchedQualityRow] = Field(default_factory=list)
    unmatched_records: list[UnmatchedRecordRow] = Field(default_factory=list)
    fx_quality: list[FxQualityRow] = Field(default_factory=list)


class UnmatchedRecordsResponse(ApiModel):
    meta: ResponseMeta
    page: int = 1
    page_size: int = 50
    total: int = 0
    rows: list[UnmatchedRecordRow] = Field(default_factory=list)
