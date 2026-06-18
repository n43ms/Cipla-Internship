import { apiGet } from "./client";
import type { DoctorDetailResponse, DoctorRoiResponse } from "../types/api";

export type DoctorRoiFilters = {
  country?: string;
  segment?: string;
  quadrant?: string;
  page?: number;
  pageSize?: number;
};

export function getDoctorRoi(filters: DoctorRoiFilters = {}) {
  const params = new URLSearchParams();
  if (filters.country) params.set("country", filters.country);
  if (filters.segment) params.set("segment", filters.segment);
  if (filters.quadrant) params.set("quadrant", filters.quadrant);
  params.set("page", String(filters.page ?? 1));
  params.set("pageSize", String(filters.pageSize ?? 25));
  return apiGet<DoctorRoiResponse>(`/api/doctors/roi?${params.toString()}`);
}

export function getDoctorDetail(countryCode: string, pcode: string) {
  return apiGet<DoctorDetailResponse>(`/api/doctors/${countryCode}/${pcode}`);
}
