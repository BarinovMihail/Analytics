import type { AnalyticsFilters, AnalyticsPoint, SummaryDto } from "@/types/analytics";
import { getArray, getNullableString, getNumber, getObject, getString } from "@/utils/parsers";

function normalizeFilters(filters: Partial<AnalyticsFilters>) {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, String(value));
    }
  });

  return params;
}

export function buildAnalyticsParams(filters: Partial<AnalyticsFilters>) {
  return normalizeFilters(filters);
}

export function serializeAnalyticsFilters(filters: Partial<AnalyticsFilters>) {
  return normalizeFilters(filters).toString();
}

export function adaptSummary(payload: unknown): SummaryDto {
  const data = getObject(payload);

  return {
    total_purchases_count: getNumber(data.total_purchases_count),
    total_amount: getNumber(data.total_amount),
    unique_suppliers: getNumber(data.unique_suppliers),
    latest_purchase_date: getNullableString(data.latest_purchase_date),
  };
}

export function adaptAnalyticsPoints(
  payload: unknown,
  kind: "month" | "supplier" | "category" | "status",
): AnalyticsPoint[] {
  return getArray(payload).map((item) => {
    const row = getObject(item);

    const labelByKind = {
      month: getString(row.year_month, "Без периода"),
      supplier: getString(row.supplier_name, "Без поставщика"),
      category: getString(row.category_name, "Без категории"),
      status: getString(row.status, "Без статуса"),
    };

    return {
      label: labelByKind[kind],
      purchasesCount: getNumber(row.purchases_count),
      totalAmount: getNumber(row.total_amount),
    };
  });
}
