import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/api/analyticsApi";
import { queryKeys } from "@/api/queryKeys";
import { serializeAnalyticsFilters } from "@/features/analytics/adapters";
import type { AnalyticsFilters } from "@/types/analytics";

export function useAnalyticsByMonth(filters: Partial<AnalyticsFilters>) {
  return useQuery({
    queryKey: queryKeys.byMonth(serializeAnalyticsFilters(filters)),
    queryFn: () => analyticsApi.getByMonth(filters),
  });
}
