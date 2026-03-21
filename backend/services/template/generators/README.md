# 模板生成器索引

> 本文档列出所有已注册的模板生成器，帮助快速复用现有生成器添加新模板。

## 快速查找表

| 生成器模块名 | 功能描述 | 适用场景 | 关键配置参数 |
|-------------|---------|---------|-------------|
| `mixed_addition_subtraction` ⭐ | **统一加减法生成器** | 所有加减法题型及比大小 | `question_complexity`, `num.min/max`, `result_within_X`, `q_type` |
| `fraction_arithmetic_comparison` ⭐ | **分数加减乘除比较综合** | 分数所有运算及比较 | `denominator`, `numerator`, `question_complexity`, `q_type` |
| `decimal_arithmetic` ⭐ | **小数乘除法综合生成器** | 小数乘除所有运算及比较 | `decimal_places`, `factor_int`, `question_complexity`, `rules` |
| `unit_conversion_comprehensive` ⭐ | **小学单位换算综合** | 所有单位换算（人民币/长度/质量/面积/体积/时间） | `unit_category`, `convert_types`, `value_range` |

> **注意**:
> 1. `mixed_addition_subtraction` 是统一的加减法生成器，已覆盖原有的 `addition_subtraction`、`consecutive_addition_subtraction` 和 `compare_number` 功能。
> 2. `multiplication_table` 生成器已删除，其功能由 `multiplication_division_comprehensive` 统一支持（通过 `question_complexity: ["simple_multiply"]` 配置实现）。
> 3. `fraction_arithmetic_comparison` 是分数综合生成器，支持加减乘除、混合运算、比较大小、填空、倒数、带分数等 30+ 种题型。
> 4. `unit_conversion_comprehensive` 是单位换算综合生成器，已替代 `currency_conversion`、`length_comparison`、`volume_conversion` 三个旧生成器（2026-03-21 已废弃并删除）。
> 5. `fraction_arithmetic_comparison` 已替代 `fraction_comparison` 生成器（2026-03-21 已废弃并删除）。

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

### 4. DecimalArithmeticGenerator ⭐ 小数乘除法综合

**模块名**: `decimal_arithmetic`
**文件**: `decimal_arithmetic.py`

**功能**: 小数乘除法综合生成器，支持小学 3-6 年级所有小数相关题型

**题型**: `CALCULATION` 或 `FILL_BLANK`

**支持的题型** (20+ 种):

#### 小数乘法 (5 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `multiply_decimal_int` | 小数乘整数 | $0.5 \times 3 = [BLANK]$ | 三年级 |
| `multiply_decimal_decimal` | 小数乘小数 | $0.5 \times 0.3 = [BLANK]$ | 五年级 |
| `multiply_commutative` | 乘法交换律 | $0.5 \times 2.4 = 2.4 \times [BLANK]$ | 五年级 |
| `multiply_associative` | 乘法结合律 | $(0.5 \times 2.4) \times 4 = 0.5 \times (2.4 \times [BLANK])$ | 五年级 |
| `multiply_distributive` | 乘法分配律 | $0.5 \times (2.4 + 3.6) = 0.5 \times [BLANK] + 0.5 \times 3.6$ | 五年级 |
| `multiply_distributive_fill` | 乘法分配律填空 | $0.5 \times 2.4 + 0.5 \times 3.6 = 0.5 \times ([BLANK] + 3.6)$ | 五年级 |

#### 小数除法 (5 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `divide_decimal_int` | 小数除以整数 | $3.6 \div 2 = [BLANK]$ | 五年级 |
| `divide_decimal_int_with_remainder` | 小数除以整数（有余数） | $5.6 \div 2 = [BLANK]$ | 五年级 |
| `divide_int_decimal` | 整数除以小数 | $10 \div 0.5 = [BLANK]$ | 五年级 |
| `divide_decimal_decimal` | 小数除以小数 | $3.6 \div 0.4 = [BLANK]$ | 五年级 |

#### 商的近似值 (2 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `approximate_quotient` | 商的近似值 | $10 \div 3 \approx [BLANK]$（保留 2 位小数） | 五年级 |
| `approximate_quotient_real` | 实际应用题 | $35.5 \div 6 \approx [BLANK]$（保留 2 位小数） | 五年级 |

#### 循环小数 (2 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `repeating_decimal_identify` | 识别循环小数 | $1 \div 3 = 0.\dot{3}$ [BLANK] 循环小数 | 五年级 |
| `repeating_decimal_write` | 用循环小数表示 | $1 \div 3 = [BLANK]$（用循环小数表示） | 五年级 |

