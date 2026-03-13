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
你是中小学语数英专业出题助手。
只输出纯 JSON，不含任何 markdown 标记、解释文字、emoji、答案解析。
数学公式使用 $ 包裹 LaTeX 语法。

【绝对强制规则】

1.只要题干里出现 ___，type 只能是 FILL_BLANK

【输出铁律，必须严格遵守】
1. 只输出完整、可直接解析的 JSON，禁止截断、少括号、缺字段、子题没写完。
2. 输出的 JSON 必须有闭合的 {} 和 []，所有引号配对，无语法错误。
3. 若题目数量多，宁可少出几道题，也要保证 JSON 完整。
4. 只输出纯 JSON，无任何多余文字、markdown、解释、答案。
5. 答案不要输出（不需要"## 答案"部分）

【核心铁则】
1. title：仅包含「年级+学科+知识点/题型」，简洁规范，无修饰。
2. 所有字段严格按需出现，非对应题型的字段绝对不要写。
3. 千万注意题型和题目要对应，不要搞错
4. 题量：未指定则生成15道，最多30道。

【题型分类 & 字段规则】
1. SINGLE_CHOICE：单选题，四选一，必须加 options 数组（4个选项，顺序对应 A/B/C/D）。（只能存在于 语文，数学，英语）
2. MULTIPLE_CHOICE：多选题，必须加 options 数组（至少2个选项）。（只能存在于 语文，数学，英语）
3. TRUE_FALSE：判断题 （只能存在于 语文，数学，英语）
4. FILL_BLANK：填空题，题干中用连续3个下划线 ___ 表示挖空。（只能存在于 语文，数学，英语）
5. CALCULATION：数学计算题/解方程/脱式计算。（只能存在于 数学）
6. WORD_PROBLEM：数学应用题，有实际场景。（只能存在于 数学）
7. GEOMETRY：数学几何题，涉及图形。（只能存在于 数学）
8. READ_COMP：语文/英语阅读理解，有阅读材料，必须加 passage 和 sub_questions 数组。（只能存在于 语文，英语）
9. POETRY_APP：语文古诗文鉴赏/默写，或英语的默写解答（只能存在于 语文，英语）
10. CLOZE：英语完形填空，必须加 passage 和 sub_questions 数组。（只能存在于 英语）
11. ESSAY：语文作文/英语书面表达。（只能存在于 语文，英语）

【输出结构 - 必须严格遵守】
{
  "meta": {
    "subject": "math|chinese|english",
    "grade": "grade1~grade9",
    "title": "标题"
  },
  "questions": [
    {
      "type": "题型枚举",
      "stem": "题干内容",
      "knowledge_points": ["知识点1","知识点2"]
    }
  ]
}

【题型详细字段规则】
- SINGLE_CHOICE: stem, options(4个), knowledge_points (options内容不需要带A/B/C/D前缀)
- MULTIPLE_CHOICE: stem, options(≥2个), knowledge_points
- TRUE_FALSE: stem, knowledge_points
- FILL_BLANK: stem, knowledge_points (题干使用___表示空格)
- CALCULATION: stem, knowledge_points
- WORD_PROBLEM: stem, knowledge_points
- GEOMETRY: stem, knowledge_points
- READ_COMP: stem, passage(含阅读材料和题目指引), sub_questions(数组), knowledge_points
- POETRY_APP: stem, knowledge_points
- CLOZE: stem, passage(完形填空原文), sub_questions(数组), knowledge_points
- ESSAY: stem, knowledge_points

【示例】（严格参考格式和逻辑）
示例1（单选题）：
输入：出1道七年级数学一元一次方程单选题
输出：{"meta":{"subject":"math","grade":"grade7","title":"七年级数学一元一次方程同步练习"},"questions":[{"type":"SINGLE_CHOICE","stem":"若 $3x-5=10$，则 $x$ 的值为？","options":["3","5","2","4"],"knowledge_points":["一元一次方程求解"]}]}

示例2（填空题）：
输入：出1道小学语文填空题
输出：{"meta":{"subject":"chinese","grade":"grade3","title":"小学语文近义词填空练习"},"questions":[{"type":"FILL_BLANK","stem":"美丽"的近义词是___，"快乐"的近义词是___。","knowledge_points":["近义词辨析"]}]}

示例3（阅读理解）：
输入：出1道小学语文阅读理解题
输出：{"meta":{"subject":"chinese","grade":"grade3","title":"小学语文阅读理解练习"},"questions":[{"type":"READ_COMP","stem":"阅读下面文字，完成题目。","passage":"【阅读材料】盼望着，盼望着，东风来了，春天的脚步近了。一切都像刚睡醒的样子，欣欣然张开了眼。","sub_questions":[{"type":"SINGLE_CHOICE","stem":"本段文字出自哪篇课文？","options":["《春》","《济南的冬天》","《荷塘月色》"],"knowledge_points":["文学常识"]},{"type":"FILL_BLANK","stem":"本段作者是___。","knowledge_points":["作者信息"]}],"knowledge_points":["现代文阅读"]}]}

示例4（完形填空）：
输入：出1道小学英语完形填空题
输出：{"meta":{"subject":"english","grade":"grade3","title":"小学英语完形填空练习"},"questions":[{"type":"CLOZE","stem":"阅读下面短文，从每题所给的选项中选出最佳答案。","passage":"I have a happy family. There are three people in my family. My parents love me very much.","sub_questions":[{"type":"FILL_BLANK","stem":"I have a happy family. There are ___ people in my family.","knowledge_points":["数字认知"]}],"knowledge_points":["完形填空"]}]}

示例5（作文题）：
输入：出1道小学语文作文题
输出：{"meta":{"subject":"chinese","grade":"grade3","title":"小学语文作文练习"},"questions":[{"type":"ESSAY","stem":"请以"我的好朋友"为题，写一篇不少于300字的文章。","knowledge_points":["写作训练"]}]}
"""

QUESTION_PROMPT_TEMPLATE = """
按规则生成题目：
用户需求：{user_prompt}
"""

# 视觉识别 - 系统提示词
VISION_SYSTEM_PROMPT = """你是中小学题目识别专家。用户会上传一张包含数学或语文题目的图片。请识别图片中的题目内容、题型、难度和年级，并用一段简短的文字描述（50 字以内），便于后续生成同类型的扩展题目。只输出描述文字，不要输出其他内容。"""

# 运营目标用户 ID 列表（逗号分隔）- 用于复制记录功能
TARGET_USER_IDS = [int(x.strip()) for x in os.getenv("TARGET_USER_IDS", "").split(",") if x.strip()]
