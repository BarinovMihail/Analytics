import { apiClient } from "@/api/client";
import {
  adaptAnalyticsPoints,
  adaptSupplierPurchases,
  adaptSummary,
  buildAnalyticsParams,
} from "@/features/analytics/adapters";
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

  async getSupplierPurchases(filters: Partial<AnalyticsFilters>, supplierName: string) {
    const response = await apiClient.get("/api/analytics/supplier-purchases", {
      params: {
        ...Object.fromEntries(buildAnalyticsParams(filters)),
        supplier_name: supplierName,
      },
    });
    return adaptSupplierPurchases(response.data);
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
