import { Link } from "react-router-dom";
import type { UploadResult } from "@/types/uploads";
import { formatNumber } from "@/utils/format";

interface UploadResultCardProps {
  result: UploadResult;
}

export function UploadResultCard({ result }: UploadResultCardProps) {
  return (
    <section className="rounded-3xl border border-emerald-200 bg-emerald-50 p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-medium text-emerald-700">Файл загружен успешно</p>
          <h3 className="mt-2 text-2xl font-semibold text-emerald-950">{result.fileName}</h3>
          <p className="mt-2 text-sm text-emerald-900/80">
            Пакет #{result.batchId} обработан со статусом `{result.status}`.
          </p>
        </div>

        {result.rowsError > 0 ? (
          <Link
            to={`/uploads/${result.batchId}/errors`}
            className="inline-flex rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-100"
          >
            Посмотреть ошибки
          </Link>
        ) : null}
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl bg-white p-4">
          <p className="text-sm text-slate-500">Всего строк</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{formatNumber(result.rowsTotal)}</p>
        </div>
        <div className="rounded-2xl bg-white p-4">
          <p className="text-sm text-slate-500">Успешно</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{formatNumber(result.rowsSuccess)}</p>
        </div>
        <div className="rounded-2xl bg-white p-4">
          <p className="text-sm text-slate-500">С ошибками</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{formatNumber(result.rowsError)}</p>
        </div>
        <div className="rounded-2xl bg-white p-4">
          <p className="text-sm text-slate-500">Дубликаты</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{formatNumber(result.rowsDuplicate)}</p>
        </div>
      </div>
    </section>
  );
}
