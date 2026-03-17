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

## 1.4 快速添加模板指南（6 步完成）

> **目标**：让任何 AI 助手都能根据本文档准确添加新模板
>
> **重要**：按顺序完成以下 6 个步骤，每步都不可跳过

### 步骤 1：创建生成器文件

在 `backend/services/template/generators/` 目录创建新文件，例如 `volume_conversion.py`：

```python
"""
模板：模板名称说明
生成逻辑：简要描述生成规则
例题：示例题目
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MyGenerator(TemplateGenerator):
    """生成器类名（建议：功能 +Generator，如 VolumeConversionGenerator）"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 1. 读取配置参数
        # 示例：param = template_config.get("param_key", default_value)

        # 2. 循环生成题目
        for _ in range(quantity):
            max_attempts = 50
            for attempt in range(max_attempts):
                # 生成题目内容
                stem = f"题目内容"

                # 检查是否重复
                if stem in used_stems:
                    continue

                used_stems.add(stem)
                break
            else:
                continue  # 50 次尝试失败，跳过

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 1,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["知识点列表"]
```

### 步骤 2：注册生成器

编辑 `backend/services/template/generators/__init__.py`：

```python
# 1. 导入生成器类
from .my_file import MyGenerator

# 2. 添加到注册表（在 GENERATOR_REGISTRY 字典中添加）
GENERATOR_REGISTRY = {
    # ... 现有生成器
    "my_module_name": MyGenerator,  # key 是模块名，value 是生成器类
}
```

### 步骤 3：创建数据库迁移

在 `backend/db/migrations/` 目录创建 SQL 文件，例如 `005_add_my_template.sql`：

```sql
-- 添加我的模板
INSERT INTO question_templates (
    name,           -- 模板名称
    subject,        -- 学科：math/chinese/english
    grade,          -- 年级：grade1-grade9
    semester,       -- 学期：upper/lower
    textbook_version, -- 教材版本：人教版/北师大版等
    question_type,  -- 题型：CALCULATION/CHOICE/FILL_BLANK/COMPARE/WORD_PROBLEM
    template_pattern, -- 模板模式描述
    variables_config, -- JSON 配置（见下方配置规范）
    example,        -- 示例题目
    generator_module, -- 生成器模块名（与注册表 key 一致）
    sort_order,     -- 排序（从 1 开始，不要与现有重复）
    is_active       -- 是否启用：1/0
) VALUES (
    '我的模板名称',
    'math',
    'grade3',
    'upper',
    '人教版',
    'CALCULATION',
    '模板模式描述',
    '{"key": "value"}',
    '示例：3 + 4 = （ ）',
    'my_module_name',
    10,
    1
);
```

### 步骤 4：执行迁移

**方式：使用迁移管理命令（推荐）**

```bash
cd backend

# 执行所有待执行的迁移
python -m db.migrations_cli migrate

# 查看迁移状态
python -m db.migrations_cli status
```


```

**生产环境部署**

生产环境使用 `restart_backend.sh` 脚本自动执行迁移：

```bash
# 重启脚本会自动执行以下步骤
./restart_backend.sh