#### 混合运算 (2 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `multiply_divide_mixed` | 小数乘除混合 | $0.5 \times 4 \div 2 = [BLANK]$ | 五年级 |
| `multiply_multiply` | 小数连乘 | $0.5 \times 2 \times 3 = [BLANK]$ | 五年级 |

#### 比较大小 (2 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `compare_multiply_result` | 乘法结果比较 | $0.5 \times 3$ [BLANK] $1.4$ | 五年级 |
| `compare_divide_result` | 除法结果比较 | $3.6 \div 2$ [BLANK] $1.5$ | 五年级 |

#### 填空题 (2 种)
| 题型代码 | 说明 | 示例 | 年级 |
|---------|------|------|------|
| `fill_missing_factor` | 填因数 | $[BLANK] \times 3 = 1.5$ | 五年级 |
| `fill_divisor` | 填除数 | $3.6 \div [BLANK] = 1.2$ | 五年级 |

**配置参数 - 三年级 (小数乘整数基础)**:
```json
{
  "decimal_places": {"min": 1, "max": 1},
  "factor_int": {"min": 2, "max": 5},
  "question_complexity": ["multiply_decimal_int"],
  "rules": ["result_one_decimal_places"]
}
```

**配置参数 - 五年级 (小数乘除法综合)**:
```json
{
  "decimal_places": {"min": 1, "max": 2},
  "factor_int": {"min": 2, "max": 10},
  "dividend_range": {"min": 10, "max": 100},
  "divisor_range": {"min": 2, "max": 20},
  "question_complexity": [
    "multiply_decimal_int",
    "multiply_decimal_decimal",
    "divide_decimal_int",
    "divide_decimal_decimal",
    "approximate_quotient"
  ],
  "rules": ["result_two_decimal_places"]
}
```

**配置参数 - 运算定律专项**:
```json
{
  "decimal_places": {"min": 1, "max": 2},
  "question_complexity": [
    "multiply_commutative",
    "multiply_associative",
    "multiply_distributive",
    "multiply_distributive_fill"
  ]
}
```

**配置参数 - 商的近似值专项**:
```json
{
  "dividend_range": {"min": 10, "max": 100},
  "divisor_range": {"min": 3, "max": 20},
  "question_complexity": ["approximate_quotient", "approximate_quotient_real"],
  "approximate_places": 2,
  "approximate_method": "half_up"
}
```

**配置参数 - 循环小数专项**:
```json
{
  "question_complexity": ["repeating_decimal_identify", "repeating_decimal_write"]
}
```

**配置参数 - 比较大小专项**:
```json
{
  "decimal_places": {"min": 1, "max": 2},
  "question_complexity": ["compare_multiply_result", "compare_divide_result"],
  "q_type": {
    "compare_multiply_result": "circle",
    "compare_divide_result": "circle"
  }
}
```

**适用模板**:
- 三年级小数的初步认识
- 五年级小数乘法
- 五年级小数除法
- 五年级运算定律推广到小数
- 五年级商的近似值
- 五年级循环小数
- 小数乘除法综合练习

---

### 5. UnitConversionComprehensiveGenerator ⭐ 小学单位换算综合

**模块名**: `unit_conversion_comprehensive`
**文件**: `unit_conversion_comprehensive.py`

**功能**: 小学单位换算综合生成器，支持 1-6 年级所有单位换算类型

**题型**: `CALCULATION`

**支持的单位类别** (6 大类):

#### 人民币单位（一年级）
| 类型代码 | 说明 | 进率 | 示例 |
|---------|------|------|------|
| `yuan_to_jiao` | 元→角 | ×10 | 5 元 = [BLANK] 角 |
| `jiao_to_yuan` | 角→元 | ÷10 | 60 角 = [BLANK] 元 |
| `jiao_to_fen` | 角→分 | ×10 | 5 角 = [BLANK] 分 |
| `fen_to_jiao` | 分→角 | ÷10 | 50 分 = [BLANK] 角 |
| `yuan_to_fen` | 元→分 | ×100 | 5 元 = [BLANK] 分 |
| `fen_to_yuan` | 分→元 | ÷100 | 100 分 = [BLANK] 元 |
| `yuan_jiao_to_jiao` | 元 + 角→角 | - | 3 元 5 角 = [BLANK] 角 |
| `yuan_fen_to_fen` | 元 + 分→分 | - | 54 元 50 分 = [BLANK] 分 |
| `yuan_jiao_fen_to_fen` | 元 + 角 + 分→分 | - | 3 元 5 角 20 分 = [BLANK] 分 |
| `jiao_fen_to_fen` | 角 + 分→分 | - | 5 角 8 分 = [BLANK] 分 |
| `compare_*` | 比较大小 | - | 5 元 [BLANK] 48 角 |

