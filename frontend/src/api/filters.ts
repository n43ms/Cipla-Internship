import { apiGet } from "./client";
import type { DataQualityResponse, FiltersResponse, IngestionLatestResponse } from "../types/api";

export function getFilters() {
  return apiGet<FiltersResponse>("/api/filters");
}

export function getDataQuality() {
  return apiGet<DataQualityResponse>("/api/data-quality");
}

export function getLatestIngestion() {
  return apiGet<IngestionLatestResponse>("/api/ingestion/latest");
}
