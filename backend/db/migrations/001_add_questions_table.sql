-- ============================================
-- 迁移脚本：添加 questions 表
-- 日期：2026-03-14
-- 说明：创建题目表，用于存储 AI 生成的结构化题目数据
-- ============================================

-- 创建 questions 表
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

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_questions_record_id
    ON questions(record_id, question_index);

CREATE INDEX IF NOT EXISTS idx_questions_short_id
    ON questions(short_id);
