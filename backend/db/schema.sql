-- ============================================
-- AI 题库生成器 - 数据库表结构
-- 数据库：SQLite
-- ============================================

-- ============================================
-- 1. 用户表 (users)
-- ============================================
-- 用途：存储系统用户账户信息
-- 功能：
--   - 用户注册、登录认证
--   - 用户状态管理（启用/禁用）
--   - 作为其他表的外键关联（user_id）
-- 字段说明：
--   - email: 用户邮箱，作为唯一登录标识
--   - hashed_password: bcrypt 加密后的密码哈希
--   - is_disabled: 禁用标记，0=正常，1=禁用
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    grade TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_disabled INTEGER DEFAULT 0
);

-- ============================================
-- 2. OTP 验证码表 (otp_codes)
-- ============================================
-- 用途：存储一次性验证码，用于用户身份验证
-- 功能：
--   - 用户注册时的邮箱验证
--   - 重置密码时的身份验证
--   - 验证码有效期管理（默认 5 分钟过期）
-- 字段说明：
--   - code: 6 位数字验证码
--   - purpose: 验证码用途（register/reset_password）
--   - attempts: 验证尝试次数，超过 5 次失效
--   - expires_at: 验证码过期时间
-- ============================================
CREATE TABLE IF NOT EXISTS otp_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    purpose TEXT NOT NULL DEFAULT 'register',
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT (datetime('now')),
    expires_at TIMESTAMP NOT NULL
);

-- ============================================
-- 3. OTP 速率限制表 (otp_rate_limit)
-- ============================================
-- 用途：防止 OTP 验证码接口被滥用
-- 功能：
--   - 限制同一邮箱/IP 的验证码发送频率
--   - 防止短信/邮件轰炸攻击
-- 字段说明：
--   - request_count: 时间窗口内的请求次数
--   - reset_at: 计数器重置时间（默认 60 分钟窗口）
--   - ip_address: 可选，用于 IP 级限流
-- ============================================
CREATE TABLE IF NOT EXISTS otp_rate_limit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    purpose TEXT NOT NULL DEFAULT 'register',
    ip_address TEXT,
    request_count INTEGER DEFAULT 1,
    reset_at TIMESTAMP NOT NULL
);

-- ============================================
-- 4. 用户题目记录表 (user_question_records)
-- ============================================
-- 用途：存储用户生成的题目历史记录
-- 功能：
--   - 保存 AI 生成的题目内容和答案
--   - 支持题目记录的查看、删除、分享
--   - 支持通过 short_id 快速访问
-- 字段说明：
--   - title: AI 生成的题目集标题
--   - prompt_type: 输入类型（text 文字题/image 图片题）
--   - prompt_content: 用户输入的提示词全文
--   - ai_response: AI 返回的题目内容（Markdown 格式）
--   - short_id: 短 ID，用于生成分享链接
--   - share_token: 分享令牌，用于公开分享
--   - is_deleted: 软删除标记，0=正常，1=已删除
-- ============================================
CREATE TABLE IF NOT EXISTS user_question_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    title           VARCHAR(200) NOT NULL,
    prompt_type     VARCHAR(10) NOT NULL,
    prompt_content  TEXT NOT NULL,
    image_path      VARCHAR(500),
    ai_response     TEXT NOT NULL,
    short_id        TEXT UNIQUE,
    share_token     VARCHAR(64) UNIQUE,
    is_deleted      INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT (datetime('now'))
);

-- ============================================
-- 5. AI 生成记录表 (ai_generation_records)
-- ============================================
-- 用途：记录 AI 调用的详细信息，用于监控和分析
-- 功能：
--   - 追踪 AI 生成请求的成功/失败状态
--   - 统计生成耗时，优化性能
--   - 记录错误信息，便于问题排查
-- 字段说明：
--   - prompt: 用户输入的原始提示词
--   - prompt_type: 提示词类型（text/image）
--   - success: 生成是否成功，1=成功，0=失败
--   - duration: API 调用耗时（秒）
--   - error_message: 失败时的错误信息
-- ============================================
CREATE TABLE IF NOT EXISTS ai_generation_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    prompt          TEXT NOT NULL,
    prompt_type     VARCHAR(20) NOT NULL,
    success         INTEGER NOT NULL,
    duration        REAL NOT NULL,
    error_message   TEXT,
    created_at      TIMESTAMP DEFAULT (datetime('now'))
);

