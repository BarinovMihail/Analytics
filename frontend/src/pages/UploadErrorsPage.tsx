import { ArrowLeft } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ErrorState } from "@/components/ErrorState";
import { ErrorTable } from "@/components/ErrorTable";
import { LoadingState } from "@/components/LoadingState";
import { useUploadErrors } from "@/hooks/useUploadErrors";
import { getApiErrorMessage } from "@/utils/api";

export function UploadErrorsPage() {
  const { batchId } = useParams();
  const parsedBatchId = Number(batchId);
  const [search, setSearch] = useState("");
  const errorsQuery = useUploadErrors(parsedBatchId);

  const filteredRows = useMemo(() => {
    const rows = errorsQuery.data ?? [];
    const normalizedSearch = search.trim().toLowerCase();

    if (!normalizedSearch) {
      return rows;
    }

    return rows.filter((row) => {
      const payload = JSON.stringify(row.rawRowJson).toLowerCase();
      return row.errorMessage.toLowerCase().includes(normalizedSearch) || payload.includes(normalizedSearch);
    });
  }, [errorsQuery.data, search]);

  if (!Number.isFinite(parsedBatchId) || parsedBatchId <= 0) {
    return <ErrorState title="Неверный batch_id" description="Проверьте адрес страницы ошибок." />;
  }

  if (errorsQuery.isLoading) {
    return <LoadingState lines={10} className="min-h-[320px]" />;
  }

  if (errorsQuery.isError) {
    return <ErrorState description={getApiErrorMessage(errorsQuery.error)} />;
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-panel lg:flex-row lg:items-end lg:justify-between">
        <div>
          <Link
            to="/uploads"
            className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 transition hover:text-slate-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Назад к истории загрузок
          </Link>
          <p className="mt-4 text-sm font-medium text-accent">Пакет #{parsedBatchId}</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Ошибки импорта</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
            Поиск работает по тексту ошибки и содержимому исходной JSON-строки.
          </p>
        </div>

        <label className="block w-full max-w-md">
          <span className="mb-2 block text-sm font-medium text-slate-600">Поиск по ошибкам</span>
          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Например, supplier или amount"
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-accent"
          />
        </label>
      </section>

      <ErrorTable rows={filteredRows} />
    </div>
  );
}
