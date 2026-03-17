-- =====================================================
-- 迁移：教材版本字段从中文名称转换为 ID 格式
-- 版本：017
-- 日期：2026-03-17
-- =====================================================
-- 目的：
--   - 将 question_templates 表中的 textbook_version 字段从中文名称转换为 ID 格式
--   - 便于未来修改版本名称而不影响数据库数据
--
-- 转换规则：
--   "人教版" -> "rjb"
--   "人教版（2024 新版）" -> "rjb_2024"
--   "人教版 (新)" -> "rjb_xin"
--   "北师大版" -> "bsd"
--   "苏教版" -> "sj"
--   "西师版" -> "xs"
--   "沪教版" -> "hj"
--   "北京版" -> "bj"
--   "青岛六三" -> "qd_ll"
--   "青岛五四" -> "qd_sw"
-- =====================================================

-- 开始事务
BEGIN TRANSACTION;

-- 创建临时映射表
CREATE TEMPORARY TABLE textbook_version_mapping (
    old_name TEXT PRIMARY KEY,
    new_id TEXT NOT NULL
);

-- 插入映射关系
INSERT INTO textbook_version_mapping (old_name, new_id) VALUES
    ('人教版', 'rjb'),
    ('人教版（2024 新版）', 'rjb_2024'),
    ('人教版 (新)', 'rjb_xin'),
    ('北师大版', 'bsd'),
    ('苏教版', 'sj'),
    ('西师版', 'xs'),
    ('沪教版', 'hj'),
    ('北京版', 'bj'),
    ('青岛六三', 'qd_ll'),
    ('青岛五四', 'qd_sw');

-- 执行更新：将中文名称转换为 ID
UPDATE question_templates
SET textbook_version = (
    SELECT new_id
    FROM textbook_version_mapping
    WHERE old_name = question_templates.textbook_version
)
WHERE textbook_version IN (SELECT old_name FROM textbook_version_mapping);

-- 删除临时表
DROP TABLE textbook_version_mapping;

-- 提交事务
COMMIT;
