import { Link } from "react-router-dom";
import { DataTable } from "@/components/DataTable";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { useUploads } from "@/hooks/useUploads";
import type { UploadBatch } from "@/types/uploads";
import { getApiErrorMessage } from "@/utils/api";
import { formatDateTime, formatNumber } from "@/utils/format";

function statusBadge(status: string) {
  const normalized = status.toLowerCase();
  const color =
    normalized.includes("error") || normalized.includes("fail")
      ? "bg-rose-50 text-rose-700"
      : "bg-emerald-50 text-emerald-700";

  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${color}`}>{status}</span>;
}

export function UploadsPage() {
  const uploadsQuery = useUploads();

  if (uploadsQuery.isLoading) {
    return <LoadingState lines={10} className="min-h-[320px]" />;
  }

  if (uploadsQuery.isError) {
    return <ErrorState description={getApiErrorMessage(uploadsQuery.error)} />;
  }

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm font-medium text-accent">Импорт</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">История загрузок</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          Последние пакеты импорта, статусы обработки и количество строк с ошибками.
        </p>
      </section>

      <DataTable<UploadBatch>
        rows={uploadsQuery.data ?? []}
        keyExtractor={(row) => row.id}
        emptyTitle="Загрузок пока нет"
        emptyDescription="После первой загрузки Excel-файла история импортов появится здесь."
        columns={[
          {
            key: "id",
            title: "ID",
            render: (row) => <span className="font-semibold text-slate-950">#{row.id}</span>,
          },
          { key: "file", title: "Файл", render: (row) => row.fileName },
          { key: "uploadedAt", title: "Загружен", render: (row) => formatDateTime(row.uploadedAt) },
          { key: "status", title: "Статус", render: (row) => statusBadge(row.status) },
          { key: "rowsTotal", title: "Всего", render: (row) => formatNumber(row.rowsTotal) },
          { key: "rowsSuccess", title: "Успешно", render: (row) => formatNumber(row.rowsSuccess) },
          { key: "rowsError", title: "Ошибки", render: (row) => formatNumber(row.rowsError) },
          {
            key: "actions",
            title: "Действие",
            render: (row) =>
              row.rowsError > 0 ? (
                <Link
                  to={`/uploads/${row.id}/errors`}
                  className="inline-flex rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                >
                  Посмотреть ошибки
                </Link>
              ) : (
                <span className="text-slate-400">Нет ошибок</span>
              ),
          },
        ]}
      />
    </div>
  );
}