# 脚本内部流程：
# 1. git pull 拉取代码
# 2. python3 -m py_compile main.py 代码检查
# 3. python -m db.migrations_cli migrate 执行迁移（失败则停止部署）
# 4. kill <old_pid> 停止旧服务
# 5. uvicorn main:app & 启动新服务
```

**注意**：
- 迁移脚本按版本号顺序执行（001, 002, 003...）
- 每个迁移脚本只执行一次（通过 `schema_migrations` 表记录）
- 迁移失败时会标记为 `failed` 状态，需手动修复后重新执行
- 生产环境切勿手动执行 SQL，应使用迁移命令

详见 [数据库迁移系统文档](./database-migrations.md)。

### 步骤 5：添加或更新规则（如需要）

**如果你的模板需要新的规则约束**，编辑 `backend/config/template_rules.py`：

```python
# 在相应的规则字典中添加新规则
RESULT_WITHIN_RULES = {
    # ... 现有规则
    "result_within_50": "确保结果 ≤ 50",  # 添加新规则
}
```

> **说明**：规则配置文件独立于模型文件，无需修改代码即可扩展。生成器代码中可以直接使用任何规则名，无需预先注册。但建议将通用规则添加到配置文件中供其他生成器复用。

### 步骤 6：验证测试

```bash
# 启动后端服务后，调用 API 测试
curl -X POST http://localhost:8000/api/templates/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"template_id": 你的模板 ID, "quantity": 5}'
```

---

## 1.5 规则约束完整列表

> **如何添加新规则**：如果现有规则不够用，在 `backend/config/template_rules.py` 的相应规则字典中添加即可。规则名建议用 `ensure_` 或 `result_` 前缀，然后在生成器代码中检查并实现对应逻辑。
>
> **配置化设计**：规则配置已移至独立文件 `backend/config/template_rules.py`，无需修改模型代码即可扩展。未来可通过数据库表 `generator_rules` 实现后台页面动态管理。

### 数值范围约束

| 规则名 | 说明 | 适用年级 |
|--------|------|----------|
| `result_within_10` | 确保结果 ≤ 10 | 一年级 |
| `result_within_20` | 确保结果 ≤ 20 | 二年级 |
| `result_within_100` | 确保结果 ≤ 100 | 三年级 |
| `result_within_1000` | 确保结果 ≤ 1000 | 四年级 |

### 数值属性约束

| 规则名 | 说明 | 适用场景 |
|--------|------|----------|
| `ensure_different` | 确保两个数不同 | 比大小题目 |
| `ensure_positive` | 确保结果非负（含中间结果） | 减法、连加减 |
| `ensure_non_zero` | 确保不为零 | 除法、分母 |
| `ensure_even` | 确保是偶数 | 整除练习 |
| `ensure_odd` | 确保是奇数 | 特殊数练习 |
| `ensure_prime` | 确保是质数 | 质数练习 |
| `ensure_coprime` | 确保互质 | 分数约分 |

### 运算约束

| 规则名 | 说明 | 适用场景 |
|--------|------|----------|
| `ensure_divisible` | 确保除法能整除 | 除法练习 |
| `ensure_no_remainder` | 确保除法无余数 | 除法练习 |
| `ensure_borrowing` | 确保减法需要借位 | 借位减法 |
| `ensure_carrying` | 确保加法需要进位 | 进位加法 |

### 分数相关约束

| 规则名 | 说明 | 适用场景 |
|--------|------|----------|
| `ensure_proper_fraction` | 确保是真分数（分子 < 分母） | 分数基础 |
| `ensure_simplest_form` | 确保是最简分数 | 约分练习 |
| `ensure_common_denominator` | 确保同分母 | 分数比较/加减 |

### 几何/单位约束

| 规则名 | 说明 | 适用场景 |
|--------|------|----------|
| `ensure_realistic_value` | 确保是实际存在的值 | 应用题、几何 |
| `ensure_integer_result` | 确保计算结果为整数 | 单位换算 |

### 去重约束

| 规则名 | 说明 | 适用场景 |
|--------|------|----------|
| `ensure_unique_stem` | 确保题干不重复 | 所有题型（默认开启） |

---

## 1.6 未来可扩展方向

> 以下是根据小学数学教学大纲预留的扩展方向，开发新模板时可参考。如需添加新规则，在 `backend/models/question_template.py` 的 `SUPPORTED_RULES` 中添加即可。

### 小数相关规则

```python
"ensure_one_decimal",         # 确保一位小数
"ensure_two_decimals",        # 确保两位小数
"ensure_decimal_sum_within_10",  # 确保小数和≤10
"ensure_decimal_no_rounding", # 确保小数无需四舍五入
```

### 百分数相关规则

```python
"ensure_percentage",          # 确保是百分数
"ensure_percentage_integer",  # 确保百分数是整数
"ensure_percentage_convertible",  # 确保可转换为小数
```

### 负数相关规则（高年级）

```python
"allow_negative",            # 允许负数
"ensure_negative_result",    # 确保结果为负数
"ensure_mixed_signs",        # 确保混合正负数
```

### 应用题相关规则

```python
"ensure_word_problem",       # 确保是应用题形式
"ensure_multi_step",         # 确保是多步计算
"ensure_realistic_context",  # 确保情境真实合理
"ensure_no_extraneous_info", # 确保无多余信息
```

### 图形几何相关规则

```python
"ensure_integer_area",       # 确保面积是整数
"ensure_integer_volume",     # 确保体积是整数
"ensure_triangle_valid",     # 确保能构成三角形
"ensure_right_angle",        # 确保是直角
"ensure_integer_side",       # 确保边长是整数
```

### 统计概率相关规则

```python
"ensure_integer_mean",       # 确保平均数是整数
"ensure_probability_valid",  # 确保概率在 0-1 之间
"ensure_data_consistent",    # 确保数据一致性
```

### 代数相关规则（高年级）

```python
"ensure_linear_equation",    # 确保是一元一次方程
"ensure_integer_solution",   # 确保解是整数
"ensure_positive_coefficient",  # 确保系数为正
"ensure_single_variable",    # 确保单变量
```

### 比和比例相关规则

```python
"ensure_ratio_simplifiable", # 确保比可化简
"ensure_proportion_valid",   # 确保比例成立
"ensure_integer_ratio",      # 确保比值为整数
```

---

## 1.7 教材版本和年级

### 支持的教材版本

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

### 支持的学期

| 学期 | 说明 |
|------|------|
| upper | 上学期 |
| lower | 下学期 |

### 年级代码

| 代码 | 年级 |
|------|------|
| grade1 | 一年级 |
| grade2 | 二年级 |
| grade3 | 三年级 |
| grade4 | 四年级 |
| grade5 | 五年级 |
| grade6 | 六年级 |
| grade7 | 初一 |
| grade8 | 初二 |
| grade9 | 初三 |

---

### 配置规范速查

#### variables_config JSON 结构

```json
{
    "param_name": {
        "min": 1,
        "max": 10
    },
    "rules": ["ensure_positive", "ensure_different"]
}
```

#### 支持的题型

| 题型值 | 说明 | 适用场景 |
|--------|------|----------|
| `ORAL_CALCULATION` | 口算题 | 加减乘除、混合运算 |
| `CALCULATION` | 计算题 | 加减乘除、混合运算 |
| `CHOICE` | 选择题 | 单选/多选 |
| `FILL_BLANK` | 填空题 | 填空、比大小 |
| `COMPARE` | 比较大小 | 数值/分数/单位比较 |
| `WORD_PROBLEM` | 应用题 | 文字应用题 |

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
    # 注意：multiplication_table 生成器已删除，功能由 multiplication_division_comprehensive 统一支持
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

### 5.2 MixedAdditionSubtractionGenerator - 加减法统一生成器

**文件**: `services/template/generators/mixed_addition_subtraction.py`

**适用**: 所有加减法相关题型（一年级 10 以内加减法、连加减、加减混合等）

**例题**:
- `5 + 3 = （ ）`
- `1+6+19=（ ）`
- `96-23-45=（ ）`
- `49-19+27=（ ）`
- `17-（ ）= 2`
- `54+6+16（ ）74`
- `74-28+22（ ）75`

**说明**: 这是统一的加减法生成器，已替代原有的 `AdditionSubtractionGenerator` 和 `ConsecutiveAdditionSubtractionGenerator`。

**支持的题型配置**:

| 题型代码 | 说明 | 示例 |
|---------|------|------|
| `simple` | 简单加减 | `5 + 3 = （ ）` |
| `simple_fill` | 简单填空 | `5 + （ ） = 8` |
| `consecutive_add` | 连加 | `1+6+19=（ ）` |
| `consecutive_subtract` | 连减 | `96-23-45=（ ）` |
| `mixed_operation` | 加减混合 | `49-19+27=（ ）` |
| `missing_operand` | 减法填空 | `17-（ ）=2` |
| `compare_simple` | 简单运算比较 | `5+3（ ）8` |
| `compare_with_result` | 混合运算比较 | `74-28+22（ ）75` |
| `compare_mixed_operation` | 混合运算比较（确保有加有减） | `74-28+22（ ）75` |

**配置示例 - 简单加减**:
```json
{
    "question_complexity": ["simple"],
    "num": {"min": 1, "max": 10},
    "op": {"values": ["+", "-"]},
    "rules": ["ensure_positive"]
}
```

**配置示例 - 连加减**:
```json
{
    "question_complexity": ["consecutive_add", "consecutive_subtract"],
    "num": {"min": 1, "max": 10},
    "rules": ["ensure_positive", "result_within_10"]
}
```

**配置示例 - 综合型**:
```json
{
    "question_complexity": ["mixed_operation", "missing_operand", "compare_mixed_operation"],
    "num": {"min": 1, "max": 100},
    "rules": ["ensure_positive", "result_within_100"]
}
```

**核心逻辑**:
```python
# 读取题型复杂度配置（避免与 generate() 的 question_type 参数混淆）
question_complexity = template_config.get("question_complexity", ["simple"])

