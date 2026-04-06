import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/api/analyticsApi";
import { queryKeys } from "@/api/queryKeys";
import { serializeAnalyticsFilters } from "@/features/analytics/adapters";
import type { AnalyticsFilters } from "@/types/analytics";

export function useSupplierPurchases(
  filters: Partial<AnalyticsFilters>,
  supplierName: string | null,
) {
  const serializedFilters = serializeAnalyticsFilters(filters);

  return useQuery({
    queryKey: queryKeys.supplierPurchases(serializedFilters, supplierName ?? ""),
    queryFn: () => analyticsApi.getSupplierPurchases(filters, supplierName ?? ""),
    enabled: Boolean(supplierName),
    refetchInterval: 15000,
  });
}
