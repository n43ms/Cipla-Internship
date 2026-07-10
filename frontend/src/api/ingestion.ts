import { apiGet, apiPost, apiPostForm } from "./client";
import type { BatchIngestionStatusResponse, UploadBatchResponse } from "../types/api";

export function uploadDataFiles(files: File[]): Promise<UploadBatchResponse> {
  const form = new FormData();
  for (const file of files) {
    form.append("files", file);
  }
  return apiPostForm<UploadBatchResponse>("/api/ingestion/upload-batch", form);
}

export function getUploadBatchStatus(batchId: string): Promise<BatchIngestionStatusResponse> {
  return apiGet<BatchIngestionStatusResponse>(`/api/ingestion/upload-batches/${batchId}`);
}

export function ingestUploadBatch(batchId: string): Promise<BatchIngestionStatusResponse> {
  return apiPost<BatchIngestionStatusResponse, Record<string, never>>(
    `/api/ingestion/upload-batches/${batchId}/ingest`,
    {},
  );
}
