-- 添加一年级沪教版 连加、连减及加减综合模板
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
    '连加、连减及加减综合',
    'math',
    'grade1',
    'lower',
    '沪教版',
    'FILL_BLANK',
    '百以内连加减法综合练习',
    '{"num": {"min": 1, "max": 100}, "question_types": ["consecutive_add", "consecutive_subtract", "mixed_operation", "missing_operand", "compare_with_result"], "rules": ["ensure_positive", "result_within_100"]}',
    '1+6+19=（）、17-（）=2、96-23-45=（）、54+6+16（）74',
    'mixed_addition_subtraction',
    10,
    1
);
