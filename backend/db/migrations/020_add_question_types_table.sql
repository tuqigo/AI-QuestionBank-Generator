-- ============================================
-- 迁移脚本：添加题型表
-- 日期：2026-03-16
-- 说明：创建题型表，用于存储系统支持的题型定义
-- ============================================


-- 初始化题型数据
-- 通用题型（语/数/英全学科适用）
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('SINGLE_CHOICE', '单选题', 'all');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('MULTIPLE_CHOICE', '多选题', 'all');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('TRUE_FALSE', '判断题', 'all');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('FILL_BLANK', '填空题', 'all');

-- 数学专属题型
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('CALCULATION', '计算题', 'math');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('WORD_PROBLEM', '应用题', 'math');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('ORAL_CALCULATION', '口算题', 'math');

-- 语文 + 英语通用专属题型
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('READ_COMP', '阅读理解', 'chinese_english');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('ESSAY', '作文', 'chinese_english');
INSERT OR IGNORE INTO question_types (en_name, zh_name, subjects) VALUES ('CLOZE', '完形填空', 'chinese_english');
