import { useEffect, useMemo, useRef } from "react";
import * as echarts from "echarts";

type RadarItem = {
  label?: string | null;
  score?: number | string | null;
  formula?: string | null;
  source?: string | null;
};

interface LearnerProfileRadarProps {
  radarItems: RadarItem[];
}

const clampScore = (value: number) =>
  Math.max(0, Math.min(Math.round(value), 100));

const toSafeNumber = (value: number | string | null | undefined) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const escapeHtml = (value: unknown) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

export default function LearnerProfileRadar({
  radarItems,
}: LearnerProfileRadarProps) {
  const chartRef = useRef<HTMLDivElement | null>(null);

  const radarData = useMemo(() => {
    const validItems = radarItems.filter((item) =>
      Boolean(String(item.label ?? "").trim())
    );

    return {
      hasData: validItems.length > 0,
      items: validItems,
      indicators: validItems.map((item) => ({
        name: String(item.label),
        max: 100,
      })),
      scores: validItems.map((item) => clampScore(toSafeNumber(item.score))),
    };
  }, [radarItems]);

  useEffect(() => {
    const chartDom = chartRef.current;
    if (!chartDom) return;

    const chart = echarts.init(chartDom);

    if (!radarData.hasData) {
      chart.clear();

      return () => {
        chart.dispose();
      };
    }

    const option: echarts.EChartsOption = {
      color: ["#3ddebe"],
      tooltip: {
        trigger: "item",
        confine: true,
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        borderColor: "rgba(61, 222, 190, 0.55)",
        borderWidth: 1,
        textStyle: {
          color: "#ffffff",
          fontSize: 12,
        },
        formatter: () => {
          const rows = radarData.items
            .map((item) => {
              const score = clampScore(toSafeNumber(item.score));

              return `
                <div style="margin-bottom: 8px;">
                  <div><strong>${escapeHtml(item.label)}：${score} 分</strong></div>
                  ${
                    item.formula
                      ? `<div style="opacity: .72;">公式：${escapeHtml(item.formula)}</div>`
                      : ""
                  }
                  ${
                    item.source
                      ? `<div style="opacity: .56;">来源：${escapeHtml(item.source)}</div>`
                      : ""
                  }
                </div>
              `;
            })
            .join("");

          return `
            <div>
              <div style="margin-bottom: 8px; font-weight: 600;">用户画像</div>
              ${rows}
            </div>
          `;
        },
      },
      radar: {
            radius: "52%",
            center: ["50%", "50%"],
            indicator: radarData.indicators,
            axisName: {
                color: "rgba(255, 255, 255, 0.9)",
                fontSize: 12,
                padding: [4, 6],
            },
            splitNumber: 4,
            splitLine: {
                lineStyle: {
                color: "rgba(255, 255, 255, 0.2)",
                },
            },
            splitArea: {
                areaStyle: {
                color: [
                    "rgba(255, 255, 255, 0.018)",
                    "rgba(255, 255, 255, 0.045)",
                ],
                },
            },
            axisLine: {
                lineStyle: {
                color: "rgba(255, 255, 255, 0.2)",
                },
            },
        },
      series: [
        {
          name: "用户画像",
          type: "radar",
          symbol: "circle",
          symbolSize: 5,
          data: [
            {
              value: radarData.scores,
              name: "当前画像",
              areaStyle: {
                color: "rgba(61, 222, 190, 0.22)",
              },
              lineStyle: {
                color: "#3ddebe",
                width: 3,
                shadowColor: "rgba(61, 222, 190, 0.35)",
                shadowBlur: 10,
              },
              itemStyle: {
                color: "#3ddebe",
                borderColor: "#ffffff",
                borderWidth: 1,
              },
              label: {
                show: false,
              },
            },
          ],
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
  }, [radarData]);

  return (
    <section className="learner-radar-card">
      <div className="learner-radar-card__header">
        <div>
          <h2>用户画像</h2>
          <p>根据答题记录、掌握度和复习状态生成</p>
        </div>
        <span>Radar</span>
      </div>

      <div className="learner-radar-card__chart-wrap">
        <div
          ref={chartRef}
          className="learner-radar-card__chart"
          role="img"
          aria-label="用户画像雷达图"
        />

        {!radarData.hasData && (
          <div className="learner-radar-card__empty">
            <strong>暂无用户画像</strong>
            <span>完成练习后，系统会根据后端画像维度生成雷达图。</span>
          </div>
        )}
      </div>
    </section>
  );
}