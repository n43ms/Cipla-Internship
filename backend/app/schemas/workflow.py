from __future__ import annotations

from datetime import date

from pydantic import Field

from backend.app.schemas.meta import ApiModel, ResponseMeta


class WorkflowSummary(ApiModel):
    meta: ResponseMeta
    request_approval_counts: dict[str, int]
    request_confirmation_counts: dict[str, int]
    post_approval_counts: dict[str, int]
    post_confirmation_counts: dict[str, int]
    owner_stage_counts: dict[str, int]
    pending_request_count: int = 0
    pending_report_count: int = 0
    reports_sent_for_correction: int = 0
    reports_approved: int = 0
    expense_submitted_coverage: float = 0
    expense_confirmed_coverage: float = 0
    primary_scope: bool = True
    scope_statuses: list[str] = Field(default_factory=list)
    scope_reasons: list[str] = Field(default_factory=list)


class WorkflowRequestRow(ApiModel):
    req_id: str | None = None
    country: str
    month: str
    rep_name: str | None = None
    intervention_type: str | None = None
    request_approval_status: str
    request_confirmation_status: str
    post_approval_status: str
    post_confirmation_status: str
    current_owner_stage: str | None = None
    expense_submitted_date: date | None = None
    expense_confirmed_date: date | None = None
    is_primary_phase4_scope: bool = False
    scope_status: str | None = None
    scope_reason: str | None = None


class WorkflowRequestsResponse(ApiModel):
    meta: ResponseMeta
    page: int
    page_size: int
    total: int
    rows: list[WorkflowRequestRow]
