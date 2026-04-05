import { apiClient } from "@/api/client";
import { adaptAnalyticsPoints, adaptSummary, buildAnalyticsParams } from "@/features/analytics/adapters";
import type { AnalyticsFilters } from "@/types/analytics";

export const analyticsApi = {
  async getSummary(filters: Partial<AnalyticsFilters>) {
    const response = await apiClient.get("/api/analytics/summary", {
      params: buildAnalyticsParams(filters),
    });
    return adaptSummary(response.data);
  },

  async getByMonth(filters: Partial<AnalyticsFilters>) {
    const response = await apiClient.get("/api/analytics/by-month", {
      params: buildAnalyticsParams(filters),
    });
    return adaptAnalyticsPoints(response.data, "month");
  },

  async getBySuppliers(filters: Partial<AnalyticsFilters>) {
    const response = await apiClient.get("/api/analytics/by-suppliers", {
      params: buildAnalyticsParams(filters),
    });
    return adaptAnalyticsPoints(response.data, "supplier");
  },

  async getByCategory(filters: Partial<AnalyticsFilters>) {
    const response = await apiClient.get("/api/analytics/by-category", {
      params: buildAnalyticsParams(filters),
    });
    return adaptAnalyticsPoints(response.data, "category");
  },

  async getByStatus(filters: Partial<AnalyticsFilters>) {
    const response = await apiClient.get("/api/analytics/by-status", {
      params: buildAnalyticsParams(filters),
    });
    return adaptAnalyticsPoints(response.data, "status");
  },
};
