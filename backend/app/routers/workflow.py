from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.workflow import WorkflowRequestsResponse, WorkflowSummary
from backend.app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflow", tags=["workflow"])
SESSION_DEPENDENCY = Depends(get_session)


@router.get("/summary", response_model=WorkflowSummary, response_model_by_alias=True)
def workflow_summary(
    country: str | None = None,
    month: str | None = None,
    intervention_type: Annotated[str | None, Query(alias="interventionType")] = None,
    session: Session = SESSION_DEPENDENCY,
) -> WorkflowSummary:
    return WorkflowService(session).summary(country, month, intervention_type)


@router.get("/requests", response_model=WorkflowRequestsResponse, response_model_by_alias=True)
def workflow_requests(
    country: str | None = None,
    month: str | None = None,
    intervention_type: Annotated[str | None, Query(alias="interventionType")] = None,
    workflow_status: Annotated[str | None, Query(alias="workflowStatus")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 25,
    session: Session = SESSION_DEPENDENCY,
) -> WorkflowRequestsResponse:
    return WorkflowService(session).requests(country, month, intervention_type, workflow_status, page, page_size)
