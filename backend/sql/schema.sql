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
-- 6. 管理员操作日志表 (admin_operation_logs)
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
