export const queryKeys = {
  health: ["health"] as const,
  summary: (filters: string) => ["analytics", "summary", filters] as const,
  byMonth: (filters: string) => ["analytics", "by-month", filters] as const,
  bySuppliers: (filters: string) => ["analytics", "by-suppliers", filters] as const,
  supplierPurchases: (filters: string, supplierName: string) =>
    ["analytics", "supplier-purchases", filters, supplierName] as const,
  byCategory: (filters: string) => ["analytics", "by-category", filters] as const,
  byStatus: (filters: string) => ["analytics", "by-status", filters] as const,
  uploads: ["uploads"] as const,
  uploadErrors: (batchId: number) => ["uploads", batchId, "errors"] as const,
};
