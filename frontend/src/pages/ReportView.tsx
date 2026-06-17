import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import { BarChart3, ListChecks } from "lucide-react";
import { useEducationStore } from "../stores";
import "../styles/pages/ReportView.css";

interface ReportViewProps {
  userId: number;
}

type UnknownRecord = Record<string, unknown>;

const clampScore = (value: number) =>
  Math.max(0, Math.min(Math.round(value), 100));

const isRecord = (value: unknown): value is UnknownRecord => {
  return typeof value === "object" && value !== null && !Array.isArray(value);
};

const parseNumber = (value: unknown): number | undefined => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number.parseFloat(value.trim().replace("%", ""));
    return Number.isFinite(parsed) ? parsed : undefined;
  }

  return undefined;
};

const getNumber = (source: UnknownRecord, keys: string[]) => {
  for (const key of keys) {
    const parsed = parseNumber(source[key]);

    if (parsed !== undefined) {
      return parsed;
    }
  }

  return undefined;
};

const pickFirstRecord = (source: UnknownRecord, keys: string[]) => {
  for (const key of keys) {
    const value = source[key];

    if (isRecord(value)) {
      return value;
    }
  }

  return undefined;
};

const getOverviewSource = (report: unknown): UnknownRecord => {
  if (!isRecord(report)) return {};

  const overviewKeys = [
    "overview",
    "summary",
    "stats",
    "overview_data",
    "overviewData",
  ];

  const directOverview = pickFirstRecord(report, overviewKeys);
  if (directOverview) return directOverview;

  const data = report.data;
  if (isRecord(data)) {
    const nestedOverview = pickFirstRecord(data, overviewKeys);
    return nestedOverview ?? data;
  }

  return report;
};

