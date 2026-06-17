import { useEffect, useMemo, useState } from "react";
import { BookOpen, Filter, Play, Search } from "lucide-react";
import { useEducationStore, useKnowledgeStore } from "../stores";
import PracticePage from "./PracticePage";
import "../styles/pages/KnowledgeWarehousePage.css";

interface KnowledgeWarehouseViewProps { userId: number; }

/** 知识仓库页：检索、筛选、加入知识点，并在同页打开练习弹窗。 */
export default function KnowledgeWarehouseView({ userId }: KnowledgeWarehouseViewProps) {
  const { items, subjects, loading, error, query, subject, setQuery, setSubject, loadRepository, joinPoint } = useKnowledgeStore();
  const { loadQuestions } = useEducationStore();
  const [practiceKnowledgeId, setPracticeKnowledgeId] = useState<number | undefined>();
  const [practiceOpen, setPracticeOpen] = useState(false);
  const [joiningId, setJoiningId] = useState<number | null>(null);

  useEffect(() => { void loadRepository(userId); }, [userId]);

  const stats = useMemo(() => ({
    total: items.length,
    mastered: items.filter((item) => item.status === "mastered").length,
    learning: items.filter((item) => item.status === "learning").length,
  }), [items]);

  const grouped = useMemo(() => items.reduce<Record<string, typeof items>>((acc, item) => {
    const key = item.subject || "未分类";
    acc[key] = acc[key] ? [...acc[key], item] : [item];
    return acc;
  }, {}), [items]);

  const search = async (event: React.FormEvent) => {
    event.preventDefault();
    await loadRepository(userId, { q: query, subject: subject === "全部" ? undefined : subject });
  };

  const startPractice = async (knowledgeId?: number) => {
    setPracticeKnowledgeId(knowledgeId);
    if (knowledgeId) await loadQuestions(userId, knowledgeId);
    setPracticeOpen(true);
  };

  return (
    <div className="warehouse-view">
      <header className="warehouse-header">
    
        <button type="button" className="warehouse-practice-all" onClick={() => void startPractice()}><Play size={18} />随机练习</button>
      </header>

      <div className="warehouse-stats">
        <div className="warehouse-stat-card"><strong>{stats.total}</strong><span>知识点总数</span></div>
        <div className="warehouse-stat-card"><strong>{stats.mastered}</strong><span>已掌握</span></div>
        <div className="warehouse-stat-card"><strong>{stats.learning}</strong><span>学习中</span></div>
      </div>

      <form className="warehouse-toolbar" onSubmit={search}>
        <div className="warehouse-search"><Search size={18} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="搜索知识点名称…" /></div>
        <div className="warehouse-filters"><Filter size={18} />{["全部", ...subjects].map((item) => <button key={item} type="button" className={`warehouse-filter-chip${subject === item ? " active" : ""}`} onClick={() => { setSubject(item); void loadRepository(userId, { q: query, subject: item === "全部" ? undefined : item }); }}>{item}</button>)}</div>
      </form>

      {loading && <p className="warehouse-loading">加载中…</p>}
      {error && <p className="warehouse-loading">{error}</p>}
      {!loading && items.length === 0 && <div className="warehouse-empty"><BookOpen size={48} /><p>暂无知识点</p><span>请调整筛选条件或检查后端数据。</span></div>}

      <div className="warehouse-group-list">
        {Object.entries(grouped).map(([groupName, list]) => (
          <section className="warehouse-subject-section" key={groupName}>
            <div className="warehouse-subject-header"><h2>{groupName}</h2><span>{list.length} 个知识点</span></div>
            <div className="warehouse-grid">
              {list.map((item) => (
                <article className={`warehouse-card status-${item.status}`} key={item.knowledge_id}>
                  <div className="warehouse-card-top"><span className={`warehouse-badge status-${item.status}`}>{item.status}</span><span className="warehouse-subject">{item.subject}</span></div>
                  <h2>{item.name}</h2>
                  <p className="warehouse-desc">{item.description || "暂无描述"}</p>
                  <div className="warehouse-meta"><span>难度 L{item.difficulty}</span><span>{item.question_count} 道题</span><span>练习 {item.attempts} 次</span></div>
                  <div className="warehouse-progress-row"><span>掌握度 {item.mastery_percent}%</span><div className="progress-bar"><span style={{ width: `${item.mastery_percent}%` }} /></div></div>
                  <button
                    type="button"
                    className="warehouse-start"
                    disabled={joiningId === item.knowledge_id || item.question_count === 0}
                    onClick={async () => {
                      setJoiningId(item.knowledge_id);
                      try {
                        if (item.status === "not_started" || item.status === "locked") await joinPoint(item.knowledge_id, userId);
                        await startPractice(item.knowledge_id);
                      } finally { setJoiningId(null); }
                    }}
                  >
                    {joiningId === item.knowledge_id ? "加入中…" : item.status === "not_started" ? "加入并练习" : "开始练习"}
                  </button>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>

      {practiceOpen && <PracticePage userId={userId} knowledgeId={practiceKnowledgeId} onClose={() => setPracticeOpen(false)} />}
    </div>
  );
}
