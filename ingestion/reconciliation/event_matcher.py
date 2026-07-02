from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from difflib import SequenceMatcher
from typing import Any

from ingestion.normalizers.events import normalize_event_name
from ingestion.repositories.event_match_repository import EventMatchRepository

EXACT_CONFIDENCE = Decimal("1.0000")
NORMALIZED_CONFIDENCE = Decimal("0.9500")
FUZZY_THRESHOLD = Decimal("0.8600")
WEAK_THRESHOLD = Decimal("0.7200")
IGNORED_LABELS = {
    "",
    "blank",
    "grand total",
    "header",
    "na",
    "nil",
    "none",
    "not applicable",
    "overall total",
    "summary",
    "total",
}


@dataclass(frozen=True)
class MatchCandidate:
    match_method: str
    match_status: str
    confidence: Decimal
    matched_on: dict[str, Any]
    notes: str | None = None
    unmatched_reason_code: str | None = None
    unmatched_reason_detail: str | None = None


def match_event_names(left: str | None, right: str | None) -> MatchCandidate:
    left_raw = (left or "").strip()
    right_raw = (right or "").strip()
    if _is_ignored_event_name(left_raw) or _is_ignored_event_name(right_raw):
        return MatchCandidate("ignored", "ignored", Decimal("0.0000"), {}, "Ignored non-business event label")
    if not left_raw or not right_raw:
        return MatchCandidate("none", "unmatched", Decimal("0.0000"), {}, "One side has no event name")
    if left_raw.casefold() == right_raw.casefold():
        return MatchCandidate("exact", "matched", EXACT_CONFIDENCE, {"event_name": left_raw})
    left_normalized = normalize_event_name(left_raw)
    right_normalized = normalize_event_name(right_raw)
    if left_normalized and left_normalized == right_normalized:
        return MatchCandidate("normalized", "matched", NORMALIZED_CONFIDENCE, {"event_name_normalized": left_normalized})
    confidence = Decimal(str(round(SequenceMatcher(None, left_normalized, right_normalized).ratio(), 4)))
    if confidence >= FUZZY_THRESHOLD:
        return MatchCandidate(
            "fuzzy",
            "matched",
            confidence,
            {"left_normalized": left_normalized, "right_normalized": right_normalized},
        )
    if confidence >= WEAK_THRESHOLD:
        return MatchCandidate(
            "fuzzy",
            "weak_match",
            confidence,
            {"left_normalized": left_normalized, "right_normalized": right_normalized},
            "Below confident threshold; review before using as matched KPI evidence",
            "name_mismatch",
            "The event name matched only weakly and must be reviewed before treating it as final execution evidence.",
        )
    return MatchCandidate(
        "none",
        "unmatched",
        confidence,
        {"left_normalized": left_normalized, "right_normalized": right_normalized},
    )


