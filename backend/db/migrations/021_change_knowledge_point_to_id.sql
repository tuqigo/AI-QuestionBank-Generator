-- =====================================================
-- 迁移：将 knowledge_point 字段改为 knowledge_point_id
-- 版本：018
-- 日期：2026-03-19
-- =====================================================
-- 目的：
--   - 将 question_templates.knowledge_point(TEXT) 改为 knowledge_point_id(INTEGER)
--   - 引用 knowledge_points 表的 ID
--   - 不在数据库层面添加外键约束，由业务逻辑保证一致性
--   - 保留 subject/grade/semester/textbook_version 冗余字段用于快速筛选
-- =====================================================

-- 4. 添加新索引优化查询
CREATE INDEX IF NOT EXISTS idx_question_templates_knowledge_point_id
    ON question_templates(knowledge_point_id, is_active);
