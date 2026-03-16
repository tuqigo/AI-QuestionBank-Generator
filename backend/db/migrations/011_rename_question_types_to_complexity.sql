-- ============================================
-- 重命名 variables_config 中的 question_types 为 question_complexity
-- 避免与 generate() 方法的 question_type 参数混淆
-- ============================================

-- 更新模板：一年级 10 以内的加减法
UPDATE question_templates
SET
    variables_config = REPLACE(variables_config, '"question_types"', '"question_complexity"')
WHERE name = '一年级 10 以内的加减法';

-- 更新模板：一年级 10 以内连加减法
UPDATE question_templates
SET
    variables_config = REPLACE(variables_config, '"question_types"', '"question_complexity"')
WHERE name = '一年级 10 以内连加减法';

-- 更新模板：连加、连减及加减综合
UPDATE question_templates
SET
    variables_config = REPLACE(variables_config, '"question_types"', '"question_complexity"')
WHERE name = '连加、连减及加减综合';
