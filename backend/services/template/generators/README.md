# 模板生成器索引

> 本文档列出所有已注册的模板生成器，帮助快速复用现有生成器添加新模板。

## 快速查找表

| 生成器模块名 | 功能描述 | 适用场景 | 关键配置参数 |
|-------------|---------|---------|-------------|
| `compare_number` | 数字比大小 | 两个数比较大小 | `a.min/max`, `b.min/max`, `ensure_different` |
| `mixed_addition_subtraction` ⭐ | **统一加减法生成器** | 所有加减法题型 | `question_types`, `num.min/max`, `result_within_X` |
| `currency_conversion` | 元角分换算 | 人民币单位换算 | `yuan/jiao/fen.max`, `convert_types` |
| `volume_conversion` | 体积单位换算 | 立方米/立方分米/立方厘米/升/毫升 | `conversion_types` (12 种) |
| `fraction_comparison` | 分数比大小 |  LaTeX 分数格式比较 | `denominator.min/max`, `compare_types` |
| `multiplication_table` | 九九乘法表 | 乘法口诀练习 | `factors.min/max` |

> **注意**: `mixed_addition_subtraction` 是统一的加减法生成器，已覆盖原有的 `addition_subtraction` 和 `consecutive_addition_subtraction` 功能。旧模板已通过迁移 010 更新配置。

---

## 生成器详情

### 1. CompareNumberGenerator

**模块名**: `compare_number`
**文件**: `compare_number.py`

**功能**: 生成两个数字比大小的题目

**题型**: `FILL_BLANK`

**输出格式**: `{a}（ ）{b}`

**配置参数**:
```json
{
  "a": {"min": 1, "max": 10},
  "b": {"min": 1, "max": 10},
  "rules": ["ensure_different"]
}
```

**适用模板**:
- 一年级 10 以内的数比一比
- 百以内数的大小比较

---

### 2. MixedAdditionSubtractionGenerator ⭐ 统一加减法生成器

**模块名**: `mixed_addition_subtraction`
**文件**: `mixed_addition_subtraction.py`

**功能**: 统一的加减法生成器，支持所有加减法相关题型

**题型**: `CALCULATION` 或 `FILL_BLANK`

**支持的题型** (8 种):

| 题型代码 | 说明 | 示例 | 适用配置 |
|---------|------|------|---------|
| `simple` | 简单加减 | `5 + 3 = （ ）` | 替代原 `addition_subtraction` |
| `simple_fill` | 简单填空 | `5 + （ ） = 8` | 加法/减法填空 |
| `consecutive_add` | 连加 | `1+6+19=（ ）` | 替代原 `consecutive_addition_subtraction` |
| `consecutive_subtract` | 连减 | `96-23-45=（ ）` | 替代原 `consecutive_addition_subtraction` |
| `mixed_operation` | 加减混合 | `49-19+27=（ ）` | 两运算符混合 |
| `missing_operand` | 减法填空 | `17-（ ）=2` | 逆向思维 |
| `compare_simple` | 简单运算比较 | `5+3（ ）8` | 单运算符比较 |
| `compare_with_result` | 混合运算比较 | `74-28+22（ ）75` | 两运算符比较 |
| `compare_mixed_operation` | 混合运算比较 | `74-28+22（ ）75` | 确保有加有减 |

**配置参数 - 简单加减** (替代 `addition_subtraction`):
```json
{
  "question_types": ["simple"],
  "num": {"min": 1, "max": 10},
  "op": {"values": ["+", "-"]},
  "rules": ["ensure_positive"]
}
```

**配置参数 - 连加减** (替代 `consecutive_addition_subtraction`):
```json
{
  "question_types": ["consecutive_add", "consecutive_subtract"],
  "a": {"min": 1, "max": 10},
  "b": {"min": 1, "max": 10},
  "c": {"min": 1, "max": 10},
  "rules": ["ensure_positive", "result_within_10"]
}
```

**配置参数 - 综合型**:
```json
{
  "question_types": ["mixed_operation", "missing_operand", "compare_mixed_operation"],
  "num": {"min": 1, "max": 100},
  "rules": ["ensure_positive", "result_within_100"]
}
```

**适用模板**:
- 一年级 10 以内的加减法 (已迁移)
- 一年级 10 以内连加减法 (已迁移)
- 连加、连减及加减综合

---

### 3. CurrencyConversionGenerator

**模块名**: `currency_conversion`
**文件**: `currency_conversion.py`

**功能**: 人民币元角分单位换算

**题型**: `CALCULATION`

**支持的换算类型**:
| 类型代码 | 说明 | 示例 |
|---------|------|------|
| `yuan_to_jiao` | 元→角 | `5 元 = （ ）角` |
| `jiao_to_yuan` | 角→元 | `60 角 = （ ）元` |
| `jiao_to_fen` | 角→分 | `5 角 = （ ）分` |
| `fen_to_jiao` | 分→角 | `50 分 = （ ）角` |
| `yuan_to_fen` | 元→分 | `5 元 = （ ）分` |
| `fen_to_yuan` | 分→元 | `100 分 = （ ）元` |
| `yuan_jiao_to_jiao` | 元 + 角→角 | `3 元 5 角 = （ ）角` |
| `yuan_fen_to_fen` | 元 + 分→分 | `54 元 50 分 = （ ）分` |
| `yuan_jiao_fen_to_fen` | 元 + 角 + 分→分 | `3 元 5 角 20 分 = （ ）分` |

