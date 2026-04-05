import { Menu, ServerCrash, ShieldCheck } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useHealth } from "@/hooks/useHealth";
import { cn } from "@/utils/cn";

const titles: Record<string, string> = {
  "/": "Главная",
  "/upload": "Загрузка Excel",
  "/uploads": "История загрузок",
};

export function Header() {
  const location = useLocation();
  const { data } = useHealth();
  const title =
    titles[location.pathname] ??
    (location.pathname.includes("/errors") ? "Ошибки импорта" : "Procurement Analytics");
  const isHealthy = data?.status === "ok" && data.database === "ok";

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/85 backdrop-blur">
      <div className="flex min-h-20 items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <Link
            to="/"
            className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Link>
          <div>
            <p className="text-sm text-slate-500">Панель управления закупками</p>
            <h2 className="text-2xl font-semibold tracking-tight text-slate-950">{title}</h2>
          </div>
        </div>

        <div
          className={cn(
            "inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium",
            isHealthy ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700",
          )}
        >
          {isHealthy ? <ShieldCheck className="h-4 w-4" /> : <ServerCrash className="h-4 w-4" />}
          <span>API {isHealthy ? "доступен" : "проверяется"}</span>
        </div>
      </div>
    </header>
  );
}
