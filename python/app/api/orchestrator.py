"""
Agent 编排器 -- 初始化所有Agent并连接到EventBus。

这是系统的"大脑"，负责：
1. 创建EventBus实例
2. 初始化5个Agent并注入EventBus
3. 提供对外接口供API层调用
"""

from datetime import UTC,datetime

from app.core.event_bus import EventBus, Event, EventType
from app.core.learner_model import LearnerModel
from app.dao.answerRecordDao import AnswerRecordDAO
from app.dao.learnerStateDao import LearnerStateDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents import (
    AssessmentAgent,
    TutorAgent,
    CurriculumAgent,
    HintAgent,
    EngagementAgent,
)


class AgentOrchestrator:
    """Agent编排器：管理所有Agent和共享状态。"""

    def __init__(self) -> None:
        self.event_bus = EventBus() #创建事件总线实例，所有Agent共享
        self.learner_models: dict[str, LearnerModel] = {}  # 学习者模型存储，供所有Agent访问和更新

        # 初始化所有Agent并注入EventBus和共享的学习者模型
        # 关键设计：所有Agent通过事件总线通信，解耦了Agent之间的直接依赖，提高系统的灵活性和可扩展性。
        # 只是创建了员工，没有给他们派活，等API调用时才触发事件，员工才开始工作
        self.assessment = AssessmentAgent(
            name="AssessmentAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.tutor = TutorAgent(
            name="TutorAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.curriculum = CurriculumAgent(
            name="CurriculumAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.hint = HintAgent(
            name="HintAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.engagement = EngagementAgent(
            name="EngagementAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )

  
    #创建答题记录 -> 获取或加载学习者模型 -> 发布学生提交事件 -> 更新学习者状态并持久化 -> 返回事件历史
    async def submit_answer(
        self,
        learner_id: str,
        knowledge_id: str,
        is_correct: bool,
        question_id: str,
        user_answer: str,
        quality_q: int,
        started_at: datetime,
        db: AsyncSession,
        time_spent_seconds: float | None = None,
    ) -> list[Event]:
        """学生提交答案 -> 触发完整的Agent处理链。"""
       
        now = datetime.now(UTC)
        record = await AnswerRecordDAO.create_answer_record(
            db=db,
            user_id=int(learner_id),
            question_id=int(question_id),
            knowledge_id=int(knowledge_id),
            is_correct=is_correct,
            user_answer=user_answer,
            quality_q=quality_q,
            started_at=started_at or now,
            time_spent_seconds=time_spent_seconds,
        )
        print("[Orchestrator] answer_record created:", record.record_id)

        await self.get_or_load_learner_model(
            learner_id=learner_id,
            db=db,
        )

        event = Event(
            type=EventType.STUDENT_SUBMISSION,
            source="api",
            learner_id=learner_id,
            data={
                "record_id": record.record_id,
                "knowledge_id": knowledge_id,
                "is_correct": is_correct,
                "question_id": question_id,
                "user_answer": user_answer,
                "db": db,
                "started_at": started_at or now,
                "submitted_at": now,
                "quality_q": quality_q,
                "time_spent_seconds": time_spent_seconds,
            },
        )

        await self.event_bus.publish(event)

        model = self.learner_models[learner_id]
        state = model.get_state(knowledge_id)
        await LearnerStateDAO.upsert_state(
            db=db,
            user_id=int(learner_id),
            knowledge_id=int(knowledge_id),

            mastery=state.mastery,
            alpha=state.alpha,
            beta=state.beta,
            confidence=state.confidence,

            attempts=state.attempts,
            correct_attempts=state.correct_count,

            streak=state.streak,
            last_practiced_at=state.last_attempt,
        )
        return self.event_bus.get_history(learner_id=learner_id, limit=20)


    async def ask_question(
        self, learner_id: str, knowledge_id: str, question: str
    ) -> list[Event]:
        """学生提问 -> 触发Assessment + Tutor处理。"""
        event = Event(
            type=EventType.STUDENT_QUESTION,
            source="api",
            learner_id=learner_id,
            data={"knowledge_id": knowledge_id, "question": question, "db": None},
        )
        await self.event_bus.publish(event)
        return self.event_bus.get_history(learner_id=learner_id, limit=20)

    async def send_message(
        self, learner_id: str, message: str, knowledge_id: str = "general"
    ) -> list[Event]:
        """学生发送消息 -> 触发Tutor对话。"""
        event = Event(
            type=EventType.STUDENT_MESSAGE,
            source="api",
            learner_id=learner_id,
            data={"message": message, "knowledge_id": knowledge_id, "db": None},
        )
        await self.event_bus.publish(event)
        return self.event_bus.get_history(learner_id=learner_id, limit=20)

    def get_learner_progress(self, learner_id: str) -> dict:
        """获取学习者进度。"""
        if learner_id not in self.learner_models:
            return {"learner_id": learner_id, "status": "no_data"}
        model = self.learner_models[learner_id]
        return {
            "learner_id": learner_id,
            "progress": model.get_overall_progress(),
            "weak_points": [
                {"id": s.knowledge_id, "mastery": s.mastery}
                for s in model.get_weak_points()
            ],
            "strong_points": [
                {"id": s.knowledge_id, "mastery": s.mastery}
                for s in model.get_strong_points()
            ],
        }

    async def get_or_load_learner_model(
        self,
        learner_id: str,
        db: AsyncSession,
    ) -> LearnerModel:
        if learner_id in self.learner_models:
            return self.learner_models[learner_id]

        states = await LearnerStateDAO.get_by_user_id(
            db=db,
            user_id=int(learner_id),
        )

        model = LearnerModel.from_db_states(
            learner_id=learner_id,
            db_states=states,
        )

        self.learner_models[learner_id] = model

        return model
