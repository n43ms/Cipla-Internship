from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.repositories.data_quality_repository import DataQualityRepository
from backend.app.schemas.data_quality import (
    DataQualitySummary,
    FxQualityRow,
    IngestionLatestResponse,
    SourceFileQualityRow,
    UnmatchedQualityRow,
    UnmatchedRecordRow,
    UnmatchedRecordsResponse,
    ValidationIssueRow,
)
from backend.app.schemas.filters import FilterOption, FiltersResponse
from backend.app.services.dashboard_meta import build_meta


class DataQualityService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DataQualityRepository(session)

    def summary(self) -> DataQualitySummary:
        row = self.repository.summary() or {}
        latest = self.latest_ingestion()
        stale_ingestion = _is_stale(latest.completed_at, latest.status)
        row["stale_ingestion"] = stale_ingestion
        flags = _quality_flags(row)
        limitations = []
        if row.get("derived_snapshot_count"):
            limitations.append("Sri Lanka May execution includes consolidation-derived snapshots.")
        if row.get("missing_fx_count"):
            limitations.append("Non-LKR financial rows without company FX remain local-only for USD comparisons.")
        return DataQualitySummary(
            meta=build_meta(self.session, flags=flags, limitations=limitations),
            latest_ingestion=latest,
            source_file_count=int(row.get("source_file_count") or 0),
            loaded_file_count=int(row.get("loaded_file_count") or 0),
            rows_seen=int(row.get("rows_seen") or 0),
            rows_loaded=int(row.get("rows_loaded") or 0),
            rows_skipped=int(row.get("rows_skipped") or 0),
            validation_error_count=int(row.get("validation_error_count") or 0),
            validation_warning_count=int(row.get("validation_warning_count") or 0),
            match_coverage=_decimal(row.get("match_coverage")),
            pcode_coverage=_decimal(row.get("pcode_coverage")),
            rcpa_coverage=_decimal(row.get("rcpa_coverage")),
            missing_fx_count=int(row.get("missing_fx_count") or 0),
            provisional_fx_count=int(row.get("provisional_fx_count") or 0),
            btu_btc_reconciliation_issue_count=int(row.get("btu_btc_reconciliation_issue_count") or 0),
            missing_confirmed_amount_count=int(row.get("missing_confirmed_amount_count") or 0),
            spend_without_plan_count=int(row.get("spend_without_plan_count") or 0),
            plan_without_spend_count=int(row.get("plan_without_spend_count") or 0),
            request_workflow_coverage=_decimal(row.get("request_workflow_coverage")),
            post_workflow_coverage=_decimal(row.get("post_workflow_coverage")),
            intervention_type_coverage=_decimal(row.get("intervention_type_coverage")),
            unmatched_event_count=int(row.get("unmatched_event_count") or 0),
            derived_snapshot_count=int(row.get("derived_snapshot_count") or 0),
            serial_month_parse_count=int(row.get("serial_month_parse_count") or 0),
            static_fx_seed_date=str(row.get("static_fx_seed_date")) if row.get("static_fx_seed_date") else None,
            official_lkr_rate_to_usd=row.get("official_lkr_rate_to_usd"),
            actual_attendance_missing_pcode_count=int(row.get("actual_attendance_missing_pcode_count") or 0),
            unallocated_doctor_spend_local=_decimal(row.get("unallocated_doctor_spend_local")),
            unallocated_doctor_spend_usd=_decimal(row.get("unallocated_doctor_spend_usd")),
            stale_ingestion=stale_ingestion,
            validation_issues=[ValidationIssueRow(**item) for item in self.repository.validation_issues()],
            source_files=[SourceFileQualityRow(**item) for item in self.repository.source_file_quality()],
            unmatched_by_source=[UnmatchedQualityRow(**item) for item in self.repository.unmatched_by_source()],
            unmatched_records=[UnmatchedRecordRow(**item) for item in self.repository.unmatched_records()],
            fx_quality=[FxQualityRow(**item) for item in self.repository.fx_quality()],
        )

    def unmatched_records(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        country: str | None = None,
        month: str | None = None,
        source_type: str | None = None,
        reason_code: str | None = None,
    ) -> UnmatchedRecordsResponse:
        total, rows = self.repository.unmatched_records_page(
            page=page,
            page_size=page_size,
            country=country,
            month=month,
            source_type=source_type,
            reason_code=reason_code,
        )
        return UnmatchedRecordsResponse(
            meta=build_meta(
                self.session,
                filters_applied=_filters(
                    country=country,
                    month=month,
                    sourceType=source_type,
                    reasonCode=reason_code,
                    page=page,
                    pageSize=page_size,
                ),
                flags=["weak_match_coverage"] if total else [],
                limitations=["Unmatched records are restricted to the primary Phase 4 analytical scope."],
            ),
            page=page,
            page_size=page_size,
            total=total,
            rows=[UnmatchedRecordRow(**item) for item in rows],
        )

    def latest_ingestion(self) -> IngestionLatestResponse:
        row = self.repository.latest_ingestion() or {}
        return IngestionLatestResponse(
            id=str(row["id"]) if row.get("id") else None,
            status=str(row.get("status") or "unknown"),
            started_at=row.get("started_at"),
            completed_at=row.get("completed_at"),
            source_file_count=int(row.get("source_file_count") or 0),
            total_rows_seen=int(row.get("total_rows_seen") or 0),
            total_rows_loaded=int(row.get("total_rows_loaded") or 0),
            total_rows_skipped=int(row.get("total_rows_skipped") or 0),
            warning_count=int(row.get("warning_count") or 0),
            error_count=int(row.get("error_count") or 0),
        )

    def filters(self) -> FiltersResponse:
        row = self.repository.filters()
        return FiltersResponse(
            countries=[FilterOption(**item) for item in row["countries"]],
            months=[FilterOption(**item) for item in row["months"]],
            intervention_types=[FilterOption(**item) for item in row["intervention_types"]],
            brands=[FilterOption(**item) for item in row["brands"]],
            specialities=[FilterOption(**item) for item in row["specialities"]],
            doctor_classes=[FilterOption(**item) for item in row["doctor_classes"]],
            roi_segments=[FilterOption(**item) for item in row["roi_segments"]],
            latest_ingestion_status=str(row.get("latest_ingestion_status") or "unknown"),
        )


