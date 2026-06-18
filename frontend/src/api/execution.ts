import { apiGet } from "./client";
import type { EventListResponse, ExecutionFilterOptionsResponse, ExecutionSummaryResponse } from "../types/api";

export type ExecutionFilters = {
  country?: string;
  month?: string;
  page?: number;
  pageSize?: number;
  includeOutOfScope?: boolean;
};

export function getExecutionSummary(filters: Pick<ExecutionFilters, "country" | "month" | "includeOutOfScope"> = {}) {
  return apiGet<ExecutionSummaryResponse>(`/api/execution/summary${queryString(filters)}`);
}

export function getExecutionEvents(filters: ExecutionFilters = {}) {
  return apiGet<EventListResponse>(`/api/execution/events${queryString({ page: 1, pageSize: 25, ...filters })}`);
}

export function getExecutionFilterOptions() {
  return apiGet<ExecutionFilterOptionsResponse>("/api/execution/filter-options");
}

function queryString(values: Record<string, string | number | boolean | undefined>) {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}