# 随机选择题型复杂度生成
q_type = random.choice(question_complexity)

if q_type == "simple":
    a = random.randint(num_min, num_max)
    b = random.randint(num_min, num_max)
    op = random.choice(op_values)

    if ensure_positive and op == "-" and a < b:
        continue

    stem = f"{a}{op}（    ）"

elif q_type == "consecutive_add":
    # 连加逻辑
    ...

elif q_type == "compare_mixed_operation":
    # 混合运算比较逻辑
    ...
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

### 5.5 MultiplicationDivisionComprehensiveGenerator - 乘除综合（统一生成器）

**文件**: `services/template/generators/multiplication_division_comprehensive.py`

**适用**: 小学全阶段乘除法练习（通过配置支持不同年级）

**例题**:
- 简单乘法：3 × 4 = （ ）
- 乘法填空：（ ）× 4 = 12
- 简单除法：12 ÷ 3 = （ ）
- 乘加混合：3 × 4 + 5 = （ ）
- 带余数除法：14 ÷ 3 = （ ）……（ ）

> **注意**: 原 `MultiplicationTableGenerator` 已删除，其功能由本生成器通过配置实现。
>
> 旧模板 `九九乘法表练习` 已迁移至本生成器，配置为：
> ```json
> {"factor": {"min": 1, "max": 9}, "question_complexity": ["simple_multiply"], "rules": ["result_within_81"]}
> ```

