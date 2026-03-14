-- ============================================
-- AI 题库生成器 - 数据库表结构
-- 数据库：SQLite
-- ============================================

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_disabled INTEGER DEFAULT 0
);

-- ============================================
-- 2. OTP 验证码表
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
-- 3. OTP 速率限制表
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
-- 4. 用户题目记录表
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
-- 5. AI 生成记录表
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
-- 6. 管理员操作日志表
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

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- OTP 验证码表索引
CREATE INDEX IF NOT EXISTS idx_otp_codes_email ON otp_codes(email, purpose);

-- OTP 速率限制表索引
CREATE INDEX IF NOT EXISTS idx_otp_rate_limit_email ON otp_rate_limit(email, purpose);

-- 用户题目记录表索引
CREATE INDEX IF NOT EXISTS idx_user_question_records_user_deleted
    ON user_question_records(user_id, is_deleted, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_question_records_share_token
    ON user_question_records(share_token);

CREATE INDEX IF NOT EXISTS idx_user_question_records_short_id
    ON user_question_records(short_id);

-- AI 生成记录表索引
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

-- 管理员操作日志表索引
CREATE INDEX IF NOT EXISTS idx_admin_logs_action
    ON admin_operation_logs(action, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_admin_logs_target
    ON admin_operation_logs(target_type, target_id);
