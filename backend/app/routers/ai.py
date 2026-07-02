from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_session
from backend.app.schemas.ai import AiQueryRequest, AiQueryResponse
from backend.app.services.ai.assistant_service import AssistantService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/query", response_model=AiQueryResponse, response_model_by_alias=True)
def query_ai(
    request: AiQueryRequest,
    session: Annotated[Session, Depends(get_session)],
) -> AiQueryResponse:
    return AssistantService(session).answer(request)
