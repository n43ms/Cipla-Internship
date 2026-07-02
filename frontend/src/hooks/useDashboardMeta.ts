import { useQuery } from "@tanstack/react-query";

import { getDataQuality } from "../api/filters";

export function useDashboardMeta() {
  return useQuery({
    queryKey: ["dashboard-meta"],
    queryFn: getDataQuality,
    staleTime: 60_000,
  });
}
