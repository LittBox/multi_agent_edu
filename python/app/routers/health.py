from fastapi import APIRouter, Request

from app.schemas.api_response import api_success

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check(request: Request):
    orchestrator = getattr(request.app.state, "orchestrator", None)
    return api_success(
        {
            "status": "ok",
            "service": "multi-agent-education",
            "agents": 5 if orchestrator else 0,
        },
        message="Service is healthy",
    )
