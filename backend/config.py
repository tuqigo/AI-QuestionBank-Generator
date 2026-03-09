import os
from dotenv import load_dotenv

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-2e75976e9ede47a6aa4ef4aeaf69ee16")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus-latest")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# 邮件服务配置
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.163.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "好学生AI题库")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# OTP 配置
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
OTP_MAX_ATTEMPTS = 5
OTP_RATE_LIMIT_WINDOW = 60  # 分钟
OTP_RATE_LIMIT_MAX = 5  # 次