#### 长度单位（一 - 四年级）
| 类型代码 | 说明 | 进率 | 示例 |
|---------|------|------|------|
| `m_to_cm` | 米→厘米 | ×100 | 3m = [BLANK]cm |
| `cm_to_m` | 厘米→米 | ÷100 | 300cm = [BLANK]m |
| `dm_to_cm` | 分米→厘米 | ×10 | 5dm = [BLANK]cm |
| `cm_to_dm` | 厘米→分米 | ÷10 | 50cm = [BLANK]dm |
| `m_to_dm` | 米→分米 | ×10 | 5m = [BLANK]dm |
| `dm_to_m` | 分米→米 | ÷10 | 50dm = [BLANK]m |
| `km_to_m` | 千米→米 | ×1000 | 3km = [BLANK]m |
| `m_to_km` | 米→千米 | ÷1000 | 3000m = [BLANK]km |
| `mm_to_cm` | 毫米→厘米 | ÷10 | 30mm = [BLANK]cm |
| `cm_to_mm` | 厘米→毫米 | ×10 | 3cm = [BLANK]mm |
| `m_cm_to_cm` | 米 + 厘米→厘米 | - | 2m50cm = [BLANK]cm |
| `m_dm_to_dm` | 米 + 分米→分米 | - | 3m5dm = [BLANK]dm |
| `dm_cm_to_cm` | 分米 + 厘米→厘米 | - | 2dm5cm = [BLANK]cm |
| `km_m_to_m` | 千米 + 米→米 | - | 2km500m = [BLANK]m |
| `compare_*` | 比较大小 | - | 3m [BLANK] 280cm |

#### 质量单位（三 - 四年级）
| 类型代码 | 说明 | 进率 | 示例 |
|---------|------|------|------|
| `kg_to_g` | 千克→克 | ×1000 | 3kg = [BLANK]g |
| `g_to_kg` | 克→千克 | ÷1000 | 3000g = [BLANK]kg |
| `t_to_kg` | 吨→千克 | ×1000 | 5t = [BLANK]kg |
| `kg_to_t` | 千克→吨 | ÷1000 | 5000kg = [BLANK]t |
| `kg_g_to_g` | 千克 + 克→克 | - | 3kg500g = [BLANK]g |
| `t_kg_to_kg` | 吨 + 千克→千克 | - | 2t500kg = [BLANK]kg |

#### 面积单位（四 - 五年级）
| 类型代码 | 说明 | 进率 | 示例 |
|---------|------|------|------|
| `m2_to_dm2` | 平方米→平方分米 | ×100 | 5m² = [BLANK]dm² |
| `dm2_to_m2` | 平方分米→平方米 | ÷100 | 500dm² = [BLANK]m² |
| `dm2_to_cm2` | 平方分米→平方厘米 | ×100 | 5dm² = [BLANK]cm² |
| `cm2_to_dm2` | 平方厘米→平方分米 | ÷100 | 500cm² = [BLANK]dm² |
| `hectare_to_m2` | 公顷→平方米 | ×10000 | 3 公顷 = [BLANK]m² |
| `m2_to_hectare` | 平方米→公顷 | ÷10000 | 30000m² = [BLANK] 公顷 |
| `km2_to_hectare` | 平方千米→公顷 | ×100 | 5km² = [BLANK] 公顷 |
| `hectare_to_km2` | 公顷→平方千米 | ÷100 | 500 公顷 = [BLANK]km² |

#### 体积/容积单位（五年级）
| 类型代码 | 说明 | 进率 | 示例 |
|---------|------|------|------|
| `m3_to_dm3` | 立方米→立方分米 | ×1000 | 5m³ = [BLANK]dm³ |
| `dm3_to_m3` | 立方分米→立方米 | ÷1000 | 5000dm³ = [BLANK]m³ |
| `dm3_to_cm3` | 立方分米→立方厘米 | ×1000 | 5dm³ = [BLANK]cm³ |
| `cm3_to_dm3` | 立方厘米→立方分米 | ÷1000 | 5000cm³ = [BLANK]dm³ |
| `l_to_ml` | 升→毫升 | ×1000 | 5L = [BLANK]mL |
| `ml_to_l` | 毫升→升 | ÷1000 | 5000mL = [BLANK]L |
| `dm3_to_l` | 立方分米→升 | 1:1 | 5dm³ = [BLANK]L |
| `l_to_dm3` | 升→立方分米 | 1:1 | 5L = [BLANK]dm³ |
| `cm3_to_ml` | 立方厘米→毫升 | 1:1 | 5cm³ = [BLANK]mL |
| `ml_to_cm3` | 毫升→立方厘米 | 1:1 | 5mL = [BLANK]cm³ |
| `m3_to_l` | 立方米→升 | ×1000 | 5m³ = [BLANK]L |
| `l_to_m3` | 升→立方米 | ÷1000 | 5000L = [BLANK]m³ |

