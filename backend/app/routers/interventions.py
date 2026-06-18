from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.interventions import InterventionMixResponse
from backend.app.services.intervention_service import InterventionService

router = APIRouter(prefix="/interventions", tags=["interventions"])
SESSION_DEPENDENCY = Depends(get_session)


@router.get("/mix", response_model=InterventionMixResponse, response_model_by_alias=True)
def intervention_mix(
    country: str | None = None,
    month: str | None = None,
    include_out_of_scope: Annotated[bool, Query(alias="includeOutOfScope")] = False,
    session: Session = SESSION_DEPENDENCY,
) -> InterventionMixResponse:
    return InterventionService(session).mix(country, month, include_out_of_scope)
