import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import questions, auth, extend, history, admin

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

# 注册结构化题目路由（独立导入以避免循环依赖）
from routers.questions_structured import router as structured_router
app.include_router(structured_router)

app.include_router(extend.router)
app.include_router(history.router)
app.include_router(admin.router)
# 注册分享路由（独立前缀，避免路由冲突）
app.include_router(history.share_router)


@app.get("/")
async def root():
    return {"message": "题小宝 API"}
