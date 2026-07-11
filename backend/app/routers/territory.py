from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.territory import TerritoryOpportunityResponse
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
) -> TerritoryOpportunityResponse:
    return TerritoryService(session).opportunities(
        country=country,
        opportunity_label=opportunity_label,
        page=page,
        page_size=page_size,
    )
