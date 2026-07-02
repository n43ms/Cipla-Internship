import { apiGet } from "./client";
import type { BudgetSummaryResponse } from "../types/api";

export type BudgetFilters = {
  country?: string;
  month?: string;
  includeOutOfScope?: boolean;
  page?: number;
  pageSize?: number;
  sort?: string;
  sortDirection?: "asc" | "desc";
};

export function getBudgetSummary(filters: BudgetFilters = {}) {
  const params = new URLSearchParams();
  if (filters.country) params.set("country", filters.country);
  if (filters.month) params.set("month", filters.month);
  if (filters.includeOutOfScope) params.set("includeOutOfScope", "true");
  params.set("page", String(filters.page ?? 1));
  params.set("pageSize", String(filters.pageSize ?? 100));
  if (filters.sort) params.set("sort", filters.sort);
  if (filters.sortDirection) params.set("sortDirection", filters.sortDirection);
  const query = params.toString();
  return apiGet<BudgetSummaryResponse>(`/api/budget/summary${query ? `?${query}` : ""}`);
}
