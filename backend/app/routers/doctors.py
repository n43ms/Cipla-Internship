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
    roi_segment: Annotated[str | None, Query(alias="roiSegment")] = None,
    quadrant: str | None = None,
    month_start: Annotated[str | None, Query(alias="monthStart")] = None,
    month_end: Annotated[str | None, Query(alias="monthEnd")] = None,
    brand: str | None = None,
    speciality: str | None = None,
    doctor_class: Annotated[str | None, Query(alias="doctorClass")] = None,
    doctor_search: Annotated[str | None, Query(alias="doctorSearch")] = None,
    include_out_of_scope: Annotated[bool, Query(alias="includeOutOfScope")] = False,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 25,
    sort: str = "darkHorse",
    sort_direction: Annotated[str, Query(alias="sortDirection", pattern="^(asc|desc)$")] = "desc",
    session: Session = Depends(get_session),
) -> DoctorRoiResponse:
    return DoctorService(session).roi(
        country,
        roi_segment,
        quadrant,
        month_start,
        month_end,
        brand,
        speciality,
        doctor_class,
        doctor_search,
        include_out_of_scope,
        page,
        page_size,
        sort,
        sort_direction,
    )


@router.get("/{country_code}/{pcode}", response_model=DoctorDetailResponse, response_model_by_alias=True)
def doctor_detail(country_code: str, pcode: str, session: Session = Depends(get_session)) -> DoctorDetailResponse:
    return DoctorService(session).detail(country_code, pcode)