#### 时间单位（二 - 五 - 年级）
| 类型代码 | 说明 | 进率 | 示例 |
|---------|------|------|------|
| `hour_to_minute` | 时→分 | ×60 | 3 时 = [BLANK] 分 |
| `minute_to_hour` | 分→时 | ÷60 | 180 分 = [BLANK] 时 |
| `minute_to_second` | 分→秒 | ×60 | 5 分 = [BLANK] 秒 |
| `second_to_minute` | 秒→分 | ÷60 | 300 秒 = [BLANK] 分 |
| `day_to_hour` | 日→时 | ×24 | 3 日 = [BLANK] 时 |
| `hour_to_day` | 时→日 | ÷24 | 72 时 = [BLANK] 日 |
| `year_to_month` | 年→月 | ×12 | 3 年 = [BLANK] 月 |
| `month_to_year` | 月→年 | ÷12 | 36 月 = [BLANK] 年 |
| `week_to_day` | 周→天 | ×7 | 5 周 = [BLANK] 天 |
| `day_to_week` | 天→周 | ÷7 | 35 天 = [BLANK] 周 |
| `day_to_minute` | 日→分 | ×1440 | 2 日 = [BLANK] 分 |
| `hour_to_second` | 时→秒 | ×3600 | 2 时 = [BLANK] 秒 |
| `hour_minute_to_minute` | 时 + 分→分 | - | 2 时 30 分 = [BLANK] 分 |
| `day_hour_to_hour` | 日 + 时→时 | - | 2 日 5 时 = [BLANK] 时 |
| `year_month_to_month` | 年 + 月→月 | - | 3 年 5 月 = [BLANK] 月 |

**配置参数 - 一年级人民币**:
```json
{
  "unit_category": "currency",
  "grade_level": "grade1",
  "convert_types": ["yuan_to_jiao", "jiao_to_fen", "yuan_jiao_to_jiao"],
  "value_range": {"min": 1, "max": 20}
}
```

**配置参数 - 三年级长度**:
```json
{
  "unit_category": "length",
  "grade_level": "grade3",
  "convert_types": ["km_to_m", "m_to_km", "m_cm_to_cm"],
  "value_range": {"min": 1, "max": 50}
}
```

**配置参数 - 五年级体积**:
```json
{
  "unit_category": "volume",
  "grade_level": "grade5",
  "convert_types": ["m3_to_dm3", "dm3_to_cm3", "l_to_ml", "dm3_to_l"],
  "value_range": {"min": 1, "max": 50}
}
```

**配置参数 - 综合型（混合所有单位类别）**:
```json
{
  "unit_category": "length",
  "convert_types": [
    "m_to_cm", "cm_to_m", "km_to_m", "m_to_km",
    "m_cm_to_cm", "m_dm_to_dm"
  ],
  "value_range": {"min": 1, "max": 100},
  "allow_compound": true,
  "integer_result": true
}
```

**配置参数 - 比较大小题型**:
```json
{
  "unit_category": "currency",
  "convert_types": ["yuan_to_jiao", "jiao_to_fen"],
  "is_comparison": true,
  "value_range": {"min": 1, "max": 20},
  "q_type": {
    "compare_yuan_jiao": "circle",
    "compare_jiao_fen": "circle"
  }
}
```

**比较大小题型示例**:
- 人民币：`5 元 [BLANK] 48 角`、`3 元 5 角 [BLANK] 32 角`
- 长度：`3m [BLANK] 280cm`、`2km [BLANK] 1900m`
- 质量：`5kg [BLANK] 4800g`、`3t [BLANK] 2800kg`
- 面积：`5m² [BLANK] 480dm²`、`3 公顷 [BLANK] 28000m²`
- 体积：`5m³ [BLANK] 4800dm³`、`3L [BLANK] 2800mL`
- 时间：`3 时 [BLANK] 190 分`、`2 年 [BLANK] 22 月`

**适用模板**:
- 一年级认识人民币
- 二年级长度单位初步认识
- 三年级长度单位拓展、质量单位
- 四年级面积单位、质量单位拓展
- 五年级体积/容积单位、面积单位拓展
- 六年级单位换算综合应用

**替代说明**:
此生成器是 `currency_conversion`、`length_comparison`、`volume_conversion` 的统一替代版本，推荐使用此生成器而非旧的单一单位生成器。`fraction_arithmetic_comparison` 已替代 `fraction_comparison` 生成器，请使用前者进行分数比大小练习。

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
