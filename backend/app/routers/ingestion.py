from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.schemas.ingestion_upload import BatchIngestionStatusResponse, UploadBatchResponse
from backend.app.services.ingestion_upload_service import (
    get_batch_ingestion_status,
    run_batch_ingestion,
    validate_uploaded_batch,
)

router = APIRouter(tags=["ingestion"])


@router.post(
    "/ingestion/upload-batch",
    response_model=UploadBatchResponse,
    response_model_by_alias=True,
)
async def upload_batch(request: Request) -> UploadBatchResponse:
    return await validate_uploaded_batch(request)


@router.get(
    "/ingestion/upload-batches/{batch_id}",
    response_model=BatchIngestionStatusResponse,
    response_model_by_alias=True,
)
def upload_batch_status(batch_id: str) -> BatchIngestionStatusResponse:
    return get_batch_ingestion_status(batch_id)


@router.post(
    "/ingestion/upload-batches/{batch_id}/ingest",
    response_model=BatchIngestionStatusResponse,
    response_model_by_alias=True,
)
def ingest_upload_batch(batch_id: str) -> BatchIngestionStatusResponse:
    return run_batch_ingestion(batch_id)
