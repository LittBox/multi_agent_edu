import { useEffect, useState } from "react";
import { BarChart3, TrendingUp, AlertTriangle } from "lucide-react";
import {
  fetchLearningReport,
  type LearningReport,
} from "../api/education";
import "../styles/pages/ReportView.css";

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

  if (loading) {
    return <p className="report-loading">报告加载中…</p>;
  }

  if (!report) {
    return <p className="report-loading">无法加载学习报告</p>;
  }

  const { overview, weak_points, subject_stats, daily_accuracy } = report;
  const maxDaily = Math.max(...daily_accuracy.map((d) => d.total), 1);

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
        <div className="report-bars">
          {daily_accuracy.map((day) => (
            <div key={day.date} className="report-bar-col">
              <div
                className="report-bar"
                style={{ height: `${(day.total / maxDaily) * 120}px` }}
                title={`${day.total} 题`}
              />
              <span className="report-bar-label">
                {day.date.slice(5)}
              </span>
            </div>
          ))}
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
    </div>
  );
};

export default ReportView;