class EventMatcher:
    def __init__(self, repository: EventMatchRepository) -> None:
        self.repository = repository

    def reconcile(self, ingestion_run_id: str | None = None) -> int:
        run_id = ingestion_run_id or self.repository.latest_ingestion_run_id()
        if not run_id:
            return 0
        self.repository.delete_matches_for_run(run_id)
        total = 0
        for scope in self.repository.event_scopes():
            total += self._reconcile_scope(run_id, scope)
        return total

    def _reconcile_scope(self, ingestion_run_id: str, scope: dict[str, Any]) -> int:
        plans = self.repository.plan_events(scope["country_id"], scope["calendar_month_id"])
        snapshots = self.repository.execution_snapshots(scope["country_id"], scope["calendar_month_id"])
        requests = self.repository.execution_requests(scope["country_id"], scope["calendar_month_id"])
        rows: list[dict[str, Any]] = []
        used_snapshots: set[str] = set()
        used_requests: set[str] = set()

        for plan in plans:
            if _is_ignored_event_name(plan.get("event_name")):
                rows.append(
                    self.repository.match_row(
                        ingestion_run_id=ingestion_run_id,
                        country_id=scope["country_id"],
                        calendar_month_id=scope["calendar_month_id"],
                        plan_event_id=plan["id"],
                        execution_snapshot_id=None,
                        execution_request_id=None,
                        candidate=_ignored(),
                        match_status="ignored",
                    )
                )
                continue
            snapshot, snapshot_match = self._best_match(plan, snapshots, used_snapshots)
            request_matches = self._all_confident_matches(plan, requests, used_requests)
            if snapshot:
                used_snapshots.add(str(snapshot["id"]))
            for request, _request_match in request_matches:
                used_requests.add(str(request["id"]))
            best_match = _strongest(snapshot_match, _strongest_many([match for _request, match in request_matches]))
            if request_matches:
                for request, request_match in request_matches:
                    row_match = _strongest(snapshot_match, request_match)
                    rows.append(
                        self.repository.match_row(
                            ingestion_run_id=ingestion_run_id,
                            country_id=scope["country_id"],
                            calendar_month_id=scope["calendar_month_id"],
                            plan_event_id=plan["id"],
                            execution_snapshot_id=snapshot.get("id") if snapshot else None,
                            execution_request_id=request["id"],
                            candidate=row_match,
                            match_status=row_match.match_status,
                        )
                    )
                continue
            if snapshot:
                rows.append(
                    self.repository.match_row(
                        ingestion_run_id=ingestion_run_id,
                        country_id=scope["country_id"],
                        calendar_month_id=scope["calendar_month_id"],
                        plan_event_id=plan["id"],
                        execution_snapshot_id=snapshot.get("id"),
                        execution_request_id=None,
                        candidate=best_match,
                        match_status=best_match.match_status,
                    )
                )
                continue
            rows.append(
                self.repository.match_row(
                    ingestion_run_id=ingestion_run_id,
                    country_id=scope["country_id"],
                    calendar_month_id=scope["calendar_month_id"],
                    plan_event_id=plan["id"],
                    execution_snapshot_id=None,
                    execution_request_id=None,
                    candidate=_unmatched("unmatched_plan", scope),
                    match_status="unmatched_plan",
                )
            )

        for snapshot in snapshots:
            if str(snapshot["id"]) not in used_snapshots:
                ignored = _is_ignored_event_name(snapshot.get("event_name"))
                rows.append(
                    self.repository.match_row(
                        ingestion_run_id=ingestion_run_id,
                        country_id=scope["country_id"],
                        calendar_month_id=scope["calendar_month_id"],
                        plan_event_id=None,
                        execution_snapshot_id=snapshot["id"],
                        execution_request_id=None,
                        candidate=_ignored() if ignored else _unmatched("unmatched_snapshot", scope),
                        match_status="ignored" if ignored else "unmatched_snapshot",
                    )
                )
        for request in requests:
            if str(request["id"]) not in used_requests:
                ignored = _is_ignored_event_name(request.get("event_name"))
                rows.append(
                    self.repository.match_row(
                        ingestion_run_id=ingestion_run_id,
                        country_id=scope["country_id"],
                        calendar_month_id=scope["calendar_month_id"],
                        plan_event_id=None,
                        execution_snapshot_id=None,
                        execution_request_id=request["id"],
                        candidate=_ignored() if ignored else _unmatched("unmatched_request", scope),
                        match_status="ignored" if ignored else "unmatched_request",
                    )
                )
        self.repository.insert_matches(rows)
        return len(rows)

    def _best_match(
        self,
        plan: dict[str, Any],
        candidates: list[dict[str, Any]],
        used_ids: set[str],
    ) -> tuple[dict[str, Any] | None, MatchCandidate]:
        best_row: dict[str, Any] | None = None
        best = _unmatched("unmatched")
        for candidate in candidates:
            if str(candidate["id"]) in used_ids:
                continue
            if _is_ignored_event_name(candidate.get("event_name")):
                continue
            result = match_event_names(str(plan.get("event_name") or ""), str(candidate.get("event_name") or ""))
            if result.confidence > best.confidence:
                best = result
                best_row = candidate
        if best_row and best.match_status in {"matched", "weak_match"}:
            return best_row, best
        return None, _unmatched("unmatched")

    def _all_confident_matches(
        self,
        plan: dict[str, Any],
        candidates: list[dict[str, Any]],
        used_ids: set[str],
    ) -> list[tuple[dict[str, Any], MatchCandidate]]:
        matches: list[tuple[dict[str, Any], MatchCandidate]] = []
        plan_type = normalize_event_name(plan.get("event_type"))
        for candidate in candidates:
            if str(candidate["id"]) in used_ids:
                continue
            if _is_ignored_event_name(candidate.get("event_name")):
                continue
            result = match_event_names(str(plan.get("event_name") or ""), str(candidate.get("event_name") or ""))
            if result.match_status not in {"matched", "weak_match"}:
                continue
            candidate_type = normalize_event_name(candidate.get("event_type"))
            if plan_type and candidate_type and plan_type != candidate_type:
                adjusted_confidence = max(result.confidence - Decimal("0.1200"), Decimal("0.0000"))
                if adjusted_confidence < WEAK_THRESHOLD:
                    continue
                result = MatchCandidate(
                    result.match_method,
                    "weak_match" if adjusted_confidence < FUZZY_THRESHOLD else result.match_status,
                    adjusted_confidence,
                    {**result.matched_on, "event_type_warning": {"plan": plan_type, "candidate": candidate_type}},
                    "Event name matched but intervention type differs; review before treating as final",
                    "name_mismatch" if adjusted_confidence < FUZZY_THRESHOLD else result.unmatched_reason_code,
                    (
                        "The event name or type matched only weakly and must be reviewed before treating it as final execution evidence."
                        if adjusted_confidence < FUZZY_THRESHOLD
                        else result.unmatched_reason_detail
                    ),
                )
            matches.append((candidate, result))
        return matches


