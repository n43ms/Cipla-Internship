from __future__ import annotations

from pydantic import Field

from backend.app.schemas.meta import ApiModel


class FilterOption(ApiModel):
    value: str
    label: str


class FiltersResponse(ApiModel):
    countries: list[FilterOption] = Field(default_factory=list)
    months: list[FilterOption] = Field(default_factory=list)
    intervention_types: list[FilterOption] = Field(default_factory=list)
    specialities: list[FilterOption] = Field(default_factory=list)
    doctor_classes: list[FilterOption] = Field(default_factory=list)
    roi_segments: list[FilterOption] = Field(default_factory=list)
    latest_ingestion_status: str = "unknown"
