import { useEffect, useMemo, useState } from "react";
import { useEducationStore } from "../stores";
import "../styles/pages/PracticePage.css";

interface PracticePageProps { userId: number; knowledgeId?: number; onClose: () => void; }

/** 练习弹窗：从 EducationStore 拉取下一题并提交答案。 */
export default function PracticePage({ userId, knowledgeId, onClose }: PracticePageProps) {
  const { currentQuestion, answerResult, loading, error, loadNextQuestion, submitAnswer } = useEducationStore();
  const [selected, setSelected] = useState("");
  const [startedAt, setStartedAt] = useState(() => Date.now());

  useEffect(() => { void loadNextQuestion(userId, knowledgeId).then(() => { setSelected(""); setStartedAt(Date.now()); }); }, [userId, knowledgeId]);

  const options = useMemo(() => currentQuestion ? [
    ["A", currentQuestion.option_a], ["B", currentQuestion.option_b], ["C", currentQuestion.option_c], ["D", currentQuestion.option_d],
  ].filter(([, text]) => Boolean(text)) : [], [currentQuestion]);

  const submit = async () => {
    if (!currentQuestion || !selected) return;
    await submitAnswer({ user_id: userId, question_id: currentQuestion.question_id, user_answer: selected, quality_q: 4, time_spent_seconds: Math.round((Date.now() - startedAt) / 1000) });
  };

  const next = async () => {
    await loadNextQuestion(userId, knowledgeId);
    setSelected(""); setStartedAt(Date.now());
  };

  return (
    <div className="practice-overlay">
      <div className="practice-modal">
        <header className="practice-header"><h2>知识点练习</h2><button className="practice-close" type="button" onClick={onClose}>关闭</button></header>
        {loading && <p className="practice-status">加载中…</p>}
        {error && <p className="practice-error">{error}</p>}
        {!currentQuestion && !loading && <p className="practice-status">暂无可练习题目</p>}
        {currentQuestion && (
          <>
            <p className="practice-stem">{currentQuestion.stem}</p>
            <div className="practice-options">
              {options.map(([key, text]) => <button key={key} type="button" className={`practice-option${selected === key ? " selected" : ""}`} onClick={() => setSelected(String(key))}>{key}. {text}</button>)}
            </div>
            <div className="practice-actions"><button type="button" disabled={!selected} onClick={() => void submit()}>提交答案</button></div>
          </>
        )}
        {answerResult && (
          <div className="practice-feedback">
            <p className={answerResult.is_correct ? "practice-success" : "practice-fail"}>{answerResult.is_correct ? "回答正确" : `回答错误，正确答案：${answerResult.correct_answer}`}</p>
            <p className="practice-explanation">{answerResult.explanation || "暂无解析"}</p>
            {answerResult.agent_reply && <p className="practice-agent">{answerResult.agent_reply}</p>}
            <div className="practice-actions"><button type="button" onClick={() => void next()}>下一题</button></div>
          </div>
        )}
      </div>
    </div>
  );
}
