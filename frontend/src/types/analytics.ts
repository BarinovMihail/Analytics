export interface AnalyticsFilters {
  date_from: string;
  date_to: string;
  supplier_name: string;
  category_name: string;
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
