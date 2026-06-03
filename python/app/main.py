"""
FastAPI 应用入口。

启动方式：
    cd python/
    python -m app.main
    或
    uvicorn app.main:app --reload --port 8000
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.websocket import ws_router
from app.api.orchestrator import AgentOrchestrator

from app.routers.auth import router as auth_router
from app.routers.education import router as education_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stdout,
)

orchestrator: AgentOrchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    orchestrator = AgentOrchestrator()
    app.state.orchestrator = orchestrator
    logging.getLogger(__name__).info("Agent orchestrator started with 5 agents")
    yield
    logging.getLogger(__name__).info("Shutting down")


app = FastAPI(
    title="多Agent智能教育系统",
    description=(
        "5-Agent Mesh+事件驱动架构的个性化学习系统。\n\n"
        "**Agent列表：**\n"
        "- Assessment Agent：知识点评估\n"
        "- Tutor Agent：苏格拉底式教学\n"
        "- Curriculum Agent：学习路径规划\n"
        "- Hint Agent：分级提示\n"
        "- Engagement Agent：互动监测"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api")
app.include_router(education_router, prefix="/api")
app.include_router(ws_router)

# 自定义异常处理器，专门捕获 FastAPI 的参数校验错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = err["loc"]
        field_name = loc[-1] if loc else None
        original_msg = err["msg"]

        if field_name == "username":
            # 根据原始错误消息细分用户名错误
            if "ensure this value has at least 3 characters" in original_msg:
                message = "用户名长度不能少于3个字符"
            elif "ensure this value has at most 20 characters" in original_msg:
                message = "用户名长度不能超过20个字符"
            else:
                message = "用户名格式错误"   # 兜底消息
        elif field_name == "pwd":
            # 密码错误细分（如上一轮所述）
            if "ensure this value has at least 6 characters" in original_msg:
                message = "密码长度不能少于6位"
            elif "ensure this value has at most 50 characters" in original_msg:
                message = "密码长度不能超过50位"
            elif "Password must contain at least one digit" in original_msg:
                message = "密码必须包含至少一个数字"
            elif "Password must contain at least one letter" in original_msg:
                message = "密码必须包含至少一个字母"
            else:
                message = "密码格式不正确"
        else:
            message = original_msg   # 其他字段保持原始错误信息

        field_path = " -> ".join(str(l) for l in loc)
        errors.append({"field": field_path, "message": message})

    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "请求参数校验失败，请检查输入数据。",
            "errors": errors,
        },
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
