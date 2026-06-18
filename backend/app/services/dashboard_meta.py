from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.repositories.base import DashboardRepository
from backend.app.schemas.meta import ResponseMeta


def build_meta(
    session: Session,
    *,
    filters_applied: dict[str, object] | None = None,
    flags: list[str] | None = None,
    limitations: list[str] | None = None,
    source_derivation_notes: list[str] | None = None,
) -> ResponseMeta:
    latest = DashboardRepository(session).latest_ingestion()
    return ResponseMeta(
        latest_ingestion_run_id=str(latest["id"]) if latest else None,
        latest_ingestion_status=str(latest["status"]) if latest else "unknown",
        filters_applied=filters_applied or {},
        data_quality_flags=flags or [],
        limitations=limitations or [],
        source_derivation_notes=source_derivation_notes or [],
    )
