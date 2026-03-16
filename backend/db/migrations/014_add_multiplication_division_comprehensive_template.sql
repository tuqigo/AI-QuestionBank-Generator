-- ============================================
-- 添加乘除综合模板（二年级 数学 下学期 沪教版）
-- 题目类型：口算题 (ORAL_CALCULATION)
--
-- 设计原则：
-- - 生成器本身不限制年级，所有范围通过 configuration 控制
-- - 题型复杂度通过 question_complexity 配置动态选择
-- - 规则约束通过 rules 配置动态启用
-- - 后期添加新模板只需 SQL，无需改代码
-- ============================================

-- 添加乘除综合模板（通用型，支持所有乘除题型）
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
    '乘除综合',
    'math',
    'grade2',
    'lower',
    '沪教版',
    'ORAL_CALCULATION',
    '表内乘除法综合练习（含乘加/乘减/除加/除减/带余数除法）',
    '{
        "factor": {"min": 1, "max": 9},
        "divisor": {"min": 1, "max": 9},
        "dividend": {"min": 1, "max": 81},
        "extra": {"min": 1, "max": 20},
        "question_complexity": [
            "simple_multiply",
            "simple_divide",
            "multiply_fill_first",
            "multiply_fill_second",
            "divide_fill_dividend",
            "divide_fill_divisor",
            "multiply_add",
            "multiply_subtract",
            "divide_add",
            "divide_subtract",
            "remainder_division",
            "compare_multiply",
            "compare_division"
        ],
        "rules": ["ensure_divisible", "ensure_positive", "result_within_100"]
    }',
    '3 × 4 = （ ）、12 ÷ 3 = （ ）、（ ）× 4 = 12、12 ÷ （ ）= 4、3 × 4 + 5 = （ ）、12 ÷ 3 - 2 = （ ）、14 ÷ 3 = （ ）',
    'multiplication_division_comprehensive',
    14,
    1
);

-- ============================================
-- 扩展示例（未来添加新模板时参考）：
-- 只需执行 SQL，无需修改生成器代码
-- ============================================

-- 示例 1：乘法口诀专项 - 只练 7 的乘法
-- INSERT INTO question_templates (...) VALUES (
--     '乘法口诀专项 - 7 的乘法',
--     'math', 'grade2', 'upper', '沪教版', 'ORAL_CALCULATION',
--     '7 的乘法口诀专项练习',
--     '{"factor": {"min": 1, "max": 9}, "fixed_first_factor": 7, "question_complexity": ["simple_multiply"], "rules": ["result_within_81"]}',
--     '7 × 1 = （ ）',
--     'multiplication_division_comprehensive', 20, 1
-- );

-- 示例 2：除法专项 - 除数只练 3
-- INSERT INTO question_templates (...) VALUES (
--     '除法专项 - 除数是 3',
--     'math', 'grade2', 'upper', '沪教版', 'ORAL_CALCULATION',
--     '除数是 3 的整除练习',
--     '{"divisor": {"min": 3, "max": 3}, "quotient": {"min": 1, "max": 9}, "question_complexity": ["simple_divide"], "rules": ["ensure_divisible"]}',
--     '12 ÷ 3 = （ ）',
--     'multiplication_division_comprehensive', 21, 1
-- );

-- 示例 3：乘加混合专项
-- INSERT INTO question_templates (...) VALUES (
--     '乘加混合专项',
--     'math', 'grade3', 'upper', '人教版', 'ORAL_CALCULATION',
--     '乘加混合运算练习',
--     '{"factor": {"min": 1, "max": 9}, "extra": {"min": 1, "max": 50}, "question_complexity": ["multiply_add"], "rules": ["result_within_100"]}',
--     '3 × 4 + 5 = （ ）',
--     'multiplication_division_comprehensive', 30, 1
-- );