**配置参数**: 详见第 5.9 节

---

### 5.6 VolumeConversionGenerator - 体积单位换算

**文件**: `services/template/generators/volume_conversion.py`

**适用**: 五年级 长方体和正方体体积单位的换算

**例题**:
- 5 立方米 = （ ）立方分米
- 3000 立方厘米 = （ ）立方分米
- 8 升 = （ ）毫升

**配置示例**:
```json
{
    "volume": {"min": 1, "max": 100},
    "convert_types": [
        "m3_to_dm3", "dm3_to_cm3", "cm3_to_dm3", "dm3_to_m3",
        "l_to_ml", "ml_to_l", "dm3_to_l", "l_to_dm3"
    ]
}
```

**支持的换算类型**:

| 类型 | 说明 | 例题 |
|------|------|------|
| `m3_to_dm3` | 立方米→立方分米 | 5 立方米 = （ ）立方分米 |
| `dm3_to_m3` | 立方分米→立方米 | 1000 立方分米 = （ ）立方米 |
| `dm3_to_cm3` | 立方分米→立方厘米 | 3 立方分米 = （ ）立方厘米 |
| `cm3_to_dm3` | 立方厘米→立方分米 | 2000 立方厘米 = （ ）立方分米 |
| `l_to_ml` | 升→毫升 | 5 升 = （ ）毫升 |
| `ml_to_l` | 毫升→升 | 3000 毫升 = （ ）升 |
| `dm3_to_l` | 立方分米→升 | 8 立方分米 = （ ）升 |
| `l_to_dm3` | 升→立方分米 | 10 升 = （ ）立方分米 |
| `cm3_to_ml` | 立方厘米→毫升 | 25 立方厘米 = （ ）毫升 |
| `ml_to_cm3` | 毫升→立方厘米 | 50 毫升 = （ ）立方厘米 |
| `m3_to_l` | 立方米→升 | 2 立方米 = （ ）升 |
| `l_to_m3` | 升→立方米 | 5000 升 = （ ）立方米 |

