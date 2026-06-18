from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.app.repositories.execution_repository import ExecutionRepository
from backend.app.schemas.execution import (
    EventListResponse,
    ExecutionEventRow,
    ExecutionFilterOption,
    ExecutionFilterOptions,
    ExecutionSummary,
)
from backend.app.services.dashboard_meta import build_meta
from backend.app.services.filter_validation import validate_country_month_filters


class ExecutionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ExecutionRepository(session)

    def summary(self, country: str | None = None, month: str | None = None) -> ExecutionSummary:
        validate_country_month_filters(self.session, country=country, month=month)
        filters = _filters(country=country, month=month)
        row = self.repository.summary(country, month)
        if not row:
            return ExecutionSummary(
                meta=build_meta(
                    self.session,
                    filters_applied=filters,
                    limitations=["No execution KPI rows match the selected filters."],
                )
            )
        flags = []
        if int(row.get("weak_or_unmatched_events") or 0) > 0:
            flags.append("weak_or_unmatched_events")
        if not month:
            flags.append("mixed_period_scope")
        notes = []
        snapshot_counts = row.get("snapshot_source_counts") or {}
        if snapshot_counts.get("derived_from_consolidation"):
            notes.append(
                "Some execution rows are derived from consolidation because the monthly "
                "execution tab was missing."
            )
        limitations = []
        if not month:
            limitations.append(
                "All-month scope mixes FY27 planner months with partial monthly execution "
                "snapshots and consolidation requests. Select a month for operational "
                "execution rates."
            )
        return ExecutionSummary(
            meta=build_meta(
                self.session,
                filters_applied=filters,
                flags=flags,
                limitations=limitations,
                source_derivation_notes=notes,
            ),
            planned_events=int(row.get("planned_events") or 0),
            matched_events=int(row.get("matched_events") or 0),
            weak_or_unmatched_events=int(row.get("weak_or_unmatched_events") or 0),
            executed_events=int(row.get("executed_events") or 0),
            action_due_events=int(row.get("action_due_events") or 0),
            planned_hcps=int(row.get("planned_hcps") or 0),
            engaged_hcps=int(row.get("engaged_hcps") or 0),
            hcp_execution_rate=Decimal(str(row.get("hcp_execution_rate") or 0)),
            event_execution_rate=Decimal(str(row.get("event_execution_rate") or 0)),
            match_coverage=Decimal(str(row.get("match_coverage") or 0)),
            snapshot_source_counts=dict(snapshot_counts),
        )

    def events(
        self,
        country: str | None,
        month: str | None,
        page: int,
        page_size: int,
    ) -> EventListResponse:
        validate_country_month_filters(self.session, country=country, month=month)
        filters = _filters(country=country, month=month, page=page, pageSize=page_size)
        total, rows = self.repository.event_rows(country, month, page, page_size)
        mapped = [
            ExecutionEventRow(
                source_type=str(row.get("source_type") or "unknown"),
                event_name=row.get("event_name"),
                event_type=row.get("event_type"),
                country=str(row.get("country_name") or row.get("country_code") or ""),
                month=str(row.get("month_label") or row.get("month_start_date") or ""),
                match_status=str(row.get("match_status") or "unknown"),
                confidence=Decimal(str(row.get("confidence") or 0)),
                candidate_match=row.get("candidate_match"),
                planned_hcps=row.get("planned_hcps"),
                engaged_hcps=row.get("engaged_hcps"),
                execution_status=row.get("execution_status"),
                snapshot_source=row.get("snapshot_source"),
                source_derivation_note=row.get("source_derivation_note"),
                source_references=_as_dict(row.get("source_references")),
            )
            for row in rows
        ]
        return EventListResponse(
            meta=build_meta(
                self.session,
                filters_applied=filters,
                flags=["weak_or_unmatched_events"]
                if any(
                    row.match_status
                    in {"weak_match", "unmatched_plan", "unmatched_snapshot", "unmatched_request"}
                    for row in mapped
                )
                else [],
            ),
            page=page,
            page_size=page_size,
            total=total,
            rows=mapped,
        )

    def filter_options(self) -> ExecutionFilterOptions:
        options = self.repository.filter_options()
        return ExecutionFilterOptions(
            countries=[
                ExecutionFilterOption(value=str(country["code"]), label=str(country["name"]))
                for country in options["countries"]
                if country.get("code") and country.get("name")
            ],
            months=[
                ExecutionFilterOption(value=str(month["value"]), label=str(month["label"]))
                for month in options["months"]
                if month.get("value") and month.get("label")
            ],
            recommended_month=(
                ExecutionFilterOption(
                    value=str(options["recommended_month"]["value"]),
                    label=str(options["recommended_month"]["label"]),
                )
                if options.get("recommended_month")
                else None
            ),
        )


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}
