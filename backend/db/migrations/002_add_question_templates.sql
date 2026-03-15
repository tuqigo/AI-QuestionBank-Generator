-- ============================================
-- AI 题库生成器 - 数据库迁移 002
-- 题目模板系统
-- ============================================

-- 1. 题目模板表
CREATE TABLE IF NOT EXISTS question_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           -- 模板名称
    subject TEXT NOT NULL,        -- 学科：math/chinese/english
    grade TEXT NOT NULL,          -- 年级：grade1~grade9
    semester TEXT NOT NULL,       -- 学期：upper/lower (上学期/下学期)
    textbook_version TEXT NOT NULL, -- 教材版本：人教版/人教版 (新)/北师大版/苏教版/西师版/沪教版/北京版/青岛六三/青岛五四
    question_type TEXT NOT NULL,  -- 题型：CALCULATION/FILL_BLANK 等
    template_pattern TEXT NOT NULL, -- 模板模式字符串
    variables_config TEXT NOT NULL, -- 变量配置（JSON 格式）
    example TEXT,                 -- 示例
    generator_module TEXT,        -- 生成器模块名（对应 services/template/generators 下的文件名）
    sort_order INTEGER DEFAULT 0, -- 排序序号
    is_active INTEGER DEFAULT 1,  -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 模板使用记录表（用于统计分析）
CREATE TABLE IF NOT EXISTS template_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    generated_params TEXT,        -- 生成时使用的参数（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES question_templates(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. 索引
CREATE INDEX IF NOT EXISTS idx_templates_active ON question_templates(is_active, sort_order);
CREATE INDEX IF NOT EXISTS idx_templates_subject_grade ON question_templates(subject, grade, is_active);
CREATE INDEX IF NOT EXISTS idx_templates_semester_version ON question_templates(semester, textbook_version, is_active);
CREATE INDEX IF NOT EXISTS idx_template_logs_user ON template_usage_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_template_logs_template ON template_usage_logs(template_id, created_at);

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
