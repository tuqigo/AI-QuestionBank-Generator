-- 添加一年级沪教版 人民币认识模板
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
    '人民币认识',
    'math',
    'grade1',
    'lower',
    '沪教版',
    'FILL_BLANK',
    '元角分换算：{amount} = （ ）',
    '{"yuan": {"max": 100}, "jiao": {"max": 99}, "fen": {"max": 99}, "convert_types": ["jiao_to_fen", "yuan_jiao_to_jiao", "yuan_to_jiao", "jiao_to_yuan", "fen_to_jiao"], "rules": ["ensure_integer_result"]}',
    '2 角 = （ ）分、39 元 5 角 = （ ）角',
    'currency_conversion',
    9,
    1
);
