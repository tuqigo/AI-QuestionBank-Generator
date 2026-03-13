# TODO: 需要修复的问题

## 1. JSON LaTeX 转义问题 ⭐⭐⭐
**问题**: AI 返回的 JSON 中，LaTeX 命令有时使用单反斜杠（`\frac`），导致 JSON 解析失败

**解决方案**:
1. 修改 `config.py` 的 `QUESTION_SYSTEM_PROMPT`，要求 AI 返回双反斜杠（`\\frac`）
2. 保留现有的 `_fix_latex_escapes()` 修复逻辑作为兜底

**优先级**: 高
**状态**: 待处理

---

## 2. MathJax 渲染不稳定 ⭐⭐⭐
**问题**: 预览页数学公式渲染不稳定，有时能正确渲染，有时不能

**根本原因**:
- 存在**多个 useEffect 同时触发 MathJax 渲染**：
  1. `StructuredPreviewShared.tsx` - 有自己的 useEffect
  2. `QuestionRenderer.tsx` - 有自己的 useEffect
  3. 每个题型组件（如 `SingleChoice.tsx`）- 也有自己的 useEffect
- 这些 useEffect **竞态触发**，导致：
  - MathJax 被多次调用
  - DOM 还没完全渲染就被 typeset
  - 公式渲染不完整或消失

**解决方案**:
1. **统一渲染控制**: 只在 `StructuredPreviewShared` 统一控制 MathJax 渲染
2. **移除其他地方的 MathJax 触发**:
   - `QuestionRenderer.tsx` 移除 useEffect
   - 所有题型组件移除 useEffect
3. **添加渲染完成回调**: 确保 DOM 完全渲染后再触发 MathJax
4. **使用防抖**: 避免频繁触发

**优先级**: 高
**状态**: 待处理

---

## 3. 点击按钮后公式消失 + 打印闪动 ⭐⭐⭐
**问题**:
1. 历史页点击"分享"按钮后，页面的数学公式又没有正确渲染了
2. 点击打印时，打印预览会闪一下（用户能明显感觉到页面变化）

**根本原因**:
- 点击按钮会触发**组件状态更新**（如 `setShareUrl`, `setShowCopyToast`）
- 状态更新导致**组件重新渲染**
- 重新渲染会触发 `StructuredPreviewShared` 的 useEffect
- useEffect 又会重新触发 MathJax 渲染
- **结果**: 公式消失或重新渲染

- 打印时将容器**追加到 body**，没有隐藏原页面，导致：
  - 用户看到原页面
  - 看到打印预览弹出
  - 看到原页面恢复
  - **明显闪动**

**解决方案**:

### 3.1 点击按钮后公式消失
1. **优化 useEffect 依赖**:
   - 当前依赖 `[questions, onMathJaxRendered]`
   - 改为只依赖 `questions.length`
   - 避免因为 `onMathJaxRendered` 变化而重新触发

2. **使用 useRef 缓存 MathJax 状态**:
   ```typescript
   const mathJaxInitialized = useRef(false)

   useEffect(() => {
     if (questions.length === 0 || mathJaxInitialized.current) return
     // 初始化 MathJax
     mathJaxInitialized.current = true
   }, [questions.length])
   ```

3. **题型组件不触发 MathJax**: 确保子组件的渲染不会影响父组件的 MathJax

### 3.2 打印闪动问题
**当前做法**:
```typescript
document.body.appendChild(printContainer)
window.print()
setTimeout(() => document.body.removeChild(printContainer), 500)
```

**问题**: 原页面一直可见，打印容器叠加在上面

**改进方案**:

#### 方案A: 隐藏原页面（推荐）
```typescript
// 创建遮罩层
const overlay = document.createElement('div')
overlay.style.cssText = `
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: white;
  z-index: 999998;
  display: none;
`

// 打印时显示遮罩 + 打印容器
document.body.appendChild(overlay)
document.body.appendChild(printContainer)
overlay.style.display = 'block'

// 等待渲染
await new Promise(resolve => setTimeout(resolve, 300))

// 打印
window.print()

// 恢复
overlay.style.display = 'none'
document.body.removeChild(printContainer)
document.body.removeChild(overlay)
```

#### 方案B: 使用 print stylesheet（更优雅）
```css
@media print {
  body > *:not(#print-container) {
    display: none !important;
  }

  #print-container {
    position: static !important;
    width: auto !important;
    margin: 0 !important;
  }
}
```

**优先级**: 高
**状态**: 待处理

---

## 4. 代码重构建议
**问题**: 当前代码结构存在重复和混乱

**建议**:
1. **移除所有题型组件中的 MathJax useEffect**
2. **移除 QuestionRenderer 中的 MathJax useEffect**
3. **只在 StructuredPreviewShared 中统一管理 MathJax**
4. **使用回调函数通知渲染完成**

**优先级**: 中
**状态**: 待处理

---

## 实施计划

### 第一阶段（紧急）
1. 修复 MathJax 渲染不稳定问题（统一控制）
2. 修复点击按钮后公式消失问题（优化 useEffect）
3. 修复打印闪动问题（隐藏原页面）

### 第二阶段（优化）
4. 修改 System Prompt 要求双反斜杠
5. 代码重构，移除重复的 MathJax 触发
6. 添加更好的错误处理和日志

### 第三阶段（完善）
7. 添加单元测试
8. 性能优化
