-- 添加长方体和正方体体积单位换算模板
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
    '长方体和正方体体积单位的换算',
    'math',
    'grade5',
    'lower',
    '人教版',
    'CALCULATION',
    '生成体积单位之间的换算题目（立方米、立方分米、立方厘米、升、毫升）',
    '{"volume": {"min": 1, "max": 100}, "convert_types": ["m3_to_dm3", "dm3_to_cm3", "cm3_to_dm3", "dm3_to_m3", "l_to_ml", "ml_to_l", "dm3_to_l", "l_to_dm3", "cm3_to_ml", "ml_to_cm3", "m3_to_l", "l_to_m3"]}',
    '5 立方米 = （ ）立方分米',
    'volume_conversion',
    6,
    1
);
