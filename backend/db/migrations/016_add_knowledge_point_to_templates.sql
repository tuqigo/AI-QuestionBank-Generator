-- =====================================================
-- 迁移：添加知识点分组字段到题目模板表
-- 版本：016
-- 日期：2026-03-17
-- =====================================================
-- 目的：
--   - 为 question_templates 表添加 knowledge_point 字段
--   - 支持模板按知识点分组管理
--   - 前端可按知识点分组展示模板
--
-- knowledge_point 字段存储 JSON 格式字符串（可选）：
-- 例如：{"subject":"math","grade":"grade1","semester":"upper","textbook":"人教版","knowledge_point":["5 以内数的认识"]}
-- 或者简单存储知识点名称字符串："5 以内数的认识和加、减法"
-- =====================================================

-- 添加 knowledge_point 字段（TEXT 类型，存储 JSON 或纯文本）
ALTER TABLE question_templates ADD COLUMN knowledge_point TEXT;

-- 添加索引以优化查询
CREATE INDEX IF NOT EXISTS idx_question_templates_knowledge_point
    ON question_templates(knowledge_point, is_active);

-- 记录迁移
INSERT INTO schema_migrations (version, filename)
VALUES ('016', '016_add_knowledge_point_to_templates.sql');
