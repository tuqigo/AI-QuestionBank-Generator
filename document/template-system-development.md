# 模板系统开发指南

## 1. 系统概述

### 1.1 背景

模板题目系统是 2026-03 新增的核心功能，旨在提供不依赖 AI 服务的题目生成方式。通过预定义的模板规则和生成器，实现零成本、高性能、可预测的题目生成。

### 1.2 系统特点

| 特点 | 说明 |
|------|------|
| 零成本 | 无需调用 AI API，完全基于规则生成 |
| 高性能 | 毫秒级响应，适合高频使用场景 |
| 可预测 | 题目格式和内容完全可控 |
| 易扩展 | 每个模板对应独立生成器，符合开闭原则 |
| 可配置 | 通过数据库配置灵活调整题目规则 |

### 1.3 适用场景

- 基础计算题（加减乘除）
- 固定题型的练习题
- 需要大量生成的场景
- 对成本敏感的使用场景

---

## 2. 需求分析

### 2.1 功能需求

#### FR1: 模板管理
- 支持创建、查询、更新、删除模板
- 模板包含名称、学科、年级、题型、配置等信息
- 支持模板启用/禁用状态管理

#### FR2: 题目生成
- 根据模板 ID 生成指定数量的题目
- 题目格式符合学科规范
- 支持多种题型（计算题、填空题、比大小等）

#### FR3: 规则约束
- 支持配置生成规则（如确保非负、结果范围等）
- 规则在生成器层面执行，确保题目质量

#### FR4: 使用记录
- 记录模板使用情况（模板 ID、用户 ID、生成参数）
- 用于数据分析和模板优化

### 2.2 非功能需求

| 需求类型 | 要求 |
|----------|------|
| 响应时间 | < 100ms |
| 并发能力 | 支持 100+ QPS |
| 可扩展性 | 新增模板无需修改核心代码 |
| 可维护性 | 生成器代码独立，易于测试 |

---

## 3. 系统设计

### 3.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      API 层                                  │
│  /api/templates/list    - 获取模板列表                       │
│  /api/templates/generate - 生成题目                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      服务层                                  │
│  services/template/                                          │
│  ├── template_store.py    - 数据访问                         │
│  └── generators/          - 生成器目录                       │
│       ├── base.py         - 抽象基类                         │
│       ├── __init__.py     - 注册表                           │
│       └── *.py            - 具体生成器                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层                                  │
│  question_templates     - 模板表                             │
│  template_usage_logs    - 使用记录表                         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心接口

#### TemplateGenerator 抽象基类

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class TemplateGenerator(ABC):
    @abstractmethod
    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        """
        生成题目

        Args:
            template_config: 模板配置（来自数据库 variables_config 字段）
            quantity: 生成数量
            question_type: 题目类型（来自模板 question_type 字段）

        Returns:
            题目列表，每项包含：
            - type: 题目类型
            - stem: 题干
            - knowledge_points: 知识点列表
            - rows_to_answer: 答题行数
        """
        pass

    @abstractmethod
    def get_knowledge_points(self, template_config: dict) -> List[str]:
        """获取知识点列表"""
        pass
```

### 3.3 生成器注册表

```python
# services/template/generators/__init__.py

GENERATOR_REGISTRY = {
    "compare_number": CompareNumberGenerator,
    "addition_subtraction": AdditionSubtractionGenerator,
    "consecutive_addition_subtraction": ConsecutiveAdditionSubtractionGenerator,
    "currency_conversion": CurrencyConversionGenerator,
}


def get_generator(generator_name: str) -> TemplateGenerator:
    """
    根据生成器名称获取生成器实例

    Args:
        generator_name: 生成器名称（对应 generator_module 字段）

    Returns:
        生成器实例

    Raises:
        ValueError: 生成器不存在
    """
    if generator_name not in GENERATOR_REGISTRY:
        raise ValueError(f"未知的生成器：{generator_name}")

    return GENERATOR_REGISTRY[generator_name]()
