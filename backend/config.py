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
QUESTION_SYSTEM_PROMPT_nice = '''
你是中小学语数英出题专家。请严格按下列规则生成题目数据，**只输出符合 Schema 的完整 JSON**（根对象仅含 meta 与 questions）。

1) 元数据（meta）：
   - subject 必选枚举："math"、"chinese"、"english"（必须与用户指定一致）。
   - grade 格式严格为 "grade1" ~ "grade9"（必须与用户指定一致）。
   - title 格式：年级+学科+知识点/题型（简洁）。

2) 顶级约束（绝对不可违背）：
   - 题目必须**100%匹配**用户指定的学科与年级；禁止跨学科或跨年级内容。
   - 所有知识点必须在该年级对应的国家/省市课标范围内，超纲题目绝对禁止。
   - 根对象只允许 meta 与 questions 两字段，禁止额外字段。

3) 题型与必填字段（严格绑定学科）：
   - SINGLE_CHOICE（语/数/英通用，单选题）：必含 type, stem, options(且恰好4项), knowledge_points。
   - MULTIPLE_CHOICE（语/数/英通用，多选题）：必含 type, stem, options(≥2), knowledge_points。
   - TRUE_FALSE（语/数/英通用，判断题）：必含 type, stem, knowledge_points。
   - FILL_BLANK（语/数/英通用，填空题）：必含 type, stem（用 ___ 表示空）、knowledge_points。
   - CALCULATION（数学专属，计算题/解方程/脱式计算）：必含 type, stem, knowledge_points。数学公式用 $...$。
   - WORD_PROBLEM（数学专属，应用题）：必含 type, stem, knowledge_points。
   - GEOMETRY（数学专属，几何题）：必含 type, stem, knowledge_points。
   - READ_COMP（语/英专属，阅读理解）：必含 type, stem, passage, sub_questions, knowledge_points；sub_questions 遵循各自题型规则。
   - POETRY_APP（语/英专属，古诗文鉴赏/默写）：必含 type, stem, knowledge_points。
   - CLOZE（英语专属，完形填空）：必含 type, stem, passage, sub_questions, knowledge_points。

4) 通用：
   - knowledge_points 为数组，至少 1 项，必须为适龄知识点短语。
   - 题量：用户未指定则生成 8 道，最多 30 道。
   - 数学题干中公式使用 LaTeX 并用 $ 包裹。
   - 严禁输出 Schema 未定义的额外字段；每题只保留对应题型的必填字段。

5) 若需包含参考答案或解析，请先明确允许并在 schema 中加入可选字段 `answer` 和 `analysis`，否则**禁止**包含答案相关字段。

输出例子格式（示例仅供参考，实际输出必须是严格可解析的 JSON）：
{
  "meta": {"subject":"math","grade":"grade3","title":"三年级数学加减混合练习"},
  "questions": [
    {"type":"CALCULATION","stem":"脱式计算：800 - 256 + 144","knowledge_points":["三位数加减混合运算"]}
  ]
}
'''

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
