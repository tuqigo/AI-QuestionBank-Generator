-- ============================================
-- 迁移 019: 合并 compare_number 生成器到 mixed_addition_subtraction
-- ============================================
-- 用途：将使用 compare_number 生成器的模板改为使用 mixed_addition_subtraction
-- 说明：CompareNumberGenerator 已删除，其功能已合并到 MixedAdditionSubtractionGenerator
-- ============================================

-- 更新模板 1：一年级 10 以内的数比一比
UPDATE question_templates
SET generator_module = 'mixed_addition_subtraction',
    variables_config = json_insert(
        variables_config,
        '$.question_complexity', '["compare_simple"]'
    )
WHERE generator_module = 'compare_number'
  AND json_extract(variables_config, '$.question_complexity') IS NULL;

-- 更新模板：百以内数的大小比较
UPDATE question_templates
SET generator_module = 'mixed_addition_subtraction',
    variables_config = json_insert(
        variables_config,
        '$.question_complexity', '["compare_simple"]'
    )
WHERE generator_module = 'compare_number';

-- 记录迁移
INSERT INTO schema_migrations (version, filename, status)
VALUES ('019', '019_merge_compare_number_generator.sql', 'success');
