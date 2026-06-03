
from datetime import datetime

from sqlalchemy import select

from app.db.models.answer_record import AnswerRecord
from app.db.models.learner_state import LearnerState
from app.db.models.question import Question
from app.db.models.review_schedule import ReviewSchedule
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
from sqlalchemy import func

class LearningService:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    async def submit_answer(self, db, req):
        question = (
            await db.execute(
                select(Question).where(Question.question_id == req.question_id)
            )
        ).scalar_one()

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
        )

        return {
            "is_correct": is_correct,
            "correct_answer": question.answer,
            "events_triggered": len(events),
            "events": [
                {"type": e.type.value, "source": e.source, "data": e.data}
                for e in events[-10:]
            ],
        }
    
    async def get_next_question(
            self,
            db: AsyncSession,
            user_id: int,
            knowledge_id: int | None = None,
        ):
            # 1. 优先返回没做过的题
            query = (
                select(Question)
                .outerjoin(
                    AnswerRecord,
                    and_(
                        AnswerRecord.question_id == Question.question_id,
                        AnswerRecord.user_id == user_id,
                    )
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

            # 2. 如果该知识点题都做过了，找到期复习知识点
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

            # 3. 找掌握度最低的知识点
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

            # 4. 最后兜底：随机返回一道题
            question = (
                await db.execute(
                    select(Question)
                    .order_by(func.random())
                    .limit(1)
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
        # 优先找该知识点没做过的题
        question = (
            await db.execute(
                select(Question)
                .outerjoin(
                    AnswerRecord,
                    and_(
                        AnswerRecord.question_id == Question.question_id,
                        AnswerRecord.user_id == user_id,
                    )
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

        # 如果都做过了，再随机复习该知识点旧题
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
        
    async def get_review_list(self, db, learner_id: str):
        # 这里可以根据学习者模型和复习计划来推荐需要复习的题目
        # 目前简单地返回所有需要复习的题
        result = await db.execute(
            select(Question).join(ReviewSchedule).where(
                ReviewSchedule.user_id == int(learner_id),
                ReviewSchedule.next_review_at <= datetime.now()
            )
        )
        questions = result.scalars().all()
        return [
            {
                "question_id": q.question_id,
                "content": q.content,
                "knowledge_id": q.knowledge_id,
            }
            for q in questions
        ]
    
    async def get_learning_state(self, db, learner_id: str, knowledge_id: str):
        model = self.orchestrator.learner_models.get(learner_id)
        if not model:
            return None
        state = model.get_state(knowledge_id)
        if not state:
            return None
        return dict(
            mastery=state.mastery,
            confidence=state.confidence,
            attempts=state.attempts,
            correct_attempts=state.correct_count,
            streak=state.streak,
            last_practiced_at=state.last_attempt,
        )
    
    async def ask_question(self, db, learner_id: str, knowledge_id: str, question: str):
        events = await self.orchestrator.ask_question(
            learner_id=learner_id,
            knowledge_id=knowledge_id,
            question=question,
        )
        return {
            "events_triggered": len(events),
            "events": [
                {"type": e.type.value, "source": e.source, "data": e.data}
                for e in events[-10:]
            ],
        }
    
    async def get_progress(
        self,
        db,
        user_id: int,
    ):
        result = await db.execute(
            select(LearnerState)
            .where(
                LearnerState.user_id == user_id
            )
        )

        states = result.scalars().all()

        return [
            {
                "knowledge_id": s.knowledge_id,
                "mastery": s.mastery,
                "confidence": s.confidence,
                "attempts": s.attempts,
                "streak": s.streak,
            }
            for s in states
        ]
    
    async def get_due_reviews(
        self,
        db,
        user_id: int,
    ):
        result = await db.execute(
            select(ReviewSchedule)
            .where(
                ReviewSchedule.user_id == user_id
            )
            .order_by(
                ReviewSchedule.next_review_at
            )
        )

        schedules = result.scalars().all()

        return [
            {
                "knowledge_id": s.knowledge_id,
                "next_review_at": s.next_review_at,
                "interval_days": s.interval_days,
                "ef": s.ef,
            }
            for s in schedules
        ]