# 口算题网格布局配置

## 功能说明

口算题（`ORAL_CALCULATION`）支持网格布局配置，可在打印预览时以多列方式展示，节省纸张空间。

## 配置位置

`frontend/src/config/questionConfig.ts`

## 配置示例

```typescript
ORAL_CALCULATION: {
  render: {
    // 屏幕渲染配置
    layout: {
      type: 'grid',        // 布局类型：'grid'=网格布局
      columns: 3,          // 列数：每行显示的题目数量
      gap: '12px'          // 间距：题目之间的间隔
    }
  },
  print: {
    // 打印配置
    layout: {
      type: 'grid',
      columns: 3,
      gap: '12px'
    }
  }
}
```

## 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `'default' \| 'grid'` | 是 | 布局类型：`default`=默认垂直排列，`grid`=网格布局 |
| `columns` | `number` | 仅 grid 需要 | 列数，每行显示的题目数量 |
| `gap` | `string` | 否 | 题目之间的间距，如 `'12px'`、`'16px'` |
| `itemPadding` | `string` | 否 | 题目内边距（默认 `'0'`） |
| `itemBorder` | `string` | 否 | 题目边框（默认 `'none'`） |

## 快速调整

### 修改为 2 列布局

```typescript
layout: {
  type: 'grid',
  columns: 2,  // 改为 2
  gap: '16px'  // 列数减少时可增大间距
}
```

### 修改为 4 列布局

```typescript
layout: {
  type: 'grid',
  columns: 4,  // 改为 4
  gap: '8px'   // 列数增多时减小间距
}
```

## 扩展到其他题型

为其他题型添加网格布局，只需在对应题型配置中添加 `layout` 字段：

```typescript
// 填空题 - 2 列布局
FILL_BLANK: {
  print: {
    layout: {
      type: 'grid',
      columns: 2,
      gap: '16px'
    }
  }
}

// 判断题 - 3 列布局
TRUE_FALSE: {
  print: {
    layout: {
      type: 'grid',
      columns: 3,
      gap: '12px'
    }
  }
}
```

## 注意事项

1. **预览区无边框**：屏幕渲染时默认无边框、无内边距
2. **打印可配边框**：如需打印边框，在 `print.layout` 中配置 `itemBorder: '1px solid #000'`
3. **题型分组**：连续相同题型的题目会自动归为一组，使用相同的布局
4. **混合题型**：不同题型按各自配置渲染，互不影响

## 相关文件

| 文件 | 说明 |
|------|------|
| `frontend/src/config/questionConfig.ts` | 题型配置中心 |
| `frontend/src/utils/printUtils.ts` | 打印渲染工具 |
| `frontend/src/components/questions/OralCalculation.tsx` | 口算题组件 |
| `frontend/src/types/question.ts` | 题型类型定义 |
