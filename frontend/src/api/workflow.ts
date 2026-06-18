import { apiGet } from "./client";
import type { WorkflowRequestsResponse, WorkflowSummaryResponse } from "../types/api";

export type WorkflowFilters = {
  country?: string;
  month?: string;
  interventionType?: string;
  workflowStatus?: string;
  page?: number;
  pageSize?: number;
};

export function getWorkflowSummary(filters: Pick<WorkflowFilters, "country" | "month" | "interventionType"> = {}) {
  return apiGet<WorkflowSummaryResponse>(`/api/workflow/summary${queryString(filters)}`);
}

export function getWorkflowRequests(filters: WorkflowFilters = {}) {
  return apiGet<WorkflowRequestsResponse>(`/api/workflow/requests${queryString({ page: 1, pageSize: 10, ...filters })}`);
}

function queryString(values: Record<string, string | number | undefined>) {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}