/** 学习报告：使用 EducationStore 汇总学习概览、薄弱知识点和最近答题。 */
export default function ReportView({ userId }: ReportViewProps) {
  const { report, loading, error, loadReport } = useEducationStore();

  const overviewChartRef = useRef<HTMLDivElement | null>(null);
  const accuracyChartRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (userId) void loadReport(userId);
  }, [userId, loadReport]);

  const overviewSource = getOverviewSource(report);

  const totalAnswers = Math.max(
    0,
    Math.round(
      getNumber(overviewSource, [
        "total_answers",
        "totalAnswers",
        "answers_total",
        "answer_total",
        "answerCount",
        "answer_count",
        "total_answer_count",
        "total_count",
        "totalQuestions",
        "total_questions",
        "question_count",
        "answered_count",
      ]) ?? 0
    )
  );

  const correctAnswers = Math.max(
    0,
    Math.round(
      getNumber(overviewSource, [
        "correct_answers",
        "correctAnswers",
        "correct_answer_count",
        "correctCount",
        "correct_count",
        "right_answers",
        "rightAnswers",
        "right_count",
        "correct",
      ]) ?? 0
    )
  );

  const rawAccuracy = getNumber(overviewSource, [
    "accuracy",
    "accuracy_percent",
    "accuracyPercent",
    "correct_rate",
    "correctRate",
    "rate",
    "correct_ratio",
  ]);

  const accuracyPercent = clampScore(
    rawAccuracy !== undefined
      ? rawAccuracy <= 1
        ? rawAccuracy * 100
        : rawAccuracy
      : totalAnswers > 0
        ? (correctAnswers / totalAnswers) * 100
        : 0
  );

  const streakDays = Math.max(
    0,
    Math.round(
      getNumber(overviewSource, [
        "streak_days",
        "streakDays",
        "continuous_days",
        "continuousDays",
        "consecutive_days",
        "consecutiveDays",
        "study_streak",
        "studyStreak",
      ]) ?? 0
    )
  );

  // 雷达图只展示 0-100 的归一化能力分，避免把题数、百分比、天数混在同一坐标系里。
  const activityScore = clampScore((totalAnswers / 20) * 100);
  const completionScore = clampScore((correctAnswers / 20) * 100);
  const accuracyScore = accuracyPercent;
  const persistenceScore = clampScore((streakDays / 7) * 100);
  const hasEnoughOverviewData = totalAnswers >= 5;

  const overviewStats = [
    { label: "答题总数", value: `${totalAnswers}` },
    { label: "正确题数", value: `${correctAnswers}` },
    { label: "正确率", value: `${accuracyPercent}%` },
    { label: "连续学习", value: `${streakDays} 天` },
  ];

  useEffect(() => {
    const chartDom = overviewChartRef.current;
    if (!chartDom) return;

    const chart = echarts.init(chartDom);

    const currentScores = [
      activityScore,
      completionScore,
      accuracyScore,
      persistenceScore,
    ];
    const targetScores = [70, 70, 80, 60];

    const formatScores = (scores: number[]) => {
      return `
        <div>学习活跃度：${scores[0]} 分</div>
        <div>答题完成度：${scores[1]} 分</div>
        <div>正确率表现：${scores[2]} 分</div>
        <div>学习坚持度：${scores[3]} 分</div>
      `;
    };

    const option: echarts.EChartsOption = {
      color: ["rgba(255, 255, 255, 0.45)", "#33ddb9"],
      tooltip: {
        show: hasEnoughOverviewData,
        trigger: "item",
        confine: true,
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        borderColor: "rgba(51, 221, 185, 0.55)",
        borderWidth: 1,
        textStyle: {
          color: "#ffffff",
          fontSize: 12,
        },
        formatter: (params) => {
          const safeParams = params as {
            name?: string;
            value?: Array<number | string>;
          };
          const isTarget = safeParams.name === "阶段目标";
          const scores = isTarget
            ? targetScores
            : (safeParams.value ?? currentScores).map((item) => Number(item));

          if (isTarget) {
            return `
              <div>
                <div style="margin-bottom: 6px; font-weight: 600;">阶段目标</div>
                ${formatScores(scores)}
              </div>
            `;
          }

          return `
            <div>
              <div style="margin-bottom: 6px; font-weight: 600;">当前表现</div>
              ${formatScores(scores)}
              <div style="height: 1px; margin: 8px 0; background: rgba(255, 255, 255, 0.16);"></div>
              <div>答题总数：${totalAnswers}</div>
              <div>正确题数：${correctAnswers}</div>
              <div>正确率：${accuracyPercent}%</div>
              <div>连续学习：${streakDays} 天</div>
            </div>
          `;
        },
      },
      radar: {
        radius: "64%",
        center: ["50%", "52%"],
        indicator: [
          { name: "学习活跃度", max: 100 },
          { name: "答题完成度", max: 100 },
          { name: "正确率表现", max: 100 },
          { name: "学习坚持度", max: 100 },
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
      series: hasEnoughOverviewData
        ? [
            {
              name: "学习概览",
              type: "radar",
              symbol: "circle",
              symbolSize: 5,
              data: [
                {
                  value: targetScores,
                  name: "阶段目标",
                  areaStyle: {
                    color: "rgba(255, 255, 255, 0.04)",
                  },
                  lineStyle: {
                    color: "rgba(255, 255, 255, 0.38)",
                    width: 2,
                    type: "dashed",
                  },
                  itemStyle: {
                    color: "rgba(255, 255, 255, 0.68)",
                  },
                },
                {
                  value: currentScores,
                  name: "当前表现",
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
  }, [
    activityScore,
    completionScore,
    accuracyScore,
    persistenceScore,
    hasEnoughOverviewData,
    totalAnswers,
    correctAnswers,
    accuracyPercent,
    streakDays,
  ]);

  useEffect(() => {
    const chartDom = accuracyChartRef.current;
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    const dailyAccuracy = report?.daily_accuracy ?? [];

    const xAxisData = dailyAccuracy.map((item) => item.date);
    const seriesData = dailyAccuracy.map((item) =>
      Math.round(Number(item.accuracy ?? 0) * 100)
    );

    const option: echarts.EChartsOption = {
      grid: {
        top: 24,
        right: 20,
        bottom: 28,
        left: 42,
      },
      color: ["#33ddb9"],
      tooltip: {
        trigger: "axis",
        confine: true,
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
          barWidth: 42,
          itemStyle: {
            color: "#33ddb9",
            borderRadius: [4, 4, 0, 0],
          },
          label: {
            show: false,
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
          学习概览
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
              aria-label="学习概览雷达图"
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
                  完成 5 道题后生成学习画像
                </strong>
                <span
                  style={{
                    display: "block",
                    color: "rgba(255, 255, 255, 0.58)",
                    fontSize: "12px",
                    lineHeight: 1.6,
                  }}
                >
                  当前数据较少，建议先完成一次练习，再查看能力趋势。
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