**进率关系**:
- 1 立方米 = 1000 立方分米
- 1 立方分米 = 1000 立方厘米
- 1 升 = 1000 毫升
- 1 立方分米 = 1 升
- 1 立方厘米 = 1 毫升

---

### 5.7 FractionComparisonGenerator - 分数比大小

**文件**: `services/template/generators/fraction_comparison.py`

**适用**: 五年级 下学期 分数比大小

**例题**:
- $\frac{3}{4}$ （ ） $\frac{2}{3}$
- $\frac{2}{5}$ （ ） $\frac{3}{5}$
- $\frac{2}{3}$ （ ） $\frac{2}{5}$

**配置示例**:
```json
{
    "denominator": {"min": 2, "max": 12},
    "numerator": {"min": 1},
    "compare_types": ["common_denominator", "common_numerator", "different"],
    "rules": ["ensure_different", "ensure_proper_fraction"]
}
```

**支持的比较类型**:

| 类型 | 说明 | 例题 |
|------|------|------|
| `common_denominator` | 同分母比较 | $\frac{2}{5}$ （ ） $\frac{3}{5}$ |
| `common_numerator` | 同分子比较 | $\frac{2}{3}$ （ ） $\frac{2}{5}$ |
| `different` | 异分母比较 | $\frac{3}{4}$ （ ） $\frac{2}{3}$ |

**支持的规则**:
- `ensure_different`: 确保两个分数不相等
- `ensure_proper_fraction`: 确保是真分数（分子 < 分母）

**核心逻辑**:
```python
# 异分母比较：交叉相乘判断大小
if numerator1 * denominator2 > numerator2 * denominator1:
    # 第一个分数大
```

---

### 5.8 LengthComparisonGenerator - 长度单位换算

**文件**: `services/template/generators/length_comparison.py`

**适用**: 一年级 下学期 长度单位换算（沪教版）

**例题**:
- 7m = （ ）cm
- 500cm = （ ）m
- 1dm = （ ）cm
- 30cm = （ ）dm
- 5m = （ ）dm
- 40dm = （ ）m
- 2m50cm = （ ）cm
- 3m5dm = （ ）dm

**配置示例**:
```json
{
    "value": {"min": 1, "max": 100},
    "convert_types": [
        "m_to_cm", "cm_to_m",
        "dm_to_cm", "cm_to_dm",
        "m_to_dm", "dm_to_m",
        "m_cm_to_cm", "m_dm_to_dm"
    ]
}
```

**支持的换算类型**:

| 类型 | 说明 | 例题 |
|------|------|------|
| `m_to_cm` | 米→厘米 | 7m = （ ）cm |
| `cm_to_m` | 厘米→米 | 500cm = （ ）m |
| `dm_to_cm` | 分米→厘米 | 1dm = （ ）cm |
| `cm_to_dm` | 厘米→分米 | 30cm = （ ）dm |
| `m_to_dm` | 米→分米 | 5m = （ ）dm |
| `dm_to_m` | 分米→米 | 40dm = （ ）m |
| `m_cm_to_cm` | 米 + 厘米→厘米 | 2m50cm = （ ）cm |
| `m_dm_to_dm` | 米 + 分米→分米 | 3m5dm = （ ）dm |