**配置参数**:
```json
{
  "yuan": {"max": 50},
  "jiao": {"max": 50},
  "fen": {"max": 50},
  "convert_types": ["yuan_to_jiao", "jiao_to_fen", "yuan_jiao_to_jiao"]
}
```

**适用模板**:
- 认识人民币 - 元角分换算
- 人民币认识

---

### 4. VolumeConversionGenerator

**模块名**: `volume_conversion`
**文件**: `volume_conversion.py`

**功能**: 体积/容积单位换算

**题型**: `CALCULATION`

**支持的换算类型** (12 种):
| 类型代码 | 说明 | 进率 |
|---------|------|------|
| `m3_to_dm3` | 立方米→立方分米 | ×1000 |
| `dm3_to_cm3` | 立方分米→立方厘米 | ×1000 |
| `cm3_to_dm3` | 立方厘米→立方分米 | ÷1000 |
| `dm3_to_m3` | 立方分米→立方米 | ÷1000 |
| `l_to_ml` | 升→毫升 | ×1000 |
| `ml_to_l` | 毫升→升 | ÷1000 |
| `dm3_to_l` | 立方分米→升 | 1:1 |
| `l_to_dm3` | 升→立方分米 | 1:1 |
| `cm3_to_ml` | 立方厘米→毫升 | 1:1 |
| `ml_to_cm3` | 毫升→立方厘米 | 1:1 |
| `m3_to_l` | 立方米→升 | ×1000 |
| `l_to_m3` | 升→立方米 | ÷1000 |

**配置参数**:
```json
{
  "conversion_types": ["m3_to_dm3", "dm3_to_cm3", "l_to_ml"],
  "integer_result": true
}
```

**适用模板**:
- 长方体和正方体体积单位的换算

---

### 5. FractionComparisonGenerator

**模块名**: `fraction_comparison`
**文件**: `fraction_comparison.py`

**功能**: 生成 LaTeX 分数格式的比较题目

**题型**: `FILL_BLANK`

**输出格式**: `$\frac{a}{b}$ （ ） $\frac{c}{d}$`

**支持的比较类型**:
| 类型代码 | 说明 | 示例 |
|---------|------|------|
| `common_denominator` | 同分母 | $\frac{3}{7}$ （ ） $\frac{5}{7}$ |
| `common_numerator` | 同分子 | $\frac{2}{9}$ （ ） $\frac{2}{5}$ |
| `different` | 异分母 | $\frac{3}{4}$ （ ） $\frac{2}{3}$ |

**配置参数**:
```json
{
  "denominator": {"min": 2, "max": 12},
  "numerator": {"min": 1},
  "compare_types": ["common_denominator", "different"],
  "rules": ["ensure_different", "ensure_proper_fraction"]
}
```

**适用模板**:
- 分数比大小

---

### 6. MultiplicationTableGenerator

**模块名**: `multiplication_table`
**文件**: `multiplication_table.py`

**功能**: 九九乘法表练习

**题型**: `CALCULATION`

**输出格式**: `{a} × {b} = （ ）`

**配置参数**:
```json
{
  "factors": {"min": 1, "max": 9}
}
```

**适用模板**:
- 九九乘法表练习

---

## 规则列表

所有生成器支持的全局规则：

| 规则名 | 说明 |
|-------|------|
| `ensure_different` | 确保两个数不同 |
| `ensure_positive` | 确保结果为正数 |
| `ensure_non_zero` | 确保结果非零 |
| `result_within_10` | 结果在 10 以内 |
| `result_within_100` | 结果在 100 以内 |
| `ensure_integer_result` | 确保结果为整数 |

---

## 添加新模板的步骤

1. **选择合适的生成器** - 根据上表选择功能匹配的生成器
2. **编写 SQL 迁移** - 在 `db/migrations/` 下创建新的 SQL 文件
3. **配置变量** - 根据生成器文档设置 `variables_config`
4. **执行迁移** - 运行 SQL 插入新模板记录

### SQL 模板

```sql
INSERT INTO question_templates (
    name, subject, grade, semester, textbook_version,
    question_type, template_pattern, variables_config,
    example, generator_module, sort_order, is_active
) VALUES (
    '模板名称',
    'math',
    'grade1',
    'lower',
    '人教版',
    'FILL_BLANK',
    '模板模式描述',
    '{"a": {"min": 1, "max": 10}}',
    '示例题目',
    'generator_module_name',
    1,
    1
);
```

---

## 何时需要新建生成器？

当现有生成器无法满足需求时：

1. **新的题型** - 如判断题、选择题（现有主要是填空和计算）
2. **新的学科** - 如语文、英语（现有主要是数学）
3. **新的数学概念** - 如小数、百分数、负数、方程
4. **特殊的生成逻辑** - 现有生成器无法通过配置实现的

### 新建生成器步骤

1. 在 `backend/services/template/generators/` 创建新文件
2. 继承 `TemplateGenerator` 基类
3. 实现 `generate()` 方法
4. 在 `__init__.py` 中注册
5. 更新本文档
