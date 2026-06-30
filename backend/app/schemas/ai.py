from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from backend.app.schemas.meta import ApiModel


class AiQueryRequest(ApiModel):
    question: str = Field(min_length=3, max_length=1000)
    page_context: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)


class DashboardPointer(ApiModel):
    page: str
    section: str
    detail: str
    reason: str


class AiContextScope(ApiModel):
    page_context: str
    filters: dict[str, Any] = Field(default_factory=dict)
    top_n: int
    max_characters: int
    sections: list[str] = Field(default_factory=list)


class AiQueryResponse(ApiModel):
    answer: str
    dashboard_pointers: list[DashboardPointer] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"]
    provider_used: str
    model_used: str | None = None
    fallback_used: bool = False
    redaction_applied: bool = False
    context_scope: AiContextScope