**进率关系**:
- 1 米 (m) = 100 厘米 (cm)
- 1 分米 (dm) = 10 厘米 (cm)
- 1 米 (m) = 10 分米 (dm)

---

### 5.9 MultiplicationDivisionComprehensiveGenerator - 乘除综合（全小学阶段通用）

**文件**: `services/template/generators/multiplication_division_comprehensive.py`

**设计理念**: 生成器本身不限制年级，所有范围通过 configuration 控制。后期添加新模板只需 SQL 配置，无需修改代码。

**适用**: 小学全阶段（通过配置适应不同年级）

**例题**:
- 3 × 4 = （ ）
- 12 ÷ 3 = （ ）
- （ ）× 4 = 12
- 12 ÷ （ ） = 4
- 3 × 4 + 5 = （ ）
- 12 ÷ 3 - 2 = （ ）
- 14 ÷ 3 = （ ）……（ ）
- 3 × 4 （ ） 10

**配置示例（二年级 - 表内乘除）**:
```json
{
    "factor": {"min": 1, "max": 9},
    "divisor": {"min": 1, "max": 9},
    "dividend": {"min": 1, "max": 81},
    "extra": {"min": 1, "max": 20},
    "question_complexity": [
        "simple_multiply",
        "simple_divide",
        "multiply_fill_first",
        "multiply_fill_second",
        "divide_fill_dividend",
        "divide_fill_divisor",
        "multiply_add",
        "multiply_subtract",
        "divide_add",
        "divide_subtract",
        "remainder_division",
        "compare_multiply",
        "compare_division"
    ],
    "rules": ["ensure_divisible", "ensure_positive", "result_within_100"]
}
```

**支持的题型**:

| 题型 | 说明 | 例题 |
|------|------|------|
| `simple_multiply` | 简单乘法 | 3 × 4 = （ ） |
| `simple_divide` | 简单除法 | 12 ÷ 3 = （ ） |
| `multiply_fill_first` | 乘法填空（求第一个因子） | （ ）× 4 = 12 |
| `multiply_fill_second` | 乘法填空（求第二个因子） | 3 × （ ） = 12 |
| `divide_fill_dividend` | 除法填空（求被除数） | （ ）÷ 3 = 4 |
| `divide_fill_divisor` | 除法填空（求除数） | 12 ÷ （ ） = 4 |
| `multiply_add` | 乘加混合 | 3 × 4 + 5 = （ ） |
| `multiply_subtract` | 乘减混合 | 3 × 4 - 5 = （ ） |
| `divide_add` | 除加混合 | 12 ÷ 3 + 5 = （ ） |
| `divide_subtract` | 除减混合 | 12 ÷ 3 - 2 = （ ） |
| `remainder_division` | 带余数除法 | 14 ÷ 3 = （ ）……（ ） |
| `compare_multiply` | 乘法比较 | 3 × 4 （ ） 10 |
| `compare_division` | 除法比较 | 12 ÷ 3 （ ） 4 |
| `multiply_chain` | 连乘 | 2 × 3 × 4 = （ ） |
| `mixed_compare` | 混合运算比较 | 3 × 4 + 2 （ ） 15 |

**支持的规则**:
- `ensure_divisible`: 确保除法能整除
- `ensure_positive`: 确保结果不为负
- `ensure_remainder`: 确保有余数（用于带余数除法）
- `ensure_no_remainder`: 确保无余数
- `ensure_different`: 确保两个因子不同
- `result_within_20`: 确保结果 ≤ 20
- `result_within_100`: 确保结果 ≤ 100

