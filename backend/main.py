import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import questions, auth, extend

app = FastAPI(title="好学生 AI 题库生成器 API")

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
app.include_router(extend.router)


@app.get("/")
async def root():
    return {"message": "好学生 AI 题库生成器 API"}
