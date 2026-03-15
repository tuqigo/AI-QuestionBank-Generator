-- ============================================
-- 统一加减法生成器配置迁移
-- 将旧的加减法相关模板配置统一改为使用 mixed_addition_subtraction 生成器
-- ============================================

-- 更新模板 1：一年级 10 以内的数比一比（使用 compare_number，无需修改）

-- 更新模板 2：一年级 10 以内的加减法 -> 使用 mixed_addition_subtraction
UPDATE question_templates
SET
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"question_types": ["simple"], "num": {"min": 1, "max": 10}, "op": {"values": ["+", "-"]}, "rules": ["ensure_positive"]}',
    template_pattern = '{a} {op} {b} = （ ）'
WHERE name = '一年级 10 以内的加减法';

-- 更新模板 3：一年级 10 以内连加减法 -> 使用 mixed_addition_subtraction
UPDATE question_templates
SET
    generator_module = 'mixed_addition_subtraction',
    variables_config = '{"question_types": ["consecutive_add", "consecutive_subtract"], "num": {"min": 1, "max": 10}, "rules": ["ensure_positive", "result_within_10"]}',
    template_pattern = '{a} {op1} {b} {op2} {c} = （ ）'
WHERE name = '一年级 10 以内连加减法';

-- 更新模板：百以内数的大小比较（使用 compare_number，无需修改）

-- 更新模板：连加、连减及加减综合 -> 使用统一的 mixed_addition_subtraction（已有配置）
-- 配置保持不变，因为已经是使用这个生成器
