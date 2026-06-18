import { useEffect, useRef } from "react";
import * as echarts from "echarts";

type DailyAccuracyItem = {
  date?: string | null;
  accuracy?: number | string | null;
};

interface AccuracyTrendChartProps {
  dailyAccuracy: DailyAccuracyItem[];
}

const clampScore = (value: number) =>
  Math.max(0, Math.min(Math.round(value), 100));

const toSafeNumber = (value: number | string | null | undefined) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const toPercent = (value: number | string | null | undefined) => {
  const raw = toSafeNumber(value);
  return clampScore(raw <= 1 ? raw * 100 : raw);
};

export default function AccuracyTrendChart({
  dailyAccuracy,
}: AccuracyTrendChartProps) {
  const chartRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const chartDom = chartRef.current;
    if (!chartDom) return;

    const chart = echarts.init(chartDom);

    const xAxisData = dailyAccuracy.map((item) => item.date || "-");
    const seriesData = dailyAccuracy.map((item) => toPercent(item.accuracy));

    const option: echarts.EChartsOption = {
      grid: {
        top: "12%",
        right: "4%",
        bottom: "14%",
        left: "8%",
      },
      tooltip: {
        trigger: "axis",
        confine: true,
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        borderColor: "rgba(61, 222, 190, 0.45)",
        borderWidth: 1,
        textStyle: {
          color: "#ffffff",
          fontSize: 12,
        },
        valueFormatter: (value) => `${value}%`,
      },
      xAxis: {
        type: "category",
        data: xAxisData,
        axisTick: {
          show: false,
        },
        axisLabel: {
          color: "rgba(255, 255, 255, 0.76)",
        },
        axisLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.28)",
          },
        },
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 100,
        axisLabel: {
          color: "rgba(255, 255, 255, 0.76)",
          formatter: "{value}%",
        },
        splitLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.14)",
          },
        },
      },
      series: [
        {
          name: "正确率",
          type: "bar",
          data: seriesData,
          barWidth: "34%",
          itemStyle: {
            borderRadius: [999, 999, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(61, 222, 190, 1)" },
              { offset: 0.34, color: "rgba(61, 222, 190, 0.74)" },
              { offset: 1, color: "rgba(61, 222, 190, 0.16)" },
            ]),
            shadowBlur: 8,
            shadowColor: "rgba(61, 222, 190, 0.18)",
          },
          emphasis: {
            itemStyle: {
              borderRadius: [999, 999, 0, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "rgba(61, 222, 190, 1)" },
                { offset: 0.34, color: "rgba(61, 222, 190, 0.82)" },
                { offset: 1, color: "rgba(61, 222, 190, 0.22)" },
              ]),
            },
          },
        },
      ],
    };

    chart.setOption(option, true);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [dailyAccuracy]);

  return (
    <section className="accuracy-trend-card">
      <div className="accuracy-trend-card__header">
        <div>
          <h2>最近 7 天正确率</h2>
          <p>根据每日答题记录统计正确率变化</p>
        </div>
        <span>Accuracy</span>
      </div>

      <div className="accuracy-trend-card__chart-wrap">
        <div
          ref={chartRef}
          className="accuracy-trend-card__chart"
          role="img"
          aria-label="最近 7 天正确率柱状图"
        />

        {!dailyAccuracy.length && (
          <div className="accuracy-trend-card__empty">
            <strong>暂无正确率趋势</strong>
            <span>完成答题后，这里会展示最近 7 天表现。</span>
          </div>
        )}
      </div>
    </section>
  );
}