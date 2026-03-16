-- 添加长度比较模板（一年级 下学期 沪教版）
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
    '长度比较 - 长度单位换算',
    'math',
    'grade1',
    'lower',
    '沪教版',
    'CALCULATION',
    '长度单位换算：m/cm/dm 互化',
    '{"value": {"min": 1, "max": 100}, "convert_types": ["m_to_cm", "cm_to_m", "dm_to_cm", "cm_to_dm", "m_to_dm", "dm_to_m", "m_cm_to_cm", "m_dm_to_dm"]}',
    '7m = （ ）cm、500cm = （ ）m、1dm = （ ）cm、70m2dm = （ ）dm',
    'length_comparison',
    13,
    1
);
