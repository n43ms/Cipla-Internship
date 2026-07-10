from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.schemas.ingestion_upload import UploadBatchResponse
from backend.app.services.ingestion_upload_service import validate_uploaded_batch

router = APIRouter(tags=["ingestion"])


@router.post(
    "/ingestion/upload-batch",
    response_model=UploadBatchResponse,
    response_model_by_alias=True,
)
async def upload_batch(request: Request) -> UploadBatchResponse:
    return await validate_uploaded_batch(request)
