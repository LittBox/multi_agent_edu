import { useCallback, useEffect, useState } from "react";
import {
  Bot,
  Lightbulb,
  Target,
  Heart,
  Calendar,
  Plus,
  Trash2,
  Check,
  Circle,
  Lock,
} from "lucide-react";
import {
  fetchAgentSuggestions,
  fetchDashboard,
  fetchKnowledgeCards,
  type AgentSuggestions,
  type DashboardSummary,
  type KnowledgeCard,
  type PathNode,
  type StudyTrendPoint,
} from "../api/dashboard";
import ReactECharts from "echarts-for-react";
interface HomeDashboardViewProps {
  userId: number;
  username?: string;
  onPractice: () => void;
}

function formatMinutes(minutes: number): string {
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return mins > 0 ? `${hours}h${mins}min` : `${hours}h`;
  }
  return `${Math.round(minutes)}min`;
}



const HomeDashboardView: React.FC<HomeDashboardViewProps> = ({
  userId,
  username,
  onPractice,
}) => {
  const today = new Date().toISOString().slice(0, 10);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [cards, setCards] = useState<KnowledgeCard[]>([]);
  const [path, setPath] = useState<PathNode[]>([]);
  const [suggestions, setSuggestions] = useState<AgentSuggestions | null>(null);
  const [loading, setLoading] = useState(true);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const [dashboard, knowledgeCards, agentSuggestions] = await Promise.all([
        fetchDashboard(userId),
        fetchKnowledgeCards(userId),
        fetchAgentSuggestions(userId),
      ]);
      setSummary(dashboard.summary);
      setPath(dashboard.learning_path);
      setCards(knowledgeCards);
      setSuggestions(agentSuggestions);
    } catch {
      setSummary(null);
      setCards([]);
      setPath([]);
      setSuggestions(null);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const trend = summary?.trend ?? [];


  const option = {
    backgroundColor: "transparent",

    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(6, 38, 42, 0.88)",
      borderColor: "rgba(98, 244, 213, 0.35)",
      textStyle: {
        color: "#fff",
      },
      axisPointer: {
        type: "line",
        lineStyle: {
          color: "rgba(98, 244, 213, 0.5)",
          width: 2,
        },
      },
    },

    grid: {
      left: 42,
      right: 24,
      top: 28,
      bottom: 32,
    },

    xAxis: {
      type: "category",
      boundaryGap: false,
      data: trend.map((item) => item.date.slice(5)),
      axisLine: {
        lineStyle: {
          color: "rgba(255,255,255,0.22)",
        },
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: "rgba(255,255,255,0.7)",
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: "rgba(255,255,255,0.07)",
        },
      },
    },

    yAxis: {
      type: "value",
      axisLabel: {
        color: "rgba(255,255,255,0.6)",
        formatter: "{value}min",
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: "rgba(255,255,255,0.07)",
        },
      },
    },

    series: [
      {
        name: "学习时间",
        type: "line",
        smooth: true,
        data: trend.map((item) => item.minutes),
        symbol: "circle",
        symbolSize: 9,
        lineStyle: {
          width: 4,
          color: "#20d6b0",
        },
        itemStyle: {
          color: "#20d6b0",
        },
        emphasis: {
          focus: "series",
          scale: true,
          itemStyle: {
            borderColor: "#fff",
            borderWidth: 3,
          },
        },
        areaStyle: {
          color: "rgba(32, 214, 176, 0.1)",
        },
      },
    ],
  };

  const emptySlots = Math.max(0, 2 - cards.length);

  return (
    <>
      <section className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>
            欢迎回来，{username || "同学"}，继续你的个性化学习之旅吧！
          </p>
        </div>

        <button type="button" className="dashboard-date">
          <Calendar size={18} />
          <span>{today}</span>
        </button>
      </section>

      {loading && <p className="dashboard-loading">数据加载中…</p>}

      <div className="dashboard-grid">
        <section className="study-card">
          <h2>学习时间趋势（近七天）</h2>

          <div className="chart-box">
            <ReactECharts
              option={option}
              className="study-chart"
              notMerge
              lazyUpdate
            />
          </div>

          <div className="study-summary">
            <div>
              <strong>
                {summary
                  ? formatMinutes(summary.today_study_minutes)
                  : "0min"}
              </strong>
              <span>今日学习时间</span>
            </div>
            <div>
              <strong>近七日学习情况</strong>
              <span>
                平均每日{" "}
                {summary ? formatMinutes(summary.week_avg_minutes) : "0min"}
              </span>
            </div>
            <div>
              <strong>{summary?.streak_days ?? 0} Days</strong>
              <span>连续学习天数</span>
            </div>
          </div>
        </section>

        <aside className="assistant-card">
          <div className="assistant-title">
            <div className="robot">
              <Bot size={42} strokeWidth={1.5} />
            </div>
            <div>
              <h2>小智能体</h2>
              <p>AI Assistant</p>
            </div>
          </div>

          <div className="assistant-item">
            <Lightbulb size={20} className="assistant-icon" />
            <div>
              {suggestions?.start_learning.title ?? "建议开始学习"}
              <span>
                {suggestions?.start_learning.detail ??
                  "完成答题后获取个性化推荐"}
              </span>
            </div>
          </div>
          <div className="assistant-item">
            <Target size={20} className="assistant-icon" />
            <div>
              {suggestions?.weak_point.title ?? "薄弱知识点"}
              <span>{suggestions?.weak_point.detail ?? "暂无数据"}</span>
            </div>
          </div>
          <div className="assistant-item">
            <Heart size={20} className="assistant-icon" />
            <div>
              {suggestions?.encouragement.title ?? "鼓励建议"}
              <span>
                {suggestions?.encouragement.detail ?? "开始今日学习吧"}
              </span>
            </div>
          </div>
        </aside>

        {cards.map((card) => (
          <section key={card.knowledge_id} className="knowledge-card">
            <div className="knowledge-card-header">
              <h2>{card.name}</h2>
              <button
                type="button"
                className="knowledge-delete"
                aria-label="删除知识点"
              >
                <Trash2 size={18} />
              </button>
            </div>
            <p>
              掌握情况 <strong>{card.mastery_percent}%</strong>
            </p>
            <div className="progress-bar">
              <span style={{ width: `${card.mastery_percent}%` }}></span>
            </div>
            <button
              type="button"
              className="knowledge-start"
              onClick={onPractice}
            >
              开始学习
            </button>
          </section>
        ))}

        {cards.length === 0 && !loading && (
          <section className="knowledge-card knowledge-card-empty">
            <h2>暂无学习记录</h2>
            <p>点击下方开始答题，系统将追踪你的知识点掌握度</p>
            <button
              type="button"
              className="knowledge-start"
              onClick={onPractice}
            >
              开始第一题
            </button>
          </section>
        )}

        {Array.from({ length: emptySlots }).map((_, index) => (
          <section key={`add-${index}`} className="add-card">
            <Plus size={32} strokeWidth={1.5} />
            <span>添加知识点</span>
          </section>
        ))}

        <section className="path-card">
          <h2>知识图谱学习路径</h2>
          <div className="path-list">
            {path.map((node, index) => (
              <div key={node.knowledge_id} className="path-segment">
                {index > 0 && <span className="path-arrow">→</span>}
                <div className={`path-node ${node.status}`}>
                  <span className="path-node-icon">
                    {node.status === "done" && <Check size={18} />}
                    {node.status === "learning" && <Circle size={18} />}
                    {node.status === "locked" && <Lock size={18} />}
                  </span>
                  <span className="path-node-line">{node.name}</span>
                </div>
              </div>
            ))}
            {path.length === 0 && !loading && (
              <p className="path-empty">暂无知识图谱数据</p>
            )}
          </div>
        </section>
      </div>
    </>
  );
};

export default HomeDashboardView;
