# 模板生成器索引

> 本文档列出所有已注册的模板生成器，帮助快速复用现有生成器添加新模板。

## 快速查找表

| 生成器模块名 | 功能描述 | 适用场景 | 关键配置参数 |
|-------------|---------|---------|-------------|
| `mixed_addition_subtraction` ⭐ | **统一加减法生成器** | 所有加减法题型及比大小 | `question_complexity`, `num.min/max`, `result_within_X`, `q_type` |
| `fraction_arithmetic_comparison` ⭐ | **分数加减乘除比较综合** | 分数所有运算及比较 | `denominator`, `numerator`, `question_complexity`, `q_type` |
| `fraction_comparison` | 分数比大小 |  LaTeX 分数格式比较 | `denominator.min/max`, `compare_types` |
| `currency_conversion` | 元角分换算 | 人民币单位换算 | `yuan/jiao/fen.max`, `convert_types` |
| `volume_conversion` | 体积单位换算 | 立方米/立方分米/立方厘米/升/毫升 | `conversion_types` (12 种) |

> **注意**:
> 1. `mixed_addition_subtraction` 是统一的加减法生成器，已覆盖原有的 `addition_subtraction`、`consecutive_addition_subtraction` 和 `compare_number` 功能。
> 2. `multiplication_table` 生成器已删除，其功能由 `multiplication_division_comprehensive` 统一支持（通过 `question_complexity: ["simple_multiply"]` 配置实现）。
> 3. `fraction_arithmetic_comparison` 是分数综合生成器，支持加减乘除、混合运算、比较大小、填空、倒数、带分数等 30+ 种题型。

---

## 生成器详情

### 1. MixedAdditionSubtractionGenerator ⭐ 统一加减法生成器

**模块名**: `mixed_addition_subtraction`
**文件**: `mixed_addition_subtraction.py`

**功能**: 统一的加减法生成器，支持所有加减法及比大小相关题型

**题型**: `CALCULATION` 或 `FILL_BLANK` 或 `ORAL_CALCULATION`

**支持的题型** (9 种):

| 题型代码 | 说明 | 示例 | 适用配置 |
|---------|------|------|---------|
| `simple` | 简单加减 | `5 + 3 = （ ）` | 基础加减法 |
| `simple_fill` | 简单填空 | `5 + （ ） = 8` | 加法/减法填空 |
| `consecutive_add` | 连加 | `1+6+19=（ ）` | 连加练习 |
| `consecutive_subtract` | 连减 | `96-23-45=（ ）` | 连减练习 |
| `mixed_operation` | 加减混合 | `49-19+27=（ ）` | 两运算符混合 |
| `missing_operand` | 减法填空 | `17-（ ）=2` | 逆向思维 |
| `compare_simple` | 简单比较 | `5（ ）8` | 两数比大小 |
| `compare_with_result` | 运算后比较 | `74-28+22（ ）75` | 混合运算比较 |
| `compare_mixed_operation` | 混合运算比较 | `74-28+22（ ）75` | 确保有加有减 |

**配置参数 - 简单加减**:
```json
{
  "question_complexity": ["simple"],
  "num": {"min": 1, "max": 10},
  "op": {"values": ["+", "-"]},
  "rules": ["ensure_positive"]
}
```

**配置参数 - 连加减**:
```json
{
  "question_complexity": ["consecutive_add", "consecutive_subtract"],
  "a": {"min": 1, "max": 10},
  "b": {"min": 1, "max": 10},
  "c": {"min": 1, "max": 10},
  "rules": ["ensure_positive", "result_within_10"]
}
```

**配置参数 - 比大小题目**:
```json
{
  "question_complexity": ["compare_simple"],
  "num": {"min": 1, "max": 10},
  "rules": ["ensure_different"],
  "q_type": {
    "compare_simple": "circle"
  }
}
```

**配置参数 - 混合题型（不同题型使用不同 answer_style）**:
```json
{
  "question_complexity": ["simple", "compare_simple", "compare_with_result"],
  "num": {"min": 1, "max": 20},
  "q_type": {
    "compare_simple": "circle",
    "compare_with_result": "circle"
  }
}
```
> **说明**: `q_type` 用于为特定题型单独设置 `answer_style`，优先级高于 `rendering_config` 中的配置。

**配置参数 - 综合型**:
```json
{
  "question_complexity": ["mixed_operation", "missing_operand", "compare_mixed_operation"],
  "num": {"min": 1, "max": 100},
  "rules": ["ensure_positive", "result_within_100"]
}
```

**适用模板**:
- 一年级 10 以内的加减法
- 一年级 10 以内连加减法
- 一年级 10 以内的数比一比
- 百以内数的大小比较
- 连加、连减及加减综合

**特殊配置说明**:
- `q_type`: 用于设置特定题型的 answer_style，例如 `{"compare_simple": "circle"}` 会让比大小题目使用圆圈作答样式

---

### 2. FractionArithmeticComparisonGenerator ⭐ 分数加减乘除比较综合

