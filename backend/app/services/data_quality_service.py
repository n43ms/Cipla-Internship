from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.repositories.data_quality_repository import DataQualityRepository
from backend.app.schemas.data_quality import (
    DataQualitySummary,
    IngestionLatestResponse,
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
        flags = _quality_flags(row)
        limitations = []
        if row.get("derived_snapshot_count"):
            limitations.append("Sri Lanka May execution includes consolidation-derived snapshots.")
        if row.get("missing_fx_count"):
            limitations.append("Non-LKR financial rows without company FX remain local-only for USD comparisons.")
        return DataQualitySummary(
            meta=build_meta(self.session, flags=flags, limitations=limitations),
            latest_ingestion=self.latest_ingestion(),
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
            stale_ingestion=bool(row.get("stale_ingestion")),
            validation_issues=[ValidationIssueRow(**item) for item in self.repository.validation_issues()],
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
    return flags
