-- ============================================
-- 添加乘法口诀练习模板（使用乘除综合生成器）
-- 题目类型：口算题 (ORAL_CALCULATION)
--
-- 说明：
-- - 原 multiplication_table 生成器已删除
-- - 本模板使用 multiplication_division_comprehensive 生成器
-- - 通过 question_complexity 配置只启用 simple_multiply 题型
-- ============================================

-- 添加乘法口诀练习模板
INSERT INTO question_templates (
    name,
    subject,
    grade,
    semester,
    textbook_version,
    question_type,
    template_pattern,
    variables_config,
    example,
    generator_module,
    sort_order,
    is_active
) VALUES (
    '乘法口诀练习',
    'math',
    'grade2',
    'upper',
    '沪教版',
    'ORAL_CALCULATION',
    '乘法口诀基础练习（支持 1-9 任意范围配置）',
    '{
        "factor": {"min": 1, "max": 9},
        "question_complexity": ["simple_multiply"],
        "rules": ["result_within_81"]
    }',
    '3 × 4 = （ ）、7 × 8 = （ ）、9 × 6 = （ ）',
    'multiplication_division_comprehensive',
    5,
    1
);

-- ============================================
-- 使用说明：
--
-- 1. 基础乘法口诀（1-9）：
--    {"factor": {"min": 1, "max": 9}, "question_complexity": ["simple_multiply"]}
--
-- 2. 乘法口诀专项（如只练 7 的乘法）：
--    {"factor": {"min": 1, "max": 9}, "fixed_first_factor": 7, "question_complexity": ["simple_multiply"]}
--
-- 3. 乘法口诀专项（如只练 5 的乘法）：
--    {"factor": {"min": 1, "max": 9}, "fixed_first_factor": 5, "question_complexity": ["simple_multiply"]}
--
-- 4. 乘法填空练习：
--    {"factor": {"min": 1, "max": 9}, "question_complexity": ["multiply_fill_first", "multiply_fill_second"]}
--
-- 5. 乘加混合练习：
--    {"factor": {"min": 1, "max": 9}, "extra": {"min": 1, "max": 20}, "question_complexity": ["multiply_add"]}
-- ============================================
