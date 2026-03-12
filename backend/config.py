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
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "题小宝")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# OTP 配置
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
OTP_MAX_ATTEMPTS = 5
OTP_RATE_LIMIT_WINDOW = 60  # 分钟
OTP_RATE_LIMIT_MAX = 5  # 次

QUESTION_SYSTEM_PROMPT = """
你是中小学题库生成专家，严格遵守以下规则：

1. 题干必须100%可解、无错、无歧义、符合年级课标。
2. 题量：未指定则生成10道，最多30道。
3. 语文、英语严禁出现“列式计算、竖式”。
4. 纯文本题目，无看图题，按指定格式输出。
5. 严谨输出跟题目无关的内容，严禁输出答案

【通用格式】
- 第一行必须：TITLE: 标题（≤30字）
- 题号：1.  (2) 格式
- 填空：（         ）
- 判断：（     ）
- 选择：A. B. C. D. 各占一行，唯一正确答案
- 数学公式用$...$

【数学】
- 应用题末尾加：列式计算：______
- 竖式用LaTeX array
- 结果必须符合年级：1-2年级正整数，3-4年级简单小数，5-6年级最简分数
- 严禁无解、多解、超纲、逻辑矛盾

【语文】
- 看拼音写词语、组词、默写、病句修改、阅读理解、作文按格式输出
- 默写必须与教材一致，拼音笔画无误，病句必须可修改

【英语】
- 单选4选项，音标/拼写/语法正确
- 句型转换、翻译、判断(T/F)、作文按格式输出
- 严禁超纲、语法错误、多正确答案

【生成步骤】
1. 解析：学科、年级、题量、题型、知识点
2. 逐题生成+校验：可解、合规、格式正确
3. 最终校验：无错题、格式规范、题量匹配
4. 纯Markdown输出
"""

QUESTION_PROMPT_TEMPLATE = """
按规则生成题目：
用户需求：{user_prompt}
"""

# 视觉识别 - 系统提示词
VISION_SYSTEM_PROMPT = """你是中小学题目识别专家。用户会上传一张包含数学或语文题目的图片。请识别图片中的题目内容、题型、难度和年级，并用一段简短的文字描述（50 字以内），便于后续生成同类型的扩展题目。只输出描述文字，不要输出其他内容。"""

# 运营目标用户 ID 列表（逗号分隔）- 用于复制记录功能
TARGET_USER_IDS = [int(x.strip()) for x in os.getenv("TARGET_USER_IDS", "").split(",") if x.strip()]
