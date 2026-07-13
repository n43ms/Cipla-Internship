from __future__ import annotations

from typing import Annotated
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.territory import TerritoryDoctorsResponse, TerritoryOpportunityResponse
from backend.app.services.territory_service import TerritoryService

router = APIRouter(prefix="/territory", tags=["territory"])


@router.get(
    "/opportunities",
    response_model=TerritoryOpportunityResponse,
    response_model_by_alias=True,
)
def territory_opportunities(
    session: Annotated[Session, Depends(get_session)],
    country: str | None = None,
    opportunity_label: Annotated[str | None, Query(alias="opportunityLabel")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 25,
    sort_by: Annotated[
        Literal["territoryName", "opportunityLabel", "doctorCount", "totalPrescriptionQty"],
        Query(alias="sortBy"),
    ] = "totalPrescriptionQty",
    sort_dir: Annotated[Literal["asc", "desc"], Query(alias="sortDir")] = "desc",
) -> TerritoryOpportunityResponse:
    return TerritoryService(session).opportunities(
        country=country,
        opportunity_label=opportunity_label,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get(
    "/doctors",
    response_model=TerritoryDoctorsResponse,
    response_model_by_alias=True,
)
def territory_doctors(
    session: Annotated[Session, Depends(get_session)],
    country: str,
    territory_name: Annotated[str, Query(alias="territoryName")],
    patch_name: Annotated[str | None, Query(alias="patchName")] = None,
) -> TerritoryDoctorsResponse:
    return TerritoryService(session).doctors(
        country=country,
        territory_name=territory_name,
        patch_name=patch_name,
    )
