import { CalendarRange, CircleDollarSign, PackageSearch, Users } from "lucide-react";
import { useMemo, useState } from "react";
import type { EChartsOption } from "echarts";
import { ChartCard } from "@/components/ChartCard";
import { ErrorState } from "@/components/ErrorState";
import { FiltersPanel } from "@/components/FiltersPanel";
import { LoadingState } from "@/components/LoadingState";
import { StatCard } from "@/components/StatCard";
import { useAnalyticsByMonth } from "@/hooks/useAnalyticsByMonth";
import { useAnalyticsByStatus } from "@/hooks/useAnalyticsByStatus";
import { useAnalyticsBySuppliers } from "@/hooks/useAnalyticsBySuppliers";
import { useSummary } from "@/hooks/useSummary";
import type { AnalyticsFilters, AnalyticsPoint } from "@/types/analytics";
import { getApiErrorMessage } from "@/utils/api";
import { formatCurrency, formatDate, formatMonthLabel, formatNumber } from "@/utils/format";

const defaultFilters: AnalyticsFilters = {
  date_from: "",
  date_to: "",
  supplier_name: "",
};

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
        showSymbol: true,
        symbolSize: 8,
        lineStyle: { color: "#0f766e", width: 3 },
        itemStyle: { color: "#0f766e" },
        areaStyle: { color: "rgba(15, 118, 110, 0.12)" },
      },
    ],
  };
}

function buildHorizontalBarOption(points: AnalyticsPoint[]): EChartsOption {
  return {
    ...chartBase(),
    tooltip: {
      ...chartBase().tooltip,
      axisPointer: { type: "shadow" },
    },
    xAxis: {
      type: "value",
      splitLine: { lineStyle: { color: "#e2e8f0" } },
      axisLabel: { color: "#475569" },
    },
    yAxis: {
      type: "category",
      data: points.map((point) => point.label),
      axisLabel: { color: "#334155", width: 130, overflow: "truncate" },
      axisTick: { show: false },
    },
    series: [
      {
        type: "bar",
        data: points.map((point) => point.totalAmount),
        itemStyle: {
          color: "#0f766e",
          borderRadius: [0, 10, 10, 0],
        },
      },
    ],
  };
}

function buildDonutOption(points: AnalyticsPoint[]): EChartsOption {
  return {
    tooltip: {
      trigger: "item",
      backgroundColor: "#0f172a",
      borderWidth: 0,
      textStyle: { color: "#f8fafc" },
    },
    legend: {
      bottom: 0,
      left: "center",
      textStyle: { color: "#475569" },
    },
    series: [
      {
        type: "pie",
        radius: ["52%", "74%"],
        itemStyle: {
          borderRadius: 10,
          borderColor: "#ffffff",
          borderWidth: 3,
        },
        label: { color: "#334155", formatter: "{b}: {d}%" },
        data: points.map((point, index) => ({
          name: point.label,
          value: point.totalAmount,
          itemStyle: {
            color: ["#0f766e", "#14b8a6", "#2dd4bf", "#5eead4", "#99f6e4"][index % 5],
          },
        })),
      },
    ],
  };
}

export function DashboardPage() {
  const [draftFilters, setDraftFilters] = useState(defaultFilters);
  const [appliedFilters, setAppliedFilters] = useState(defaultFilters);

  const summaryQuery = useSummary(appliedFilters);
  const monthQuery = useAnalyticsByMonth(appliedFilters);
  const suppliersQuery = useAnalyticsBySuppliers(appliedFilters);
  const statusQuery = useAnalyticsByStatus(appliedFilters);

  const topSuppliers = useMemo(() => (suppliersQuery.data ?? []).slice(0, 8), [suppliersQuery.data]);

  const hasError =
    summaryQuery.isError ||
    monthQuery.isError ||
    suppliersQuery.isError ||
    statusQuery.isError;

  const errorMessage = getApiErrorMessage(
    summaryQuery.error ?? monthQuery.error ?? suppliersQuery.error ?? statusQuery.error,
  );

  return (
    <div className="space-y-6">
      <FiltersPanel
        value={draftFilters}
        onChange={setDraftFilters}
        onSubmit={() => setAppliedFilters(draftFilters)}
        onReset={() => {
          setDraftFilters(defaultFilters);
          setAppliedFilters(defaultFilters);
        }}
      />

      {hasError ? <ErrorState description={errorMessage} /> : null}

      <section className="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
        {summaryQuery.isLoading ? (
          Array.from({ length: 4 }).map((_, index) => <LoadingState key={index} lines={4} />)
        ) : (
          <>
            <StatCard
              title="Всего закупок"
              value={formatNumber(summaryQuery.data?.total_purchases_count)}
              description="Количество записей в текущей выборке"
              icon={PackageSearch}
            />
            <StatCard
              title="Общая сумма"
              value={formatCurrency(summaryQuery.data?.total_amount)}
              description="Сумма закупок по применённым фильтрам"
              icon={CircleDollarSign}
            />
            <StatCard
              title="Уникальные поставщики"
              value={formatNumber(summaryQuery.data?.unique_suppliers)}
              description="Количество разных поставщиков"
              icon={Users}
            />
            <StatCard
              title="Последняя закупка"
              value={formatDate(summaryQuery.data?.latest_purchase_date)}
              description="Максимальная дата закупки в выборке"
              icon={CalendarRange}
            />
          </>
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        {monthQuery.isLoading ? (
          <LoadingState lines={8} className="min-h-[390px]" />
        ) : (
          <ChartCard
            title="Закупки по месяцам"
            subtitle="Динамика сумм закупок по месяцам"
            option={buildMonthOption(monthQuery.data ?? [])}
            hasData={Boolean(monthQuery.data?.length)}
            height={340}
          />
        )}

        {suppliersQuery.isLoading ? (
          <LoadingState lines={8} className="min-h-[390px]" />
        ) : (
          <ChartCard
            title="Топ поставщиков"
            subtitle="Поставщики с наибольшим объёмом закупок"
            option={buildHorizontalBarOption(topSuppliers)}
            hasData={Boolean(topSuppliers.length)}
            height={340}
          />
        )}

        {statusQuery.isLoading ? (
          <LoadingState lines={8} className="min-h-[390px]" />
        ) : (
          <ChartCard
            title="Статусы закупок"
            subtitle="Распределение сумм по статусам"
            option={buildDonutOption(statusQuery.data ?? [])}
            hasData={Boolean(statusQuery.data?.length)}
            height={340}
          />
        )}
      </section>
    </div>
  );
}
