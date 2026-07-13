import { apiGet } from "./client";
import type { TerritoryDoctorsResponse, TerritoryOpportunityResponse } from "../types/api";

export type TerritoryOpportunityFilters = {
  country?: string;
  opportunityLabel?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortDir?: "asc" | "desc";
};

export function getTerritoryOpportunities(filters: TerritoryOpportunityFilters = {}) {
  const params = new URLSearchParams();
  if (filters.country) params.set("country", filters.country);
  if (filters.opportunityLabel) params.set("opportunityLabel", filters.opportunityLabel);
  params.set("page", String(filters.page ?? 1));
  params.set("pageSize", String(filters.pageSize ?? 25));
  if (filters.sortBy) params.set("sortBy", filters.sortBy);
  if (filters.sortDir) params.set("sortDir", filters.sortDir);
  return apiGet<TerritoryOpportunityResponse>(`/api/territory/opportunities?${params.toString()}`);
}

export function getTerritoryDoctors(filters: { country: string; territoryName: string; patchName?: string | null }) {
  const params = new URLSearchParams();
  params.set("country", filters.country);
  params.set("territoryName", filters.territoryName);
  if (filters.patchName) params.set("patchName", filters.patchName);
  return apiGet<TerritoryDoctorsResponse>(`/api/territory/doctors?${params.toString()}`);
}
