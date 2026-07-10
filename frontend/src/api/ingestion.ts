import { apiPostForm } from "./client";
import type { UploadBatchResponse } from "../types/api";

export function uploadDataFiles(files: File[]): Promise<UploadBatchResponse> {
  const form = new FormData();
  for (const file of files) {
    form.append("files", file);
  }
  return apiPostForm<UploadBatchResponse>("/api/ingestion/upload-batch", form);
}
