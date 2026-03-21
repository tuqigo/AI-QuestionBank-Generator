-- Migration: Merge deprecated generators into comprehensive generators
-- Date: 2026-03-21
-- Description: Update question_templates to use comprehensive generators instead of deprecated ones
--
-- Changes:
--   1. currency_conversion → unit_conversion_comprehensive (unit_category: currency)
--   2. length_comparison → unit_conversion_comprehensive (unit_category: length)
--   3. volume_conversion → unit_conversion_comprehensive (unit_category: volume)
--   4. fraction_comparison → fraction_arithmetic_comparison
--
-- Note: This migration also deprecates the old generator files which are removed from:
--   - backend/services/template/generators/currency_conversion.py
--   - backend/services/template/generators/length_comparison.py
--   - backend/services/template/generators/volume_conversion.py
--   - backend/services/template/generators/fraction_comparison.py

-- ============================================
-- 1. Update currency_conversion templates
-- ============================================
-- Convert variables_config from old format to new unit_category format
UPDATE question_templates
SET
    generator_module = 'unit_conversion_comprehensive',
    variables_config = json_insert(
        json_insert(
            variables_config,
            '$.unit_category', 'currency'
        ),
        '$.grade_level',
        CASE
            WHEN grade = 'grade1' THEN 'grade1'
            WHEN grade = 'grade2' THEN 'grade2'
            WHEN grade = 'grade3' THEN 'grade3'
            ELSE 'grade1'
        END
    ),
    template_pattern = '单位换算：元角分之间的换算题目',
    updated_at = CURRENT_TIMESTAMP
WHERE generator_module = 'currency_conversion';

-- ============================================
-- 2. Update length_comparison templates
-- ============================================
UPDATE question_templates
SET
    generator_module = 'unit_conversion_comprehensive',
    variables_config = json_insert(
        json_insert(
            variables_config,
            '$.unit_category', 'length'
        ),
        '$.grade_level',
        CASE
            WHEN grade = 'grade1' THEN 'grade1'
            WHEN grade = 'grade2' THEN 'grade2'
            WHEN grade = 'grade3' THEN 'grade3'
            WHEN grade = 'grade4' THEN 'grade4'
            ELSE 'grade1'
        END
    ),
    template_pattern = '单位换算：长度单位之间的换算题目',
    updated_at = CURRENT_TIMESTAMP
WHERE generator_module = 'length_comparison';

-- ============================================
-- 3. Update volume_conversion templates
-- ============================================
UPDATE question_templates
SET
    generator_module = 'unit_conversion_comprehensive',
    variables_config = json_insert(
        json_insert(
            variables_config,
            '$.unit_category', 'volume'
        ),
        '$.grade_level', 'grade5'
    ),
    template_pattern = '单位换算：体积/容积单位之间的换算题目',
    updated_at = CURRENT_TIMESTAMP
WHERE generator_module = 'volume_conversion';

-- ============================================
-- 4. Update fraction_comparison templates
-- ============================================
UPDATE question_templates
SET
    generator_module = 'fraction_arithmetic_comparison',
    variables_config = json_insert(
        variables_config,
        '$.operation_types',
        CASE
            WHEN json_extract(variables_config, '$.compare_types') IS NOT NULL
            THEN json_extract(variables_config, '$.compare_types')
            ELSE json('["common_denominator", "common_numerator", "different"]')
        END
    ),
    template_pattern = '分数比大小：使用 LaTeX 分数格式生成两个分数进行比较',
    updated_at = CURRENT_TIMESTAMP
WHERE generator_module = 'fraction_comparison';

-- ============================================
-- Verification queries (for manual check after migration)
-- ============================================
-- Check that no templates still use deprecated generators:
-- SELECT COUNT(*) FROM question_templates WHERE generator_module IN (
--     'currency_conversion', 'length_comparison', 'volume_conversion', 'fraction_comparison'
-- );
-- Expected result: 0
