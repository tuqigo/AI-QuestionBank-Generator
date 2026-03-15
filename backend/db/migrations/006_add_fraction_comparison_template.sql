-- 添加分数比大小模板
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
    '分数比大小',
    'math',
    'grade5',
    'lower',
    '人教版',
    'FILL_BLANK',
    '使用 LaTeX 分数格式生成两个分数进行比较：$\\frac{a}{b}$ （ ） $\\frac{c}{d}$',
    '{"denominator": {"min": 2, "max": 12}, "numerator": {"min": 1}, "compare_types": ["common_denominator", "common_numerator", "different"], "rules": ["ensure_different", "ensure_proper_fraction"]}',
    '$\\frac{3}{4}$ （ ） $\\frac{2}{3}$',
    'fraction_comparison',
    7,
    1
);
