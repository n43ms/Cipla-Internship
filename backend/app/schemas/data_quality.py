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
    stale_ingestion: bool = False
    validation_issues: list[ValidationIssueRow] = Field(default_factory=list)
