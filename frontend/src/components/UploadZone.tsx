import { FileSpreadsheet, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { cn } from "@/utils/cn";

interface UploadZoneProps {
  file: File | null;
  onFileSelect: (file: File | null) => void;
  disabled?: boolean;
}

export function UploadZone({ file, onFileSelect, disabled = false }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isOver, setIsOver] = useState(false);

  function handleFile(fileToCheck: File | null | undefined) {
    if (!fileToCheck) {
      return;
    }

    if (!fileToCheck.name.toLowerCase().endsWith(".xlsx")) {
      onFileSelect(null);
      return;
    }

    onFileSelect(fileToCheck);
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => !disabled && inputRef.current?.click()}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          if (!disabled) {
            inputRef.current?.click();
          }
        }
      }}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) {
          setIsOver(true);
        }
      }}
      onDragLeave={() => setIsOver(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsOver(false);
        if (!disabled) {
          handleFile(event.dataTransfer.files?.[0]);
        }
      }}
      className={cn(
        "cursor-pointer rounded-[28px] border border-dashed px-6 py-10 text-center transition",
        isOver ? "border-accent bg-accent-soft/40" : "border-slate-300 bg-slate-50",
        disabled && "cursor-not-allowed opacity-60",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx"
        disabled={disabled}
        onChange={(event) => handleFile(event.target.files?.[0])}
        className="hidden"
      />

      <div className="mx-auto flex max-w-xl flex-col items-center">
        <div className="rounded-3xl bg-white p-4 text-accent shadow-panel">
          <UploadCloud className="h-8 w-8" />
        </div>
        <h3 className="mt-5 text-xl font-semibold text-slate-950">
          Перетащите `.xlsx` файл сюда или выберите вручную
        </h3>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Поддерживаются только Excel-файлы формата `.xlsx`. После загрузки данные будут обработаны backend-сервисом.
        </p>

        <button
          type="button"
          disabled={disabled}
          className="mt-6 rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-white transition hover:bg-accent-dark disabled:cursor-not-allowed disabled:opacity-70"
        >
          Выбрать файл
        </button>

        <div className="mt-5 flex min-h-10 items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
          <FileSpreadsheet className="h-4 w-4 text-accent" />
          <span>{file?.name ?? "Файл пока не выбран"}</span>
        </div>
      </div>
    </div>
  );
}
