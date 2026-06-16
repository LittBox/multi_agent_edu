import { useEffect } from "react";
import { BarChart3, ListChecks } from "lucide-react";
import { useEducationStore } from "../stores";
import "../styles/pages/ReportView.css";

interface ReportViewProps { userId: number; }

/** 学习报告：使用 EducationStore 汇总学习概览、薄弱知识点和最近答题。 */
export default function ReportView({ userId }: ReportViewProps) {
  const { report, loading, error, loadReport } = useEducationStore();

  useEffect(() => { if (userId) void loadReport(userId); }, [userId, loadReport]);

  const overview = report?.overview;

  return (
    <div className="report-view">
      <header className="report-header"><h1>学习报告</h1><p>根据答题记录、掌握度和复习计划生成学习反馈。</p></header>
      {loading && <p className="report-loading">加载中…</p>}
      {error && <p className="report-loading">{error}</p>}

      <div className="report-overview">
        <div className="report-metric"><strong>{overview?.total_answers ?? 0}</strong><span>答题总数</span></div>
        <div className="report-metric"><strong>{overview?.correct_answers ?? 0}</strong><span>正确题数</span></div>
        <div className="report-metric"><strong>{Math.round((overview?.accuracy ?? 0) * 100)}%</strong><span>正确率</span></div>
        <div className="report-metric"><strong>{overview?.streak_days ?? 0}</strong><span>连续学习天数</span></div>
      </div>

      <section className="report-card">
        <h2><BarChart3 size={18} />最近 7 天正确率</h2>
        <div className="report-chart-box">
          <svg className="report-chart" viewBox="0 0 700 260">
            {(report?.daily_accuracy ?? []).map((item, index) => (
              <rect key={item.date} x={40 + index * 90} y={220 - item.accuracy * 180} width="42" height={item.accuracy * 180} rx="8" />
            ))}
          </svg>
        </div>
      </section>

      <div className="report-columns">
        <section className="report-card">
          <h2><ListChecks size={18} />薄弱知识点</h2>
          <ul className="report-list">
            {(report?.weak_points ?? []).map((item) => <li key={item.knowledge_id}><div><strong>{item.name}</strong><span>{item.subject}</span></div><em>{item.mastery_percent}%</em></li>)}
          </ul>
          {!report?.weak_points?.length && <p className="report-empty">暂无薄弱知识点</p>}
        </section>
        <section className="report-card">
          <h2>学科统计</h2>
          <ul className="report-list">
            {(report?.subject_stats ?? []).map((item) => <li key={item.subject}><div><strong>{item.subject}</strong><span>{item.count} 个知识点</span></div><em>{Math.round(item.avg_mastery * 100)}%</em></li>)}
          </ul>
        </section>
      </div>
    </div>
  );
}