```

---

## 4. 实现指南

### 4.1 新增生成器步骤

#### 步骤 1: 创建生成器文件

在 `services/template/generators/` 目录下创建新文件：

```python
"""
模板：XXX 模板说明
生成逻辑：简要描述生成规则
例题：示例题目
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MyCustomGenerator(TemplateGenerator):
    """自定义生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置
        # 示例：a_min = template_config.get("a", {}).get("min", 1)

        for _ in range(quantity):
            max_attempts = 50
            for attempt in range(max_attempts):
                # 生成题目逻辑
                stem = "..."  # 题干
                # answer = ...  # 答案（可选，根据需求）

                # 检查是否重复
                if stem in used_stems:
                    continue

                used_stems.add(stem)
                break
            else:
                # 50 次尝试后仍未生成有效题目，跳过
                continue

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 1,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["知识点 1", "知识点 2"]
```

#### 步骤 2: 注册生成器

在 `services/template/generators/__init__.py` 中添加：

```python
from .my_custom import MyCustomGenerator

GENERATOR_REGISTRY = {
    # ... 现有生成器
    "my_custom": MyCustomGenerator,
}
```

#### 步骤 3: 创建数据库模板记录

```sql
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version, question_type,
    template_pattern, variables_config, example,
    generator_module, sort_order, is_active
) VALUES (
    '我的自定义模板',
    'math',
    'grade1',
    'upper',
    '人教版',
    'CALCULATION',
    '{a} + {b} = ( )',
    '{"a": {"min": 1, "max": 10}, "b": {"min": 1, "max": 10}, "rules": []}',
    '示例：3 + 5 = ( )',
    'my_custom',
    10,
    1
);
```

### 4.2 配置规范

#### variables_config JSON 结构

```json
{
    "a": {
        "min": 1,
        "max": 10
    },
    "b": {
        "min": 1,
        "max": 10
    },
    "op": {
        "values": ["+", "-"]
    },
    "rules": ["ensure_positive", "result_within_10"],
    "custom_param": "custom_value"
}
```

#### 支持的规则约束

| 规则名 | 说明 | 适用场景 |
|--------|------|----------|
| `ensure_different` | 确保两个数不同 | 比大小题目 |
| `ensure_positive` | 确保结果非负（含中间结果） | 减法、连加减 |
| `result_within_10` | 确保结果 ≤ 10 | 一年级题目 |
| `result_within_20` | 确保结果 ≤ 20 | 二年级题目 |
| `result_within_100` | 确保结果 ≤ 100 | 三年级题目 |

#### 支持的教材版本

| 版本 | 说明 |
|------|------|
| 人教版 | 人民教育出版社 |
| 人教版 (新) | 人教版新教材 |
| 北师大版 | 北京师范大学出版社 |
| 苏教版 | 江苏教育出版社 |
| 西师版 | 西南师范大学出版社 |
| 沪教版 | 上海教育出版社 |
| 北京版 | 北京出版社 |
| 青岛六三 | 青岛出版社（六三学制） |
| 青岛五四 | 青岛出版社（五四学制） |

#### 支持的学期

| 学期 | 说明 |
|------|------|
| upper | 上学期 |
| lower | 下学期 |

### 4.3 边界情况处理

使用 `for...else` 语法处理边界情况：

```python
for _ in range(quantity):
    max_attempts = 50
    for attempt in range(max_attempts):
        # 生成题目
        # 检查是否符合规则
        if not is_valid:
            continue

        # 检查是否重复
        if stem in used_stems:
            continue

        # 有效题目，跳出循环
        break
    else:
        # 50 次尝试后仍未生成有效题目，跳过该题
        continue

    # 添加到结果列表
    questions.append(...)
```

---

## 5. 已实现生成器

### 5.1 CompareNumberGenerator - 比大小

**文件**: `services/template/generators/compare_number.py`

**适用**: 一年级 10 以内数比一比

**例题**: 4（）5

**配置示例**:
```json
{
    "a": {"min": 1, "max": 10},
    "b": {"min": 1, "max": 10},
    "rules": ["ensure_different"]
}
```

**核心逻辑**:
```python
a = random.randint(a_min, a_max)
b = random.randint(b_min, b_max)