**模块名**: `fraction_arithmetic_comparison`
**文件**: `fraction_arithmetic_comparison.py`

**功能**: 分数加减乘除比较大小综合生成器，支持小学 3-6 年级所有分数相关题型

**题型**: `CALCULATION` 或 `FILL_BLANK`

**支持的题型** (30+ 种):

#### 加减法 (4 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `same_denominator_add` | 同分母分数加法 | $1/5 + 2/5 = [BLANK]$ | 三年级 |
| `same_denominator_subtract` | 同分母分数减法 | $3/5 - 1/5 = [BLANK]$ | 三年级 |
| `different_denominator_add` | 异分母分数加法 | $1/3 + 1/4 = [BLANK]$ | 五年级 |
| `different_denominator_subtract` | 异分母分数减法 | $3/4 - 1/3 = [BLANK]$ | 五年级 |

#### 乘法 (3 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `multiply_fraction_int` | 分数乘整数 | $2/3 \times 4 = [BLANK]$ | 五年级 |
| `multiply_fraction_fraction` | 分数乘分数 | $1/2 \times 2/3 = [BLANK]$ | 六年级 |
| `multiply_mixed` | 带分数乘法 | $1\frac{1}{2} \times 2/3 = [BLANK]$ | 六年级 |

#### 除法 (3 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `divide_fraction_int` | 分数除整数 | $3/4 \div 2 = [BLANK]$ | 五年级 |
| `divide_fraction_fraction` | 分数除分数 | $1/2 \div 1/4 = [BLANK]$ | 六年级 |
| `divide_mixed` | 带分数除法 | $1\frac{1}{2} \div 1/2 = [BLANK]$ | 六年级 |

#### 混合运算 (6 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `mixed_add_subtract` | 分数加减混合 | $1/2 + 1/3 - 1/6 = [BLANK]$ | 五年级 |
| `multiply_divide_mixed` | 分数乘除混合 | $1/2 \times 3/4 \div 1/8 = [BLANK]$ | 六年级 |
| `multiply_add` | 分数乘加 | $1/2 \times 3 + 1/4 = [BLANK]$ | 六年级 |
| `multiply_subtract` | 分数乘减 | $3/4 \times 2 - 1/2 = [BLANK]$ | 六年级 |
| `divide_add` | 分数除加 | $3/4 \div 2 + 1/8 = [BLANK]$ | 六年级 |
| `divide_subtract` | 分数除减 | $3/4 \div 2 - 1/8 = [BLANK]$ | 六年级 |

#### 比较大小 (5 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `compare_same_denominator` | 同分母比较 | $2/5 [BLANK] 3/5$ | 三年级 |
| `compare_same_numerator` | 同分子比较 | $2/3 [BLANK] 2/5$ | 四年级 |
| `compare_different` | 异分母比较 | $3/4 [BLANK] 2/3$ | 五年级 |
| `compare_with_result` | 运算后比较 | $1/2 + 1/3 [BLANK] 5/6$ | 五年级 |
| `compare_multiply` | 乘法结果比较 | $1/2 \times 3 [BLANK] 2$ | 五年级 |

#### 填空题 (3 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `fill_blank_numerator` | 填分子 | $[BLANK]/5 + 2/5 = 4/5$ | 五年级 |
| `fill_blank_denominator` | 填分母 | $1/[BLANK] + 1/5 = 2/5$ | 五年级 |
| `fill_blank_operation` | 填运算符 | $1/2 [BLANK] 1/3 = 5/6$ | 六年级 |

#### 其他 (3 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `reciprocal` | 求倒数 | $3/4 的倒数是 [BLANK]$ | 六年级 |
| `mixed_number_add` | 带分数加法 | $1\frac{1}{2} + 2\frac{1}{3} = [BLANK]$ | 六年级 |
| `mixed_number_subtract` | 带分数减法 | $3\frac{3}{4} - 1\frac{1}{2} = [BLANK]$ | 六年级 |

**配置参数 - 三年级 (同分母分数)**:
```json
{
  "denominator": {"min": 2, "max": 10},
  "numerator": {"min": 1},
  "question_complexity": ["same_denominator_add", "same_denominator_subtract"],
  "rules": ["ensure_proper_fraction"]
}
```

**配置参数 - 五年级 (异分母分数)**:
```json
{
  "denominator": {"min": 2, "max": 20},
  "numerator": {"min": 1},
  "question_complexity": ["different_denominator_add", "different_denominator_subtract", "multiply_fraction_int"],
  "rules": ["ensure_simplest_result"]
}
```

**配置参数 - 六年级 (综合)**:
```json
{
  "denominator": {"min": 2, "max": 15},
  "numerator": {"min": 1},
  "whole": {"min": 1, "max": 5},
  "question_complexity": [
    "multiply_fraction_fraction", "divide_fraction_fraction",
    "multiply_divide_mixed", "mixed_number_add"
  ],
  "rules": ["ensure_simplest_result", "ensure_proper_fraction"]
}
```

