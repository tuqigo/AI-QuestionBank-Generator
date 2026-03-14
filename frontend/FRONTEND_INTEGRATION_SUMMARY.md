# 前端对接完成报告

## 对接日期
2026-03-14

---

## 一、改造内容

### 1. 类型定义更新
**文件**: `frontend/src/types/structured.ts`

更新 `StructuredQuestion` 接口，添加后端填充字段：
```typescript
export interface StructuredQuestion extends Question {
  rows_to_answer: number;    // 预留作答行数
  answer_blanks?: number;    // 填空题空格数
  answer_text?: string;      // 参考答案
}
```

### 2. API 函数新增
**文件**: `frontend/src/api/history.ts`

新增 4 个 API 函数：

| 函数名 | 接口 | 说明 |
|--------|------|------|
| `getHistoryQuestions(shortId)` | `/api/history/{shortId}/questions` | 获取试卷题目详情（需登录） |
| `getHistoryAnswers(shortId)` | `/api/history/{shortId}/answers` | 获取整卷答案（需登录） |
| `getSharedQuestions(shortId, token)` | `/api/share/history/{shortId}/questions` | 分享页获取题目（无需登录） |
| `getSharedAnswers(shortId, token)` | `/api/share/history/{shortId}/answers` | 分享页获取答案（无需登录） |

### 3. HistoryDetail.tsx 改造
**文件**: `frontend/src/HistoryDetail.tsx`

**主要变更**：
1. 调用新接口 `getHistoryQuestions()` 获取结构化题目数据
2. 新增"查看答案"按钮和答案显示区域
3. 答案列表按题号显示，包含题型标签

**新增状态**：
```typescript
const [answers, setAnswers] = useState<...>([])
const [showAnswers, setShowAnswers] = useState(false)
const [answersLoading, setAnswersLoading] = useState(false)
```

**新增方法**：
- `handleToggleAnswers()` - 切换答案显示

### 4. StructuredPreview.tsx 改造
**文件**: `frontend/src/StructuredPreview.tsx`

**主要变更**：
1. 生成题目后保存 `short_id`
2. 新增"查看答案"按钮（仅生成题目后可用）
3. 答案显示区域与题目列表分离

**新增状态**：
```typescript
const [shortId, setShortId] = useState<string | null>(null)
const [answers, setAnswers] = useState<...>([])
const [showAnswers, setShowAnswers] = useState(false)
const [answersLoading, setAnswersLoading] = useState(false)
```

### 5. 样式文件更新
**文件**:
- `frontend/src/HistoryDetail.css`
- `frontend/src/StructuredPreview.css`

**新增样式类**：
```css
.answers-section      /* 答案区域容器 */
.answers-list         /* 答案列表 */
.answer-item          /* 单题答案卡片 */
.answer-header        /* 答案头部（题号 + 题型） */
.answer-index         /* 题号标签 */
.answer-type          /* 题型标签 */
.answer-content       /* 答案内容 */
```

---

## 二、数据流程

### 历史记录详情页
```
用户进入详情页
    ↓
并行请求：
  1. getHistoryDetail(id) → 试卷基本信息
  2. getHistoryQuestions(id) → 结构化题目数据
    ↓
渲染题目列表（StructuredPreviewShared）
    ↓
用户点击"查看答案"
    ↓
getHistoryAnswers(id) → 答案列表
    ↓
显示答案区域
```

### 生成题目页
```
用户输入提示词
    ↓
generateStructuredQuestions(prompt)
    ↓
保存 short_id, 渲染题目
    ↓
用户点击"查看答案"
    ↓
getHistoryAnswers(shortId) → 答案列表
    ↓
显示答案区域
```

---

## 三、UI 效果

### 答案显示区域
- **位置**: 题目列表下方，用虚线分隔
- **样式**: 渐变橙色背景卡片
- **内容**: 题号标签 + 题型标签 + 答案文本
- **打印**: 支持打印分页控制

### 按钮状态
| 按钮 | 正常状态 | 加载状态 | 不可用状态 |
|------|----------|----------|------------|
| 查看答案 | 橙色渐变 | "加载中..." | 禁用（灰色） |
| 打印 | 绿色渐变 | - | 禁用（灰色，无 short_id 时） |

---

## 四、构建验证

```bash
cd frontend
npm run build
```

**结果**: 构建成功，无 TypeScript 错误
- 166 modules transformed
- Output: 423.33 kB (gzipped: 142.60 kB)

---

## 五、后续工作（可选）

### 分享页答案显示
如需在分享页也支持查看答案，需要：
1. 创建分享页专用组件或使用现有 HistoryDetail
2. 调用 `getSharedAnswers(shortId, token)` 接口
3. 添加"查看答案"按钮控制逻辑

### 答案导出功能
- 导出答案为 PDF
- 导出答案为 Markdown
- 批量导出多套试卷答案

### 答案管理
- 教师端答案编辑功能
- 答案审核流程
- 多版本答案支持

---

## 六、文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `src/types/structured.ts` | 修改 | 添加 answer_blanks, answer_text 字段 |
| `src/api/history.ts` | 修改 | 新增 4 个 API 函数 |
| `src/HistoryDetail.tsx` | 修改 | 调用新接口，添加答案显示 |
| `src/HistoryDetail.css` | 修改 | 添加答案区域样式 |
| `src/StructuredPreview.tsx` | 修改 | 保存 short_id，添加答案显示 |
| `src/StructuredPreview.css` | 修改 | 添加答案区域样式 |

---

## 七、测试建议

### 功能测试
1. 进入历史记录详情页 → 题目正常显示
2. 点击"查看答案" → 答案正常加载显示
3. 再次点击"收起答案" → 答案区域隐藏
4. 生成新题目 → 保存 short_id 正确
5. 生成后立即查看答案 → 答案正确

### 边界测试
1. 空答案文本 → 显示"暂无答案"
2. 网络错误 → Toast 提示错误信息
3. 旧数据记录 → 显示"不支持查看"

### 兼容性测试
1. 移动端响应式布局
2. 打印预览分页
3. 不同浏览器 MathJax 渲染

---

**前端对接完成，可以开始测试。**