if ensure_different and a == b:
    continue

stem = f"{a}（    ）{b}"
```

---

### 5.2 AdditionSubtractionGenerator - 加减法

**文件**: `services/template/generators/addition_subtraction.py`

**适用**: 一年级 10 以内加减法

**例题**: 2 + 2 = （ ）

**配置示例**:
```json
{
    "a": {"min": 1, "max": 10},
    "b": {"min": 1, "max": 10},
    "op": {"values": ["+", "-"]},
    "rules": ["ensure_positive"]
}
```

**核心逻辑**:
```python
a = random.randint(a_min, a_max)
b = random.randint(b_min, b_max)
op = random.choice(operators)

if ensure_positive and op == "-" and a < b:
    continue

stem = f"{a} {op} {b} = （    ）"
```

---

### 5.3 ConsecutiveAdditionSubtractionGenerator - 连加减

**文件**: `services/template/generators/consecutive_addition_subtraction.py`

**适用**: 一年级 10 以内连加减

**例题**: 2 + 3 + 4 = （ ）

**特点**: 检查中间结果非负

**配置示例**:
```json
{
    "a": {"min": 1, "max": 10},
    "b": {"min": 1, "max": 10},
    "c": {"min": 1, "max": 10},
    "op1_values": ["+", "-"],
    "op2_values": ["+", "-"],
    "rules": ["ensure_positive"]
}
```

**核心逻辑**:
```python
a, b, c = random.randint(...), random.randint(...), random.randint(...)
op1, op2 = random.choice(op1_values), random.choice(op2_values)

# 计算中间结果
intermediate = a + b if op1 == "+" else a - b

# 确保中间结果非负
if ensure_positive and intermediate < 0:
    continue

# 计算最终结果
final = intermediate + c if op2 == "+" else intermediate - c

# 确保最终结果非负
if ensure_positive and final < 0:
    continue

stem = f"{a} {op1} {b} {op2} {c} = （    ）"
```

---

### 5.4 CurrencyConversionGenerator - 人民币换算

**文件**: `services/template/generators/currency_conversion.py`

**适用**: 认识人民币 - 元角分换算

**例题**:
- 50 分 = （ ）角
- 6 元 = （ ）角
- 54 元 50 分 = （ ）分

**配置示例**:
```json
{
    "yuan": {"max": 50},
    "jiao": {"max": 50},
    "fen": {"max": 50},
    "convert_types": [
        "yuan_to_jiao",
        "jiao_to_fen",
        "yuan_fen_to_fen"
    ]
}
```

**支持的换算类型**:

| 类型 | 说明 | 例题 |
|------|------|------|
| `yuan_to_jiao` | 元→角 | 6 元 = （ ）角 |
| `jiao_to_yuan` | 角→元 | 60 角 = （ ）元 |
| `jiao_to_fen` | 角→分 | 5 角 = （ ）分 |
| `fen_to_jiao` | 分→角 | 50 分 = （ ）角 |
| `yuan_to_fen` | 元→分 | 5 元 = （ ）分 |
| `fen_to_yuan` | 分→元 | 100 分 = （ ）元 |
| `yuan_jiao_to_jiao` | 元 + 角→角 | 3 元 5 角 = （ ）角 |
| `yuan_fen_to_fen` | 元 + 分→分 | 54 元 50 分 = （ ）分 |
| `yuan_jiao_fen_to_fen` | 元 + 角 + 分→分 | 3 元 5 角 20 分 = （ ）分 |

**核心逻辑**:
```python
convert_type = random.choice(convert_types)

if convert_type == "yuan_to_jiao":
    yuan = random.randint(1, yuan_max)
    stem = f"{yuan}元 = （    ）角"
    answer = yuan * 10
