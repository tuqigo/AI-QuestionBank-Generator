-- ============================================
-- 迁移脚本：添加题型表
-- 日期：2026-03-16
-- 说明：创建题型表，用于存储系统支持的题型定义
-- ============================================

-- 创建 question_types 表
CREATE TABLE IF NOT EXISTS question_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_name TEXT UNIQUE NOT NULL,
    zh_name TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT 'all',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_question_types_subject
    ON question_types(subject, is_active);

CREATE INDEX IF NOT EXISTS idx_question_types_en_name
    ON question_types(en_name);

-- 初始化题型数据
-- 通用题型（语/数/英全学科适用）
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('SINGLE_CHOICE', '单选题', 'all');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('MULTIPLE_CHOICE', '多选题', 'all');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('TRUE_FALSE', '判断题', 'all');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('FILL_BLANK', '填空题', 'all');

-- 数学专属题型
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('CALCULATION', '计算题', 'math');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('WORD_PROBLEM', '应用题', 'math');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('ORAL_CALCULATION', '口算题', 'math');

-- 语文 + 英语通用专属题型
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('READ_COMP', '阅读理解', 'chinese_english');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('ESSAY', '作文', 'chinese_english');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subject) VALUES ('CLOZE', '完形填空', 'chinese_english');
