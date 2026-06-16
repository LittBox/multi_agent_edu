"""健康检查路由。"""
from __future__ import annotations

from fastapi import APIRouter, Request
from app.schemas.api_response import api_success

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check(request: Request):
    """服务健康检查，同时返回 orchestrator 是否已经挂载。"""
    orchestrator = getattr(request.app.state, "orchestrator", None)
    return api_success({"status": "ok", "service": "multi-agent-education", "agents": 5 if orchestrator else 0}, message="Service is healthy")
