import type { UploadErrorItem } from "@/types/uploads";
import { DataTable } from "@/components/DataTable";
import { formatDateTime, prettyJson } from "@/utils/format";

interface ErrorTableProps {
  rows: UploadErrorItem[];
}

export function ErrorTable({ rows }: ErrorTableProps) {
  return (
    <DataTable
      rows={rows}
      keyExtractor={(row) => row.id}
      emptyTitle="Ошибок не найдено"
      emptyDescription="У этого пакета загрузки нет ошибок импорта."
      columns={[
        {
          key: "rowNumber",
          title: "Строка",
          render: (row) => <span className="font-medium text-slate-950">{row.rowNumber}</span>,
        },
        {
          key: "message",
          title: "Ошибка",
          render: (row) => <p className="max-w-md leading-6">{row.errorMessage}</p>,
        },
        {
          key: "json",
          title: "Исходные данные",
          render: (row) => (
            <pre className="max-w-xl overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs leading-5 text-slate-100">
              {prettyJson(row.rawRowJson)}
            </pre>
          ),
        },
        {
          key: "createdAt",
          title: "Создано",
          render: (row) => formatDateTime(row.createdAt),
        },
      ]}
    />
  );
}
