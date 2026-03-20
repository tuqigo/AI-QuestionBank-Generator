-- Migration: Add unit_conversion_comprehensive generator and deprecate old generators
-- Date: 2026-03-20
-- Description: Add the new comprehensive unit conversion generator that replaces
--              currency_conversion, length_comparison, and volume_conversion generators

-- Note: This migration does not modify existing templates.
-- Existing templates using old generators will continue to work.
-- New templates should use unit_conversion_comprehensive instead.

-- No database schema changes required.
-- The generator is already registered in:
-- 1. backend/services/template/generators/__init__.py
-- 2. backend/core/constants.py
-- 3. backend/services/template/generators/unit_conversion_comprehensive.py

-- Example: How to create a new template using the comprehensive generator
/*
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version,
    question_type, template_pattern, variables_config,
    example, generator_module, sort_order, is_active
) VALUES (
    '单位换算综合练习',
    'math',
    'grade1',
    'lower',
    '人教版',
    'CALCULATION',
    '单位换算',
    '{"unit_category": "currency", "convert_types": ["yuan_to_jiao", "jiao_to_fen"], "value_range": {"min": 1, "max": 20}}',
    '5 元 = （ ）角',
    'unit_conversion_comprehensive',
    1,
    1
);
*/

-- Example: Length conversion template (Grade 3)
/*
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version,
    question_type, template_pattern, variables_config,
    example, generator_module, sort_order, is_active
) VALUES (
    '千米和米的换算',
    'math',
    'grade3',
    'lower',
    '人教版',
    'CALCULATION',
    '长度单位换算',
    '{"unit_category": "length", "convert_types": ["km_to_m", "m_to_km"], "value_range": {"min": 1, "max": 50}}',
    '3km = （ ）m',
    'unit_conversion_comprehensive',
    1,
    1
);
*/

-- Example: Volume conversion template (Grade 5)
/*
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version,
    question_type, template_pattern, variables_config,
    example, generator_module, sort_order, is_active
) VALUES (
    '体积单位换算',
    'math',
    'grade5',
    'lower',
    '人教版',
    'CALCULATION',
    '体积单位换算',
    '{"unit_category": "volume", "convert_types": ["m3_to_dm3", "dm3_to_cm3", "l_to_ml"], "value_range": {"min": 1, "max": 50}}',
    '5m³ = （ ）dm³',
    'unit_conversion_comprehensive',
    1,
    1
);
*/

-- Example: Time conversion template (Grade 3)
/*
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version,
    question_type, template_pattern, variables_config,
    example, generator_module, sort_order, is_active
) VALUES (
    '时间单位换算',
    'math',
    'grade3',
    'upper',
    '人教版',
    'CALCULATION',
    '时间单位换算',
    '{"unit_category": "time", "convert_types": ["hour_to_minute", "minute_to_second", "year_to_month"], "value_range": {"min": 1, "max": 12}}',
    '3 时 = （ ）分',
    'unit_conversion_comprehensive',
    1,
    1
);
*/
