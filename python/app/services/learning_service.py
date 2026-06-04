from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import EventType
from app.db.models.answer_record import AnswerRecord
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.db.models.question import Question
from app.db.models.review_schedule import ReviewSchedule
from app.schemas.learning import HintRequest, TutorAskRequest, TutorMessageRequest
from app.services.dashboard_service import DashboardService
from app.utils.event_serializer import extract_teaching_reply, serialize_events

MASTERY_MASTERED = 0.6


class LearningService:
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator

    async def submit_answer(self, db, req):
        if not self.orchestrator:
            raise RuntimeError("Orchestrator is required for submit_answer")

        question = (
            await db.execute(
                select(Question).where(Question.question_id == req.question_id)
            )
        ).scalar_one_or_none()

        if not question:
            raise ValueError("Question not found")

        is_correct = req.user_answer.strip() == question.answer.strip()

        events = await self.orchestrator.submit_answer(
            learner_id=str(req.user_id),
            knowledge_id=str(question.knowledge_id),
            is_correct=is_correct,
            question_id=str(question.question_id),
            user_answer=req.user_answer.strip(),
            quality_q=req.quality_q,
            started_at=datetime.now(),
            db=db,
            time_spent_seconds=req.time_spent_seconds,
        )

        reply = extract_teaching_reply(events)

        return {
            "is_correct": is_correct,
            "correct_answer": question.answer,
            "explanation": question.explanation,
            "knowledge_id": question.knowledge_id,
            "events_triggered": len(events),
            "events": serialize_events(events),
            "agent_reply": reply,
        }

    async def get_next_question(
        self,
        db: AsyncSession,
        user_id: int,
        knowledge_id: int | None = None,
    ):
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
        )

        if knowledge_id is not None:
            query = query.where(Question.knowledge_id == knowledge_id)

        question = (
            await db.execute(
                query.order_by(Question.difficulty.asc(), func.random()).limit(1)
            )
        ).scalar_one_or_none()

        if question:
            return self._format_question(question, reason="new_question")

        due_schedule = (
            await db.execute(
                select(ReviewSchedule)
                .where(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.next_review_at <= datetime.now(),
                )
                .order_by(ReviewSchedule.next_review_at.asc())
                .limit(1)
            )
        ).scalar_one_or_none()

        if due_schedule:
            question = await self._get_question_by_knowledge(
                db,
                user_id=user_id,
                knowledge_id=due_schedule.knowledge_id,
            )
            if question:
                return self._format_question(question, reason="due_review")

        weak_state = (
            await db.execute(
                select(LearnerState)
                .where(LearnerState.user_id == user_id)
                .order_by(LearnerState.mastery.asc())
                .limit(1)
            )
        ).scalar_one_or_none()

        if weak_state:
            question = await self._get_question_by_knowledge(
                db,
                user_id=user_id,
                knowledge_id=weak_state.knowledge_id,
            )
            if question:
                return self._format_question(question, reason="weak_knowledge")

        question = (
            await db.execute(
                select(Question).order_by(func.random()).limit(1)
            )
        ).scalar_one_or_none()

        if question:
            return self._format_question(question, reason="fallback_random")

        return None

    async def _get_question_by_knowledge(
        self,
        db: AsyncSession,
        user_id: int,
        knowledge_id: int,
    ):
        question = (
            await db.execute(
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
        ).scalar_one_or_none()

        if question:
            return question

        return (
            await db.execute(
                select(Question)
                .where(Question.knowledge_id == knowledge_id)
                .order_by(func.random())
                .limit(1)
            )
        ).scalar_one_or_none()

    def _format_question(self, question: Question, reason: str):
        return {
            "question_id": question.question_id,
            "knowledge_id": question.knowledge_id,
            "question_type": question.question_type,
            "stem": question.stem,
            "option_a": question.option_a,
            "option_b": question.option_b,
            "option_c": question.option_c,
            "option_d": question.option_d,
            "difficulty": question.difficulty,
            "image_url": question.image_url,
            "reason": reason,
        }

    async def get_progress(self, db, user_id: int):
        result = await db.execute(
            select(LearnerState, KnowledgePoint)
            .join(
                KnowledgePoint,
                KnowledgePoint.knowledge_id == LearnerState.knowledge_id,
            )
            .where(LearnerState.user_id == user_id)
            .order_by(LearnerState.mastery.desc())
        )

        rows = result.all()
        return [
            {
                "knowledge_id": state.knowledge_id,
                "name": kp.name,
                "subject": kp.subject,
                "mastery": round(state.mastery, 2),
                "mastery_percent": int(round(state.mastery * 100)),
                "confidence": round(state.confidence, 2),
                "attempts": state.attempts,
                "correct_attempts": state.correct_attempts,
                "streak": state.streak,
                "status": "mastered"
                if state.mastery >= MASTERY_MASTERED
                else "learning",
                "last_practiced_at": state.last_practiced_at.isoformat()
                if state.last_practiced_at
                else None,
            }
            for state, kp in rows
        ]

    async def get_due_reviews(
        self,
        db,
        user_id: int,
        due_only: bool = True,
    ):
        query = select(ReviewSchedule, KnowledgePoint).join(
            KnowledgePoint,
            KnowledgePoint.knowledge_id == ReviewSchedule.knowledge_id,
        ).where(ReviewSchedule.user_id == user_id)

        if due_only:
            query = query.where(ReviewSchedule.next_review_at <= datetime.now())

        result = await db.execute(
            query.order_by(ReviewSchedule.next_review_at.asc())
        )

        return [
            {
                "knowledge_id": schedule.knowledge_id,
                "name": kp.name,
                "subject": kp.subject,
                "next_review_at": schedule.next_review_at.isoformat(),
                "last_review_at": schedule.last_review_at.isoformat()
                if schedule.last_review_at
                else None,
                "interval_days": schedule.interval_days,
                "repetition": schedule.repetition,
                "ef": schedule.ef,
                "is_due": schedule.next_review_at <= datetime.now(),
            }
            for schedule, kp in result.all()
        ]

    async def get_answer_history(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ):
        total = (
            await db.execute(
                select(func.count(AnswerRecord.record_id)).where(
                    AnswerRecord.user_id == user_id
                )
            )
        ).scalar_one()

        rows = (
            await db.execute(
                select(AnswerRecord, Question, KnowledgePoint)
                .join(Question, Question.question_id == AnswerRecord.question_id)
                .join(
                    KnowledgePoint,
                    KnowledgePoint.knowledge_id == AnswerRecord.knowledge_id,
                )
                .where(AnswerRecord.user_id == user_id)
                .order_by(AnswerRecord.submitted_at.desc())
                .limit(limit)
                .offset(offset)
            )
        ).all()

        return {
            "total": total,
            "items": [
                {
                    "record_id": record.record_id,
                    "question_id": record.question_id,
                    "knowledge_id": record.knowledge_id,
                    "knowledge_name": kp.name,
                    "stem": question.stem[:120],
                    "user_answer": record.user_answer,
                    "is_correct": record.is_correct,
                    "submitted_at": record.submitted_at.isoformat(),
                    "time_spent_seconds": record.time_spent_seconds,
                }
                for record, question, kp in rows
            ],
        }

    async def get_knowledge_graph(self, db: AsyncSession, user_id: int):
        dashboard = DashboardService(db)
        path = await dashboard.get_learning_path(user_id)

        points = (
            await db.execute(
                select(KnowledgePoint).order_by(KnowledgePoint.knowledge_id.asc())
            )
        ).scalars().all()

        nodes = [
            {
                "knowledge_id": kp.knowledge_id,
                "name": kp.name,
                "subject": kp.subject,
                "parent_id": kp.parent_id,
                "difficulty": kp.difficulty,
            }
            for kp in points
        ]

        return {
            "nodes": nodes,
            "learning_path": path,
        }

    async def tutor_ask(self, db: AsyncSession, req: TutorAskRequest):
        if not self.orchestrator:
            raise RuntimeError("Orchestrator is required")

        await self.orchestrator.get_or_load_learner_model(
            str(req.user_id),
            db,
        )
        events = await self.orchestrator.ask_question(
            learner_id=str(req.user_id),
            knowledge_id=str(req.knowledge_id),
            question=req.question,
        )
        return {
            "reply": extract_teaching_reply(events),
            "events_triggered": len(events),
            "events": serialize_events(events),
        }

    async def tutor_message(self, db: AsyncSession, req: TutorMessageRequest):
        if not self.orchestrator:
            raise RuntimeError("Orchestrator is required")

        knowledge_id = str(req.knowledge_id or "general")
        await self.orchestrator.get_or_load_learner_model(str(req.user_id), db)
        events = await self.orchestrator.send_message(
            learner_id=str(req.user_id),
            message=req.message,
            knowledge_id=knowledge_id,
        )
        return {
            "reply": extract_teaching_reply(events),
            "events_triggered": len(events),
            "events": serialize_events(events),
        }

    async def request_hint(self, db: AsyncSession, req: HintRequest):
        if not self.orchestrator:
            raise RuntimeError("Orchestrator is required")

        learner_id = str(req.user_id)
        knowledge_id = str(req.knowledge_id)
        await self.orchestrator.get_or_load_learner_model(learner_id, db)
        model = self.orchestrator.learner_models[learner_id]
        state = model.get_state(knowledge_id)

        from app.core.event_bus import Event

        event = Event(
            type=EventType.HINT_NEEDED,
            source="api",
            learner_id=learner_id,
            data={
                "knowledge_id": knowledge_id,
                "mastery": state.mastery,
                "attempts": max(state.attempts, 1),
                "level": state.level.value,
                "question_id": req.question_id,
                "db": db,
            },
        )
        await self.orchestrator.event_bus.publish(event)

        events = self.orchestrator.event_bus.get_history(
            learner_id=learner_id,
            limit=20,
        )
        return {
            "hint": extract_teaching_reply(events),
            "events_triggered": len(events),
            "events": serialize_events(events),
        }

    async def get_orchestrator_progress(self, user_id: int):
        if not self.orchestrator:
            return {"status": "no_orchestrator"}
        return self.orchestrator.get_learner_progress(str(user_id))
