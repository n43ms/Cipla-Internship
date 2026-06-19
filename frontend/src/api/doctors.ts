import { apiGet } from "./client";
import type { DoctorDetailResponse, DoctorRoiResponse } from "../types/api";

export type DoctorRoiFilters = {
  country?: string;
  roiSegment?: string;
  quadrant?: string;
  monthStart?: string;
  monthEnd?: string;
  brand?: string;
  speciality?: string;
  doctorClass?: string;
  includeOutOfScope?: boolean;
  page?: number;
  pageSize?: number;
};

export function getDoctorRoi(filters: DoctorRoiFilters = {}) {
  const params = new URLSearchParams();
  if (filters.country) params.set("country", filters.country);
  if (filters.roiSegment) params.set("roiSegment", filters.roiSegment);
  if (filters.quadrant) params.set("quadrant", filters.quadrant);
  if (filters.monthStart) params.set("monthStart", filters.monthStart);
  if (filters.monthEnd) params.set("monthEnd", filters.monthEnd);
  if (filters.brand) params.set("brand", filters.brand);
  if (filters.speciality) params.set("speciality", filters.speciality);
  if (filters.doctorClass) params.set("doctorClass", filters.doctorClass);
  if (filters.includeOutOfScope) params.set("includeOutOfScope", "true");
  params.set("page", String(filters.page ?? 1));
  params.set("pageSize", String(filters.pageSize ?? 25));
  return apiGet<DoctorRoiResponse>(`/api/doctors/roi?${params.toString()}`);
}

export function getDoctorDetail(countryCode: string, pcode: string) {
  return apiGet<DoctorDetailResponse>(`/api/doctors/${countryCode}/${pcode}`);
}
