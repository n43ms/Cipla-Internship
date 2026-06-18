import { apiGet } from "./client";
import type { InterventionMixResponse } from "../types/api";

export function getInterventionMix(filters: { country?: string; month?: string } = {}) {
  return apiGet<InterventionMixResponse>(`/api/interventions/mix${queryString(filters)}`);
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
