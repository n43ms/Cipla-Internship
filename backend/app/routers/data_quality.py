from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.data_quality import DataQualitySummary, IngestionLatestResponse
from backend.app.schemas.filters import FiltersResponse
from backend.app.services.data_quality_service import DataQualityService

router = APIRouter(tags=["data-quality"])


@router.get("/data-quality", response_model=DataQualitySummary, response_model_by_alias=True)
def data_quality(session: Session = Depends(get_session)) -> DataQualitySummary:
    return DataQualityService(session).summary()


@router.get("/filters", response_model=FiltersResponse, response_model_by_alias=True)
def filters(session: Session = Depends(get_session)) -> FiltersResponse:
    return DataQualityService(session).filters()


@router.get("/ingestion/latest", response_model=IngestionLatestResponse, response_model_by_alias=True)
def latest_ingestion(session: Session = Depends(get_session)) -> IngestionLatestResponse:
    return DataQualityService(session).latest_ingestion()
