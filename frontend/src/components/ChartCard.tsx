import { useEffect, useRef } from "react";
import type { EChartsOption } from "echarts";
import * as echarts from "echarts/core";
import { BarChart, LineChart, PieChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { EmptyState } from "@/components/EmptyState";

echarts.use([LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

interface ChartCardProps {
  title: string;
  subtitle?: string;
  option: EChartsOption;
  height?: number;
  hasData: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function ChartCard({
  title,
  subtitle,
  option,
  height = 320,
  hasData,
  emptyTitle = "Нет данных",
  emptyDescription = "Данные появятся после загрузки и обработки Excel-файлов.",
}: ChartCardProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || !hasData) {
      return undefined;
    }

    const chart = echarts.init(containerRef.current, undefined, { renderer: "canvas" });
    chart.setOption(option);

    const resizeObserver = new ResizeObserver(() => chart.resize());
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.dispose();
    };
  }, [hasData, option]);

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-panel">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-950">{title}</h3>
        {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
      </div>

      {hasData ? (
        <div ref={containerRef} style={{ height }} />
      ) : (
        <EmptyState title={emptyTitle} description={emptyDescription} />
      )}
    </section>
  );
}
