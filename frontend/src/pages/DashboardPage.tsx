import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import * as echarts from "echarts";
import {
  BookOpen,
  CalendarDays,
  ClipboardList,
  FileText,
  GraduationCap,
  Home,
  LogOut,
  Settings,
  UserRound,
} from "lucide-react";
import { useAuthStore, useDashboardStore } from "../stores";
import KnowledgeWarehouseView from "./KnowledgeWarehouseView";
import CourseManagementView from "./CourseManagementView";
import StudentCourseView from "./StudentCourseView";
import ExamView from "./ExamView";
import TaskView from "./TaskView";

import AdminView from "./AdminView";
import "../styles/pages/DashboardPage.css";
import PersonalCenterView from "./PersonalCenterView";

type PageKey =
  | "home"
  | "knowledge"
  | "courses"
  | "exams"
  | "tasks"
  | "profile"
  | "admin";

type TrendItem = {
  date?: string;
  day?: string;
  label?: string;
  name?: string;
  minutes?: number | string;
};

type DashboardSummaryLike = {
  today_study_minutes?: number | string;
  week_avg_minutes?: number | string;
  week_total_minutes?: number | string;
  streak_days?: number | string;
  trend?: TrendItem[];
};

const pageTitle: Record<PageKey, string> = {
  home: "学习首页",
  knowledge: "知识仓库",
  courses: "课程选课",
  exams: "考试中心",
  tasks: "作业中心",
  profile: "个人中心",
  admin: "后台管理",
};

const toStudyMinutes = (value: number | string | null | undefined) =>
  Math.max(0, Number(value) || 0);

/**
 * 首页统一按“整数分钟”展示和绘图。
 * 只要后端返回大于 0 但不足 1 分钟，也按 1 分钟展示，
 * 避免图表柱子高度和文字标签出现“都是 1 分钟但高度不同”的情况。
 */
const toDisplayMinutes = (value: number | string | null | undefined) => {
  const rawMinutes = toStudyMinutes(value);

  if (rawMinutes <= 0) {
    return 0;
  }

  return Math.max(1, Math.round(rawMinutes));
};

const formatStudyDuration = (value: number | string) => {
  const minutes = toDisplayMinutes(value);

  if (minutes < 60) {
    return `${minutes}分钟`;
  }

  const hours = Math.floor(minutes / 60);
  const restMinutes = minutes % 60;

  if (restMinutes === 0) {
    return `${hours}小时`;
  }

  return `${hours}小时${restMinutes}分钟`;
};

const formatMetricDuration = (value: number | string | null | undefined) => {
  const minutes = toDisplayMinutes(value);

  if (minutes <= 0) {
    return "0";
  }

  return formatStudyDuration(minutes);
};

const getTrendMinutes = (trend: TrendItem[]) =>
  trend.map((item) => toDisplayMinutes(item.minutes));

const getWeekTotalMinutes = (
  trend: TrendItem[],
  weekAvgMinutes: number,
  explicitWeekTotal?: number | string
) => {
  const parsedWeekTotal = Number(explicitWeekTotal);

  if (Number.isFinite(parsedWeekTotal)) {
    return toDisplayMinutes(parsedWeekTotal);
  }

  const recentSevenDays = getTrendMinutes(trend).slice(-7);

  if (recentSevenDays.length > 0) {
    return recentSevenDays.reduce((sum, minutes) => sum + minutes, 0);
  }

  return toDisplayMinutes(weekAvgMinutes * 7);
};

const buildTrendYAxis = (maxMinutes: number) => {
  if (maxMinutes <= 5) {
    return { max: 5, interval: 1 };
  }

  if (maxMinutes <= 20) {
    return { max: 20, interval: 5 };
  }

  if (maxMinutes <= 60) {
    return { max: 60, interval: 10 };
  }

  if (maxMinutes <= 120) {
    return { max: 120, interval: 20 };
  }

  const upperBound = Math.ceil(maxMinutes / 30) * 30;

  return {
    max: upperBound,
    interval: Math.max(30, Math.ceil(upperBound / 6 / 10) * 10),
  };
};

