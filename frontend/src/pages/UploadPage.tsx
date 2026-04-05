import { useState } from "react";
import { ErrorState } from "@/components/ErrorState";
import { UploadResultCard } from "@/components/UploadResultCard";
import { UploadZone } from "@/components/UploadZone";
import { useToast } from "@/components/ToastProvider";
import { useUploadFileMutation } from "@/hooks/useUploadFileMutation";
import { getApiErrorMessage } from "@/utils/api";

export function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { showToast } = useToast();
  const uploadMutation = useUploadFileMutation();
  const errorMessage = uploadMutation.isError ? getApiErrorMessage(uploadMutation.error) : null;

  async function handleUpload() {
    if (!selectedFile) {
      showToast({
        title: "Файл не выбран",
        description: "Выберите `.xlsx` файл перед отправкой.",
        variant: "error",
      });
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".xlsx")) {
      showToast({
        title: "Неверный формат файла",
        description: "Допускаются только `.xlsx` файлы.",
        variant: "error",
      });
      return;
    }

    try {
      await uploadMutation.mutateAsync(selectedFile);
      showToast({
        title: "Файл успешно загружен",
        description: "История загрузок и аналитика уже обновлены.",
        variant: "success",
      });
      setSelectedFile(null);
    } catch {
      showToast({
        title: "Ошибка загрузки",
        description: getApiErrorMessage(uploadMutation.error),
        variant: "error",
      });
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(340px,0.9fr)]">
      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-panel">
        <div>
          <p className="text-sm font-medium text-accent">Импорт закупок</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Загрузка Excel-файла</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
            Загрузите Excel-файл с закупочными данными. Backend проверит формат, обработает строки и сохранит результаты импорта.
          </p>
        </div>

        <div className="mt-6">
          <UploadZone file={selectedFile} onFileSelect={setSelectedFile} disabled={uploadMutation.isPending} />
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            className="rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-white transition hover:bg-accent-dark disabled:cursor-not-allowed disabled:opacity-70"
          >
            {uploadMutation.isPending ? "Загрузка..." : "Загрузить"}
          </button>
          <button
            type="button"
            disabled={uploadMutation.isPending}
            onClick={() => {
              setSelectedFile(null);
              uploadMutation.reset();
            }}
            className="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed"
          >
            Очистить
          </button>
        </div>

        {errorMessage ? (
          <div className="mt-6">
            <ErrorState description={errorMessage} />
          </div>
        ) : null}
      </section>

      <section className="space-y-6">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-panel">
          <p className="text-sm font-medium text-slate-500">Подсказки</p>
          <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
            <li>Используйте только файлы формата `.xlsx`.</li>
            <li>Во время отправки кнопки блокируются, чтобы избежать дублирования.</li>
            <li>После успешной загрузки история импортов и dashboard обновятся автоматически.</li>
          </ul>
        </div>

        {uploadMutation.data ? <UploadResultCard result={uploadMutation.data} /> : null}
      </section>
    </div>
  );
}
