import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.config.settings import settings
from app.services.llm_service import llm_service
from app.schemas.api_response import api_success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tutor", tags=["tutor"])


ANSWER_ANALYSIS_SYSTEM_PROMPT = (
    "你是一个高质量的答题解析 agent。"
    "你的任务是根据题目、用户答案、正确答案与知识点，输出结构化、重点明确、便于学生复盘的解析。\n\n"
    "输出要求：\n"
    "1. 必须使用中文。\n"
    "2. 必须结构化，建议使用以下小标题：\n"
    "   - 结论\n"
    "   - 关键思路\n"
    "   - 步骤解析\n"
    "   - 易错点\n"
    "   - 记忆/复盘建议\n"
    "3. 解析要突出重点，不要长篇大论，不要空话套话。\n"
    "4. 如果题目信息不足，也要先给出可用的分析框架，再说明需要补充哪些信息。\n"
    "5. 适合学生阅读，语气清晰、直接、友好。\n"
    "6. 如果能确定标准答案，先明确对错再分析原因。"
)


class AnswerAnalysisRequest(BaseModel):
    learner_id: str = "default"
    knowledge_id: str
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool | None = None




def build_answer_analysis_messages(request: AnswerAnalysisRequest) -> list[dict[str, str]]:
    user_prompt = (
        f"题目知识点：{request.knowledge_id}\n"
        f"题目/问题：{request.question or '未提供'}\n"
        f"学生答案：{request.user_answer or '未提供'}\n"
        f"标准答案：{request.correct_answer or '未提供'}\n"
        f"是否正确：{request.is_correct if request.is_correct is not None else '未知'}\n\n"
        "请输出结构化解析，要求：\n"
        "- 先给结论，再给原因\n"
        "- 用清晰小标题分段\n"
        "- 每一段控制简洁，突出重点\n"
        "- 如果学生答案错误，明确指出错因和如何避免\n"
        "- 如果学生答案正确，强调关键步骤和可迁移的方法"
    )

    return [
        {"role": "system", "content": ANSWER_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def fallback_answer_analysis(request: AnswerAnalysisRequest) -> str:
    status = "正确" if request.is_correct is True else "错误" if request.is_correct is False else "待判断"

    return (
        f"## 结论\n"
        f"- 这道题的判断结果：{status}\n\n"
        f"## 关键思路\n"
        f"- 先抓住「{request.knowledge_id}」对应的核心概念，再对照题目要求逐步分析。\n\n"
        f"## 步骤解析\n"
        f"1. 题目要解决的问题：{request.question or '请补充题目内容'}\n"
        f"2. 学生答案：{request.user_answer or '未提供'}\n"
        f"3. 标准答案：{request.correct_answer or '未提供'}\n\n"
        f"## 易错点\n"
        f"- 容易把题目中的核心知识点和无关任务混淆。\n\n"
        f"## 记忆/复盘建议\n"
        f"- 下次遇到类似题目时，先判断题目考查的概念归属，再选择答案。"
    )


@router.post("/answer-analysis")
async def generate_answer_analysis(request: AnswerAnalysisRequest):
    try:
        analysis = await llm_service.chat_with_deepseek(
            messages=build_answer_analysis_messages(request),
            temperature=0.2,
        )
    except Exception as exc:
        logger.exception("Answer analysis generation failed: %s", exc)
        analysis = fallback_answer_analysis(request)

    return api_success(
        data={
            "learner_id": request.learner_id,
            "knowledge_id": request.knowledge_id,
            "is_correct": request.is_correct,
            "agent": "TutorAgent",
            "model": settings.deepseek_model,
            "analysis": analysis,
        }
    )