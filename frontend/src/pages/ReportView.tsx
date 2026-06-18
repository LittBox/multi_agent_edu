import { useEffect, useMemo, useRef } from "react";
import * as echarts from "echarts";
import { BarChart3, ListChecks } from "lucide-react";
import { useEducationStore } from "../stores";
import "../styles/pages/ReportView.css";

interface ReportViewProps {
  userId: number;
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

const escapeHtml = (value: unknown) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

/** 学习报告：展示后端计算好的学生画像、正确率趋势、薄弱点和学科统计。 */
export default function ReportView({ userId }: ReportViewProps) {
  const { report, loading, error, loadReport } = useEducationStore();

  const overviewChartRef = useRef<HTMLDivElement | null>(null);
  const accuracyChartRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (userId) void loadReport(userId);
  }, [userId, loadReport]);

  const overview = report?.overview ?? report?.summary;

  const totalAnswers = Math.max(
    0,
    Math.round(toSafeNumber(overview?.total_answers))
  );

  const correctAnswers = Math.max(
    0,
    Math.round(toSafeNumber(overview?.correct_answers))
  );

  const accuracyPercent = toPercent(overview?.accuracy);

  const masteredCount = Math.max(
    0,
    Math.round(toSafeNumber(overview?.mastered_count))
  );

  const learningCount = Math.max(
    0,
    Math.round(toSafeNumber(overview?.learning_count))
  );

  const trackedKnowledgeCount = Math.max(
    0,
    Math.round(toSafeNumber(overview?.knowledge_points_tracked))
  );

  const todayStudyMinutes = Math.max(
    0,
    Math.round(toSafeNumber(overview?.today_study_minutes))
  );

  const radarItems = useMemo(
    () => report?.profile?.radar ?? [],
    [report?.profile?.radar]
  );

  const radarChartData = useMemo(() => {
    const indicators = radarItems.map((item) => ({
      name: item.label,
      max: 100,
    }));

    const scores = radarItems.map((item) =>
      clampScore(toSafeNumber(item.score))
    );

    return {
      indicators,
      scores,
      hasData: radarItems.length > 0,
    };
  }, [radarItems]);

  const overviewStats = [
    { label: "答题总数", value: `${totalAnswers}` },
    { label: "正确题数", value: `${correctAnswers}` },
    { label: "正确率", value: `${accuracyPercent}%` },
    { label: "跟踪知识点", value: `${trackedKnowledgeCount}` },
  ];

  const hasEnoughOverviewData =
    radarChartData.hasData && (totalAnswers > 0 || trackedKnowledgeCount > 0);

  useEffect(() => {
    const chartDom = overviewChartRef.current;
    if (!chartDom) return;

    const chart = echarts.init(chartDom);

    const option: echarts.EChartsOption = {
      color: ["#33ddb9"],
      tooltip: {
        show: radarChartData.hasData,
        trigger: "item",
        confine: true,
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        borderColor: "rgba(51, 221, 185, 0.55)",
        borderWidth: 1,
        textStyle: {
          color: "#ffffff",
          fontSize: 12,
        },
        formatter: () => {
          const rows = radarItems
            .map((item) => {
              const score = clampScore(toSafeNumber(item.score));

              return `
                <div style="margin-bottom: 8px;">
                  <div><strong>${escapeHtml(item.label)}：${score} 分</strong></div>
                  <div style="opacity: .72;">公式：${escapeHtml(item.formula)}</div>
                  <div style="opacity: .56;">来源：${escapeHtml(item.source)}</div>
                </div>
              `;
            })
            .join("");

          return `
            <div>
              <div style="margin-bottom: 8px; font-weight: 600;">学生画像</div>
              ${rows}
            </div>
          `;
        },
      },
      radar: {
        radius: "64%",
        center: ["50%", "52%"],
        indicator:
          radarChartData.indicators.length > 0
            ? radarChartData.indicators
            : [
                { name: "知识掌握", max: 100 },
                { name: "答题准确", max: 100 },
                { name: "练习活跃", max: 100 },
                { name: "学习稳定", max: 100 },
                { name: "复习健康", max: 100 },
              ],
        axisName: {
          color: "rgba(255, 255, 255, 0.92)",
          fontSize: 12,
          padding: [3, 5],
        },
        splitNumber: 4,
        splitLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.22)",
          },
        },
        splitArea: {
          areaStyle: {
            color: [
              "rgba(255, 255, 255, 0.025)",
              "rgba(255, 255, 255, 0.055)",
            ],
          },
        },
        axisLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.22)",
          },
        },
      },
      series: radarChartData.hasData
        ? [
            {
              name: "学生画像",
              type: "radar",
              symbol: "circle",
              symbolSize: 5,
              data: [
                {
                  value: radarChartData.scores,
                  name: "当前画像",
                  areaStyle: {
                    color: "rgba(51, 221, 185, 0.22)",
                  },
                  lineStyle: {
                    color: "#33ddb9",
                    width: 3,
                    shadowColor: "rgba(51, 221, 185, 0.35)",
                    shadowBlur: 10,
                  },
                  itemStyle: {
                    color: "#33ddb9",
                    borderColor: "#ffffff",
                    borderWidth: 1,
                  },
                  label: {
                    show: false,
                  },
                },
              ],
            },
          ]
        : [],
    };

    chart.setOption(option, true);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [radarChartData, radarItems]);

  useEffect(() => {
    const chartDom = accuracyChartRef.current;
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    const dailyAccuracy = report?.daily_accuracy ?? [];

    const xAxisData = dailyAccuracy.map((item) => item.date);
    const seriesData = dailyAccuracy.map((item) => toPercent(item.accuracy));

    const option: echarts.EChartsOption = {
      grid: {
        top: 24,
        right: 20,
        bottom: 28,
        left: 42,
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
          color: "#ffffff",
        },
        axisLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.35)",
          },
        },
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 100,
        axisLabel: {
          color: "#ffffff",
          formatter: "{value}%",
        },
        splitLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.18)",
          },
        },
      },
      series: [
        {
          name: "正确率",
          type: "bar",
          data: seriesData,
          barWidth: 28,
          itemStyle: {
            borderRadius: [999, 999, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(61, 222, 190, 1)" },
              { offset: 0.32, color: "rgba(61, 222, 190, 0.74)" },
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
                { offset: 0.32, color: "rgba(61, 222, 190, 0.8)" },
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
  }, [report?.daily_accuracy]);

  return (
    <div className="report-view">
      {loading && <p className="report-loading">加载中…</p>}
      {error && <p className="report-loading">{error}</p>}

      <section className="report-card">
        <h2>
          <BarChart3 size={18} />
          学生画像
        </h2>

        <div
          className="report-overview-layout"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "24px",
            flexWrap: "wrap",
          }}
        >
          <div
            className="report-chart-box"
            style={{
              position: "relative",
              flex: "1 1 420px",
              minWidth: 0,
            }}
          >
            <div
              ref={overviewChartRef}
              className="report-chart"
              role="img"
              aria-label="学生画像雷达图"
              style={{ width: "100%", height: "300px" }}
            />

            {!hasEnoughOverviewData && (
              <div
                className="report-overview-empty"
                style={{
                  position: "absolute",
                  left: "50%",
                  top: "50%",
                  transform: "translate(-50%, -42%)",
                  width: "min(280px, 78%)",
                  textAlign: "center",
                  pointerEvents: "none",
                }}
              >
                <strong
                  style={{
                    display: "block",
                    color: "rgba(255, 255, 255, 0.92)",
                    fontSize: "15px",
                    marginBottom: "8px",
                  }}
                >
                  完成练习后生成学生画像
                </strong>
                <span
                  style={{
                    display: "block",
                    color: "rgba(255, 255, 255, 0.58)",
                    fontSize: "12px",
                    lineHeight: 1.6,
                  }}
                >
                  画像维度由后端根据答题记录、掌握度和复习计划统一计算。
                </span>
              </div>
            )}
          </div>

          <div
            className="report-overview-stats"
            style={{
              flex: "0 0 196px",
              display: "grid",
              gap: "12px",
            }}
            aria-label="学习概览统计"
          >
            {overviewStats.map((item) => (
              <div
                className="report-overview-stat"
                key={item.label}
                style={{
                  padding: "13px 15px",
                  borderRadius: "16px",
                  background: "rgba(255, 255, 255, 0.065)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                }}
              >
                <span
                  style={{
                    display: "block",
                    color: "rgba(255, 255, 255, 0.62)",
                    fontSize: "12px",
                    marginBottom: "6px",
                  }}
                >
                  {item.label}
                </span>
                <strong
                  style={{
                    display: "block",
                    color: "#ffffff",
                    fontSize: "24px",
                    lineHeight: 1.15,
                  }}
                >
                  {item.value}
                </strong>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="report-card">
        <h2>
          <BarChart3 size={18} />
          最近 7 天正确率
        </h2>
        <div className="report-chart-box">
          <div
            ref={accuracyChartRef}
            className="report-chart"
            role="img"
            aria-label="最近 7 天正确率图"
            style={{ width: "100%", height: "260px" }}
          />
        </div>
      </section>

      <div className="report-columns">
        <section className="report-card">
          <h2>
            <ListChecks size={18} />
            薄弱知识点
          </h2>
          <ul className="report-list">
            {(report?.weak_points ?? []).map((item) => (
              <li key={item.knowledge_id}>
                <div>
                  <strong>{item.name}</strong>
                  <span>{item.subject}</span>
                </div>
                <em>{item.mastery_percent}%</em>
              </li>
            ))}
          </ul>
          {!report?.weak_points?.length && (
            <p className="report-empty">暂无薄弱知识点</p>
          )}
        </section>

        <section className="report-card">
          <h2>学科统计</h2>
          <ul className="report-list">
            {(report?.subject_stats ?? []).map((item) => (
              <li key={item.subject}>
                <div>
                  <strong>{item.subject}</strong>
                  <span>{item.count} 个知识点</span>
                </div>
                <em>{Math.round(item.avg_mastery * 100)}%</em>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}