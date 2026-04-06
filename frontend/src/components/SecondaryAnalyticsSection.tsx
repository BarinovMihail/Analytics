import type { EChartsOption } from "echarts";
import { ChartCard } from "@/components/ChartCard";
import { LoadingState } from "@/components/LoadingState";
import type { AnalyticsPoint } from "@/types/analytics";
import { formatMonthLabel } from "@/utils/format";

interface SecondaryAnalyticsSectionProps {
  monthData: AnalyticsPoint[] | undefined;
  supplierData: AnalyticsPoint[] | undefined;
  isMonthLoading: boolean;
  isSuppliersLoading: boolean;
}

function chartBase(): Pick<EChartsOption, "grid" | "tooltip"> {
  return {
    grid: {
      left: 16,
      right: 16,
      top: 32,
      bottom: 8,
      containLabel: true,
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#0f172a",
      borderWidth: 0,
      textStyle: { color: "#f8fafc" },
    },
  };
}

function buildMonthOption(points: AnalyticsPoint[]): EChartsOption {
  return {
    ...chartBase(),
    xAxis: {
      type: "category",
      data: points.map((point) => formatMonthLabel(point.label)),
      axisLine: { lineStyle: { color: "#cbd5e1" } },
      axisLabel: { color: "#475569" },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#475569" },
      splitLine: { lineStyle: { color: "#e2e8f0" } },
    },
    series: [
      {
        type: "line",
        data: points.map((point) => point.totalAmount),
        smooth: true,
        lineStyle: { color: "#0f766e", width: 3 },
        itemStyle: { color: "#0f766e" },
        areaStyle: { color: "rgba(15, 118, 110, 0.10)" },
      },
    ],
  };
}

function buildSuppliersOption(points: AnalyticsPoint[]): EChartsOption {
  return {
    ...chartBase(),
    xAxis: {
      type: "value",
      splitLine: { lineStyle: { color: "#e2e8f0" } },
      axisLabel: { color: "#475569" },
    },
    yAxis: {
      type: "category",
      data: points.map((point) => point.label),
      axisLabel: { color: "#334155", width: 160, overflow: "truncate" },
      axisTick: { show: false },
    },
    series: [
      {
        type: "bar",
        data: points.map((point) => point.totalAmount),
        itemStyle: { color: "#0f766e", borderRadius: [0, 10, 10, 0] },
      },
    ],
  };
}

export function SecondaryAnalyticsSection({
  monthData,
  supplierData,
  isMonthLoading,
  isSuppliersLoading,
}: SecondaryAnalyticsSectionProps) {
  const topSuppliers = (supplierData ?? []).slice(0, 10);

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          Вторичная аналитика
        </p>
        <h3 className="mt-1 text-xl font-semibold text-slate-950">Обзор распределений</h3>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {isMonthLoading ? (
          <LoadingState lines={8} className="min-h-[340px]" />
        ) : (
          <ChartCard
            title="Закупки по месяцам"
            subtitle="Динамика сумм в выбранной выборке"
            option={buildMonthOption(monthData ?? [])}
            hasData={Boolean(monthData?.length)}
            height={300}
          />
        )}

        {isSuppliersLoading ? (
          <LoadingState lines={8} className="min-h-[340px]" />
        ) : (
          <ChartCard
            title="Top-10 поставщиков"
            subtitle="Только лидеры по сумме закупок"
            option={buildSuppliersOption(topSuppliers)}
            hasData={Boolean(topSuppliers.length)}
            height={300}
          />
        )}

      </div>
    </section>
  );
}
