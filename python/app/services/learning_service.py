"""学习练习服务。

面向前端练习模块：获取下一题、提交答案、学习进度、复习计划、答题历史。
"""
from datetime import datetime, UTC

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.answerRecordDao import AnswerRecordDAO
from app.dao.learnerStateDao import LearnerStateDAO
from app.dao.reviewScheduleDao import ReviewScheduleDAO
from app.db.models.answer_record import AnswerRecord
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.db.models.question import Question
from app.db.models.review_schedule import ReviewSchedule
from app.services._helpers import question_to_dict, iso
from app.core.learner_model import LearnerModel, KnowledgeState, MasteryLevel





class LearningService:
    def __init__(self, orchestrator=None):
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
            events_payload = [str(e) for e in events]
        else:
            await AnswerRecordDAO.create_answer_record(
                db,
                user_id=user_id,
                question_id=question.question_id,
                knowledge_id=question.knowledge_id,
                is_correct=is_correct,
                user_answer=str(user_answer).strip(),
                quality_q=quality_q,
                started_at=datetime.now(UTC),
                submitted_at=datetime.now(UTC),
                time_spent_seconds=time_spent_seconds,
            )
            state = await LearnerStateDAO.get_by_user_knowledge(
                db,
                user_id,
                question.knowledge_id,
            )

            learner_model = LearnerModel.from_db_states(
                learner_id=str(user_id),
                db_states=[state] if state else [],
            )

            updated_state = learner_model.update_mastery(
                knowledge_id=str(question.knowledge_id),
                is_correct=is_correct,
            )

            await LearnerStateDAO.upsert_state(
                db,
                user_id=user_id,
                knowledge_id=question.knowledge_id,
                mastery=updated_state.mastery,
                alpha=updated_state.alpha,
                beta=updated_state.beta,
                attempts=updated_state.attempts,
                correct_attempts=updated_state.correct_count,
                streak=updated_state.streak,
                confidence=updated_state.confidence,
                last_practiced_at=datetime.now(UTC),
            )

            await ReviewScheduleDAO.upsert_schedule(
                db,
                user_id=user_id,
                knowledge_id=question.knowledge_id,
                last_review_at=datetime.now(UTC),
                next_review_at=datetime.now(UTC),
            )
            events_payload = []

        return {
            "is_correct": is_correct,
            "correct_answer": question.answer,
            "explanation": question.explanation,
            "knowledge_id": question.knowledge_id,
            "question_id": question.question_id,
            "events_triggered": len(events_payload),
            "events": events_payload,
        }

    async def get_next_question(self, db: AsyncSession, user_id: int,
                                knowledge_id: int | None = None) -> dict | None:
        query = select(Question).outerjoin(
            AnswerRecord,
            and_(AnswerRecord.question_id == Question.question_id, AnswerRecord.user_id == user_id),
        ).where(AnswerRecord.record_id.is_(None))
        if knowledge_id is not None:
            query = query.where(Question.knowledge_id == knowledge_id)
        question = (await db.execute(query.order_by(Question.difficulty.asc(), func.random()).limit(1))).scalar_one_or_none()
        reason = "new_question"
        if not question:
            due = (await db.execute(select(ReviewSchedule).where(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.next_review_at <= datetime.now(UTC),
            ).order_by(ReviewSchedule.next_review_at.asc()).limit(1))).scalar_one_or_none()
            if due:
                question = (await db.execute(select(Question).where(Question.knowledge_id == due.knowledge_id).order_by(func.random()).limit(1))).scalar_one_or_none()
                reason = "due_review"
        if not question:
            question = (await db.execute(select(Question).order_by(func.random()).limit(1))).scalar_one_or_none()
            reason = "fallback_random"
        if not question:
            return None
        data = question_to_dict(question, include_answer=False)
        data["reason"] = reason
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
