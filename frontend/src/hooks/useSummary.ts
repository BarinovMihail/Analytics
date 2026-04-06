import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/api/analyticsApi";
import { queryKeys } from "@/api/queryKeys";
import { serializeAnalyticsFilters } from "@/features/analytics/adapters";
import type { AnalyticsFilters } from "@/types/analytics";

export function useSummary(filters: Partial<AnalyticsFilters>) {
  return useQuery({
    queryKey: queryKeys.summary(serializeAnalyticsFilters(filters)),
    queryFn: () => analyticsApi.getSummary(filters),
    refetchInterval: 15000,
  });
}
