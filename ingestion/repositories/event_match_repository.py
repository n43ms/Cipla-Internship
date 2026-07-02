from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy import text
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from ingestion.reconciliation.event_matcher import MatchCandidate


class EventMatchRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def latest_ingestion_run_id(self) -> str | None:
        return self.session.execute(
            text("select id from ingestion_runs order by started_at desc limit 1")
        ).scalar_one_or_none()

    def delete_matches_for_run(self, ingestion_run_id: str) -> None:
        self.session.execute(text("delete from event_matches"))

    def event_scopes(self) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                with scope as (
                    select distinct country_id, calendar_month_id from plan_events
                    union
                    select distinct country_id, calendar_month_id from execution_snapshots
                    union
                    select distinct country_id, calendar_month_id from execution_requests
                )
                select
                    s.country_id,
                    s.calendar_month_id,
                    c.name as country_name,
                    cm.month_label,
                    exists (
                        select 1 from plan_events pe
                        where pe.country_id = s.country_id
                          and pe.calendar_month_id = s.calendar_month_id
                    ) as planner_available,
                    exists (
                        select 1 from execution_snapshots es
                        where es.country_id = s.country_id
                          and es.calendar_month_id = s.calendar_month_id
                    ) as snapshot_available,
                    exists (
                        select 1 from execution_requests er
                        where er.country_id = s.country_id
                          and er.calendar_month_id = s.calendar_month_id
                    ) as consolidation_available
                from scope s
                join countries c on c.id = s.country_id
                join calendar_months cm on cm.id = s.calendar_month_id
                """
            )
        ).mappings()
        return [dict(row) for row in rows]

    def plan_events(self, country_id: str, calendar_month_id: str) -> list[dict[str, Any]]:
        return self._rows(
            "plan_events",
            "event_name, event_name_normalized, event_type",
            country_id,
            calendar_month_id,
        )

    def execution_snapshots(self, country_id: str, calendar_month_id: str) -> list[dict[str, Any]]:
        return self._rows(
            "execution_snapshots",
            "event_name, event_name_normalized, event_type",
            country_id,
            calendar_month_id,
        )

    def execution_requests(self, country_id: str, calendar_month_id: str) -> list[dict[str, Any]]:
        return self._rows(
            "execution_requests",
            "intervention_name as event_name, intervention_name_normalized as event_name_normalized, intervention_type as event_type",
            country_id,
            calendar_month_id,
        )

    def match_row(
        self,
        *,
        ingestion_run_id: str,
        country_id: str,
        calendar_month_id: str,
        plan_event_id: str | None,
        execution_snapshot_id: str | None,
        execution_request_id: str | None,
        candidate: MatchCandidate,
        match_status: str,
    ) -> dict[str, Any]:
        return {
            "ingestion_run_id": ingestion_run_id,
            "country_id": country_id,
            "calendar_month_id": calendar_month_id,
            "plan_event_id": plan_event_id,
            "execution_snapshot_id": execution_snapshot_id,
            "execution_request_id": execution_request_id,
            "match_method": candidate.match_method,
            "match_confidence": candidate.confidence,
            "match_status": match_status,
            "matched_on": json.dumps(candidate.matched_on),
            "notes": candidate.notes,
            "unmatched_reason_code": candidate.unmatched_reason_code,
            "unmatched_reason_detail": candidate.unmatched_reason_detail,
        }

    def insert_matches(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        self.session.execute(
            text(
                """
                insert into event_matches (
                    ingestion_run_id, country_id, calendar_month_id, plan_event_id,
                    execution_snapshot_id, execution_request_id, match_method, match_confidence,
                    match_status, matched_on, notes, unmatched_reason_code, unmatched_reason_detail
                )
                values (
                    :ingestion_run_id, :country_id, :calendar_month_id, :plan_event_id,
                    :execution_snapshot_id, :execution_request_id, :match_method, :match_confidence,
                    :match_status, cast(:matched_on as json), :notes, :unmatched_reason_code, :unmatched_reason_detail
                )
                """
            ),
            rows,
        )

    def _rows(self, table: str, columns: str, country_id: str, calendar_month_id: str) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                f"""
                select id, {columns}
                from {table}
                where country_id = :country_id and calendar_month_id = :calendar_month_id
                order by source_row_number nulls last, id
                """
            ),
            {"country_id": country_id, "calendar_month_id": calendar_month_id},
        ).mappings()
        return [dict(row) for row in rows]
