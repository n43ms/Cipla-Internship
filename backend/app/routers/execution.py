from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.execution import (
    EventListResponse,
    ExecutionFilterOptions,
    ExecutionSummary,
)
from backend.app.services.execution_service import ExecutionService

router = APIRouter(prefix="/execution", tags=["execution"])
SESSION_DEPENDENCY = Depends(get_session)


@router.get("/summary", response_model=ExecutionSummary, response_model_by_alias=True)
def execution_summary(
    country: str | None = None,
    month: str | None = None,
    include_out_of_scope: Annotated[bool, Query(alias="includeOutOfScope")] = False,
    session: Session = SESSION_DEPENDENCY,
) -> ExecutionSummary:
    return ExecutionService(session).summary(country, month, include_out_of_scope)


@router.get("/filter-options", response_model=ExecutionFilterOptions, response_model_by_alias=True)
def execution_filter_options(session: Session = SESSION_DEPENDENCY) -> ExecutionFilterOptions:
    return ExecutionService(session).filter_options()


@router.get("/events", response_model=EventListResponse, response_model_by_alias=True)
def execution_events(
    country: str | None = None,
    month: str | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 25,
    include_out_of_scope: Annotated[bool, Query(alias="includeOutOfScope")] = False,
    session: Session = SESSION_DEPENDENCY,
) -> EventListResponse:
    return ExecutionService(session).events(country, month, page, page_size, include_out_of_scope)
