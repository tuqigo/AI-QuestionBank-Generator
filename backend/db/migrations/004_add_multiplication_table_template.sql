-- 添加九九乘法表练习模板
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
    '九九乘法表练习',
    'math',
    'grade3',
    'upper',
    '人教版',
    'CALCULATION',
    '生成 1-9 的乘法算式，用于练习乘法口诀表',
    '{"min_factor": 1, "max_factor": 9, "allow_commute": false}',
    '3 × 4 =（ ）',
    'multiplication_table',
    5,
    1
);
