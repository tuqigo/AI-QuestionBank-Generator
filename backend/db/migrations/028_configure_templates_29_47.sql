-- =====================================================
-- 迁移：配置 ID 29-47 题目模板
-- 版本：028
-- 日期：2026-03-26
-- =====================================================
-- 目的：
--   - 配置 ID 29-47 的 question_templates 记录
--   - 填充 template_pattern、variables_config、generator_module 字段
--   - 使模板能够正常生成题目
-- =====================================================

-- 说明：
--   线下开发环境已执行配置脚本（scripts/configure_templates_29_47.py）
--   此迁移文件用于线上环境
-- =====================================================

-- ID=29: 连减（6~10 的认识）
UPDATE question_templates
SET template_pattern = '{a}-{b}-{c}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 10}, "op": {"values": ["-"]}, "question_complexity": ["consecutive_subtract"], "rules": ["ensure_positive", "result_within_10"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 29;

-- ID=30: 加减混合（6~10 的认识）
UPDATE question_templates
SET template_pattern = '{a}+{b}-{c}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 10}, "op": {"values": ["+", "-"]}, "op1": {"values": ["+", "-"]}, "op2": {"values": ["+", "-"]}, "question_complexity": ["mixed_operation"], "rules": ["ensure_positive", "result_within_10"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 30;

-- ID=31: 整理和复习（6~10 的认识，综合题型）
UPDATE question_templates
SET template_pattern = 'mixed',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 10}, "op": {"values": ["+", "-"]}, "question_complexity": ["simple", "missing_operand", "compare_with_result", "mixed_operation"], "rules": ["ensure_positive", "result_within_10"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 31;

-- ID=32: 11~20 的认识（填空题型）
UPDATE question_templates
SET template_pattern = '[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 10, "max": 20}, "question_complexity": ["simple_fill"], "rules": ["ensure_positive"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 32;

-- ID=33: 11~20 的大小比较
UPDATE question_templates
SET template_pattern = '{a}[BLANK]{b}',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 11, "max": 20}, "question_complexity": ["compare_simple"], "rules": ["ensure_different"], "q_type": {"compare_simple": "circle"}, "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "circle", "show_question_number": true}}',
    is_active = 1
WHERE id = 33;

-- ID=34: 十加几与相应的减法
UPDATE question_templates
SET template_pattern = '10+{a}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 9}, "op": {"values": ["+", "-"]}, "question_complexity": ["simple"], "rules": ["ensure_positive"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 34;

-- ID=35: 十几加几与相应的减法
UPDATE question_templates
SET template_pattern = '{a}+{b}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 11, "max": 19}, "op": {"values": ["+", "-"]}, "question_complexity": ["simple"], "rules": ["ensure_positive"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 35;

-- ID=36: 连加、连减、加减混合（11~20）
UPDATE question_templates
SET template_pattern = '{a}+{b}+{c}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 20}, "op": {"values": ["+", "-"]}, "op1": {"values": ["+", "-"]}, "op2": {"values": ["+", "-"]}, "question_complexity": ["consecutive_add", "consecutive_subtract", "mixed_operation"], "rules": ["ensure_positive"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 36;

-- ID=37: 比大小（11~20，带运算）
UPDATE question_templates
SET template_pattern = '{a}+{b}[BLANK]{c}',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 10, "max": 20}, "op": {"values": ["+", "-"]}, "question_complexity": ["compare_with_result"], "rules": ["ensure_positive"], "q_type": {"compare_with_result": "circle"}, "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "circle", "show_question_number": true}}',
    is_active = 1
WHERE id = 37;

-- ID=38: 整理和复习（11~20 综合）
UPDATE question_templates
SET template_pattern = 'mixed',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 10, "max": 20}, "op": {"values": ["+", "-"]}, "op1": {"values": ["+", "-"]}, "op2": {"values": ["+", "-"]}, "question_complexity": ["simple", "missing_operand", "compare_simple", "compare_with_result", "consecutive_add"], "rules": ["ensure_positive"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 38;

-- ID=39: 9 加几（进位加法）
UPDATE question_templates
SET template_pattern = '9+{a}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 2, "max": 9}, "op": {"values": ["+"]}, "question_complexity": ["simple"], "rules": ["ensure_positive"], "fixed_addend": [9], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 39;

-- ID=40: 8、7、6 加几（进位加法）
UPDATE question_templates
SET template_pattern = '{a}+{b}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 3, "max": 9}, "op": {"values": ["+"]}, "question_complexity": ["simple"], "rules": ["ensure_positive", "result_within_20"], "fixed_addend": [6, 7, 8], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 40;

-- ID=41: 5、4、3、2 加几（进位加法，结果>10）
UPDATE question_templates
SET template_pattern = '{a}+{b}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 6, "max": 9}, "op": {"values": ["+"]}, "question_complexity": ["simple"], "rules": ["ensure_positive"], "fixed_addend": [2, 3, 4, 5], "min_result": 11, "result_within": 19, "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 41;

-- ID=42: 比大小（带加法）
UPDATE question_templates
SET template_pattern = '{a}+{b}[BLANK]{c}',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 20}, "op": {"values": ["+"]}, "question_complexity": ["compare_with_result"], "rules": ["ensure_positive"], "q_type": {"compare_with_result": "circle"}, "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "circle", "show_question_number": true}}',
    is_active = 1
WHERE id = 42;

-- ID=43: 整理和复习（20 以内进位加法综合）
UPDATE question_templates
SET template_pattern = 'mixed',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 2, "max": 9}, "op": {"values": ["+"]}, "question_complexity": ["simple", "missing_operand", "compare_with_result"], "rules": ["ensure_positive", "result_within_20"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 43;

-- ID=44: 复习与关练（综合）
UPDATE question_templates
SET template_pattern = 'mixed',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 20}, "op": {"values": ["+", "-"]}, "question_complexity": ["simple", "missing_operand", "mixed_operation"], "rules": ["ensure_positive"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 44;

-- ID=45: 10 以内的加、减法
UPDATE question_templates
SET template_pattern = '{a}+{b}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 1, "max": 9}, "op": {"values": ["+", "-"]}, "question_complexity": ["simple"], "rules": ["ensure_positive", "result_within_10"], "rendering_config": {"layout": "multi", "columns": 5, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 45;

-- ID=46: 20 以内的进位加法
UPDATE question_templates
SET template_pattern = '{a}+{b}=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 2, "max": 9}, "op": {"values": ["+"]}, "question_complexity": ["simple"], "rules": ["ensure_positive", "result_within_20"], "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 46;

-- ID=47: 十几减 9
UPDATE question_templates
SET template_pattern = '{a}-9=[BLANK]',
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"num": {"min": 11, "max": 19}, "op": {"values": ["-"]}, "question_complexity": ["simple"], "rules": ["ensure_positive"], "fixed_subtractor": 9, "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": true}}',
    is_active = 1
WHERE id = 47;

-- =====================================================
-- 迁移完成
-- =====================================================