-- ============================================
-- 6. 题目表 (questions)
-- ============================================
-- 用途：存储 AI 生成的每道题目的结构化数据
-- 功能：
--   - 支持按试卷 ID 批量获取题目
--   - 支持按题目 ID 查询单题答案
--   - 支持前端打印时预留作答区域
-- 字段说明：
--   - record_id: 关联 user_question_records.id（所属试卷）
--   - question_index: 题目在试卷中的序号（1, 2, 3...）
--   - type: 题型（SINGLE_CHOICE, CALCULATION 等）
--   - stem: 题干内容
--   - options: 选项数组（JSON 格式，仅选择题有值）
--   - passage: 阅读材料（JSON 格式，仅阅读理解/完形填空有值）
--   - sub_questions: 子题列表（JSON 格式，仅阅读理解/完形填空有值）
--   - knowledge_points: 知识点列表（JSON 数组）
--   - answer_blanks: 填空题预留空格数（后端自动计算）
--   - rows_to_answer: 预留作答行数（后端自动计算）
--   - answer_text: 标准答案（后端从 AI 响应中提取）
-- ============================================
CREATE TABLE IF NOT EXISTS questions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    short_id         TEXT UNIQUE,
    record_id        INTEGER NOT NULL,
    question_index   INTEGER NOT NULL,
    type             TEXT NOT NULL,
    stem             TEXT NOT NULL,
    options          TEXT,
    passage          TEXT,
    sub_questions    TEXT,
    knowledge_points TEXT NOT NULL,
    answer_blanks    INTEGER,
    rows_to_answer   INTEGER,
    answer_text      TEXT,
    created_at       TIMESTAMP DEFAULT (datetime('now')),
    FOREIGN KEY (record_id) REFERENCES user_question_records(id)
);

-- 题目表索引
CREATE INDEX IF NOT EXISTS idx_questions_record_id
    ON questions(record_id, question_index);

CREATE INDEX IF NOT EXISTS idx_questions_short_id
    ON questions(short_id);

-- ============================================
-- 7. 管理员操作日志表 (admin_operation_logs)
-- ============================================
-- 用途：记录管理员的所有操作行为，用于审计
-- 功能：
--   - 追踪管理员操作历史
--   - 安全审计和问题追溯
--   - 记录操作对象和详细信息
-- 字段说明：
--   - operator: 操作人标识（通常是管理员 ID 或邮箱）
--   - action: 操作类型（create/update/delete/disable 等）
--   - target_type: 操作对象类型（user/question_record 等）
--   - target_id: 操作对象 ID
--   - ip: 操作来源 IP 地址
--   - details: 操作详细信息的 JSON 描述
-- ============================================
CREATE TABLE IF NOT EXISTS admin_operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operator TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id INTEGER,
    ip TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT (datetime('now'))
);

-- ============================================
-- 8. 题目模板表 (question_templates)
-- ============================================
-- 用途：存储题目模板配置，用于快速生成题目
-- 功能：
--   - 模板化管理题目生成
--   - 支持前端下拉选择
--   - 支持后台动态配置
-- 字段说明：
--   - name: 模板名称（如"一年级 10 以内的加减法"）
--   - subject: 学科（math/chinese/english）
--   - grade: 年级（grade1~grade9）
--   - semester: 学期（upper/lower，上学期/下学期）
--   - textbook_version: 教材版本（人教版/人教版 (新)/北师大版/苏教版/西师版/沪教版/北京版/青岛六三/青岛五四）
--   - question_type: 题型（CALCULATION/FILL_BLANK 等）
--   - template_pattern: 模板模式字符串（如"{a} {op} {b} = （ ）"）
--   - variables_config: 变量配置（JSON 格式）
--   - example: 示例题目
--   - generator_module: 生成器模块名（可选，用于特殊逻辑）
--   - sort_order: 排序序号
--   - is_active: 是否启用
-- ============================================
CREATE TABLE IF NOT EXISTS question_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    grade TEXT NOT NULL,
    semester TEXT NOT NULL,
    textbook_version TEXT NOT NULL,
    question_type TEXT NOT NULL,
    template_pattern TEXT NOT NULL,
    variables_config TEXT NOT NULL,
    knowledge_point_id INTEGER,  -- 关联 knowledge_points.id，不在数据库层面加外键约束
    example TEXT,
    generator_module TEXT,  -- 可选，指定特殊生成逻辑的模块名
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加索引以优化查询
CREATE INDEX IF NOT EXISTS idx_question_templates_knowledge_point_id
    ON question_templates(knowledge_point_id, is_active);

