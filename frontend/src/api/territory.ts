import { apiGet } from "./client";
import type { TerritoryOpportunityResponse } from "../types/api";

export type TerritoryOpportunityFilters = {
  country?: string;
  opportunityLabel?: string;
  page?: number;
  pageSize?: number;
};

export function getTerritoryOpportunities(filters: TerritoryOpportunityFilters = {}) {
  const params = new URLSearchParams();
  if (filters.country) params.set("country", filters.country);
  if (filters.opportunityLabel) params.set("opportunityLabel", filters.opportunityLabel);
  params.set("page", String(filters.page ?? 1));
  params.set("pageSize", String(filters.pageSize ?? 25));
  return apiGet<TerritoryOpportunityResponse>(`/api/territory/opportunities?${params.toString()}`);
}