elif convert_type == "yuan_jiao_to_jiao":
    yuan = random.randint(1, yuan_max)
    jiao = random.randint(1, 9)
    stem = f"{yuan}元{jiao}角 = （    ）角"
    answer = yuan * 10 + jiao
# ... 其他类型
```

---

## 6. API 使用

### 6.1 获取模板列表

```http
GET /api/templates/list
```

**响应**:
```json
{
    "items": [
        {
            "id": 1,
            "name": "比一比大小",
            "subject": "math",
            "grade": "grade1",
            "question_type": "COMPARE",
            "template_pattern": "{a}（）{b}",
            "example": "4（）5",
            "generator_module": "compare_number",
            "sort_order": 0,
            "is_active": true
        }
    ]
}
```

### 6.2 生成题目

```http
POST /api/templates/generate
Content-Type: application/json

{
    "template_id": 1,
    "quantity": 10
}
```

**响应**:
```json
{
    "questions": [
        {
            "type": "COMPARE",
            "stem": "4（    ）5",
            "knowledge_points": ["数的大小比较"],
            "rows_to_answer": 1
        },
        {
            "type": "COMPARE",
            "stem": "7（    ）3",
            "knowledge_points": ["数的大小比较"],
            "rows_to_answer": 1
        }
    ]
}
```

---

## 7. 测试指南

### 7.1 单元测试示例

```python
import pytest
from services.template.generators.compare_number import CompareNumberGenerator


class TestCompareNumberGenerator:
    def setup_method(self):
        self.generator = CompareNumberGenerator()

    def test_generate_basic(self):
        template_config = {
            "a": {"min": 1, "max": 10},
            "b": {"min": 1, "max": 10},
            "rules": []
        }
        questions = self.generator.generate(template_config, quantity=5, question_type="COMPARE")

        assert len(questions) == 5
        for q in questions:
            assert "type" in q
            assert "stem" in q
            assert "knowledge_points" in q
            assert "rows_to_answer" in q

    def test_generate_ensure_different(self):
        template_config = {
            "a": {"min": 1, "max": 2},  # 范围很小，测试 ensure_different
            "b": {"min": 1, "max": 2},
            "rules": ["ensure_different"]
        }
        questions = self.generator.generate(template_config, quantity=10, question_type="COMPARE")

        # 验证生成的题目都符合规则
        for q in questions:
            # 解析题干验证
            pass

    def test_knowledge_points(self):
        template_config = {}
        points = self.generator.get_knowledge_points(template_config)

        assert isinstance(points, list)
        assert len(points) > 0
```

### 7.2 集成测试

```python
def test_template_generation_end_to_end(client, auth_headers):
    # 1. 获取模板列表
    response = client.get("/api/templates/list", headers=auth_headers)
    assert response.status_code == 200
    templates = response.json()["items"]

    # 2. 选择第一个模板生成题目
    template_id = templates[0]["id"]
    response = client.post(
        "/api/templates/generate",
        json={"template_id": template_id, "quantity": 5},
        headers=auth_headers
    )
    assert response.status_code == 200

    questions = response.json()["questions"]
    assert len(questions) == 5
```

---

## 8. 数据库迁移

### 8.1 创建模板表

```sql
-- db/migrations/002_add_question_templates.sql

-- 题目模板表
CREATE TABLE question_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    grade TEXT NOT NULL,
    semester TEXT NOT NULL,       -- 学期：upper/lower
    textbook_version TEXT NOT NULL, -- 教材版本：人教版/人教版 (新)/北师大版/苏教版/西师版/沪教版/北京版/青岛六三/青岛五四
    question_type TEXT NOT NULL,
    template_pattern TEXT NOT NULL,
    variables_config TEXT NOT NULL,
    example TEXT,
    generator_module TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模板使用记录表
