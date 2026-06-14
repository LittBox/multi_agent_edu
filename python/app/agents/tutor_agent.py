"""
Tutor Agent（教学Agent）-- 苏格拉底式提问教学。

核心职责：
1. 根据学生水平采用苏格拉底式提问，引导而非告知
2. 根据Assessment结果动态调整教学难度
3. 当学生卡住时，请求Hint Agent提供分级提示
4. 当用户明确要求“解析/解释”时，使用 DeepSeek 生成结构化、重点明确的答案解析

面试要点：
- 苏格拉底式教学：不给答案，通过反问让学生自己发现
- Prompt Engineering：针对不同mastery等级设计不同的Prompt模板
- 引导率85%目标：大部分情况只给暗示和引导
"""

import json
import logging

from openai import AsyncOpenAI

from app.agents.base_agent import BaseAgent
from app.config.settings import settings
from app.core.event_bus import Event, EventType

logger = logging.getLogger(__name__)

SOCRATIC_PROMPTS = {
    "beginner": (
        "你是一位耐心的数学老师，学生刚开始学习这个知识点。\n"
        "请用最简单的语言和例子帮助学生理解概念。\n"
        "不要直接给答案，而是：\n"
        "1. 先问学生对相关基础概念是否了解\n"
        "2. 用生活化的类比帮助理解\n"
        "3. 给一个最简单的例题让学生尝试"
    ),
    "developing": (
        "你是一位苏格拉底式的数学老师，学生正在学习中。\n"
        "请通过提问引导学生思考：\n"
        "1. 问学生已经知道哪些相关知识\n"
        "2. 引导学生发现问题的关键步骤\n"
        "3. 当学生卡住时，给一个关键提示而非答案"
    ),
    "proficient": (
        "你是一位挑战型的数学老师，学生已经比较熟练。\n"
        "请：\n"
        "1. 提出更深层的思考问题（为什么？还有其他方法吗？）\n"
        "2. 引导学生发现知识点之间的联系\n"
        "3. 给出变式题目拓展思维"
    ),
    "mastered": (
        "你是一位高级数学导师，学生已掌握此知识点。\n"
        "请：\n"
        "1. 引导学生总结归纳方法论\n"
        "2. 布置综合性、跨知识点的挑战题\n"
        "3. 鼓励学生尝试教别人（费曼学习法）"
    ),
}

ANSWER_EXPLANATION_SYSTEM_PROMPT = (
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
    "6. 如果能确定标准答案，先明确对错再分析原因。\n"
)


