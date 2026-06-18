from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ResponseMeta(ApiModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    latest_ingestion_run_id: str | None = None
    latest_ingestion_status: str = "unknown"
    filters_applied: dict[str, Any] = Field(default_factory=dict)
    data_quality_flags: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    source_derivation_notes: list[str] = Field(default_factory=list)


class PageResponse(ApiModel):
    meta: ResponseMeta
    page: int
    page_size: int
    total: int
    rows: list[dict[str, Any]]
