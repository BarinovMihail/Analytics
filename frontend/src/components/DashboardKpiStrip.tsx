import { CalendarClock, CircleDollarSign, FileStack, Users } from "lucide-react";
import type { SummaryDto } from "@/types/analytics";
import { formatCurrency, formatDate, formatNumber } from "@/utils/format";

interface DashboardKpiStripProps {
  summary: SummaryDto | undefined;
}

const kpiConfig = [
  {
    key: "suppliers",
    title: "Всего поставщиков",
    icon: Users,
    getValue: (summary: SummaryDto | undefined) => formatNumber(summary?.unique_suppliers),
  },
  {
    key: "purchases",
    title: "Всего закупок",
    icon: FileStack,
    getValue: (summary: SummaryDto | undefined) => formatNumber(summary?.total_purchases_count),
  },
  {
    key: "amount",
    title: "Общая сумма",
    icon: CircleDollarSign,
    getValue: (summary: SummaryDto | undefined) => formatCurrency(summary?.total_amount),
  },
  {
    key: "latest",
    title: "Последняя закупка",
    icon: CalendarClock,
    getValue: (summary: SummaryDto | undefined) => formatDate(summary?.latest_purchase_date),
  },
];

export function DashboardKpiStrip({ summary }: DashboardKpiStripProps) {
  return (
    <section className="grid gap-3 md:grid-cols-2 2xl:grid-cols-4">
      {kpiConfig.map((item) => {
        const Icon = item.icon;
        return (
          <article
            key={item.key}
            className="rounded-3xl border border-slate-200 bg-white px-4 py-4 shadow-sm"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-slate-500">{item.title}</p>
                <p className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
                  {item.getValue(summary)}
                </p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-slate-700">
                <Icon className="h-5 w-5" />
              </div>
            </div>
          </article>
        );
      })}
    </section>
  );
}