**配置参数说明**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `factor.min` | int | 1 | 乘法因子最小值 |
| `factor.max` | int | 9 | 乘法因子最大值 |
| `fixed_first_factor` | int | null | 固定第一个因子（用于乘法口诀专项，如设为 7 则只生成 7 的乘法） |
| `divisor.min` | int | 1 | 除数最小值 |
| `divisor.max` | int | 9 | 除数最大值 |
| `dividend.min` | int | 1 | 被除数最小值 |
| `dividend.max` | int | 81 | 被除数最大值 |
| `quotient.min` | int | 1 | 商最小值 |
| `quotient.max` | int | 9 | 商最大值 |
| `extra.min` | int | 1 | 混合运算中加/减数最小值 |
| `extra.max` | int | 20 | 混合运算中加/减数最大值 |
| `chain_factors` | int | 3 | 连乘因子数量 |
| `compare_offset.min` | int | 1 | 比较题偏移最小值 |
| `compare_offset.max` | int | 10 | 比较题偏移最大值 |
| `knowledge_points` | array | 自动判断 | 自定义知识点列表 |
| `result_within` | int | null | 自定义结果上限 |

**不同年级配置示例**:

```sql
-- ============================================
-- 示例 1：二年级 表内乘除（只练习 1-5 的乘法）
-- ============================================
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version, question_type,
    template_pattern, variables_config, example,
    generator_module, sort_order, is_active
) VALUES (
    '乘除基础 - 1 至 5 的乘法',
    'math', 'grade2', 'upper', '沪教版', 'ORAL_CALCULATION',
    '表内乘法基础练习（1-5）',
    '{"factor": {"min": 1, "max": 5}, "divisor": {"min": 1, "max": 5}, "dividend": {"min": 1, "max": 25}, "question_complexity": ["simple_multiply"], "rules": ["result_within_25"]}',
    '3 × 4 = （ ）',
    'multiplication_division_comprehensive', 1, 1
);

-- ============================================
-- 示例 2：三年级 多位数乘法（整十/整百）
-- ============================================
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version, question_type,
    template_pattern, variables_config, example,
    generator_module, sort_order, is_active
) VALUES (
    '多位数乘法 - 整十整百',
    'math', 'grade3', 'upper', '人教版', 'ORAL_CALCULATION',
    '整十/整百数乘法',
    '{"factor": {"min": 10, "max": 90, "step": 10}, "divisor": {"min": 1, "max": 9}, "question_complexity": ["simple_multiply", "multiply_chain"], "rules": ["result_within_1000"]}',
    '30 × 4 = （ ）、200 × 3 = （ ）',
    'multiplication_division_comprehensive', 2, 1
);

-- ============================================
-- 示例 3：四年级 除数是两位数的除法
-- ============================================
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version, question_type,
    template_pattern, variables_config, example,
    generator_module, sort_order, is_active
) VALUES (
    '除数是两位数的除法',
    'math', 'grade4', 'upper', '人教版', 'ORAL_CALCULATION',
    '除数是两位数的整除练习',
    '{"divisor": {"min": 10, "max": 99}, "quotient": {"min": 1, "max": 20}, "dividend": {"min": 100, "max": 1000}, "question_complexity": ["simple_divide", "divide_fill_dividend"], "rules": ["ensure_divisible", "result_within_100"]}',
    '120 ÷ 12 = （ ）、（ ）÷ 15 = 8',
    'multiplication_division_comprehensive', 3, 1
);

-- ============================================
-- 扩展示例 - 新增模板只需 SQL（生成器无需修改）
-- ============================================
-- 场景：添加一个"乘法口诀专项练习 - 只练 7 的乘法"
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version, question_type,
    template_pattern, variables_config, example,
    generator_module, sort_order, is_active
) VALUES (
    '乘法口诀专项 - 7 的乘法',
    'math', 'grade2', 'upper', '沪教版', 'ORAL_CALCULATION',
    '7 的乘法口诀专项练习',
    '{"factor": {"min": 1, "max": 9}, "fixed_first_factor": 7, "question_complexity": ["simple_multiply"], "rules": ["result_within_81"], "knowledge_points": ["7 的乘法口诀"]}',
    '7 × 1 = （ ）、7 × 2 = （ ）...',
    'multiplication_division_comprehensive', 10, 1
);

-- 场景：添加一个"乘法口诀专项 - 只练 9 的乘法"
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version, question_type,
    template_pattern, variables_config, example,
    generator_module, sort_order, is_active
) VALUES (
    '乘法口诀专项 - 9 的乘法',
    'math', 'grade2', 'upper', '沪教版', 'ORAL_CALCULATION',
    '9 的乘法口诀专项练习',
    '{"factor": {"min": 1, "max": 9}, "fixed_first_factor": 9, "question_complexity": ["simple_multiply"], "rules": ["result_within_81"], "knowledge_points": ["9 的乘法口诀"]}',
    '9 × 1 = （ ）、9 × 2 = （ ）...',
    'multiplication_division_comprehensive', 11, 1
);
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

## 8. 常见问题

### Q1: 生成器返回空列表怎么办？

**原因**: 配置范围太小或规则太严格，导致无法生成有效题目

**解决**:
1. 检查 `template_config` 配置是否合理
2. 增大数值范围
3. 放宽规则约束
4. 生成器会自动跳过无法生成的题目，不会抛出异常

### Q2: 如何添加新的规则约束？

**步骤**:
1. 在 `backend/config/template_rules.py` 的相应规则字典中添加规则名
2. 在生成器的 `generate` 方法中实现规则检查逻辑

```python
# 示例：添加 ensure_even 规则（确保偶数）
# 1. 在 template_rules.py 中添加:
NUMERIC_PROPERTY_RULES = {
    # ... 现有规则
    "ensure_even": "确保是偶数",
}

