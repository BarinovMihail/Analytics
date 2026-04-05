import type { AnalyticsFilters } from "@/types/analytics";

interface FiltersPanelProps {
  value: AnalyticsFilters;
  onChange: (next: AnalyticsFilters) => void;
  onSubmit: () => void;
  onReset: () => void;
}

export function FiltersPanel({ value, onChange, onSubmit, onReset }: FiltersPanelProps) {
  function updateField<K extends keyof AnalyticsFilters>(field: K, fieldValue: AnalyticsFilters[K]) {
    onChange({
      ...value,
      [field]: fieldValue,
    });
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-panel">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-950">Фильтры аналитики</h3>
          <p className="mt-1 text-sm text-slate-500">
            Отфильтруйте данные по периоду и поставщику.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Дата от</span>
            <input
              type="date"
              value={value.date_from}
              onChange={(event) => updateField("date_from", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-accent"
            />
          </label>
          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Дата до</span>
            <input
              type="date"
              value={value.date_to}
              onChange={(event) => updateField("date_to", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-accent"
            />
          </label>
          <label className="space-y-2 text-sm">
            <span className="font-medium text-slate-600">Поставщик</span>
            <input
              type="text"
              value={value.supplier_name}
              placeholder="Например, ООО Альфа"
              onChange={(event) => updateField("supplier_name", event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-accent"
            />
          </label>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onSubmit}
          className="rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-white transition hover:bg-accent-dark"
        >
          Применить фильтры
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          Сбросить
        </button>
      </div>
    </section>
  );
}
