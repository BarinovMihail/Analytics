import { ArrowRight, UploadCloud } from "lucide-react";
import { Link } from "react-router-dom";
import { useMemo, useState } from "react";
import { DashboardFilterBar } from "@/components/DashboardFilterBar";
import { DashboardKpiStrip } from "@/components/DashboardKpiStrip";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { SecondaryAnalyticsSection } from "@/components/SecondaryAnalyticsSection";
import { SupplierPurchasesPanel } from "@/components/SupplierPurchasesPanel";
import { SuppliersTable } from "@/components/SuppliersTable";
import { useAnalyticsByMonth } from "@/hooks/useAnalyticsByMonth";
import { useAnalyticsBySuppliers } from "@/hooks/useAnalyticsBySuppliers";
import { useSupplierPurchases } from "@/hooks/useSupplierPurchases";
import { useSummary } from "@/hooks/useSummary";
import { adaptSupplierRegistry } from "@/features/analytics/adapters";
import type { AnalyticsFilters } from "@/types/analytics";
import { getApiErrorMessage } from "@/utils/api";

const defaultFilters: AnalyticsFilters = {
  date_from: "",
  date_to: "",
  supplier_name: "",
  category_name: "",
  status: "",
};

export function DashboardPage() {
  const [draftFilters, setDraftFilters] = useState(defaultFilters);
  const [appliedFilters, setAppliedFilters] = useState(defaultFilters);
  const [selectedSupplierName, setSelectedSupplierName] = useState<string | null>(null);

  const summaryQuery = useSummary(appliedFilters);
  const suppliersQuery = useAnalyticsBySuppliers(appliedFilters);
  const monthQuery = useAnalyticsByMonth(appliedFilters);
  const supplierPurchasesQuery = useSupplierPurchases(appliedFilters, selectedSupplierName);

  const supplierRegistry = useMemo(
    () => adaptSupplierRegistry(suppliersQuery.data ?? [], appliedFilters),
    [appliedFilters, suppliersQuery.data],
  );

  const sharedErrorMessage = getApiErrorMessage(
    summaryQuery.error ?? suppliersQuery.error ?? monthQuery.error,
  );

  return (
    <div className="space-y-5">
      <section className="flex flex-wrap gap-3">
        <Link
          to="/upload"
          className="inline-flex items-center gap-2 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          <UploadCloud className="h-4 w-4" />
          Загрузить файл
        </Link>
        <Link
          to="/uploads"
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          История загрузок
          <ArrowRight className="h-4 w-4" />
        </Link>
      </section>

      <DashboardFilterBar
        value={draftFilters}
        onChange={setDraftFilters}
        onSubmit={() => setAppliedFilters(draftFilters)}
        onReset={() => {
          setDraftFilters(defaultFilters);
          setAppliedFilters(defaultFilters);
        }}
      />

      {summaryQuery.isLoading ? (
        <section className="grid gap-3 md:grid-cols-2 2xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <LoadingState key={index} lines={3} />
          ))}
        </section>
      ) : summaryQuery.isError ? (
        <ErrorState title="Не удалось загрузить KPI" description={sharedErrorMessage} />
      ) : (
        <DashboardKpiStrip summary={summaryQuery.data} />
      )}

      <SuppliersTable
        suppliers={supplierRegistry}
        filters={appliedFilters}
        isLoading={suppliersQuery.isLoading}
        errorMessage={suppliersQuery.isError ? sharedErrorMessage : undefined}
        selectedSupplierName={selectedSupplierName}
        onSelectSupplier={setSelectedSupplierName}
      />

      <SupplierPurchasesPanel
        supplierName={selectedSupplierName}
        purchases={supplierPurchasesQuery.data}
        isLoading={supplierPurchasesQuery.isLoading}
        errorMessage={
          supplierPurchasesQuery.isError
            ? getApiErrorMessage(supplierPurchasesQuery.error)
            : undefined
        }
        onClose={() => setSelectedSupplierName(null)}
      />

      {monthQuery.isError ? (
        <ErrorState
          title="Не удалось загрузить вторичную аналитику"
          description={sharedErrorMessage}
        />
      ) : (
        <SecondaryAnalyticsSection
          monthData={monthQuery.data}
          supplierData={suppliersQuery.data}
          isMonthLoading={monthQuery.isLoading}
          isSuppliersLoading={suppliersQuery.isLoading}
        />
      )}
    </div>
  );
}
