# 暗黑模式修改计划

## 问题分析

### 当前实现
1. **自动检测系统主题**: `theme.css` 第 254 行使用 `@media (prefers-color-scheme: dark)` 根据系统主题自动切换
2. **微信暗黑模式问题**: 微信内置浏览器可能强制应用暗黑模式，导致页面样式异常
3. **用户痛点**:
   - 不需要自动切换，想要手动控制
   - 微信中暗黑模式样式看起来奇怪

### 需要修复的问题
1. 移除 `@media (prefers-color-scheme: dark)` 自动检测
2. 添加手动主题切换功能（按钮 + localStorage 持久化）
3. 完善暗黑模式样式，确保在微信中显示正常

---

## 实施方案

### Phase 1: 创建主题管理 Hook (复杂度：低)

**文件**: `src/hooks/useTheme.ts`

创建一个管理主题切换的自定义 Hook：

```typescript
import { useState, useEffect } from 'react'

type Theme = 'light' | 'dark'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>('light')
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    // 从 localStorage 读取主题
    const saved = localStorage.getItem('theme') as Theme | null
    if (saved) {
      setTheme(saved)
    }
    setIsInitialized(true)
  }, [])

  useEffect(() => {
    if (!isInitialized) return

    // 应用主题到 document
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme, isInitialized])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return { theme, toggleTheme, isInitialized }
}
```

---

### Phase 2: 修改 CSS 主题系统 (复杂度：中)

**文件**: `src/theme.css`

**修改内容**:

1. **移除自动检测媒体查询**:
```css
/* 删除以下代码 */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    /* ... */
  }
}
```

2. **添加 data-theme 属性选择器**:
```css
/* 亮色主题 (默认) */
:root,
[data-theme="light"] {
  --bg-primary: #fffdf9;
  --bg-secondary: #ffffff;
  --gray-50: #f9fafb;
  /* ... 所有亮色变量 */
}

/* 暗黑主题 */
[data-theme="dark"] {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-elevated: #21262d;
  --gray-50: #161b22;
  --gray-100: #21262d;
  --gray-200: #30363d;
  --gray-300: #484f58;
  --gray-400: #6e7681;
  --gray-500: #8b949e;
  --gray-600: #c9d1d9;
  --gray-700: #e6edf3;
  --gray-800: #f0f6fc;
  --gray-900: #ffffff;
}
```

---

### Phase 3: 添加主题切换按钮 (复杂度：中)

**文件**: `src/features/question-generator/MainContent.tsx`

在主界面 Header 区域添加主题切换按钮：

```typescript
import { useTheme } from '@/hooks/useTheme'

export default function MainContent({ email, onLogout }: Props) {
  const { theme, toggleTheme } = useTheme()

  // ... 现有代码

  // 在 Header 区域添加按钮
  <button
    className="theme-toggle-btn"
    onClick={toggleTheme}
    aria-label={`切换到${theme === 'light' ? '暗黑' : '亮色'}模式`}
  >
    {theme === 'light' ? (
      <svg>🌙</svg>
    ) : (
      <svg>☀️</svg>
    )}
  </button>
```

**样式文件**: `src/features/question-generator/header.css`

```css
.theme-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--gray-100);
  border: 1px solid var(--gray-200);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1.25rem;
}

.theme-toggle-btn:hover {
  background: var(--gray-200);
  transform: scale(1.05);
}

[data-theme="dark"] .theme-toggle-btn {
  background: var(--gray-800);
  border-color: var(--gray-700);
}

[data-theme="dark"] .theme-toggle-btn:hover {
  background: var(--gray-700);
}
```

---

### Phase 4: 完善暗黑模式样式 (复杂度：中)

需要检查并修复以下文件的暗黑模式样式：

1. **LandingPage.css** - 落地页
2. **MainContent.css** - 主界面
3. **sidebar.css** - 侧边栏
4. **preview.css** - 预览区
5. **modals.css** - 弹窗
6. **questions.css** - 题目组件

**关键修复点**:

```css
/* LandingPage.css 示例 */
[data-theme="dark"] .landing-page {
  background: var(--bg-primary);
}

[data-theme="dark"] .landing-nav {
  background: rgba(22, 27, 34, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .landing-hero {
  background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
}

[data-theme="dark"] .feature-card,
[data-theme="dark"] .use-case-card,
[data-theme="dark"] .demo-card {
  background: var(--bg-secondary);
  border-color: var(--gray-800);
}

[data-theme="dark"] .testimonial-card {
  filter: brightness(0.85);
}
```

---

### Phase 5: 移动端/微信优化 (复杂度：低)

针对微信内置浏览器优化：

```css
/* 防止微信强制暗黑模式 */
@media (prefers-color-scheme: dark) {
  html {
    color-scheme: light dark;
  }

  body {
    background-color: var(--bg-primary);
    color: var(--gray-800);
  }
}

/* 确保在微信中主题切换生效 */
[data-theme="dark"] body,
[data-theme="dark"] .landing-page,
[data-theme="dark"] .app {
  background: var(--bg-primary) !important;
}
```

---

## 实施步骤

### 第 1 步：创建主题 Hook
- [ ] 创建 `src/hooks/useTheme.ts`
- [ ] 在 `src/hooks/index.ts` 导出

### 第 2 步：修改主题 CSS
- [ ] 修改 `src/theme.css` - 使用 data-theme 属性
- [ ] 移除 `@media (prefers-color-scheme: dark)` 自动检测

### 第 3 步：添加切换按钮
- [ ] 在 `MainContent.tsx` Header 区域添加主题切换按钮
- [ ] 在 `header.css` 添加按钮样式

### 第 4 步：完善暗黑模式样式
- [ ] `LandingPage.css` - 落地页暗黑样式
- [ ] `MainContent.css` - 主界面暗黑样式
- [ ] `sidebar.css` - 侧边栏暗黑样式
- [ ] `preview.css` - 预览区暗黑样式
- [ ] `modals.css` - 弹窗暗黑样式
- [ ] `questions.css` - 题目组件暗黑样式

### 第 5 步：测试验证
- [ ] 在微信中测试亮色模式
- [ ] 在微信中测试暗黑模式
- [ ] 在普通浏览器中测试切换功能
- [ ] 验证 localStorage 持久化

---

## 预估复杂度

| 阶段 | 复杂度 | 预计时间 |
|------|--------|----------|
| Phase 1: 主题 Hook | 低 | 0.5 小时 |
| Phase 2: CSS 修改 | 中 | 1 小时 |
| Phase 3: 切换按钮 | 中 | 0.5 小时 |
| Phase 4: 样式完善 | 中 | 2 小时 |
| Phase 5: 测试验证 | 低 | 1 小时 |
| **总计** | | **5 小时** |

---

## 注意事项

1. **向后兼容**: 默认主题为亮色，确保老用户不受影响
2. **平滑过渡**: 添加 CSS `transition` 属性，使主题切换更流畅
3. **可访问性**: 确保按钮有正确的 aria-label
4. **性能**: 避免在主题切换时触发大量重绘
5. **微信特殊处理**: 微信可能使用 `prefers-color-scheme` 强制应用暗黑，需要用 `!important` 覆盖

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 微信仍强制暗黑 | 中 | 使用 `color-scheme` CSS 属性 + `!important` |
| 主题切换闪烁 | 低 | 在 HTML 加载时就应用主题 |
| 样式遗漏 | 中 | 逐一检查所有 CSS 文件 |
| 用户不习惯 | 低 | 默认亮色，提供明显切换按钮 |

---

**等待用户确认**: 是否按此计划执行？(yes/modify)
