import { PackageOpen, X } from "lucide-react";
import type { SupplierPurchaseItem } from "@/types/analytics";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { formatCurrency, formatDate, formatDateTime, formatEmpty } from "@/utils/format";

interface SupplierPurchasesPanelProps {
  supplierName: string | null;
  purchases: SupplierPurchaseItem[] | undefined;
  isLoading: boolean;
  errorMessage?: string;
  onClose: () => void;
}

export function SupplierPurchasesPanel({
  supplierName,
  purchases,
  isLoading,
  errorMessage,
  onClose,
}: SupplierPurchasesPanelProps) {
  if (!supplierName) {
    return (
      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <EmptyState
          title="Выберите поставщика"
          description="Нажмите на строку в реестре, и здесь появится список закупок выбранного поставщика."
        />
      </section>
    );
  }

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white shadow-sm">
      <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            Детализация поставщика
          </p>
          <h3 className="mt-1 text-xl font-semibold text-slate-950">{supplierName}</h3>
          <p className="mt-1 text-sm text-slate-500">
            Список закупок по выбранному поставщику в текущей выборке.
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="inline-flex rounded-2xl border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-50 hover:text-slate-900"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {isLoading ? (
        <div className="p-5">
          <LoadingState lines={8} className="min-h-[320px]" />
        </div>
      ) : errorMessage ? (
        <div className="p-5">
          <ErrorState title="Не удалось загрузить закупки поставщика" description={errorMessage} />
        </div>
      ) : !purchases?.length ? (
        <div className="p-5">
          <EmptyState
            title="Закупки не найдены"
            description="У выбранного поставщика нет закупок в рамках текущих фильтров."
          />
        </div>
      ) : (
        <div className="max-h-[480px] overflow-auto">
          <table className="min-w-full border-separate border-spacing-0">
            <thead className="sticky top-0 z-10 bg-white">
              <tr>
                <th className="border-b border-slate-200 px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Закупка
                </th>
                <th className="border-b border-slate-200 px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Код
                </th>
                <th className="border-b border-slate-200 px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Категория
                </th>
                <th className="border-b border-slate-200 px-5 py-3 text-right text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Сумма
                </th>
                <th className="border-b border-slate-200 px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Дата закупки
                </th>
                <th className="border-b border-slate-200 px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Поставка
                </th>
                <th className="border-b border-slate-200 px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Статус
                </th>
              </tr>
            </thead>
            <tbody>
              {purchases.map((purchase) => (
                <tr key={purchase.id} className="hover:bg-slate-50/80">
                  <td className="border-b border-slate-100 px-5 py-4 align-top">
                    <div className="max-w-[320px]">
                      <div className="flex items-start gap-3">
                        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-2 text-slate-500">
                          <PackageOpen className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-950">{purchase.itemName}</p>
                          <p className="mt-1 text-xs text-slate-500">
                            Batch #{purchase.batchId} • {formatDateTime(purchase.createdAt)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="border-b border-slate-100 px-5 py-4 text-sm text-slate-600">
                    {formatEmpty(purchase.itemCode)}
                  </td>
                  <td className="border-b border-slate-100 px-5 py-4 text-sm text-slate-600">
                    {formatEmpty(purchase.categoryName)}
                  </td>
                  <td className="border-b border-slate-100 px-5 py-4 text-right text-sm font-medium text-slate-900">
                    {formatCurrency(purchase.amount)}
                  </td>
                  <td className="border-b border-slate-100 px-5 py-4 text-sm text-slate-600">
                    {formatDate(purchase.purchaseDate)}
                  </td>
                  <td className="border-b border-slate-100 px-5 py-4 text-sm text-slate-600">
                    {formatDate(purchase.deliveryDate)}
                  </td>
                  <td className="border-b border-slate-100 px-5 py-4 text-sm text-slate-600">
                    {formatEmpty(purchase.status)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
