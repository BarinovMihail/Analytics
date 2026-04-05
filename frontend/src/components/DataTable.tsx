import type { TableColumn } from "@/types/common";
import { EmptyState } from "@/components/EmptyState";
import { cn } from "@/utils/cn";

interface DataTableProps<T> {
  columns: TableColumn<T>[];
  rows: T[];
  keyExtractor: (row: T) => string | number;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function DataTable<T>({
  columns,
  rows,
  keyExtractor,
  emptyTitle = "Нет данных",
  emptyDescription = "Таблица будет заполнена после появления данных.",
}: DataTableProps<T>) {
  if (!rows.length) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={cn(
                    "px-5 py-4 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500",
                    column.className,
                  )}
                >
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row) => (
              <tr key={keyExtractor(row)} className="transition hover:bg-slate-50/70">
                {columns.map((column) => (
                  <td key={column.key} className="px-5 py-4 align-top text-sm text-slate-700">
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