**配置参数 - 比较大小专项**:
```json
{
  "denominator": {"min": 2, "max": 12},
  "numerator": {"min": 1},
  "question_complexity": [
    "compare_same_denominator", "compare_same_numerator", "compare_different"
  ],
  "q_type": {
    "compare_same_denominator": "circle",
    "compare_different": "circle"
  }
}
```

**适用模板**:
- 三年级同分母分数加减法
- 五年级异分母分数加减法
- 五年级分数乘法
- 六年级分数除法
- 六年级分数混合运算
- 分数比大小专项练习

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

### 6. FractionComparisonGenerator (续)

**适用模板**:
- 分数比大小

---

## 规则列表

> **重要**: 规则配置已移至 `backend/config/template_rules.py`，无需修改代码即可添加新规则。
>
> 未来如需添加新规则（如 `result_within_50`），只需在配置文件中添加，无需修改模型文件。

所有生成器支持的全局规则：

| 规则名 | 说明 | 适用场景 |
|-------|------|----------|
| `ensure_different` | 确保两个数不同 | 比大小题目 |
| `ensure_positive` | 确保结果为正数（含中间结果） | 减法、连加减 |
| `ensure_non_zero` | 确保结果非零 | 除法、分母 |
| `ensure_even` | 确保是偶数 | 整除练习 |
| `ensure_odd` | 确保是奇数 | 特殊数练习 |
| `ensure_prime` | 确保是质数 | 质数练习 |
| `ensure_coprime` | 确保互质 | 分数约分 |
| `ensure_divisible` | 确保除法能整除 | 除法练习 |
| `ensure_borrowing` | 确保减法需要借位 | 借位减法 |
| `ensure_carrying` | 确保加法需要进位 | 进位加法 |
| `ensure_proper_fraction` | 确保是真分数（分子 < 分母） | 分数基础 |
| `ensure_simplest_form` | 确保是最简分数 | 约分练习 |
| `ensure_realistic_value` | 确保是实际存在的值 | 应用题、几何 |
| `ensure_integer_result` | 确保计算结果为整数 | 单位换算 |
| `ensure_unique_stem` | 确保题干不重复（默认开启） | 所有题型 |
| `result_within_10` | 结果在 10 以内 | 一年级 |
| `result_within_20` | 结果在 20 以内 | 二年级 |
| `result_within_100` | 结果在 100 以内 | 三年级 |
| `result_within_1000` | 结果在 1000 以内 | 四年级 |

### 按年级分类的规则

| 年级 | 可用规则 |
|------|----------|
| 一年级 | `result_within_10`, `ensure_positive`, `ensure_different`, `ensure_non_zero` |
| 二年级 | `result_within_20`, `ensure_positive`, `ensure_different`, `ensure_even`, `ensure_odd` |
| 三年级 | `result_within_100`, `ensure_divisible`, `ensure_borrowing`, `ensure_carrying` |
| 四年级 | `result_within_1000`, `ensure_prime`, `ensure_coprime`, `ensure_simplest_form` |

---

## 添加新模板的步骤

### 快速添加模板（复用现有生成器）

1. **选择合适的生成器** - 根据上表选择功能匹配的生成器
2. **编写 SQL 迁移** - 在 `db/migrations/` 下创建新的 SQL 文件
3. **配置变量** - 根据生成器文档设置 `variables_config`
4. **执行迁移** - 运行 SQL 插入新模板记录
5. **添加规则**（如需要） - 在 `backend/config/template_rules.py` 中添加新规则名

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
    '沪教版',
    'FILL_BLANK',
    '模板模式描述',
    '{"num": {"min": 1, "max": 10}, "rules": ["ensure_positive"]}',
    '示例题目',
    'generator_module_name',
    1,
    1
);
```

### 添加新规则（如需要）

如果现有规则不够用（例如需要 `result_within_50`），编辑 `backend/config/template_rules.py`：

```python
RESULT_WITHIN_RULES = {
    # ... 现有规则
    "result_within_50": "确保结果 ≤ 50",  # 新增规则
}
```

然后在生成器代码中使用：

```python
result_within_50 = "result_within_50" in template_config.get("rules", [])
if result_within_50 and result > 50:
    continue
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

---

## 配置化设计

### 为什么不写死规则？

早期版本将规则定义在 `question_template.py` 中，但这样存在以下问题：

- **扩展性差**: 每次添加新规则（如 `result_within_50`）都需要修改模型文件
- **违反开闭原则**: 模型文件频繁变动，增加维护成本
- **部署风险**: 简单的配置变更需要代码发布

### 现在的做法

```
backend/config/template_rules.py  # 规则配置文件
├── RESULT_WITHIN_RULES      # 数值范围规则
├── NUMERIC_PROPERTY_RULES   # 数值属性规则
├── OPERATION_RULES          # 运算规则
├── FRACTION_RULES           # 分数规则
├── GEOMETRY_RULES           # 几何规则
└── UNIQUENESS_RULES         # 去重规则
```

**未来扩展方向**:
- 通过数据库表 `generator_rules` 管理规则，实现后台页面动态配置
- 支持按年级过滤可用规则
- 规则说明支持多语言
