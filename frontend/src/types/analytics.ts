export interface AnalyticsFilters {
  date_from: string;
  date_to: string;
  supplier_name: string;
  category_name: string;
  status: string;
}

export interface SummaryDto {
  total_purchases_count: number;
  total_amount: number;
  unique_suppliers: number;
  latest_purchase_date: string | null;
}

export interface AnalyticsPoint {
  label: string;
  purchasesCount: number;
  totalAmount: number;
}

export type SupplierActivity = "active" | "watch" | "no_amount";

export interface SupplierRegistryItem {
  id: string;
  supplierName: string;
  supplierInn: string | null;
  purchasesCount: number;
  totalAmount: number;
  latestPurchaseDate: string | null;
  primaryCategory: string | null;
  activity: SupplierActivity;
}

export interface SupplierPurchaseItem {
  id: number;
  batchId: number;
  itemName: string;
  itemCode: string | null;
  categoryName: string | null;
  amount: number | null;
  purchaseDate: string | null;
  deliveryDate: string | null;
  status: string | null;
  createdAt: string | null;
}

export type SupplierSortKey =
  | "supplierName"
  | "supplierInn"
  | "purchasesCount"
  | "totalAmount"
  | "latestPurchaseDate"
  | "primaryCategory"
  | "activity";
