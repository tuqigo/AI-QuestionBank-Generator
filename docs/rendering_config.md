# 题目渲染配置指南 (rendering_config)

本文档用于配置模板题目的渲染样式，适用于后台模板的 `rendering_config` 字段。

---

## 快速配置表

| 配置项 | 类型 | 可选值 | 默认值 | 作用 | 适用题型 |
|--------|------|--------|--------|------|----------|
| `layout` | string | `single` / `multi` / `inline` | `single` | 控制题目布局方式 | 所有题型 |
| `columns` | number | 1-10 | `3` | 多列布局时的列数 | 口算题、计算题 |
| `font_size` | number | 12-24 | `14` | 题目字体大小 (px) | 所有题型 |
| `latex_scale` | number | 0.5-2.0 | `1.0` | LaTeX 公式缩放比例 | 竖式计算题 |
| `rows_to_answer` | number | 1-20 | `1` | 预留作答行数 | 计算题、应用题、作文题 |
| `answer_width` | number | 20-300 或 `-1` | `80` | 作答区域宽度 (px)，`-1` 自适应 | 填空题、口算题 |
| `answer_style` | string | 见下方表格 | `line` | 作答区域样式 | 填空题、口算题、判断题 |
| `keep_together` | boolean | `true` / `false` | `true` | 避免题目被分页打断 | 阅读理解、完形填空 |
| `show_question_number` | boolean | `true` / `false` | `true` | 是否显示题号 | 所有题型 |

---

## answer_style 可选值

| 值 | 效果 | 示例 | 适用场景 |
|----|------|------|----------|
| `box` | 实线方框 | ┌────┐ | 填空题 |
| `line` | 下划线 | ────── | 填空题（默认） |
| `dashed_box` | 虚线方框 | ┌┈┈┈┐ | 口算题 |
| `circle` | 圆圈/圆形 | ⭕ | 口算题、判断题 |
| `parentheses` | 括号虚线 | （┈┈） | 填空题 |
| `blank` | 灰色背景 | ████ | 计算题 |

---

## 各题型推荐配置

### 口算题 (ORAL_CALCULATION)
```json
{
  "layout": "multi",
  "columns": 4,
  "font_size": 18,
  "answer_width": 80,
  "answer_style": "circle",
  "show_question_number": false
}
```

### 填空题 (FILL_BLANK)
```json
{
  "layout": "single",
  "font_size": 14,
  "answer_width": 150,
  "answer_style": "line",
  "show_question_number": true
}
```

### 计算题 (CALCULATION)
```json
{
  "layout": "multi",
  "columns": 3,
  "font_size": 18,
  "rows_to_answer": 2,
  "answer_style": "blank",
  "show_question_number": false
}
```

### 应用题 (WORD_PROBLEM)
```json
{
  "layout": "single",
  "font_size": 14,
  "rows_to_answer": 5
}
```

### 竖式计算 (VERTICAL_ARITHMETIC)
```json
{
  "layout": "single",
  "font_size": 16,
  "latex_scale": 1.2,
  "keep_together": false
}
```

### 阅读理解 (READ_COMP)
```json
{
  "layout": "single",
  "font_size": 14,
  "keep_together": true
}
```

### 判断题 (TRUE_FALSE)
```json
{
  "layout": "single",
  "font_size": 14,
  "answer_width": 40,
  "answer_style": "circle",
  "keep_together": true
}
```

### 作文题 (ESSAY)
```json
{
  "layout": "single",
  "font_size": 14,
  "rows_to_answer": 10
}
```

---

## 配置示例

### 示例 1：3 列布局的口算题（圆圈作答）
```json
{
  "rendering_config": {
    "layout": "multi",
    "columns": 3,
    "font_size": 18,
    "answer_width": 60,
    "answer_style": "circle",
    "show_question_number": false
  }
}
```

### 示例 2：大字体应用题（5 行作答区）
```json
{
  "rendering_config": {
    "layout": "single",
    "font_size": 16,
    "rows_to_answer": 5,
    "keep_together": true
  }
}
```

### 示例 3：竖式计算题（放大 1.3 倍）
```json
{
  "rendering_config": {
    "layout": "single",
    "font_size": 16,
    "latex_scale": 1.3,
    "keep_together": false
  }
}
```

---

## 详细说明

### layout（布局方式）
- `single`：单列布局，每题独立一行（默认）
- `multi`：多列网格布局，适合口算题等简短题目
- `inline`：行内布局，题目紧密排列

### columns（列数）
- 仅在 `layout: "multi"` 时生效
- 建议值：口算题 3-5 列，计算题 2-3 列

### font_size（字体大小）
- 单位：像素 (px)
- 范围：12-24
- 推荐：小学低年级 16-18px，高年级 14px

### latex_scale（LaTeX 缩放）
- 仅适用于竖式计算等使用 LaTeX 渲染的题型
- `1.0`：原始大小
- `1.2`：放大 20%（推荐）
- `0.8`：缩小 20%

### rows_to_answer（作答行数）
- 适用于需要书写过程的题目
- 计算题：2-3 行
- 应用题：4-6 行
- 作文题：8-15 行

### answer_width（作答宽度）
- 单位：像素 (px)
- 填空/口算题：60-150px
- `-1`：自适应宽度（根据内容自动调整）

### keep_together（避免分页）
- `true`：题目尽量保持在同一页
- `false`：允许被分页打断
- 阅读理解、完形填空建议设为 `true`

### show_question_number（显示题号）
- `true`：显示题号（如 "1."）
- `false`：不显示题号（口算题常用）

---

## 默认配置参考

系统默认配置位于 `backend/services/template/rendering_defaults.json`，各题型已有推荐值。

如需自定义，在模板的 `rendering_config` 中覆盖对应字段即可。