-- ============================================
-- 9. 模板使用记录表 (template_usage_logs)
-- ============================================
-- 用途：记录模板使用情况，用于统计分析
-- 功能：
--   - 追踪模板使用频率
--   - 分析用户偏好
-- 字段说明：
--   - template_id: 关联模板 ID
--   - user_id: 用户 ID
--   - generated_params: 生成时使用的参数（JSON）
-- ============================================
CREATE TABLE IF NOT EXISTS template_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    generated_params TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES question_templates(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================================
-- 索引定义
-- ============================================

-- 用户表索引：加速邮箱查询（登录场景）
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- OTP 验证码表索引：加速邮箱 + 用途组合查询（验证场景）
CREATE INDEX IF NOT EXISTS idx_otp_codes_email ON otp_codes(email, purpose);

-- OTP 速率限制表索引：加速邮箱 + 用途组合查询（限流场景）
CREATE INDEX IF NOT EXISTS idx_otp_rate_limit_email ON otp_rate_limit(email, purpose);

-- 用户题目记录表索引：
--   - idx_user_question_records_user_deleted: 用户记录列表查询（主索引）
--   - idx_user_question_records_share_token: 分享链接访问
--   - idx_user_question_records_short_id: 短 ID 快速访问
CREATE INDEX IF NOT EXISTS idx_user_question_records_user_deleted
    ON user_question_records(user_id, is_deleted, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_question_records_share_token
    ON user_question_records(share_token);

CREATE INDEX IF NOT EXISTS idx_user_question_records_short_id
    ON user_question_records(short_id);

-- ============================================
-- 配置表 - 学科/年级/学期/教材版本
-- ============================================
-- 用途：存储系统配置常量，支持管理后台动态配置
-- 说明：这些表的数据通过迁移脚本 018 初始化
-- ============================================

-- 1. subjects - 学科表
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,      -- "math", "chinese", "english"
    name_zh TEXT NOT NULL,          -- "数学", "语文", "英语"
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subjects_code ON subjects(code, is_active);

-- 2. grades - 年级表
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,      -- "grade1" ~ "grade9"
    name_zh TEXT NOT NULL,          -- "一年级" ~ "九年级"
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_grades_code ON grades(code, is_active);

-- 3. semesters - 学期表
CREATE TABLE IF NOT EXISTS semesters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,      -- "upper", "lower"
    name_zh TEXT NOT NULL,          -- "上学期", "下学期"
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_semesters_code ON semesters(code, is_active);

-- 4. textbook_versions - 教材版本表
CREATE TABLE IF NOT EXISTS textbook_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_code TEXT NOT NULL,     -- "rjb", "bsd", "sj" 等
    name_zh TEXT NOT NULL,          -- "人教版", "北师大版" 等
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_textbook_versions_code ON textbook_versions(version_code, is_active);

-- ============================================
-- 知识点表 (knowledge_points)
-- ============================================
-- 说明：扁平结构，直接存储学科/年级/学期/教材版本代码
-- 用于模板化题目生成时关联知识点
CREATE TABLE IF NOT EXISTS knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject_code TEXT NOT NULL,
    grade_code TEXT NOT NULL,
    semester_code TEXT NOT NULL,
    textbook_version_code TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kp_filters
    ON knowledge_points(subject_code, grade_code, semester_code, textbook_version_code);

CREATE INDEX IF NOT EXISTS idx_kp_active
    ON knowledge_points(is_active, name);

-- AI 生成记录表索引：
--   - idx_ai_generation_records_user_id: 用户记录筛选
--   - idx_ai_generation_records_success: 成功/失败统计
--   - idx_ai_generation_records_prompt_type: 类型筛选
--   - idx_ai_generation_records_created_at: 时间排序
--   - idx_ai_generation_records_composite: 复合查询优化
CREATE INDEX IF NOT EXISTS idx_ai_generation_records_user_id
    ON ai_generation_records(user_id);

CREATE INDEX IF NOT EXISTS idx_ai_generation_records_success
    ON ai_generation_records(success);

CREATE INDEX IF NOT EXISTS idx_ai_generation_records_prompt_type
    ON ai_generation_records(prompt_type);

CREATE INDEX IF NOT EXISTS idx_ai_generation_records_created_at
    ON ai_generation_records(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_generation_records_composite
    ON ai_generation_records(user_id, success, prompt_type, created_at DESC);

-- 管理员操作日志表索引：
--   - idx_admin_logs_action: 按操作类型查询
--   - idx_admin_logs_target: 按操作对象查询
CREATE INDEX IF NOT EXISTS idx_admin_logs_action
    ON admin_operation_logs(action, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_admin_logs_target
    ON admin_operation_logs(target_type, target_id);

-- ============================================
-- 10. 题型表 (question_types)
-- ============================================
-- 说明：subjects 字段使用逗号分隔存储多个学科，如 "math,chinese,english"
CREATE TABLE IF NOT EXISTS question_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_name TEXT UNIQUE NOT NULL,
    zh_name TEXT NOT NULL,
    subjects TEXT NOT NULL DEFAULT 'math,chinese,english',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_question_types_en_name
    ON question_types(en_name);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_question_types_en_name
    ON question_types(en_name);

-- ============================================
-- 11：创建 schema_migrations 元数据表
-- 说明：记录已执行的迁移脚本，确保每个迁移只执行一次
-- ============================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT (datetime('now')),
    checksum TEXT,
    status TEXT DEFAULT 'success'
);

CREATE INDEX IF NOT EXISTS idx_schema_migrations_version ON schema_migrations(version);

