import { ChevronDown, ChevronLeft, ChevronRight, Search, ArrowUpDown } from "lucide-react";
import { useMemo, useState } from "react";
import type {
  AnalyticsFilters,
  SupplierRegistryItem,
  SupplierSortKey,
} from "@/types/analytics";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { cn } from "@/utils/cn";
import { formatCurrency, formatDate, formatNumber } from "@/utils/format";

interface SuppliersTableProps {
  suppliers: SupplierRegistryItem[];
  filters: AnalyticsFilters;
  isLoading: boolean;
  errorMessage?: string;
  selectedSupplierName: string | null;
  onSelectSupplier: (supplierName: string) => void;
}

type SortDirection = "asc" | "desc";

const pageSize = 12;

const activityMeta: Record<
  SupplierRegistryItem["activity"],
  { label: string; className: string }
> = {
  active: {
    label: "Активный",
    className: "bg-emerald-50 text-emerald-700 border-emerald-100",
  },
  watch: {
    label: "Требует внимания",
    className: "bg-amber-50 text-amber-700 border-amber-100",
  },
  no_amount: {
    label: "Без суммы",
    className: "bg-slate-100 text-slate-600 border-slate-200",
  },
};

export function SuppliersTable({
  suppliers,
  filters,
  isLoading,
  errorMessage,
  selectedSupplierName,
  onSelectSupplier,
}: SuppliersTableProps) {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<SupplierSortKey>("totalAmount");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [page, setPage] = useState(1);

  const filteredSuppliers = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return suppliers
      .filter((supplier) => {
        if (filters.status && supplier.activity !== filters.status) {
          return false;
        }

        if (!normalizedSearch) {
          return true;
        }

        return (
          supplier.supplierName.toLowerCase().includes(normalizedSearch) ||
          (supplier.supplierInn ?? "").toLowerCase().includes(normalizedSearch)
        );
      })
      .sort((left, right) => compareSuppliers(left, right, sortKey, sortDirection));
  }, [filters.status, search, sortDirection, sortKey, suppliers]);

  const totalPages = Math.max(1, Math.ceil(filteredSuppliers.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const pageRows = filteredSuppliers.slice((safePage - 1) * pageSize, safePage * pageSize);

  function handleSort(nextKey: SupplierSortKey) {
    if (sortKey === nextKey) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }

    setSortKey(nextKey);
    setSortDirection(nextKey === "supplierName" || nextKey === "supplierInn" ? "asc" : "desc");
  }

  if (isLoading) {
    return <LoadingState lines={10} className="min-h-[520px]" />;
  }

  if (errorMessage) {
    return <ErrorState title="Не удалось загрузить реестр поставщиков" description={errorMessage} />;
  }

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-4 border-b border-slate-200 px-5 py-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            Главный реестр
          </p>
          <h3 className="mt-1 text-xl font-semibold text-slate-950">Все поставщики</h3>
          <p className="mt-1 text-sm text-slate-500">
            Основной рабочий список для поиска, сортировки и будущего перехода к карточке поставщика.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label className="relative min-w-[280px]">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder="Быстрый поиск по поставщику"
              className="w-full rounded-2xl border border-slate-200 bg-white py-2.5 pl-11 pr-4 text-sm outline-none transition focus:border-accent"
            />
          </label>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-600">
            Найдено: <span className="font-semibold text-slate-950">{formatNumber(filteredSuppliers.length)}</span>
          </div>
        </div>
      </div>

      {!filteredSuppliers.length ? (
        <div className="p-5">
          <EmptyState
            title="Поставщики не найдены"
            description="Измените фильтры или попробуйте другой поисковый запрос по реестру."
          />
        </div>
      ) : (
        <>
          <div className="max-h-[720px] overflow-auto">
            <table className="min-w-full border-separate border-spacing-0">
              <thead className="sticky top-0 z-10 bg-white">
                <tr className="text-left">
                  <HeaderCell title="Поставщик" onClick={() => handleSort("supplierName")} />
                  <HeaderCell title="Кол-во закупок" onClick={() => handleSort("purchasesCount")} align="right" />
                  <HeaderCell title="Общая сумма" onClick={() => handleSort("totalAmount")} align="right" />
                  <HeaderCell title="Последняя закупка" onClick={() => handleSort("latestPurchaseDate")} />
                  <HeaderCell title="Активность" onClick={() => handleSort("activity")} />
                  <th className="border-b border-slate-200 bg-white px-5 py-3 text-right text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                    Дальше
                  </th>
                </tr>
              </thead>
              <tbody>
                {pageRows.map((supplier) => {
                  const activity = activityMeta[supplier.activity];

                  return (
                    <tr key={supplier.id} className="group hover:bg-slate-50/80">
                      <td className="border-b border-slate-100 px-5 py-4 align-top">
                        <div className="max-w-[340px]">
                          <button
                            type="button"
                            onClick={() => onSelectSupplier(supplier.supplierName)}
                            className="text-left"
                          >
                            <p
                              className={cn(
                                "font-semibold transition",
                                selectedSupplierName === supplier.supplierName
                                  ? "text-accent"
                                  : "text-slate-950 group-hover:text-accent",
                              )}
                            >
                              {supplier.supplierName}
                            </p>
                          </button>
                          <p className="mt-1 text-xs text-slate-500">
                            Нажмите на поставщика, чтобы открыть его закупки.
                          </p>
                        </div>
                      </td>
                      <td className="border-b border-slate-100 px-5 py-4 text-right text-sm font-medium text-slate-900">
                        {formatNumber(supplier.purchasesCount)}
                      </td>
                      <td className="border-b border-slate-100 px-5 py-4 text-right text-sm font-medium text-slate-900">
                        {formatCurrency(supplier.totalAmount)}
                      </td>
                      <td className="border-b border-slate-100 px-5 py-4 text-sm text-slate-600">
                        {formatDate(supplier.latestPurchaseDate)}
                      </td>
                      <td className="border-b border-slate-100 px-5 py-4 text-sm">
                        <span
                          className={cn(
                            "inline-flex rounded-full border px-3 py-1 text-xs font-semibold",
                            activity.className,
                          )}
                        >
                          {activity.label}
                        </span>
                      </td>
                      <td className="border-b border-slate-100 px-5 py-4 text-right">
                        <button
                          type="button"
                          onClick={() => onSelectSupplier(supplier.supplierName)}
                          className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-white hover:text-slate-900"
                        >
                          Открыть
                          <ChevronDown className="h-4 w-4 -rotate-90" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-3 border-t border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-slate-500">
              Показаны <span className="font-semibold text-slate-950">{formatNumber(pageRows.length)}</span> из{" "}
              <span className="font-semibold text-slate-950">{formatNumber(filteredSuppliers.length)}</span> поставщиков
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPage((current) => Math.max(1, current - 1))}
                disabled={safePage <= 1}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <ChevronLeft className="h-4 w-4" />
                Назад
              </button>
              <div className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700">
                {safePage} / {totalPages}
              </div>
              <button
                type="button"
                onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
                disabled={safePage >= totalPages}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Вперёд
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

function HeaderCell({
  title,
  onClick,
  align = "left",
}: {
  title: string;
  onClick: () => void;
  align?: "left" | "right";
}) {
  return (
    <th
      className={cn(
        "border-b border-slate-200 bg-white px-5 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400",
        align === "right" ? "text-right" : "text-left",
      )}
    >
      <button
        type="button"
        onClick={onClick}
        className={cn(
          "inline-flex items-center gap-2 transition hover:text-slate-700",
          align === "right" ? "ml-auto" : "",
        )}
      >
        <span>{title}</span>
        <ArrowUpDown className="h-3.5 w-3.5" />
      </button>
    </th>
  );
}

function compareSuppliers(
  left: SupplierRegistryItem,
  right: SupplierRegistryItem,
  sortKey: SupplierSortKey,
  sortDirection: SortDirection,
) {
  const direction = sortDirection === "asc" ? 1 : -1;

  const leftValue = left[sortKey] ?? "";
  const rightValue = right[sortKey] ?? "";

  if (typeof leftValue === "number" && typeof rightValue === "number") {
    return (leftValue - rightValue) * direction;
  }

  return String(leftValue).localeCompare(String(rightValue), "ru") * direction;
}
