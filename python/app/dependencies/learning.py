from app.core.agent_runtime import agent_orchestrator
from app.services.learning_service import LearningService



# 依赖注入函数，供 FastAPI 注入 LearningService 实例
def get_learning_service() -> LearningService:
    return LearningService(orchestrator=agent_orchestrator)