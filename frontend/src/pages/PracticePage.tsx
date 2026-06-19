import { useEffect, useMemo, useState } from "react";
import type { CSSProperties } from "react";
import { useEducationStore } from "../stores";
import GlassToast from "../components/GlassToast/GlassToast";
import type { Question, SubmitAnswerResult } from "../api/education";
import "../styles/pages/PracticePage.css";
import { generateAnswerAnalysis } from "../api/tutor";
import ReactMarkdown from "react-markdown";
interface PracticePageProps {
  userId: number;
  knowledgeId?: number;
  onClose: () => void;
}

type ToastType = "info" | "success" | "warning" | "error";

interface ToastState {
  open: boolean;
  title: string;
  message: string;
  type: ToastType;
  confirmText?: string;
  onConfirm?: () => void;
}

const emptyToast: ToastState = {
  open: false,
  title: "提示",
  message: "",
  type: "info",
};

function previewText(value?: string | null, max = 20) {
  const text = (value || "").trim();
  if (!text) return "未命名题目";
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

function formatDateTime(value?: string | null) {
  if (!value) return "暂未排期";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "暂未排期";

  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function clampPercent(value?: number | null) {
  const num = Number(value ?? 0);
  if (!Number.isFinite(num)) return 0;
  return Math.max(0, Math.min(100, Math.round(num)));
}

type RealQuestion = Question & {
  question_id: number;
};

function isRealQuestion(
  question: Question | null | undefined
): question is RealQuestion {
  return Boolean(question && question.question_id != null);
}

function getQuestionDifficulty(question: Question | null | undefined) {
  return question?.difficulty ?? 999;
}

/** 三栏练习页：左题单，中间做题，右掌握度看板。 */
export default function PracticePage({
  userId,
  knowledgeId,
  onClose,
}: PracticePageProps) {
  const {
    questions,
    currentQuestion,
    progress,
    reviews,
    loading,
    error,
    loadQuestions,
    loadQuestion,
    loadNextQuestion,
    submitAnswer,
    loadProgress,
    loadReviews,
  } = useEducationStore();

  const [selected, setSelected] = useState("");
  const [startedAt, setStartedAt] = useState(() => Date.now());
  const [roundStartedAt] = useState(() => Date.now());

  const [roundAnswered, setRoundAnswered] = useState(0);
  const [roundCorrect, setRoundCorrect] = useState(0);
  const [answeredQuestionIds, setAnsweredQuestionIds] = useState<Set<number>>(
    () => new Set(),
  );
  const [answerAnalysis, setAnswerAnalysis] = useState("");
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");
  const [lastResult, setLastResult] = useState<SubmitAnswerResult | null>(null);
  const [resultQuestionId, setResultQuestionId] = useState<number | null>(null);
  const [toast, setToast] = useState<ToastState>(emptyToast);

  const activeKnowledgeId =
    knowledgeId ?? currentQuestion?.knowledge_id ?? undefined;

  const orderedQuestions = useMemo(() => {
    return [...questions]
      .filter((item) => {
        if (!activeKnowledgeId) return true;
        return item.knowledge_id === activeKnowledgeId;
      })
      .filter((item) => item.question_id != null)
      .sort((a, b) => Number(a.question_id ?? 0) - Number(b.question_id ?? 0));
  }, [questions, activeKnowledgeId]);

  const currentReview = useMemo(() => {
    if (!activeKnowledgeId) return null;

    return (
      reviews.find((item) => item.knowledge_id === activeKnowledgeId) ?? null
    );
  }, [reviews, activeKnowledgeId]);

  /**
   * 当前后端 review_schedule 是知识点级别，不是题目级别。
   * 所以这里的“复习排期”是在当前知识点题目中按：
   * 未练优先 -> 难度低优先 -> question_id 顺序
   * 来排展示。
   */
  const scheduledQuestions = useMemo(() => {
    return [...orderedQuestions].sort((a, b) => {
      const aId = Number(a.question_id ?? -1);
      const bId = Number(b.question_id ?? -1);

      const aAnswered = answeredQuestionIds.has(aId) ? 1 : 0;
      const bAnswered = answeredQuestionIds.has(bId) ? 1 : 0;

      if (aAnswered !== bAnswered) return aAnswered - bAnswered;

      const aDifficulty = getQuestionDifficulty(a);
      const bDifficulty = getQuestionDifficulty(b);

      if (aDifficulty !== bDifficulty) return aDifficulty - bDifficulty;

      return aId - bId;
    });
  }, [orderedQuestions, answeredQuestionIds]);

  const knowledgeProgress = useMemo(() => {
    if (!activeKnowledgeId) return null;

    return (
      progress.find((item) => item.knowledge_id === activeKnowledgeId) ?? null
    );
  }, [progress, activeKnowledgeId]);

  const options = useMemo(() => {
    if (!isRealQuestion(currentQuestion)) return [];

    const rows: Array<[string, string | null | undefined]> = [
      ["A", currentQuestion.option_a],
      ["B", currentQuestion.option_b],
      ["C", currentQuestion.option_c],
      ["D", currentQuestion.option_d],
    ];

    return rows.filter(([, text]) => Boolean(text)) as Array<[string, string]>;
  }, [currentQuestion]);

  const currentQuestionId = currentQuestion?.question_id ?? null;

  const showResult =
    lastResult !== null &&
    currentQuestionId !== null &&
    resultQuestionId === currentQuestionId;

  const showToast = (nextToast: Omit<ToastState, "open">) => {
    setToast({
      ...nextToast,
      open: true,
    });
  };

  const closeToast = () => {
    const onConfirm = toast.onConfirm;
    setToast(emptyToast);
    onConfirm?.();
  };

  const resetQuestionState = () => {
    setSelected("");
    setStartedAt(Date.now());
    setLastResult(null);
    setResultQuestionId(null);
    setAnswerAnalysis("");
    setAnalysisLoading(false);
    setAnalysisError("");
  };

  const selectQuestion = async (questionId: number) => {
    await loadQuestion(questionId);
    resetQuestionState();
  };

  const loadInitialData = async () => {
    const [questionList] = await Promise.all([
      loadQuestions(userId, knowledgeId),
      loadReviews(userId, false),
      loadProgress(userId),
    ]);

    const next = await loadNextQuestion(userId, knowledgeId);

    if (
      next &&
      next.question_id != null &&
      (!knowledgeId || next.knowledge_id === knowledgeId)
    ) {
      await loadQuestion(next.question_id);
      resetQuestionState();
      return;
    }

    const firstQuestion = questionList.find(
      (item) => item.question_id != null,
    );

    if (firstQuestion?.question_id != null) {
      await loadQuestion(firstQuestion.question_id);
      resetQuestionState();

      if (next && knowledgeId && next.knowledge_id !== knowledgeId) {
        showToast({
          title: "已限制当前知识点",
          message:
            "后端返回了其他知识点题目，页面已自动停留在当前知识点题目列表。",
          type: "warning",
        });
      }

      return;
    }

    showToast({
      title: "暂无题目",
      message:
        next?.message ||
        "当前知识点暂无可练习题目，请选择其他知识点或联系教师添加题目。",
      type: "warning",
    });
  };

  useEffect(() => {
    void loadInitialData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId, knowledgeId]);

  const submit = async () => {
    if (!isRealQuestion(currentQuestion) || !selected) return;

    const questionId = currentQuestion.question_id;

    setAnswerAnalysis("");
    setAnalysisError("");
    setAnalysisLoading(true);

    const result = await submitAnswer({
      user_id: userId,
      question_id: questionId,
      user_answer: selected,
      quality_q: 4,
      time_spent_seconds: Math.max(
        1,
        Math.round((Date.now() - startedAt) / 1000),
      ),
    });

    setLastResult(result);
    setResultQuestionId(questionId);

    setRoundAnswered((value) => value + 1);
    setRoundCorrect((value) => value + (result.is_correct ? 1 : 0));

    setAnsweredQuestionIds((prev) => {
      const next = new Set(prev);
      next.add(questionId);
      return next;
    });

    const selectedOptionText =
      options.find(([key]) => key === selected)?.[1] ?? selected;

    const correctOptionText =
      options.find(([key]) => key === result.correct_answer)?.[1] ??
      result.correct_answer ??
      "";

    try {
      const analysisResult = await generateAnswerAnalysis({
        learner_id: String(userId),
        knowledge_id: String(currentQuestion.knowledge_id ?? knowledgeId ?? "general"),
        question: currentQuestion.stem || "题干为空",
        user_answer: selectedOptionText,
        correct_answer: correctOptionText,
        is_correct: result.is_correct,
      });

      setAnswerAnalysis(analysisResult.analysis);
    } catch (error) {
      console.error(error);
      setAnalysisError("AI 解析生成失败，已保留基础解析。");
    } finally {
      setAnalysisLoading(false);
    }

    await Promise.allSettled([
      loadQuestions(userId, knowledgeId),
      loadReviews(userId, false),
      loadProgress(userId),
    ]);
  };

  const goRecommendedNext = async () => {
    const next = await loadNextQuestion(userId, knowledgeId);

    if (!next || next.question_id == null) {
      showToast({
        title: "暂无新题",
        message:
          next?.message ||
          "当前知识点暂无新的可练习题目，你可以从左侧题目列表中手动选择复盘。",
        type: "warning",
      });
      return;
    }

    if (knowledgeId && next.knowledge_id !== knowledgeId) {
      showToast({
        title: "已阻止跨知识点跳题",
        message: "当前知识点没有新的推荐题，系统不会再自动切到其他知识点。",
        type: "warning",
      });
      return;
    }

    await selectQuestion(next.question_id);
  };

  const finishPractice = () => {
    const minutes = Math.max(
      1,
      Math.round((Date.now() - roundStartedAt) / 60000),
    );

    const accuracy =
      roundAnswered > 0 ? Math.round((roundCorrect / roundAnswered) * 100) : 0;

    const message =
      roundAnswered > 0
        ? `本轮完成 ${roundAnswered} 题，答对 ${roundCorrect} 题，正确率 ${accuracy}%，练习时长约 ${minutes} 分钟。`
        : "本轮还没有提交题目，已为你保留当前练习进度。";

    showToast({
      title: "本轮练习总结",
      message,
      type: roundAnswered > 0 ? "success" : "info",
      confirmText: "返回",
      onConfirm: onClose,
    });
  };

  const masteryPercent = clampPercent(knowledgeProgress?.mastery_percent);
  const confidencePercent = clampPercent(
    Number(knowledgeProgress?.confidence ?? 0) * 100,
  );

  const masteryRingStyle = {
    "--mastery-percent": `${masteryPercent}%`,
  } as CSSProperties;

  return (
    <section className="practice-page">
      <header className="practice-page-header">
        <button className="practice-back" type="button" onClick={finishPractice}>
          ← 返回
        </button>

        <div>
          <p className="practice-eyebrow">Knowledge Practice</p>
          <h1>知识点练习</h1>
        </div>

        <div className="practice-header-meta">
          <span>用户 #{userId}</span>
          {activeKnowledgeId && <span>知识点 #{activeKnowledgeId}</span>}
        </div>
      </header>

      <main className="practice-three-column">
        <aside className="practice-left-panel">
          <section className="practice-card">
            <div className="practice-card-title">
              <h2>顺序题目</h2>
              <span>{orderedQuestions.length} 题</span>
            </div>

            <div className="practice-square-grid">
              {orderedQuestions.map((question, index) => {
                const questionId = question.question_id;
                if (questionId == null) return null;

                const active = currentQuestionId === questionId;
                const answered = answeredQuestionIds.has(questionId);

                return (
                  <button
                    key={questionId}
                    type="button"
                    className={[
                      "practice-question-square",
                      active ? "active" : "",
                      answered ? "answered" : "",
                    ].join(" ")}
                    onClick={() => void selectQuestion(questionId)}
                    title={question.stem || `题目 ${questionId}`}
                  >
                    {index + 1}
                  </button>
                );
              })}

              {!orderedQuestions.length && (
                <p className="practice-empty">当前知识点暂无题目</p>
              )}
            </div>
          </section>

          <section className="practice-card practice-schedule-card">
            <div className="practice-card-title">
              <h2>复习排期</h2>
              <span>{currentReview?.is_due ? "已到期" : "计划中"}</span>
            </div>

            <div className="practice-schedule-summary">
              <span>下次复习</span>
              <strong>{formatDateTime(currentReview?.next_review_at)}</strong>
            </div>

            <div className="practice-table">
              <div className="practice-table-head">
                <span>题目</span>
                <span>难度</span>
                <span>状态</span>
              </div>

              {scheduledQuestions.map((question) => {
                const questionId = question.question_id;
                if (questionId == null) return null;

                const active = currentQuestionId === questionId;
                const answered = answeredQuestionIds.has(questionId);

                return (
                  <button
                    key={questionId}
                    type="button"
                    className={`practice-table-row${active ? " active" : ""}`}
                    onClick={() => void selectQuestion(questionId)}
                  >
                    <span title={question.stem || ""}>
                      {previewText(question.stem)}
                    </span>
                    <span>D{question.difficulty ?? "-"}</span>
                    <span>
                      {answered
                        ? "已练"
                        : currentReview?.is_due
                          ? "待复习"
                          : "未练"}
                    </span>
                  </button>
                );
              })}

              {!scheduledQuestions.length && (
                <p className="practice-empty">
                  当前知识点暂无复习排期；你仍然可以从上方顺序题目开始练习。
                </p>
              )}
            </div>
          </section>
        </aside>

        <section className="practice-center-panel">
          <div className="practice-question-card">
            {loading && <p className="practice-status">加载中…</p>}

            {error && <p className="practice-error">{error}</p>}

            {!loading && !currentQuestion && (
              <div className="practice-empty-state">
                <h2>暂无题目</h2>
                <p>当前知识点暂无可练习题目。</p>
              </div>
            )}

            {!loading && currentQuestion && currentQuestion.question_id == null && (
              <div className="practice-empty-state">
                <h2>暂无可练习题目</h2>
                <p>
                  {currentQuestion.message ||
                    "当前知识点暂无可练习题目，请选择其他知识点。"}
                </p>
              </div>
            )}

            {!loading && isRealQuestion(currentQuestion) && (
              <>
                <div className="practice-question-toolbar">
                  <span>题目 #{currentQuestion.question_id}</span>
                  <span>难度 D{currentQuestion.difficulty ?? "-"}</span>
                </div>

                <h2 className="practice-stem">
                  {currentQuestion.stem || "题干为空"}
                </h2>

                <div className="practice-options">
                  {options.map(([key, text]) => {
                    const isSelected = selected === key;
                    const isCorrectOption =
                      showResult && key === lastResult?.correct_answer;
                    const isWrongSelected =
                      showResult && isSelected && !lastResult?.is_correct;

                    return (
                      <button
                        key={key}
                        type="button"
                        className={[
                          "practice-option",
                          isSelected ? "selected" : "",
                          isCorrectOption ? "correct" : "",
                          isWrongSelected ? "wrong" : "",
                        ].join(" ")}
                        onClick={() => {
                          if (!showResult) setSelected(key);
                        }}
                      >
                        <span>{key}</span>
                        <p>{text}</p>
                      </button>
                    );
                  })}
                </div>

                <div className="practice-actions">
                  <button
                    type="button"
                    className="practice-primary"
                    disabled={!selected || showResult}
                    onClick={() => void submit()}
                  >
                    提交答案
                  </button>

                  <button
                    type="button"
                    className="practice-secondary"
                    onClick={() => void goRecommendedNext()}
                  >
                    推荐下一题
                  </button>
                </div>

                {showResult && lastResult && (
                  <div className="practice-feedback">
                    <strong
                      className={
                        lastResult.is_correct
                          ? "practice-success"
                          : "practice-fail"
                      }
                    >
                      {lastResult.is_correct
                        ? "回答正确"
                        : `回答错误，正确答案：${lastResult.correct_answer}`}
                    </strong>

                        {analysisLoading && (
                          <p className="practice-status">Tutor Agent 正在生成解析…</p>
                        )}

                        {analysisError && (
                          <p className="practice-error">{analysisError}</p>
                        )}

                      <div className="practice-analysis-markdown">
                        <ReactMarkdown>
                          {answerAnalysis || lastResult.explanation || "暂无解析"}
                        </ReactMarkdown>
                      </div>

                        {lastResult.agent_reply && (
                          <div className="practice-agent">
                            {lastResult.agent_reply}
                          </div>
                        )}

                  </div>
                )}
              </>
            )}
          </div>
        </section>

        <aside className="practice-right-panel">
          <section className="practice-card practice-mastery-card">
            <div className="practice-card-title">
              <h2>掌握度看板</h2>
              <span>{knowledgeProgress?.status || "暂无状态"}</span>
            </div>

            <div className="practice-mastery-ring" style={masteryRingStyle}>
              <div>
                <strong>{masteryPercent}%</strong>
                <span>Mastery</span>
              </div>
            </div>

            <div className="practice-stat-grid">
              <div>
                <span>掌握概率</span>
                <strong>
                  {knowledgeProgress?.mastery?.toFixed(2) ?? "0.00"}
                </strong>
              </div>

              <div>
                <span>置信度</span>
                <strong>{confidencePercent}%</strong>
              </div>

              <div>
                <span>累计尝试</span>
                <strong>{knowledgeProgress?.attempts ?? 0}</strong>
              </div>

              <div>
                <span>答对次数</span>
                <strong>{knowledgeProgress?.correct_attempts ?? 0}</strong>
              </div>

              <div>
                <span>连续正确</span>
                <strong>{knowledgeProgress?.streak ?? 0}</strong>
              </div>

              <div>
                <span>上次练习</span>
                <strong>
                  {formatDateTime(knowledgeProgress?.last_practiced_at)}
                </strong>
              </div>
            </div>
          </section>

          <section className="practice-card">
            <div className="practice-card-title">
              <h2>本轮情况</h2>
              <span>实时</span>
            </div>

            <div className="practice-round-list">
              <p>
                已提交 <strong>{roundAnswered}</strong> 题
              </p>
              <p>
                答对 <strong>{roundCorrect}</strong> 题
              </p>
              <p>
                正确率{" "}
                <strong>
                  {roundAnswered
                    ? Math.round((roundCorrect / roundAnswered) * 100)
                    : 0}
                  %
                </strong>
              </p>
            </div>
          </section>
        </aside>
      </main>

      <GlassToast
        open={toast.open}
        title={toast.title}
        message={toast.message}
        type={toast.type}
        confirmText={toast.confirmText}
        onClose={closeToast}
      />
    </section>
  );
}