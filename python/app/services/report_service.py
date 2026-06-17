"""学习报告服务。"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.learner_model import KnowledgeState, MasteryLevel
from app.db.models.answer_record import AnswerRecord
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.db.models.review_schedule import ReviewSchedule


def _clamp_score(value: float) -> int:
    """把画像分数限制在 0-100。"""
    return max(0, min(100, round(value)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _record_date(record: AnswerRecord) -> date | None:
        submitted_at = getattr(record, "submitted_at", None)
        if submitted_at is None:
            return None
        return submitted_at.date()

    @staticmethod
    def _schedule_date(value: datetime | None) -> date | None:
        if value is None:
            return None
        return value.date()

    @staticmethod
    def _to_knowledge_state(state: LearnerState) -> KnowledgeState:
        """把数据库 LearnerState 转成 BKT KnowledgeState，用统一 level 规则判断掌握状态。"""
        return KnowledgeState(
            knowledge_id=str(state.knowledge_id),
            mastery=_safe_float(state.mastery),
            alpha=_safe_float(getattr(state, "alpha", 1.0), 1.0),
            beta=_safe_float(getattr(state, "beta", 9.0), 9.0),
            attempts=_safe_int(state.attempts),
            correct_count=_safe_int(getattr(state, "correct_attempts", 0)),
            streak=_safe_int(getattr(state, "streak", 0)),
            last_attempt=getattr(state, "last_practiced_at", None),
        )

    @classmethod
    def _is_mastered(cls, state: LearnerState) -> bool:
        """统一使用 learner_model.py 的 MasteryLevel.MASTERED，不再单独写 0.6/0.85 常量。"""
        return cls._to_knowledge_state(state).level == MasteryLevel.MASTERED

    async def _build_learning_profile(
        self,
        user_id: int,
        records: list[AnswerRecord],
        states: list[tuple[LearnerState, KnowledgePoint]],
    ) -> dict:
        """
        构建学生画像雷达图数据。

        画像维度由后端统一定义和计算，前端只负责展示：
        1. 知识掌握：learner_state.mastery 平均值
        2. 答题准确：answer_record.is_correct 正确率
        3. 练习活跃：近 7 天答题数 / 20
        4. 学习稳定：近 7 天有答题记录的天数 / 7
        5. 复习健康：review_schedule.next_review_at 逾期/到期情况
        """
        today = datetime.now(UTC).date()
        window_days = 7
        target_answers = 20
        window_start_day = today - timedelta(days=window_days - 1)

        total_answers = len(records)
        correct_answers = sum(1 for record in records if record.is_correct)

        tracked_knowledge_points = len(states)
        avg_mastery = (
            sum(_safe_float(state.mastery) for state, _ in states)
            / tracked_knowledge_points
            if tracked_knowledge_points
            else 0.0
        )

        recent_records = [
            record
            for record in records
            if (record_day := self._record_date(record)) is not None
            and window_start_day <= record_day <= today
        ]

        recent_answers = len(recent_records)
        active_days = len(
            {
                record_day
                for record in recent_records
                if (record_day := self._record_date(record)) is not None
            }
        )

        schedules = (
            await self.db.execute(
                select(ReviewSchedule).where(ReviewSchedule.user_id == user_id)
            )
        ).scalars().all()

        due_today_reviews = 0
        overdue_reviews = 0

        for schedule in schedules:
            next_review_day = self._schedule_date(schedule.next_review_at)
            if next_review_day is None:
                continue

            if next_review_day < today:
                overdue_reviews += 1
            elif next_review_day == today:
                due_today_reviews += 1

        due_reviews = overdue_reviews + due_today_reviews

        mastery_score = _clamp_score(avg_mastery * 100)

        accuracy_score = _clamp_score(
            (correct_answers / total_answers) * 100 if total_answers else 0
        )

        activity_score = _clamp_score(
            (recent_answers / target_answers) * 100 if target_answers else 0
        )

        consistency_score = _clamp_score(
            (active_days / window_days) * 100 if window_days else 0
        )

        if not schedules:
            review_score = 0
        else:
            review_score = _clamp_score(
                100 - overdue_reviews * 20 - due_today_reviews * 10
            )

        return {
            "window_days": window_days,
            "target_answers": target_answers,
            "radar": [
                {
                    "key": "mastery",
                    "label": "知识掌握",
                    "score": mastery_score,
                    "raw": {
                        "avg_mastery": round(avg_mastery, 4),
                        "tracked_knowledge_points": tracked_knowledge_points,
                    },
                    "source": "learner_state.mastery",
                    "formula": "所有已跟踪知识点 mastery 平均值 × 100",
                },
                {
                    "key": "accuracy",
                    "label": "答题准确",
                    "score": accuracy_score,
                    "raw": {
                        "total_answers": total_answers,
                        "correct_answers": correct_answers,
                    },
                    "source": "answer_record.is_correct",
                    "formula": "正确题数 / 总答题数 × 100",
                },
                {
                    "key": "activity",
                    "label": "练习活跃",
                    "score": activity_score,
                    "raw": {
                        "recent_answers": recent_answers,
                        "target_answers": target_answers,
                        "window_days": window_days,
                    },
                    "source": "answer_record.submitted_at",
                    "formula": "近 7 天答题数 / 20 × 100，上限 100",
                },
                {
                    "key": "consistency",
                    "label": "学习稳定",
                    "score": consistency_score,
                    "raw": {
                        "active_days": active_days,
                        "window_days": window_days,
                    },
                    "source": "answer_record.submitted_at",
                    "formula": "近 7 天有答题记录的天数 / 7 × 100",
                },
                {
                    "key": "review",
                    "label": "复习健康",
                    "score": review_score,
                    "raw": {
                        "review_schedules": len(schedules),
                        "due_reviews": due_reviews,
                        "due_today_reviews": due_today_reviews,
                        "overdue_reviews": overdue_reviews,
                    },
                    "source": "review_schedule.next_review_at",
                    "formula": "100 - 逾期复习数 × 20 - 今日到期复习数 × 10",
                },
            ],
        }

    async def get_learning_report(self, user_id: int) -> dict:
        records = (
            await self.db.execute(
                select(AnswerRecord)
                .where(AnswerRecord.user_id == user_id)
                .order_by(AnswerRecord.submitted_at.desc())
            )
        ).scalars().all()

        states = (
            await self.db.execute(
                select(LearnerState, KnowledgePoint)
                .join(
                    KnowledgePoint,
                    KnowledgePoint.knowledge_id == LearnerState.knowledge_id,
                )
                .where(LearnerState.user_id == user_id)
            )
        ).all()

        total = len(records)
        correct = sum(1 for record in records if record.is_correct)

        subject_stats: dict[str, dict] = {}
        for state, knowledge_point in states:
            bucket = subject_stats.setdefault(
                knowledge_point.subject,
                {
                    "subject": knowledge_point.subject,
                    "count": 0,
                    "avg_mastery": 0.0,
                },
            )
            bucket["count"] += 1
            bucket["avg_mastery"] += _safe_float(state.mastery)

        for bucket in subject_stats.values():
            bucket["avg_mastery"] = (
                round(bucket["avg_mastery"] / bucket["count"], 2)
                if bucket["count"]
                else 0.0
            )

        today = datetime.now(UTC).date()

        today_records = [
            record
            for record in records
            if self._record_date(record) == today
        ]

        today_study_seconds = sum(
            max(0, _safe_float(getattr(record, "time_spent_seconds", 0)))
            for record in today_records
        )
        today_study_minutes = round(today_study_seconds / 60)

        daily_accuracy = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            day_records = [
                record
                for record in records
                if self._record_date(record) == day
            ]
            day_total = len(day_records)
            day_correct = sum(1 for record in day_records if record.is_correct)

            daily_accuracy.append(
                {
                    "date": day.isoformat(),
                    "total": day_total,
                    "correct": day_correct,
                    "accuracy": round(day_correct / day_total, 4)
                    if day_total
                    else 0.0,
                }
            )

        mastered_count = sum(
            1 for state, _ in states if self._is_mastered(state)
        )

        learning_count = sum(
            1
            for state, _ in states
            if _safe_int(state.attempts) > 0 and not self._is_mastered(state)
        )

        overview = {
            "total_answers": total,
            "correct_answers": correct,
            "accuracy": round(correct / total, 4) if total else 0.0,
            "mastered_count": mastered_count,
            "learning_count": learning_count,
            "knowledge_points_tracked": len(states),
            "today_study_minutes": today_study_minutes,
        }

        weak_points = sorted(
            [
                {
                    "knowledge_id": knowledge_point.knowledge_id,
                    "name": knowledge_point.name,
                    "subject": knowledge_point.subject,
                    "mastery": round(_safe_float(state.mastery), 2),
                    "mastery_percent": int(round(_safe_float(state.mastery) * 100)),
                    "attempts": _safe_int(state.attempts),
                }
                for state, knowledge_point in states
                if _safe_int(state.attempts) > 0 and not self._is_mastered(state)
            ],
            key=lambda item: item["mastery"],
        )[:5]

        recent_answers = [
            {
                "record_id": record.record_id,
                "question_id": record.question_id,
                "knowledge_id": record.knowledge_id,
                "is_correct": record.is_correct,
                "submitted_at": record.submitted_at.isoformat()
                if record.submitted_at
                else None,
            }
            for record in records[:10]
        ]

        profile = await self._build_learning_profile(
            user_id=user_id,
            records=records,
            states=states,
        )

        return {
            "overview": overview,
            "summary": overview,
            "profile": profile,
            "weak_points": weak_points,
            "subject_stats": list(subject_stats.values()),
            "daily_accuracy": daily_accuracy,
            "recent_answers": recent_answers,
        }