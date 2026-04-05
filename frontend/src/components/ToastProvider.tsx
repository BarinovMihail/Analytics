import { createContext, PropsWithChildren, useCallback, useContext, useMemo, useState } from "react";
import { CheckCircle2, CircleAlert, X } from "lucide-react";
import { cn } from "@/utils/cn";

type ToastVariant = "success" | "error";

interface ToastItem {
  id: number;
  title: string;
  description?: string;
  variant: ToastVariant;
}

interface ToastContextValue {
  showToast: (input: Omit<ToastItem, "id">) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: PropsWithChildren) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    (input: Omit<ToastItem, "id">) => {
      const id = Date.now() + Math.random();
      const toast = { ...input, id };
      setToasts((current) => [...current, toast]);
      window.setTimeout(() => removeToast(id), 4200);
    },
    [removeToast],
  );

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-full max-w-sm flex-col gap-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              "pointer-events-auto rounded-2xl border p-4 shadow-panel backdrop-blur",
              toast.variant === "success"
                ? "border-emerald-200 bg-emerald-50 text-emerald-950"
                : "border-rose-200 bg-rose-50 text-rose-950",
            )}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                {toast.variant === "success" ? (
                  <CheckCircle2 className="h-5 w-5" />
                ) : (
                  <CircleAlert className="h-5 w-5" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold">{toast.title}</p>
                {toast.description ? (
                  <p className="mt-1 text-sm opacity-80">{toast.description}</p>
                ) : null}
              </div>
              <button
                type="button"
                onClick={() => removeToast(toast.id)}
                className="rounded-full p-1 opacity-70 transition hover:bg-black/5 hover:opacity-100"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }

  return context;
}