def _strongest(left: MatchCandidate, right: MatchCandidate) -> MatchCandidate:
    return left if left.confidence >= right.confidence else right


def _strongest_many(matches: list[MatchCandidate]) -> MatchCandidate:
    best = _unmatched("unmatched")
    for match in matches:
        best = _strongest(best, match)
    return best


def _unmatched(status: str, scope: dict[str, Any] | None = None) -> MatchCandidate:
    code, detail = _unmatched_reason(status, scope or {})
    return MatchCandidate("none", status, Decimal("0.0000"), {}, None, code, detail)


def _ignored() -> MatchCandidate:
    return MatchCandidate("ignored", "ignored", Decimal("0.0000"), {}, "Ignored non-business event label")


def _is_ignored_event_name(value: Any) -> bool:
    normalized = normalize_event_name(value)
    return normalized in IGNORED_LABELS or normalized.startswith("total ")


def _unmatched_reason(status: str, scope: dict[str, Any]) -> tuple[str | None, str | None]:
    country_name = str(scope.get("country_name") or "")
    month_label = str(scope.get("month_label") or "")
    planner_available = bool(scope.get("planner_available", True))
    snapshot_available = bool(scope.get("snapshot_available", True))
    if status == "weak_match":
        return (
            "name_mismatch",
            "The event name matched only weakly and must be reviewed before treating it as final execution evidence.",
        )
    if country_name and country_name not in {"Nepal", "Sri Lanka"}:
        return "no_planner_for_country", "This market has no FY27 planner in the supplied Phase 4 source set."
    if month_label and month_label < "2026-04":
        return (
            "historical_request_no_fy27_plan",
            "This record is before FY27 planner coverage and is retained as historical consolidation evidence.",
        )
    if month_label and month_label > "2026-05":
        return (
            "future_plan_no_execution_yet",
            "This record is outside the April-May 2026 execution snapshot window and is retained for future analysis.",
        )
    if not planner_available:
        return "no_planner_for_country", "No planner row exists for this country/month."
    if status == "unmatched_plan" and not snapshot_available:
        return "no_snapshot_for_month", "No execution snapshot exists for this planned event month."
    if status == "unmatched_plan":
        return "planner_only", "The planned event has no confident matching execution or consolidation evidence."
    if status == "unmatched_snapshot":
        return "snapshot_only_no_matching_plan", "The snapshot row has no matching planner event in the same scoped country/month."
    if status == "unmatched_request":
        return "consolidation_only", "The consolidation request has no matching planner event."
    return None, None
