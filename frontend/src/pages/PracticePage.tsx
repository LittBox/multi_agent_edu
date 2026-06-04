import { useCallback, useEffect, useState } from "react";
import {
  fetchNextQuestion,
  submitAnswer,
  type Question,
} from "../api/education";
import "../styles/pages/PracticePage.css";

interface PracticePageProps {
  userId: number;
  knowledgeId?: number;
  onClose: () => void;
  onSubmitted?: () => void;
}

const OPTIONS = ["A", "B", "C", "D"] as const;

const PracticePage: React.FC<PracticePageProps> = ({
  userId,
  knowledgeId,
  onClose,
  onSubmitted,
}) => {
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{
    isCorrect: boolean;
    correctAnswer: string;
    explanation: string | null;
    agentReply: string | null;
  } | null>(null);
  const [error, setError] = useState("");
  const [startedAt] = useState(() => Date.now());

  const loadQuestion = useCallback(async () => {
    setLoading(true);
    setError("");
    setFeedback(null);
    setSelected("");

    try {
      const next = await fetchNextQuestion(userId, knowledgeId);
      setQuestion(next);
      if (!next) {
        setError("暂无可用题目，请稍后再试");
      }
    } catch {
      setError("加载题目失败");
    } finally {
      setLoading(false);
    }
  }, [userId, knowledgeId]);

  useEffect(() => {
    loadQuestion();
  }, [loadQuestion]);

  const handleSubmit = async () => {
    if (!question || !selected) return;

    setSubmitting(true);
    setError("");

    try {
      const timeSpent = (Date.now() - startedAt) / 1000;
      const result = await submitAnswer({
        user_id: userId,
        question_id: question.question_id,
        user_answer: selected,
        quality_q: 4,
        time_spent_seconds: timeSpent,
      });

      setFeedback({
        isCorrect: result.is_correct,
        correctAnswer: result.correct_answer,
        explanation: result.explanation,
        agentReply: result.agent_reply,
      });
      onSubmitted?.();
    } catch {
      setError("提交失败，请重试");
    } finally {
      setSubmitting(false);
    }
  };

  const optionValue = (key: (typeof OPTIONS)[number]) => {
    if (!question) return "";
    const map = {
      A: question.option_a,
      B: question.option_b,
      C: question.option_c,
      D: question.option_d,
    };
    return map[key] ?? "";
  };

  return (
    <div className="practice-overlay">
      <div className="practice-modal">
        <header className="practice-header">
          <h2>答题练习</h2>
          <button type="button" className="practice-close" onClick={onClose}>
            关闭
          </button>
        </header>

        {loading && <p className="practice-status">加载中…</p>}
        {error && <p className="practice-error">{error}</p>}

        {!loading && question && (
          <>
            <p className="practice-stem">{question.stem}</p>
            <div className="practice-options">
              {OPTIONS.map((key) => {
                const text = optionValue(key);
                if (!text) return null;
                return (
                  <button
                    key={key}
                    type="button"
                    className={`practice-option${
                      selected === key ? " selected" : ""
                    }`}
                    onClick={() => setSelected(key)}
                    disabled={!!feedback}
                  >
                    <strong>{key}.</strong> {text}
                  </button>
                );
              })}
            </div>

            {feedback && (
              <div className="practice-feedback">
                <p
                  className={
                    feedback.isCorrect ? "practice-success" : "practice-fail"
                  }
                >
                  {feedback.isCorrect
                    ? "回答正确！"
                    : `回答错误，正确答案：${feedback.correctAnswer}`}
                </p>
                {feedback.explanation && (
                  <p className="practice-explanation">{feedback.explanation}</p>
                )}
                {feedback.agentReply && (
                  <p className="practice-agent">{feedback.agentReply}</p>
                )}
              </div>
            )}

            <div className="practice-actions">
              {!feedback ? (
                <button
                  type="button"
                  disabled={!selected || submitting}
                  onClick={handleSubmit}
                >
                  {submitting ? "提交中…" : "提交答案"}
                </button>
              ) : (
                <button type="button" onClick={loadQuestion}>
                  下一题
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PracticePage;