class TutorAgent(BaseAgent):
    """教学Agent：采用苏格拉底式提问教学法。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._student_attempts: dict[str, dict[str, int]] = {}
        self._deepseek_client = (
            AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com",
            )
            if settings.deepseek_api_key
            else None
        )

    @property
    def subscribed_events(self) -> list[EventType]:
        return [
            EventType.ASSESSMENT_COMPLETE,
            EventType.STUDENT_MESSAGE,
            EventType.HINT_RESPONSE,
            EventType.ENGAGEMENT_ALERT,
        ]

    async def handle_event(self, event: Event) -> None:
        if event.type == EventType.ASSESSMENT_COMPLETE:
            await self._handle_assessment(event)
        elif event.type == EventType.STUDENT_MESSAGE:
            await self._handle_student_message(event)
        elif event.type == EventType.HINT_RESPONSE:
            await self._handle_hint_response(event)
        elif event.type == EventType.ENGAGEMENT_ALERT:
            await self._handle_engagement_alert(event)

    async def _handle_assessment(self, event: Event) -> None:
        """根据评估结果调整教学策略。"""
        learner_id = event.learner_id
        knowledge_id = event.data.get("knowledge_id", "")
        mastery = event.data.get("mastery", 0.0)
        level = event.data.get("level", "beginner")
        is_correct = event.data.get("is_correct")

        _ = SOCRATIC_PROMPTS.get(level, SOCRATIC_PROMPTS["beginner"])

        if is_correct is False:
            attempt_key = f"{learner_id}:{knowledge_id}"
            attempts = self._student_attempts.get(attempt_key, 0) + 1
            self._student_attempts[attempt_key] = attempts

            if attempts >= 2:
                await self.emit(
                    EventType.HINT_NEEDED,
                    learner_id,
                    {
                        "knowledge_id": knowledge_id,
                        "mastery": mastery,
                        "attempts": attempts,
                        "level": level,
                    },
                )
                return

        response = self._generate_teaching_response(
            knowledge_id, level, mastery, is_correct, event.data.get("question", "")
        )

        await self.emit(
            EventType.TEACHING_RESPONSE,
            learner_id,
            {
                "knowledge_id": knowledge_id,
                "response": response,
                "teaching_style": "socratic",
                "difficulty_level": level,
                "prompt_template_used": level,
            },
        )

    def _build_deepseek_explanation_messages(
        self,
        knowledge_id: str,
        question: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool | None,
    ) -> list[dict[str, str]]:
        user_prompt = (
            f"题目知识点：{knowledge_id}\n"
            f"题目/问题：{question or '未提供'}\n"
            f"学生答案：{user_answer or '未提供'}\n"
            f"标准答案：{correct_answer or '未提供'}\n"
            f"是否正确：{is_correct if is_correct is not None else '未知'}\n\n"
            "请输出结构化解析，要求：\n"
            "- 先给结论，再给原因\n"
            "- 用清晰小标题分段\n"
            "- 每一段控制简洁，突出重点\n"
            "- 如果学生答案错误，明确指出错因和如何避免\n"
            "- 如果学生答案正确，强调关键步骤和可迁移的方法\n"
        )
        return [
            {"role": "system", "content": ANSWER_EXPLANATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

    async def _generate_deepseek_explanation(
        self,
        knowledge_id: str,
        question: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool | None,
    ) -> str:
        if not settings.deepseek_api_key:
            return self._fallback_explanation(
                knowledge_id=knowledge_id,
                question=question,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
            )

        try:
            response = await self._deepseek_client.chat.completions.create(
                model=settings.deepseek_model,
                messages=self._build_deepseek_explanation_messages(
                    knowledge_id=knowledge_id,
                    question=question,
                    user_answer=user_answer,
                    correct_answer=correct_answer,
                    is_correct=is_correct,
                ),
                temperature=0.2,
            )
            content = response.choices[0].message.content or ""
            return content.strip() or self._fallback_explanation(
                knowledge_id=knowledge_id,
                question=question,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
            )
        except Exception as exc:  # pragma: no cover - external API failure path
            logger.exception("DeepSeek explanation generation failed: %s", exc)
            return self._fallback_explanation(
                knowledge_id=knowledge_id,
                question=question,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
            )

    def _fallback_explanation(
        self,
        knowledge_id: str,
        question: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool | None,
    ) -> str:
        status = "正确" if is_correct is True else "错误" if is_correct is False else "待判断"
        return (
            f"## 结论\n"
            f"- 这道题的判断结果：{status}\n\n"
            f"## 关键思路\n"
            f"- 先抓住「{knowledge_id}」对应的核心概念，再对照题目要求逐步分析。\n\n"
            f"## 步骤解析\n"
            f"1. 题目要你解决什么问题：{question or '请补充题目内容'}\n"
            f"2. 学生答案：{user_answer or '未提供'}\n"
            f"3. 标准答案：{correct_answer or '未提供'}\n\n"
            f"## 易错点\n"
            f"- 容易忽略题干中的关键条件，或者步骤跳跃过快。\n\n"
            f"## 记忆/复盘建议\n"
            f"- 做完后把这类题的解题步骤总结成 1 个模板，下次先套模板再微调。"
        )

    def _generate_teaching_response(
        self,
        knowledge_id: str,
        level: str,
        mastery: float,
        is_correct: bool | None,
        question: str,
    ) -> str:
        """
        生成教学回复。

        实际生产环境中，这里会调用LLM（如DeepSeek）。
        当前优先演示苏格拉底式教学的逻辑框架。
        """
        if is_correct is True:
            return (
                f"很好！你在「{knowledge_id}」上的表现不错。"
                f"当前掌握度：{mastery:.0%}。\n"
                f"让我问你一个更深入的问题：你能用自己的话解释一下这个概念吗？"
                f"或者，你觉得这个知识点和之前学过的哪个知识点有联系？"
            )
        elif is_correct is False:
            return (
                f"没关系，让我们一起来分析「{knowledge_id}」。\n"
                f"先不看答案，我想问你几个问题：\n"
                f"1. 你觉得这道题考查的是什么知识点？\n"
                f"2. 你做题的时候卡在了哪一步？\n"
                f"3. 能不能先试试用最简单的数字代入看看？"
            )
        else:
            return (
                f"好的，关于「{knowledge_id}」，你的问题是：{question}\n"
                f"在我回答之前，让我先问你：\n"
                f"你对这个知识点已经了解了哪些内容？\n"
                f"试着说说你的理解，我们一起看看对不对。"
            )

    async def _handle_student_message(self, event: Event) -> None:
        """处理学生消息。"""
        learner_id = event.learner_id
        message = event.data.get("message", "")
        knowledge_id = event.data.get("knowledge_id", "general")

        model = self.get_learner_model(learner_id)
        state = model.get_state(knowledge_id)

        response = self._generate_teaching_response(
            knowledge_id, state.level.value, state.mastery, None, message
        )

        await self.emit(
            EventType.TEACHING_RESPONSE,
            learner_id,
            {
                "knowledge_id": knowledge_id,
                "response": response,
                "teaching_style": "socratic",
                "difficulty_level": state.level.value,
            },
        )

    async def _handle_hint_response(self, event: Event) -> None:
        """转发Hint Agent的回复给学生。"""
        await self.emit(
            EventType.TEACHING_RESPONSE,
            event.learner_id,
            {
                "knowledge_id": event.data.get("knowledge_id", ""),
                "response": event.data.get("hint_text", ""),
                "teaching_style": "hint",
                "hint_level": event.data.get("hint_level", 1),
            },
        )

    async def _handle_engagement_alert(self, event: Event) -> None:
        """响应Engagement Agent的警报，调整教学难度。"""
        alert_type = event.data.get("alert_type", "")
        if alert_type == "frustration":
            await self.emit(
                EventType.DIFFICULTY_ADJUSTED,
                event.learner_id,
                {
                    "action": "decrease",
                    "reason": "检测到学生挫败感",
                    "message": "我注意到你可能遇到了困难，让我们换一个角度来看这个问题，从更简单的地方开始。",
                },
            )
        elif alert_type == "boredom":
            await self.emit(
                EventType.DIFFICULTY_ADJUSTED,
                event.learner_id,
                {
                    "action": "increase",
                    "reason": "检测到学生可能感到无聊",
                    "message": "看起来这对你来说太简单了！让我给你一个更有挑战性的问题。",
                },
            )

    async def generate_answer_explanation(
        self,
        knowledge_id: str,
        question: str,
        user_answer: str,
        correct_answer: str,
        is_correct: bool | None = None,
    ) -> str:
        """对外提供答题解析，优先调用 DeepSeek。"""
        return await self._generate_deepseek_explanation(
            knowledge_id=knowledge_id,
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
        )
