import { useEffect, useState } from "react";
import { BarChart3, AlertTriangle, TrendingUp } from "lucide-react";
import {
  fetchLearningReport,
  type LearningReport,
} from "../api/education";
import "../styles/pages/ReportView.css";
import ReactECharts from "echarts-for-react";
interface ReportViewProps {
  userId: number;
}

const ReportView: React.FC<ReportViewProps> = ({ userId }) => {
  const [report, setReport] = useState<LearningReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLearningReport(userId)
      .then(setReport)
      .catch(() => setReport(null))
      .finally(() => setLoading(false));
  }, [userId]);

  const recentAnswers = report?.recent_answers ?? [];

  if (loading) {
    return <p className="report-loading">报告加载中…</p>;
  }

  if (!report) {
    return <p className="report-loading">无法加载学习报告</p>;
  }

  const { overview, weak_points, subject_stats, daily_accuracy } = report;
  const dailyAnswerOption = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(255, 255, 255, 0.96)",
      borderColor: "rgba(15, 23, 42, 0.08)",
      borderWidth: 1,
      padding: [10, 14],
      textStyle: {
        color: "#0f172a",
      },
      axisPointer: {
        type: "line",
        lineStyle: {
          color: "rgba(96, 165, 250, 0.55)",
          width: 1.5,
        },
        crossStyle: {
          color: "rgba(96, 165, 250, 0.35)",
          width: 1,
        },
        label: {
          backgroundColor: "rgba(96, 165, 250, 0.9)",
          color: "#fff",
        },
      },
      formatter: "{b}<br/>答题量：{c} 题",
      extraCssText:
        "box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12); border-radius: 10px;",
    },
    grid: {
      left: 42,
      right: 24,
      top: 24,
      bottom: 32,
    },
    xAxis: {
      type: "category",
      data: daily_accuracy.map((day) => day.date.slice(5)),
      axisTick: {
        show: false,
      },
      axisLine: {
        lineStyle: {
          color: "rgba(148, 163, 184, 0.35)",
        },
      },
      axisLabel: {
        color: "rgba(100, 116, 139, 0.9)",
      },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      axisLabel: {
        color: "rgba(100, 116, 139, 0.9)",
        formatter: "{value}题",
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: "rgba(148, 163, 184, 0.16)",
        },
      },
    },
    series: [
      {
        name: "答题量",
        type: "bar",
        data: daily_accuracy.map((day) => day.total),
        barWidth: 28,
        itemStyle: {
          color: "linear-gradient(180deg, #60a5fa 0%, #3b82f6 100%)",
          borderRadius: [10, 10, 0, 0],
        },
        emphasis: {
          focus: "series",
          itemStyle: {
            color: "#3fdfbe",
          },
        },
      },
    ],
  };

  return (
    <div className="report-view">
      <header className="report-header">
        <h1>学习分析报告</h1>
        <p>基于答题记录与 BKT 知识追踪生成</p>
      </header>

      <div className="report-overview">
        <div className="report-metric">
          <TrendingUp size={20} />
          <strong>{(overview.accuracy * 100).toFixed(1)}%</strong>
          <span>总正确率</span>
        </div>
        <div className="report-metric">
          <BarChart3 size={20} />
          <strong>{overview.total_answers}</strong>
          <span>答题总数</span>
        </div>
        <div className="report-metric">
          <strong>{overview.mastered_count}</strong>
          <span>已掌握</span>
        </div>
        <div className="report-metric">
          <strong>{overview.streak_days}</strong>
          <span>连续学习天</span>
        </div>
      </div>

      <section className="report-card">
        <h2>近七日答题量</h2>
        <div className="report-chart-box">
          <ReactECharts
            option={dailyAnswerOption}
            className="report-chart"
            notMerge
            lazyUpdate
          />
        </div>
      </section>

      <div className="report-columns">
        <section className="report-card">
          <h2>
            <AlertTriangle size={20} />
            薄弱知识点 TOP5
          </h2>
          {weak_points.length === 0 ? (
            <p className="report-empty">暂无数据，请先完成练习</p>
          ) : (
            <ul className="report-list">
              {weak_points.map((item) => (
                <li key={item.knowledge_id}>
                  <div>
                    <strong>{item.name}</strong>
                    <span>{item.subject}</span>
                  </div>
                  <em>{item.mastery_percent}%</em>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="report-card">
          <h2>学科掌握情况</h2>
          {subject_stats.length === 0 ? (
            <p className="report-empty">暂无学科统计</p>
          ) : (
            <ul className="report-list">
              {subject_stats.map((item) => (
                <li key={item.subject}>
                  <div>
                    <strong>{item.subject}</strong>
                    <span>{item.count} 个知识点</span>
                  </div>
                  <em>{(item.avg_mastery * 100).toFixed(0)}%</em>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <section className="report-card">
        <h2>最近答题记录</h2>
        {recentAnswers.length === 0 ? (
          <p className="report-empty">暂无最近答题记录</p>
        ) : (
          <ul className="report-list">
            {recentAnswers.slice(0, 5).map((item) => (
              <li key={item.record_id}>
                <div>
                  <strong>题目 #{item.question_id}</strong>
                  <span>知识点 {item.knowledge_id} · {item.is_correct ? "正确" : "错误"}</span>
                </div>
                <em>{item.submitted_at.slice(0, 10)}</em>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};

export default ReportView;
