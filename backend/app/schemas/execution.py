from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import Field

from backend.app.schemas.meta import ApiModel, ResponseMeta

MatchStatus = Literal["matched", "weak_match", "unmatched_plan", "unmatched_snapshot", "unmatched_request", "ignored"]


class ExecutionSummary(ApiModel):
    meta: ResponseMeta
    planned_events: int = 0
    matched_events: int = 0
    weak_or_unmatched_events: int = 0
    executed_events: int = 0
    action_due_events: int = 0
    planned_events_with_executed_evidence: int = 0
    planned_events_with_action_due_evidence: int = 0
    executed_snapshot_count: int = 0
    action_due_snapshot_count: int = 0
    planned_hcps: int = 0
    engaged_hcps: int = 0
    matched_engaged_hcps: int = 0
    raw_engaged_hcps: int = 0
    hcp_execution_rate: Decimal = Decimal("0")
    event_execution_rate: Decimal = Decimal("0")
    match_coverage: Decimal = Decimal("0")
    snapshot_source_counts: dict[str, int] = Field(default_factory=dict)
    primary_scope: bool = True
    scope_statuses: list[str] = Field(default_factory=list)
    scope_reasons: list[str] = Field(default_factory=list)


class ExecutionFilterOption(ApiModel):
    value: str
    label: str


class ExecutionFilterOptions(ApiModel):
    countries: list[ExecutionFilterOption] = Field(default_factory=list)
    months: list[ExecutionFilterOption] = Field(default_factory=list)
    recommended_month: ExecutionFilterOption | None = None


class ExecutionEventRow(ApiModel):
    source_type: str
    event_name: str | None = None
    event_type: str | None = None
    country: str
    month: str
    match_status: MatchStatus | str
    confidence: Decimal
    candidate_match: str | None = None
    planned_hcps: int | None = None
    engaged_hcps: int | None = None
    execution_status: str | None = None
    snapshot_source: str | None = None
    source_derivation_note: str | None = None
    unmatched_reason_code: str | None = None
    unmatched_reason_detail: str | None = None
    is_primary_phase4_scope: bool = False
    scope_status: str | None = None
    scope_reason: str | None = None
    match_grain: str | None = None
    source_references: dict[str, Any] = Field(default_factory=dict)


class EventListResponse(ApiModel):
    meta: ResponseMeta
    page: int
    page_size: int
    total: int
    rows: list[ExecutionEventRow]