# 2. 在生成器中使用:
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
    ├── README.md               # 生成器使用文档
    ├── compare_number.py       # 比大小生成器
    ├── mixed_addition_subtraction.py  # 加减法统一生成器 ⭐
    ├── currency_conversion.py  # 人民币换算生成器
    ├── volume_conversion.py    # 体积单位换算生成器
    ├── fraction_comparison.py  # 分数比大小生成器
    ├── length_comparison.py    # 长度单位换算生成器 ⭐
    └── multiplication_division_comprehensive.py  # 乘除综合生成器 ⭐
```

```
backend/config/
└── template_rules.py           # 规则配置文件 ⭐
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
├── 001_add_questions_table.sql       # 题目表
├── 002_add_question_templates.sql    # 模板系统
├── 005_add_volume_conversion_template.sql     # 体积换算模板
├── 006_add_fraction_comparison_template.sql   # 分数比大小模板
├── 007_add_bainaineishu_comparison_template.sql  # 百以内数比大小模板
├── 008_add_currency_recognition_template.sql   # 人民币认识模板
├── 009_add_mixed_addition_subtraction_template.sql  # 连加连减及加减综合模板
├── 010_unify_arithmetic_generators.sql         # 统一加减法生成器迁移
├── 011_rename_question_types_to_complexity.sql
├── 012_add_question_types_table.sql
├── 013_add_length_comparison_template.sql      # 长度单位换算模板 ⭐
├── 014_add_multiplication_division_comprehensive_template.sql  # 乘除综合模板 ⭐
└── 015_add_multiplication_practice_template.sql  # 乘法口诀练习模板（替代原 multiplication_table）
```

```
提示词示例：
添加一个一年级 下学期 沪教版  题目类型为填空 `百以内数的大小比较` 的后台模板  生成的题目数字都要大于20  

线上执行sql :  sqlite3 /path/to/your/tixiaobao.db < backend/db/migrations/007_ad  d_bainaineishu_comparison_template.sql
```
