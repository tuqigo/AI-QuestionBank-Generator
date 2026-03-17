import os
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from utils.logger import api_logger

# 注意：数据库迁移不再自动执行
# 启动前请手动执行：python -m db.migrations_cli migrate
# 或者在 CI/CD 部署流程中执行迁移

from api.v1 import questions, auth, extend, history, admin, users, templates, configs

app = FastAPI(title="题小宝 API")

# 从环境变量读取允许的来源，支持 Cloudflare Pages 部署
allow_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(users.router)

# 注册结构化题目路由（独立导入以避免循环依赖）
from api.v1.questions_structured import router as structured_router
app.include_router(structured_router)

app.include_router(extend.router)
app.include_router(history.router)
app.include_router(admin.router)
app.include_router(templates.router)
app.include_router(configs.router, prefix="/api/configs", tags=["configs"])
# 注册分享路由（独立前缀，避免路由冲突）
app.include_router(history.share_router)


# ==================== 全局异常处理器 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器 - 捕获所有未处理的异常"""
    api_logger.error(f"全局异常：{exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误，请联系管理员"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    api_logger.warning(f"HTTP 异常：{exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    api_logger.warning(f"请求验证失败：{exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "请求参数验证失败", "errors": exc.errors()}
    )


# ==================== 健康检查接口 ====================

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    return {"message": "题小宝 API"}
