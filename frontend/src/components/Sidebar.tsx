import { BarChart3, FileWarning, LayoutDashboard, UploadCloud } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/utils/cn";

const items = [
  { to: "/", label: "Главная", icon: LayoutDashboard },
  { to: "/upload", label: "Загрузка файла", icon: UploadCloud },
  { to: "/uploads", label: "История загрузок", icon: FileWarning },
];

export function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 border-r border-slate-200 bg-white/90 px-5 py-6 lg:block">
      <div className="rounded-3xl bg-ink px-5 py-6 text-white">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-accent-soft/20 p-3">
            <BarChart3 className="h-6 w-6 text-teal-200" />
          </div>
          <div>
            <p className="text-sm text-slate-300">Внутренний сервис</p>
            <h1 className="text-lg font-semibold">Procurement Analytics</h1>
          </div>
        </div>
        <p className="mt-4 text-sm leading-6 text-slate-300">
          Загрузка Excel-файлов, история импортов и аналитика закупок в одном интерфейсе.
        </p>
      </div>

      <nav className="mt-8 space-y-2">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                  isActive
                    ? "bg-accent text-white shadow-panel"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
                )
              }
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
