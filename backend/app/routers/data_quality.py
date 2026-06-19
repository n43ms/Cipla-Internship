from __future__ import annotations

from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi import Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.data_quality import DataQualitySummary, IngestionLatestResponse, UnmatchedRecordsResponse
from backend.app.schemas.filters import FiltersResponse
from backend.app.services.data_quality_service import DataQualityService

router = APIRouter(tags=["data-quality"])


@router.get("/data-quality", response_model=DataQualitySummary, response_model_by_alias=True)
def data_quality(session: Session = Depends(get_session)) -> DataQualitySummary:
    return DataQualityService(session).summary()


@router.get("/data-quality/unmatched", response_model=UnmatchedRecordsResponse, response_model_by_alias=True)
def unmatched_records(
    country: str | None = None,
    month: str | None = None,
    source_type: Annotated[str | None, Query(alias="sourceType")] = None,
    reason_code: Annotated[str | None, Query(alias="reasonCode")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 50,
    session: Session = Depends(get_session),
) -> UnmatchedRecordsResponse:
    return DataQualityService(session).unmatched_records(
        page=page,
        page_size=page_size,
        country=country,
        month=month,
        source_type=source_type,
        reason_code=reason_code,
    )


@router.get("/filters", response_model=FiltersResponse, response_model_by_alias=True)
def filters(session: Session = Depends(get_session)) -> FiltersResponse:
    return DataQualityService(session).filters()


@router.get("/ingestion/latest", response_model=IngestionLatestResponse, response_model_by_alias=True)
def latest_ingestion(session: Session = Depends(get_session)) -> IngestionLatestResponse:
    return DataQualityService(session).latest_ingestion()
