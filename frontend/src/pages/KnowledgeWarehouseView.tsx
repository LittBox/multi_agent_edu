import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Search,
  Filter,
  BookOpen,
  Lock,
  Play,
  Check,
  Circle,
} from "lucide-react";
import {
  fetchKnowledgeRepository,
  type KnowledgeRepositoryItem,
  type KnowledgeStatus,
} from "../api/knowledge";
import "../styles/pages/KnowledgeWarehousePage.css";

interface KnowledgeWarehouseViewProps {
  userId: number;
  onPractice: (knowledgeId?: number) => void;
}

const STATUS_LABEL: Record<KnowledgeStatus, string> = {
  mastered: "已掌握",
  learning: "学习中",
  not_started: "未开始",
  locked: "未解锁",
};

const KnowledgeWarehouseView: React.FC<KnowledgeWarehouseViewProps> = ({
  userId,
  onPractice,
}) => {
  const [items, setItems] = useState<KnowledgeRepositoryItem[]>([]);
  const [subjects, setSubjects] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeSubject, setActiveSubject] = useState<string>("全部");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search), 300);
    return () => window.clearTimeout(timer);
  }, [search]);

  const loadRepository = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchKnowledgeRepository(userId, {
        q: debouncedSearch || undefined,
        subject: activeSubject === "全部" ? undefined : activeSubject,
      });
      setItems(data.items);
      setSubjects(data.subjects);
    } catch {
      setItems([]);
      setSubjects([]);
    } finally {
      setLoading(false);
    }
  }, [userId, debouncedSearch, activeSubject]);

  useEffect(() => {
    loadRepository();
  }, [loadRepository]);

  const stats = useMemo(() => {
    return {
      total: items.length,
      mastered: items.filter((i) => i.status === "mastered").length,
      learning: items.filter((i) => i.status === "learning").length,
    };
  }, [items]);

  return (
    <div className="warehouse-view">
      <header className="warehouse-header">
        <div>
          <h1>知识仓库</h1>
          <p>浏览全部知识点，查看掌握情况并针对性练习</p>
        </div>
        <button
          type="button"
          className="warehouse-practice-all"
          onClick={() => onPractice()}
        >
          <Play size={18} />
          随机练习
        </button>
      </header>

      <div className="warehouse-stats">
        <div className="warehouse-stat-card">
          <strong>{stats.total}</strong>
          <span>知识点总数</span>
        </div>
        <div className="warehouse-stat-card">
          <strong>{stats.mastered}</strong>
          <span>已掌握</span>
        </div>
        <div className="warehouse-stat-card">
          <strong>{stats.learning}</strong>
          <span>学习中</span>
        </div>
      </div>

      <div className="warehouse-toolbar">
        <div className="warehouse-search">
          <Search size={18} />
          <input
            type="search"
            placeholder="搜索知识点名称…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="warehouse-filters">
          <Filter size={18} />
          {["全部", ...subjects].map((subject) => (
            <button
              key={subject}
              type="button"
              className={`warehouse-filter-chip${
                activeSubject === subject ? " active" : ""
              }`}
              onClick={() => setActiveSubject(subject)}
            >
              {subject}
            </button>
          ))}
        </div>
      </div>

      {loading && <p className="warehouse-loading">加载中…</p>}

      {!loading && items.length === 0 && (
        <div className="warehouse-empty">
          <BookOpen size={48} strokeWidth={1.2} />
          <p>暂无匹配的知识点</p>
          <span>请调整搜索条件，或联系管理员导入题库</span>
        </div>
      )}

      <div className="warehouse-grid">
        {items.map((item) => (
          <article
            key={item.knowledge_id}
            className={`warehouse-card status-${item.status}`}
          >
            <div className="warehouse-card-top">
              <span className={`warehouse-badge status-${item.status}`}>
                {item.status === "mastered" && <Check size={14} />}
                {item.status === "learning" && <Circle size={14} />}
                {item.status === "locked" && <Lock size={14} />}
                {STATUS_LABEL[item.status]}
              </span>
              <span className="warehouse-subject">{item.subject}</span>
            </div>

            <h2>{item.name}</h2>
            {item.description && (
              <p className="warehouse-desc">{item.description}</p>
            )}

            <div className="warehouse-meta">
              <span>难度 L{item.difficulty}</span>
              <span>{item.question_count} 道题</span>
              <span>练习 {item.attempts} 次</span>
            </div>

            <div className="warehouse-progress-row">
              <span>掌握度 {item.mastery_percent}%</span>
              <div className="progress-bar">
                <span style={{ width: `${item.mastery_percent}%` }}></span>
              </div>
            </div>

            <button
              type="button"
              className="warehouse-start"
              disabled={item.status === "locked" || item.question_count === 0}
              onClick={() => onPractice(item.knowledge_id)}
            >
              <Play size={16} />
              {item.status === "locked" ? "未解锁" : "开始练习"}
            </button>
          </article>
        ))}
      </div>
    </div>
  );
};

export default KnowledgeWarehouseView;
