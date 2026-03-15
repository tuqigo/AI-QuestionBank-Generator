-- 添加一年级沪教版 百以内数的大小比较模板
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
    '百以内数的大小比较',
    'math',
    'grade1',
    'lower',
    '沪教版',
    'FILL_BLANK',
    '{a}（ ）{b}',
    '{"a": {"min": 20, "max": 100}, "b": {"min": 20, "max": 100}, "rules": ["ensure_different"]}',
    '35（ ）42',
    'compare_number',
    8,
    1
);
