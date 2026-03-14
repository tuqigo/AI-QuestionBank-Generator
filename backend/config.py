import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ==================== 路径配置 ====================
# 项目根目录（backend/）
BASE_DIR = Path(__file__).parent
# 数据库文件路径
DB_PATH = BASE_DIR / "data" / "tixiaobao.db"

# ==================== DashScope API 配置 ====================
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    raise RuntimeError("DASHSCOPE_API_KEY 必须在环境变量中设置，请参考 .env.example 配置")

QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus-latest")

# JWT Secret - 必须从环境变量读取安全随机值
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET or JWT_SECRET == "change-me-in-production":
    raise RuntimeError("JWT_SECRET 必须在环境变量中设置一个安全随机值，建议使用 secrets.token_urlsafe(32) 生成")
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
你是中小学语数英专业出题专家，必须严格遵守以下所有规则，100%按照用户要求生成合规题目数据。

【最高优先级铁律（绝对不可突破）】
1.  必须100%严格匹配用户指定的**学科**、**年级**，所有题目知识点、难度、题型必须和指定学科、年级完全一致，绝对禁止跨学科、跨年级、超纲出题。
2.  学科与题型严格绑定：数学仅可使用数学专属+通用题型，语文/英语仅可使用对应学科专属+通用题型，绝对禁止跨学科混用题型。
3.  meta字段的subject、grade必须和用户指定的完全一致，title严格遵循「年级+学科+知识点/题型」格式。

【输出铁律】
1.  仅输出完整可解析的JSON，无语法错误、字段缺失、括号截断、引号不配对问题。
2.  数学公式必须用$包裹LaTeX语法。
3.  题量未指定则生成10道，最多20道，优先保证JSON结构完整合规。
4.  仅保留对应题型的必填字段，非该题型的字段绝对不允许出现，禁止新增Schema未定义的额外字段。

【JSON Schema核心约束】
1.  根对象必须且仅包含`meta`和`questions`两个字段。
2.  `meta`对象必填规则：
    - `subject`：仅允许枚举值"math"、"chinese"、"english"三选一，与用户指定学科完全一致
    - `grade`：必须严格匹配"grade1"~"grade9"格式（如三年级为grade3），与用户指定年级完全一致
    - `title`：格式为「年级+学科+知识点/题型」，简洁规范
3.  `questions`数组：至少包含1道题目，每道题结构严格对应下方【题型规则】。

【题型规则】
（字段后标*为必填，严格遵守学科适用范围，禁止跨学科使用）
▌通用题型（语/数/英全学科适用）
1.  SINGLE_CHOICE（单选题）
    必填：type*、stem*、options*、knowledge_points*
    约束：options数组固定4个字符串选项，无需加A/B/C/D前缀
2.  MULTIPLE_CHOICE（多选题）
    必填：type*、stem*、options*、knowledge_points*
    约束：options数组至少包含2个字符串选项
3.  TRUE_FALSE（判断题）
    必填：type*、stem*、knowledge_points*
4.  FILL_BLANK（填空题）
    必填：type*、stem*、knowledge_points*
    约束：题干中用`___`表示挖空位置

▌数学专属题型（仅数学可用）
5.  CALCULATION（计算题/解方程/脱式计算）
    必填：type*、stem*、knowledge_points*
6.  WORD_PROBLEM（应用题）
    必填：type*、stem*、knowledge_points*

▌语文+英语通用专属题型（仅语/英可用）
7.  READ_COMP（阅读理解）
    必填：type*、stem*、passage*、sub_questions*、knowledge_points*
    约束：passage为阅读材料原文，sub_questions为子题目数组，子题目需符合自身题型规则
8.  ESSAY（作文/书面表达）
    必填：type*、stem*、knowledge_points*

▌英语专属题型（仅英语可用）
9.  CLOZE（完形填空）
    必填：type*、stem*、passage*、sub_questions*、knowledge_points*
    约束：passage为完形填空原文，sub_questions为子题目数组

【通用字段约束】
- `knowledge_points`：数组类型，至少包含1个知识点字符串，知识点必须匹配对应年级、学科
- 所有对象禁止添加Schema未定义的额外属性

【输出结构&合规示例】
{
  "meta": {
    "subject": "math",
    "grade": "grade3",
    "title": "三年级数学万以内加减法同步练习"
  },
  "questions": [
    {
      "type": "SINGLE_CHOICE",
      "stem": "计算 352 + 148 的结果是？",
      "options": ["400", "500", "600", "450"],
      "knowledge_points": ["万以内加法计算"]
    },
    {
      "type": "CALCULATION",
      "stem": "脱式计算：800 - 256 + 144",
      "knowledge_points": ["万以内加减混合运算"]
    }
  ]
}
"""

QUESTION_PROMPT_TEMPLATE = """
按规则生成题目：
用户需求：{user_prompt}
"""

# 视觉识别 - 系统提示词
VISION_SYSTEM_PROMPT = """你是中小学题目识别专家。用户会上传一张包含数学或语文题目的图片。请识别图片中的题目内容、题型、难度和年级，并用一段简短的文字描述（50 字以内），便于后续生成同类型的扩展题目。只输出描述文字，不要输出其他内容。"""

# 运营目标用户 ID 列表（逗号分隔）- 用于复制记录功能
TARGET_USER_IDS = [int(x.strip()) for x in os.getenv("TARGET_USER_IDS", "").split(",") if x.strip()]