const parseTrendDate = (value: string) => {
  const matched = value.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);

  if (!matched) {
    return null;
  }

  return {
    year: matched[1],
    month: Number(matched[2]),
    day: Number(matched[3]),
  };
};

const formatTrendDate = (value: string) => {
  if (!value) return "";

  const parsed = parseTrendDate(value);

  if (!parsed) {
    return value;
  }

  return `${parsed.month}/${parsed.day}`;
};

const formatFullTrendDate = (value: string) => {
  if (!value) return "";

  const parsed = parseTrendDate(value);

  if (!parsed) {
    return value;
  }

  return `${parsed.month}月${parsed.day}日`;
};

/** 主页面壳：统一侧边导航、角色路由和业务视图切换。 */
export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const { dashboard, knowledgeCards, loading, error, loadHomeData } =
    useDashboardStore();

  const [active, setActive] = useState<PageKey>("home");
  const trendChartRef = useRef<HTMLDivElement | null>(null);

  const userId = user?.user_id ?? user?.id ?? 0;
  const role = user?.role ?? "student";

  const refreshHomeData = useCallback(() => {
    if (!userId) return;
    void loadHomeData(userId);
  }, [userId, loadHomeData]);

  useEffect(() => {
    if (active !== "home") return;

    refreshHomeData();
  }, [active, refreshHomeData]);

  useEffect(() => {
    if (active !== "home" || !userId) return;

    const handleWindowFocus = () => {
      refreshHomeData();
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        refreshHomeData();
      }
    };

    window.addEventListener("focus", handleWindowFocus);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.removeEventListener("focus", handleWindowFocus);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [active, userId, refreshHomeData]);

  useEffect(() => {
    if (active !== "home") return;

    const chartDom = trendChartRef.current;
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    const trend = ((dashboard?.summary as DashboardSummaryLike | undefined)
      ?.trend ?? []) as TrendItem[];

    const xAxisData = trend.map((item, index) => {
      return (
        item.date ??
        item.day ??
        item.label ??
        item.name ??
        `第${index + 1}天`
      );
    });

    const seriesData = getTrendMinutes(trend);
    const maxTrendMinutes = Math.max(0, ...seriesData);
    const hasMeaningfulData = seriesData.some((minutes) => minutes > 0);
    const shouldUseStarterChart = hasMeaningfulData && maxTrendMinutes <= 5;
    const yAxisConfig = buildTrendYAxis(maxTrendMinutes);

    const option: echarts.EChartsOption = {
      color: ["#41e1c0"],
      grid: {
        top: 28,
        right: 28,
        bottom: 58,
        left: 76,
      },
      tooltip: {
        trigger: "axis",
        confine: true,
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        borderColor: "rgba(65, 225, 192, 0.55)",
        borderWidth: 1,
        textStyle: {
          color: "#ffffff",
          fontSize: 12,
        },
        axisPointer: {
          type: shouldUseStarterChart ? "shadow" : "line",
          lineStyle: {
            color: "rgba(65, 225, 192, 0.75)",
            width: 1,
          },
          shadowStyle: {
            color: "rgba(65, 225, 192, 0.12)",
          },
        },
        formatter: (params) => {
          const item = Array.isArray(params) ? params[0] : params;

          const safeItem = item as {
            axisValue?: string | number;
            name?: string | number;
            value?: number | string | Array<number | string>;
          };

          const axisValue = String(safeItem.axisValue ?? safeItem.name ?? "");
          const value = Array.isArray(safeItem.value)
            ? safeItem.value[1]
            : safeItem.value;

          return `
            <div>
              <div style="margin-bottom: 4px;">${formatFullTrendDate(axisValue)}</div>
              <div>学习时长：${formatStudyDuration(value ?? 0)}</div>
            </div>
          `;
        },
      },
      graphic: !hasMeaningfulData
        ? [
            {
              type: "text",
              left: "center",
              top: "42%",
              style: {
                text: "今天学 5 分钟，就能点亮趋势图",
                fill: "rgba(255, 255, 255, 0.9)",
                fontSize: 15,
                fontWeight: 600,
                align: "center",
              },
            },
            {
              type: "text",
              left: "center",
              top: "52%",
              style: {
                text: "开始一次练习后，这里会展示每日变化",
                fill: "rgba(255, 255, 255, 0.56)",
                fontSize: 12,
                align: "center",
              },
            },
          ]
        : undefined,
      xAxis: {
        type: "category",
        boundaryGap: shouldUseStarterChart,
        data: xAxisData,
        axisTick: {
          show: false,
        },
        axisLabel: {
          color: "#ffffff",
          fontSize: 12,
          margin: 18,
          hideOverlap: true,
          formatter: (value: string) => formatTrendDate(value),
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
        max: yAxisConfig.max,
        interval: yAxisConfig.interval,
        axisLabel: {
          color: "#ffffff",
          fontSize: 12,
          margin: 16,
          formatter: (value: number) => formatStudyDuration(value),
        },
        axisLine: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        splitLine: {
          lineStyle: {
            color: "rgba(255, 255, 255, 0.12)",
            type: "dashed",
          },
        },
      },
      series: [
        shouldUseStarterChart
          ? {
              name: "学习时长",
              type: "bar",
              data: seriesData,
              barMaxWidth: 18,
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: "rgba(65, 225, 192, 0.95)",
                  },
                  {
                    offset: 1,
                    color: "rgba(65, 225, 192, 0.22)",
                  },
                ]),
                borderRadius: [8, 8, 0, 0],
                shadowColor: "rgba(65, 225, 192, 0.36)",
                shadowBlur: 10,
              },
              label: {
                show: true,
                position: "top",
                color: "rgba(255, 255, 255, 0.9)",
                fontSize: 11,
                formatter: (params) => {
                  const safeParams = params as { value?: number | string };
                  const minutes = toDisplayMinutes(safeParams.value);
                  return minutes > 0 ? formatStudyDuration(minutes) : "";
                },
              },
              emphasis: {
                focus: "series",
              },
            }
          : {
              name: "学习时长",
              type: "line",
              data: seriesData,
              smooth: true,
              showSymbol: hasMeaningfulData,
              symbol: "circle",
              symbolSize: 8,
              emphasis: {
                focus: "series",
                itemStyle: {
                  color: "#41e1c0",
                  borderColor: "#ffffff",
                  borderWidth: 2,
                },
              },
              lineStyle: {
                color: "#41e1c0",
                width: 4,
                shadowColor: "rgba(65, 225, 192, 0.45)",
                shadowBlur: 12,
                shadowOffsetY: 6,
              },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: "rgba(65, 225, 192, 0.32)",
                  },
                  {
                    offset: 0.65,
                    color: "rgba(65, 225, 192, 0.1)",
                  },
                  {
                    offset: 1,
                    color: "rgba(65, 225, 192, 0.02)",
                  },
                ]),
              },
              markPoint: hasMeaningfulData
                ? {
                    symbol: "circle",
                    symbolSize: 12,
                    data: [{ type: "max", name: "最高" }],
                    itemStyle: {
                      color: "#41e1c0",
                      borderColor: "#ffffff",
                      borderWidth: 2,
                    },
                    label: {
                      color: "#ffffff",
                      fontSize: 11,
                      formatter: (params) => {
                        const safeParams = params as { value?: number | string };
                        return formatStudyDuration(safeParams.value ?? 0);
                      },
                    },
                  }
                : undefined,
              label: {
                show: false,
              },
            },
      ],
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [active, dashboard?.summary]);

  const navItems = useMemo(() => {
    const base = [
      { key: "home" as PageKey, label: "首页", icon: Home },
      { key: "knowledge" as PageKey, label: "知识", icon: BookOpen },
      {
        key: "courses" as PageKey,
        label: role === "student" ? "选课" : "课程",
        icon: GraduationCap,
      },
      { key: "exams" as PageKey, label: "考试", icon: FileText },
      { key: "tasks" as PageKey, label: "作业", icon: ClipboardList },
      { key: "profile" as PageKey, label: "我的", icon: UserRound },

    ];

    return role === "admin"
      ? [...base, { key: "admin" as PageKey, label: "后台", icon: Settings }]
      : base;
  }, [role]);

  const renderContent = () => {
    if (!user) return null;

    if (active === "knowledge") {
      return <KnowledgeWarehouseView userId={userId} />;
    }

    if (active === "courses") {
      return role === "student" ? (
        <StudentCourseView />
      ) : (
        <CourseManagementView role={role} />
      );
    }

    if (active === "exams") {
      return <ExamView role={role} />;
    }

    if (active === "tasks") {
      return <TaskView role={role} />;
    }

    if (active === "profile") {
      return <PersonalCenterView />;
    }

    if (active === "admin") {
      return <AdminView />;
    }

    const summary = dashboard?.summary as DashboardSummaryLike | undefined;
    const trend = summary?.trend ?? [];
    const todayStudyMinutes = toDisplayMinutes(summary?.today_study_minutes);
    const weekAvgMinutes = toStudyMinutes(summary?.week_avg_minutes);
    const weekTotalMinutes = getWeekTotalMinutes(
      trend,
      weekAvgMinutes,
      summary?.week_total_minutes
    );
    const streakDays = Math.max(0, Math.round(toStudyMinutes(summary?.streak_days)));

    return (
      <>
        {loading && <p className="dashboard-loading">加载中…</p>}
        {error && <p className="dashboard-loading">{error}</p>}

        <div className="dashboard-grid">
          <section className="study-card">
            <h2>学习趋势</h2>

            <div className="chart-box">
              <div
                ref={trendChartRef}
                className="study-chart"
                role="img"
                aria-label="学习趋势图"
                style={{ width: "100%", height: "260px" }}
              />
            </div>

            <div className="study-summary">
              <div>
                <strong>{formatMetricDuration(todayStudyMinutes)}</strong>
                <span>今日学习</span>
              </div>
              <div>
                <strong>{formatMetricDuration(weekTotalMinutes)}</strong>
                <span>本周累计</span>
              </div>
              <div>
                <strong>{streakDays}</strong>
                <span>连续学习天数</span>
              </div>
            </div>
          </section>

    

          {knowledgeCards.slice(0, 3).map((card) => (
            <article className="knowledge-card" key={card.knowledge_id}>
              <div className="knowledge-card-header">
                <h2>{card.name}</h2>
              </div>

              <p>
                <span>掌握度</span>
                <strong>{card.mastery_percent}%</strong>
              </p>

              <div className="progress-bar">
                <span style={{ width: `${card.mastery_percent}%` }} />
              </div>

              <button
                className="knowledge-start"
                type="button"
                onClick={() => setActive("knowledge")}
              >
                继续学习
              </button>
            </article>
          ))}

       
        </div>
      </>
    );
  };

  return (
    <div className="dashboard-page">
      <aside className="dashboard-sidebar">
        <div className="dashboard-avatar">
          {user?.username?.slice(0, 1)?.toUpperCase() || "U"}
        </div>

        <nav className="dashboard-nav">
          {navItems.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              type="button"
              className={`dashboard-nav-item${active === key ? " active" : ""}`}
              onClick={() => setActive(key)}
              title={label}
            >
              <Icon size={20} />
            </button>
          ))}
        </nav>

        <button
          type="button"
          className="dashboard-logout"
          onClick={() => void logout()}
        >
          <LogOut size={20} />
        </button>
      </aside>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <header className="dashboard-header">
            <div>
              <h1>{pageTitle[active]}</h1>
              <p>
                {user?.username} · {role}
              </p>
            </div>

            <button type="button" className="dashboard-date">
              <CalendarDays size={18} />
              {new Date().toLocaleDateString()}
            </button>
          </header>

          {renderContent()}
        </div>
      </main>
    </div>
  );
}
