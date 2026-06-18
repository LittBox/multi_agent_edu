"""学习练习服务。

面向前端练习模块：获取下一题、提交答案、学习进度、复习计划、答题历史。
"""
from datetime import datetime, UTC

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.models.answer_record import AnswerRecord
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.db.models.question import Question
from app.db.models.review_schedule import ReviewSchedule
from app.services._helpers import question_to_dict, iso
from app.core.learner_model import KnowledgeState, MasteryLevel


#将事件改成结构化、过滤后的事件
def _event_to_public_dict(event) -> dict:
    data = dict(event.data or {})
    data.pop("db", None)
    data.pop("started_at", None)

    return {
        "id": event.id,
        "type": event.type.value,
        "source": event.source,
        "timestamp": event.timestamp.isoformat(),
        "learner_id": event.learner_id,
        "data": data,
    }


class LearningService:
    def __init__(self, orchestrator):
        if orchestrator is None:
            raise RuntimeError("LearningService requires AgentOrchestrator")
        self.orchestrator = orchestrator


    async def submit_answer(self, db: AsyncSession, req) -> dict:
        """提交练习答案。

        req 兼容 Pydantic 对象或 dict，至少需要 user_id、question_id、user_answer。
        如果项目注入了 orchestrator，则由智能体链路更新状态；否则使用本地简化规则更新。
        """
        user_id = getattr(req, "user_id", None) if not isinstance(req, dict) else req.get("user_id")
        question_id = getattr(req, "question_id", None) if not isinstance(req, dict) else req.get("question_id")
        user_answer = getattr(req, "user_answer", "") if not isinstance(req, dict) else req.get("user_answer", "")
        quality_q = getattr(req, "quality_q", None) if not isinstance(req, dict) else req.get("quality_q")
        time_spent_seconds = getattr(req, "time_spent_seconds", None) if not isinstance(req, dict) else req.get("time_spent_seconds")

        question = (await db.execute(select(Question).where(Question.question_id == question_id))).scalar_one_or_none()
        if not question:
            raise ValueError("Question not found")
        is_correct = str(user_answer).strip().upper() == question.answer.strip().upper()

        # 如果 quality_q 未提供，则根据是否正确自动设置；如果不正确，则限制最大值为 2。
        if quality_q is None:
            quality_q = None
        elif not is_correct:
            quality_q = min(int(quality_q), 2)
        else:
            quality_q = int(quality_q)


        if self.orchestrator:
            events = await self.orchestrator.submit_answer(
                learner_id=str(user_id),
                knowledge_id=str(question.knowledge_id),
                is_correct=is_correct,
                question_id=str(question.question_id),
                user_answer=str(user_answer).strip(),
                quality_q=quality_q,
                started_at=datetime.now(UTC),
                db=db,
                time_spent_seconds=time_spent_seconds,
            )
            events_payload = [_event_to_public_dict(e) for e in events]

        return {
            "is_correct": is_correct,
            "correct_answer": question.answer,
            "explanation": question.explanation,
            "knowledge_id": question.knowledge_id,
            "question_id": question.question_id,
            "events_triggered": len(events_payload),
            "events": events_payload,
        }

    

    async def get_next_question(
        self,
        db: AsyncSession,
        user_id: int,
        knowledge_id: int | None = None,
    ) -> dict | None:
        """
        获取下一题。

        规则：
        1. 如果指定 knowledge_id，只允许返回该知识点下的题。
        该知识点没有可练习题时，返回 no_question_for_knowledge，不再静默切到其他知识点。
        2. 如果未指定 knowledge_id，才允许走全局推荐/随机兜底。
        """

        now = datetime.now(UTC)

        # 指定知识点：严格限制在当前知识点内
        if knowledge_id is not None:
            # 1. 优先找该知识点下未做过的新题
            query = (
                select(Question)
                .outerjoin(
                    AnswerRecord,
                    and_(
                        AnswerRecord.question_id == Question.question_id,
                        AnswerRecord.user_id == user_id,
                    ),
                )
                .where(
                    Question.knowledge_id == knowledge_id,
                    AnswerRecord.record_id.is_(None),
                )
                .order_by(Question.difficulty.asc(), func.random())
                .limit(1)
            )

            question = (await db.execute(query)).scalar_one_or_none()

            if question:
                data = question_to_dict(question, include_answer=False)
                data["reason"] = "new_question"
                data["requested_knowledge_id"] = knowledge_id
                return data

            # 2. 如果这个知识点有到期复习，则仍然只从这个知识点里抽题
            due = (
                await db.execute(
                    select(ReviewSchedule)
                    .where(
                        ReviewSchedule.user_id == user_id,
                        ReviewSchedule.knowledge_id == knowledge_id,
                        ReviewSchedule.next_review_at <= now,
                    )
                    .order_by(ReviewSchedule.next_review_at.asc())
                    .limit(1)
                )
            ).scalar_one_or_none()

            if due:
                question = (
                    await db.execute(
                        select(Question)
                        .where(Question.knowledge_id == knowledge_id)
                        .order_by(func.random())
                        .limit(1)
                    )
                ).scalar_one_or_none()

                if question:
                    data = question_to_dict(question, include_answer=False)
                    data["reason"] = "due_review"
                    data["requested_knowledge_id"] = knowledge_id
                    return data

            # 3. 该知识点没有可用题，明确返回原因
            return {
                "question_id": None,
                "knowledge_id": knowledge_id,
                "requested_knowledge_id": knowledge_id,
                "reason": "no_question_for_knowledge",
                "message": "当前知识点暂无可练习题目，请选择其他知识点或联系教师添加题目。",
            }

        # 未指定知识点：全局找未做过的新题
        query = (
            select(Question)
            .outerjoin(
                AnswerRecord,
                and_(
                    AnswerRecord.question_id == Question.question_id,
                    AnswerRecord.user_id == user_id,
                ),
            )
            .where(AnswerRecord.record_id.is_(None))
            .order_by(Question.difficulty.asc(), func.random())
            .limit(1)
        )

        question = (await db.execute(query)).scalar_one_or_none()
        reason = "new_question"

        # 全局到期复习
        if not question:
            due = (
                await db.execute(
                    select(ReviewSchedule)
                    .where(
                        ReviewSchedule.user_id == user_id,
                        ReviewSchedule.next_review_at <= now,
                    )
                    .order_by(ReviewSchedule.next_review_at.asc())
                    .limit(1)
                )
            ).scalar_one_or_none()

            if due:
                question = (
                    await db.execute(
                        select(Question)
                        .where(Question.knowledge_id == due.knowledge_id)
                        .order_by(func.random())
                        .limit(1)
                    )
                ).scalar_one_or_none()
                reason = "due_review"

        # 只有未指定 knowledge_id 时，才允许全局兜底
        if not question:
            question = (
                await db.execute(
                    select(Question)
                    .order_by(func.random())
                    .limit(1)
                )
            ).scalar_one_or_none()
            reason = "fallback_random"

        if not question:
            return None

        data = question_to_dict(question, include_answer=False)
        data["reason"] = reason
        data["requested_knowledge_id"] = None
        return data


    async def get_progress(self, db: AsyncSession, user_id: int) -> list[dict]:
        rows = (await db.execute(select(LearnerState, KnowledgePoint).join(KnowledgePoint, KnowledgePoint.knowledge_id == LearnerState.knowledge_id).where(LearnerState.user_id == user_id).order_by(LearnerState.mastery.desc()))).all()
        return [{
            "knowledge_id": s.knowledge_id,
            "name": kp.name,
            "subject": kp.subject,
            "mastery": round(s.mastery, 2),
            "mastery_percent": int(round(s.mastery * 100)),
            "confidence": round(s.confidence, 2),
            "attempts": s.attempts,
            "correct_attempts": s.correct_attempts,
            "streak": s.streak,
            "status": (
                "mastered"
                    if KnowledgeState(
                        knowledge_id=str(s.knowledge_id),
                        mastery=s.mastery,
                        attempts=s.attempts,
                    ).level == MasteryLevel.MASTERED
                    else "learning"
                ),
            "last_practiced_at": iso(s.last_practiced_at),
        } for s, kp in rows]

    async def get_due_reviews(self, db: AsyncSession, user_id: int, due_only: bool = True) -> list[dict]:
        query = select(ReviewSchedule, KnowledgePoint).join(KnowledgePoint, KnowledgePoint.knowledge_id == ReviewSchedule.knowledge_id).where(ReviewSchedule.user_id == user_id)
        if due_only:
            query = query.where(ReviewSchedule.next_review_at <= datetime.now(UTC))
        rows = (await db.execute(query.order_by(ReviewSchedule.next_review_at.asc()))).all()
        now = datetime.now(UTC)
        return [{
            "knowledge_id": schedule.knowledge_id,
            "name": kp.name,
            "subject": kp.subject,
            "next_review_at": iso(schedule.next_review_at),
            "last_review_at": iso(schedule.last_review_at),
            "interval_days": schedule.interval_days,
            "repetition": schedule.repetition,
            "ef": schedule.ef,
            "is_due": bool(schedule.next_review_at and schedule.next_review_at <= now),
        } for schedule, kp in rows]

    async def get_answer_history(self, db: AsyncSession, user_id: int,
                                 limit: int = 20, offset: int = 0) -> dict:
        total = (await db.execute(select(func.count(AnswerRecord.record_id)).where(AnswerRecord.user_id == user_id))).scalar_one()
        rows = (await db.execute(select(AnswerRecord, Question, KnowledgePoint).join(Question, Question.question_id == AnswerRecord.question_id).join(KnowledgePoint, KnowledgePoint.knowledge_id == AnswerRecord.knowledge_id).where(AnswerRecord.user_id == user_id).order_by(AnswerRecord.submitted_at.desc()).limit(limit).offset(offset))).all()
        return {"total": total, "items": [{
            "record_id": r.record_id,
            "question_id": r.question_id,
            "knowledge_id": r.knowledge_id,
            "knowledge_name": kp.name,
            "subject": kp.subject,
            "stem": q.stem,
            "user_answer": r.user_answer,
            "correct_answer": q.answer,
            "is_correct": r.is_correct,
            "submitted_at": iso(r.submitted_at),
            "time_spent_seconds": r.time_spent_seconds,
        } for r, q, kp in rows]}
