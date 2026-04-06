import type { AnalyticsFilters } from "@/types/analytics";

interface DashboardFilterBarProps {
  value: AnalyticsFilters;
  onChange: (next: AnalyticsFilters) => void;
  onSubmit: () => void;
  onReset: () => void;
}

const statusOptions = [
  { value: "", label: "Все активности" },
  { value: "active", label: "Активные" },
  { value: "watch", label: "Требуют внимания" },
  { value: "no_amount", label: "Без суммы" },
];

export function DashboardFilterBar({
  value,
  onChange,
  onSubmit,
  onReset,
}: DashboardFilterBarProps) {
  function updateField<K extends keyof AnalyticsFilters>(field: K, fieldValue: AnalyticsFilters[K]) {
    onChange({
      ...value,
      [field]: fieldValue,
    });
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            Фильтры реестра
          </p>
          <h3 className="mt-1 text-lg font-semibold text-slate-950">Рабочая выборка поставщиков</h3>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Дата от</span>
            <input
              type="date"
              value={value.date_from}
              onChange={(event) => updateField("date_from", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-2.5 outline-none transition focus:border-accent"
            />
          </label>

          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Дата до</span>
            <input
              type="date"
              value={value.date_to}
              onChange={(event) => updateField("date_to", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-2.5 outline-none transition focus:border-accent"
            />
          </label>

          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Поставщик</span>
            <input
              type="text"
              value={value.supplier_name}
              placeholder="Найти по названию"
              onChange={(event) => updateField("supplier_name", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-2.5 outline-none transition focus:border-accent"
            />
          </label>

          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Категория</span>
            <input
              type="text"
              value={value.category_name}
              placeholder="Фильтр по категории"
              onChange={(event) => updateField("category_name", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-2.5 outline-none transition focus:border-accent"
            />
          </label>

          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Активность</span>
            <select
              value={value.status}
              onChange={(event) => updateField("status", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-2.5 outline-none transition focus:border-accent"
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onSubmit}
          className="rounded-2xl bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Применить
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-2xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          Сбросить
        </button>
      </div>
    </section>
  );
}
