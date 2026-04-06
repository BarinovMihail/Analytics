import type {
  AnalyticsFilters,
  AnalyticsPoint,
  SummaryDto,
  SupplierActivity,
  SupplierPurchaseItem,
  SupplierRegistryItem,
} from "@/types/analytics";
import { getArray, getNullableString, getNumber, getObject, getString } from "@/utils/parsers";

function normalizeStatusLabel(value: string) {
  const normalized = value.split(/[.;]/, 1)[0]?.trim();
  return normalized || "Без статуса";
}

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
  const points = getArray(payload).map((item) => {
    const row = getObject(item);

    const labelByKind = {
      month: getString(row.year_month, "Без периода"),
      supplier: getString(row.supplier_name, "Без поставщика"),
      category: getString(row.category_name, "Без категории"),
      status: normalizeStatusLabel(getString(row.status, "Без статуса")),
    };

    return {
      label: labelByKind[kind],
      purchasesCount: getNumber(row.purchases_count),
      totalAmount: getNumber(row.total_amount),
    };
  });

  if (kind !== "status") {
    return points;
  }

  const aggregated = new Map<string, AnalyticsPoint>();
  for (const point of points) {
    const existing = aggregated.get(point.label);
    if (existing) {
      existing.purchasesCount += point.purchasesCount;
      existing.totalAmount += point.totalAmount;
      continue;
    }
    aggregated.set(point.label, { ...point });
  }

  return Array.from(aggregated.values()).sort((left, right) => right.totalAmount - left.totalAmount);
}

function extractInnFromSupplierName(value: string) {
  const match = value.match(/\b(\d{10}|\d{12})\b/);
  return match?.[1] ?? null;
}

function resolveSupplierActivity(point: AnalyticsPoint): SupplierActivity {
  if (point.totalAmount <= 0) {
    return "no_amount";
  }
  if (point.purchasesCount >= 5) {
    return "active";
  }
  return "watch";
}

export function adaptSupplierRegistry(
  suppliers: AnalyticsPoint[],
  filters: Partial<AnalyticsFilters>,
): SupplierRegistryItem[] {
  return suppliers.map((supplier) => ({
    id: supplier.label,
    supplierName: supplier.label,
    supplierInn: extractInnFromSupplierName(supplier.label),
    purchasesCount: supplier.purchasesCount,
    totalAmount: supplier.totalAmount,
    latestPurchaseDate: null,
    primaryCategory: filters.category_name || null,
    activity: resolveSupplierActivity(supplier),
  }));
}

export function adaptSupplierPurchases(payload: unknown): SupplierPurchaseItem[] {
  return getArray(payload).map((item) => {
    const row = getObject(item);

    return {
      id: getNumber(row.id),
      batchId: getNumber(row.batch_id),
      itemName: getString(row.item_name, "Без наименования"),
      itemCode: getNullableString(row.item_code),
      categoryName: getNullableString(row.category_name),
      amount: row.amount === null || row.amount === undefined ? null : getNumber(row.amount),
      purchaseDate: getNullableString(row.purchase_date),
      deliveryDate: getNullableString(row.delivery_date),
      status: getNullableString(row.status),
      createdAt: getNullableString(row.created_at),
    };
  });
}