CREATE TABLE template_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    generated_params TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES question_templates(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_templates_active ON question_templates(is_active);
CREATE INDEX idx_templates_semester_version ON question_templates(semester, textbook_version, is_active);
CREATE INDEX idx_logs_template_id ON template_usage_logs(template_id);
CREATE INDEX idx_logs_user_id ON template_usage_logs(user_id);

-- 初始化数据
INSERT INTO question_templates (name, subject, grade, semester, textbook_version, question_type, template_pattern, variables_config, example, generator_module, sort_order) VALUES
('比一比大小', 'math', 'grade1', 'upper', '人教版', 'COMPARE', '{a}（）{b}', '{"a": {"min": 1, "max": 10}, "b": {"min": 1, "max": 10}, "rules": ["ensure_different"]}', '4（）5', 'compare_number', 1),
('10 以内加减法', 'math', 'grade1', 'upper', '人教版', 'CALCULATION', '{a}+{b}=( )', '{"a": {"min": 1, "max": 10}, "b": {"min": 1, "max": 10}, "op": {"values": ["+", "-"]}, "rules": ["ensure_positive"]}', '2+3=( )', 'addition_subtraction', 2),
('连加减法', 'math', 'grade1', 'upper', '人教版', 'CALCULATION', '{a}+{b}+{c}=( )', '{"a": {"min": 1, "max": 10}, "b": {"min": 1, "max": 10}, "c": {"min": 1, "max": 10}, "op1_values": ["+", "-"], "op2_values": ["+", "-"], "rules": ["ensure_positive"]}', '2+3+4=( )', 'consecutive_addition_subtraction', 3),
('认识人民币 - 元角分换算', 'math', 'grade1', 'lower', '人教版', 'CALCULATION', '换算题', '{"yuan": {"max": 50}, "jiao": {"max": 50}, "fen": {"max": 50}, "convert_types": ["yuan_to_jiao", "jiao_to_fen", "fen_to_jiao", "yuan_to_fen", "fen_to_yuan", "yuan_jiao_to_jiao", "yuan_fen_to_fen", "yuan_jiao_fen_to_fen"]}', '50 分=（）角', 'currency_conversion', 4);
```

### 8.2 执行迁移

```bash
cd backend
python -c "
import sqlite3
with open('db/migrations/002_add_question_templates.sql', 'r') as f:
    conn = sqlite3.connect('data/users.db')
    conn.executescript(f.read())
    conn.commit()
    conn.close()
"
```

---

## 9. 常见问题

### Q1: 生成器返回空列表怎么办？

**原因**: 配置范围太小或规则太严格，导致无法生成有效题目

**解决**:
1. 检查 `template_config` 配置是否合理
2. 增大数值范围
3. 放宽规则约束
4. 生成器会自动跳过无法生成的题目，不会抛出异常

### Q2: 如何添加新的规则约束？

**步骤**:
1. 在 `models/question_template.py` 的 `SUPPORTED_RULES` 中添加规则名
2. 在生成器的 `generate` 方法中实现规则检查逻辑

```python
# 示例：添加 ensure_even 规则（确保偶数）
if "ensure_even" in template_config.get("rules", []) and a % 2 != 0:
    continue
```

### Q3: 如何调试生成器？

**方法**:
1. 在生成器代码中添加日志
2. 使用单元测试验证
3. 通过 API 直接调用并查看返回结果

---

## 10. 相关文档

- [后端代码结构](./backend-code-structure.md) - 整体代码结构
- [后端系统架构](./backend-system-architecture.md) - 系统架构设计
- [数据库表结构](../backend/db/schema.sql) - 完整表结构定义

---

## 附录：代码文件清单

```
backend/services/template/
├── __init__.py
├── template_store.py           # 模板数据访问
└── generators/
    ├── __init__.py             # 生成器注册表
    ├── base.py                 # 抽象基类
    ├── compare_number.py       # 比大小生成器
    ├── addition_subtraction.py # 加减法生成器
    ├── consecutive_addition_subtraction.py  # 连加减生成器
    └── currency_conversion.py  # 人民币换算生成器
```

```
backend/api/v1/
└── templates.py                # 模板路由
```

```
backend/models/
└── question_template.py        # 模板数据模型
```

```
backend/db/migrations/
└── 002_add_question_templates.sql  # 数据库迁移
```
