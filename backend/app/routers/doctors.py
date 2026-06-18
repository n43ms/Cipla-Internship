from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.doctors import DoctorDetailResponse, DoctorRoiResponse
from backend.app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/roi", response_model=DoctorRoiResponse, response_model_by_alias=True)
def doctor_roi(
    country: str | None = None,
    segment: str | None = None,
    quadrant: str | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 25,
    session: Session = Depends(get_session),
) -> DoctorRoiResponse:
    return DoctorService(session).roi(country, segment, quadrant, page, page_size)


@router.get("/{country_code}/{pcode}", response_model=DoctorDetailResponse, response_model_by_alias=True)
def doctor_detail(country_code: str, pcode: str, session: Session = Depends(get_session)) -> DoctorDetailResponse:
    return DoctorService(session).detail(country_code, pcode)
