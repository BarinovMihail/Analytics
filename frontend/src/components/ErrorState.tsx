import type { ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  description: string;
  action?: ReactNode;
}

export function ErrorState({
  title = "Не удалось загрузить данные",
  description,
  action,
}: ErrorStateProps) {
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-rose-950">
      <div className="flex items-start gap-4">
        <div className="rounded-2xl bg-white p-3 text-rose-600">
          <AlertTriangle className="h-5 w-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="mt-2 text-sm leading-6 text-rose-900/80">{description}</p>
          {action ? <div className="mt-4">{action}</div> : null}
        </div>
      </div>
    </div>
  );
}
