from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.budget import BudgetSummary
from backend.app.services.budget_service import BudgetService

router = APIRouter(prefix="/budget", tags=["budget"])


@router.get("/summary", response_model=BudgetSummary, response_model_by_alias=True)
def budget_summary(
    country: str | None = None,
    month: str | None = None,
    include_out_of_scope: Annotated[bool, Query(alias="includeOutOfScope")] = False,
    session: Session = Depends(get_session),
) -> BudgetSummary:
    return BudgetService(session).summary(country, month, include_out_of_scope)
