-- =====================================================
-- 迁移：将 question_templates.example 字段改为 JSON 数组存储
-- 版本：022
-- 日期：2026-03-19
-- =====================================================
-- 目的：
--   - 将 question_templates.example(TEXT) 改为存储 JSON 数组
--   - 支持多个示例题目，便于前端展示
--   - 支持 LaTeX 数学公式存储
--   - 兼容现有数据（将、分割的字符串转为数组）
--
-- 数据格式转换示例：
--   - '示例 1、示例 2' -> '["示例 1","示例 2"]'
--   - '单个示例' -> '["单个示例"]'
--   - NULL -> NULL (保持不变)
-- =====================================================

-- 处理包含"、"的数据（分割为数组）
-- 例如：'A、B、C' -> '["A","B","C"]'
UPDATE question_templates
SET example = '["' ||
    REPLACE(example, ',', '","') ||
    '"]'
WHERE example IS NOT NULL AND example LIKE '%、%';

-- 处理单个示例数据（包装为单元素数组）
-- 例如：'A' -> '["A"]'
UPDATE question_templates
SET example = '["' || example || '"]'
WHERE example IS NOT NULL AND example NOT LIKE '%、%' AND example NOT LIKE '["%';