def _decimal(value: object) -> Decimal:
    return Decimal(str(value or 0))


def _quality_flags(row: dict[str, object]) -> list[str]:
    flags: list[str] = []
    if row.get("stale_ingestion"):
        flags.append("stale_ingestion")
    if int(row.get("validation_error_count") or 0) or int(row.get("validation_warning_count") or 0):
        flags.append("validation_issues")
    if _decimal(row.get("match_coverage")) < Decimal("0.8"):
        flags.append("weak_match_coverage")
    if _decimal(row.get("pcode_coverage")) < Decimal("0.8"):
        flags.append("weak_pcode_coverage")
    if int(row.get("missing_fx_count") or 0):
        flags.append("missing_fx")
    if int(row.get("provisional_fx_count") or 0):
        flags.append("provisional_fx")
    if int(row.get("doctor_no_rcpa_count") or 0):
        flags.append("no_rcpa")
    if int(row.get("actual_attendance_missing_pcode_count") or 0):
        flags.append("unallocated_doctor_spend")
    return flags


def _is_stale(completed_at: datetime | None, status: str) -> bool:
    if not completed_at:
        return True
    if status not in {"completed", "completed_with_warnings"}:
        return True
    completed = completed_at if completed_at.tzinfo else completed_at.replace(tzinfo=UTC)
    max_age_days = get_settings().data_freshness_max_age_days
    return completed < datetime.now(UTC) - timedelta(days=max_age_days)


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}
