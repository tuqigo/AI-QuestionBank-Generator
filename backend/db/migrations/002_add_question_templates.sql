-- ============================================
-- AI 题库生成器 - 数据库迁移 002
-- 题目模板系统
-- ============================================

-- 4. 初始化默认模板数据
-- 模板 1：一年级 10 以内的数比一比（generator_module: compare_number）
INSERT INTO question_templates (name, subject, grade, semester, textbook_version, question_type, template_pattern, variables_config, example, sort_order, generator_module)
VALUES (
    '一年级 10 以内的数比一比',
    'math',
    'grade1',
    'upper',
    '人教版',
    'FILL_BLANK',
    '{a}（ ）{b}',
    '{"a": {"min": 1, "max": 10}, "b": {"min": 1, "max": 10}, "rules": ["ensure_different"]}',
    '4（）5',
    1,
    'compare_number'
);

-- 模板 2：一年级 10 以内的加减法（generator_module: addition_subtraction）
INSERT INTO question_templates (name, subject, grade, semester, textbook_version, question_type, template_pattern, variables_config, example, sort_order, generator_module)
VALUES (
    '一年级 10 以内的加减法',
    'math',
    'grade1',
    'upper',
    '人教版',
    'CALCULATION',
    '{a} {op} {b} = （ ）',
    '{"a": {"min": 1, "max": 10}, "b": {"min": 1, "max": 10}, "op": {"values": ["+", "-"]}, "rules": ["ensure_positive"]}',
    '2 + 2 = （ ）',
    2,
    'addition_subtraction'
);

-- 模板 3：一年级 10 以内连加减法（generator_module: consecutive_addition_subtraction）
INSERT INTO question_templates (name, subject, grade, semester, textbook_version, question_type, template_pattern, variables_config, example, sort_order, generator_module)
VALUES (
    '一年级 10 以内连加减法',
    'math',
    'grade1',
    'upper',
    '人教版',
    'CALCULATION',
    '{a} {op1} {b} {op2} {c} = （ ）',
    '{"a": {"min": 1, "max": 10}, "b": {"min": 1, "max": 10}, "c": {"min": 1, "max": 10}, "op1": {"values": ["+", "-"]}, "op2": {"values": ["+", "-"]}, "rules": ["ensure_positive", "result_within_10"]}',
    '7 + 1 - 3 = （ ）',
    3,
    'consecutive_addition_subtraction'
);

-- 模板 4：认识人民币 - 元角分换算（generator_module: currency_conversion）
INSERT INTO question_templates (name, subject, grade, semester, textbook_version, question_type, template_pattern, variables_config, example, sort_order, generator_module)
VALUES (
    '认识人民币 - 元角分换算',
    'math',
    'grade1',
    'lower',
    '人教版',
    'CALCULATION',
    '换算题',
    '{"yuan": {"max": 50}, "jiao": {"max": 50}, "fen": {"max": 50}, "convert_types": ["yuan_to_jiao", "jiao_to_fen", "fen_to_jiao", "yuan_to_fen", "fen_to_yuan", "yuan_jiao_to_jiao", "yuan_fen_to_fen", "yuan_jiao_fen_to_fen"]}',
    '50 分 = （ ）角',
    4,
    'currency_conversion'
);
