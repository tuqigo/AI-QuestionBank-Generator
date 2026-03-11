import os
import sys
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import questions, auth, extend, history, admin

# ========== 设置北京时间为默认时区 ==========
os.environ['TZ'] = 'Asia/Shanghai'
if sys.platform != 'win32':
    time.tzset()

app = FastAPI(title="好学生AI题库 API")

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
app.include_router(history.router)
app.include_router(admin.router)
# 注册分享路由（独立前缀，避免路由冲突）
app.include_router(history.share_router)


@app.get("/")
async def root():
    return {"message": "好学生AI题库 API"}
