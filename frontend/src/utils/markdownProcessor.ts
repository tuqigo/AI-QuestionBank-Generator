import MarkdownIt from 'markdown-it';

// 创建 markdown-it 实例，配置选项
// 启用 math 相关的转义保护
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  // 禁用某些可能导致 LaTeX 被错误解析的选项
  typographer: false,
  xhtmlOut: false,
});

// 禁用 backtick 和 math 冲突的处理
md.disable(['smartquotes']);

/**
 * 保护数学内容不被 markdown-it 处理
 * 返回：处理后的内容和占位符 Map
 */
function protectMath(content: string): { content: string; placeholders: Map<string, string> } {
  const placeholders = new Map<string, string>()
  let idx = 0

  // 保护 $$...$$ (display math) - 先处理 display math，避免被 inline 匹配
  content = content.replace(/\$\$((?:[^$]|\\\$)+?)\$\$/g, (match, math) => {
    // 在保护前，先将 math 内容中的 ___ 转换为安全的下划线占位符
    const processedMath = math.replace(/_{3,}/g, '\\underline{\\hspace{1.5cm}}')
    const placeholder = `MATH_DISPLAY_${idx++}`
    placeholders.set(placeholder, `$$${processedMath}$$`)
    return `@@${placeholder}@@`
  })

  // 保护 $...$ (inline math)
  content = content.replace(/(?<!\\)\$([^$\n]+?)\$/g, (match, math) => {
    // 在保护前，先将 math 内容中的 ___ 转换为安全的下划线占位符
    const trimmedMath = math.trim().replace(/_{3,}/g, '\\underline{\\hspace{1.5cm}}')
    const placeholder = `MATH_INLINE_${idx++}`
    placeholders.set(placeholder, `$${trimmedMath}$`)
    return `@@${placeholder}@@`
  })

  return { content, placeholders }
}

/**
 * 处理特殊格式（填空、括号等）
 */
function processSpecialFormats(content: string): string {
  let processed = content

  // 处理 [   ] 方框填空（2 个空格以上）
  processed = processed.replace(/\[ {2,}\]/g, '<span class="blank-box"></span>')

  // 处理带空格的括号（全角）- 使用 span 包裹空白区域，通过 CSS 控制宽度
  processed = processed.replace(/（ {2,}）/g, () => {
    return '（<span class="answer-blank"></span>）'
  })

  // 处理带空格的半角括号
  processed = processed.replace(/\( {2,}\)/g, () => {
    return '(<span class="answer-blank"></span>)'
  })

  // 处理完全空的括号（全角和半角）
  processed = processed.replace(/（）/g, '<span class="blank-parentheses"></span>')
  processed = processed.replace(/\(\)/g, '<span class="blank-parentheses"></span>')

  return processed
}

/**
 * 恢复被保护的数学内容
 */
function restoreMath(content: string, placeholders: Map<string, string>): string {
  let processed = content
  for (const [placeholder, original] of placeholders) {
    const escapedPlaceholder = `@@${placeholder}@@`.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const regex = new RegExp(escapedPlaceholder, 'g')
    processed = processed.replace(regex, original)
  }
  return processed
}

/**
 * 完整的 Markdown 渲染函数，包含特殊格式处理和保护数学内容
 */
export function renderMarkdown(content: string): string {
  if (!content || typeof content !== 'string') return ''

  // 保护数学内容
  const { content: protectedContent, placeholders } = protectMath(content)

  // 处理特殊格式
  let processed = processSpecialFormats(protectedContent)

  // 渲染 markdown
  processed = md.render(processed)

  // 恢复数学内容
  return restoreMath(processed, placeholders)
}

/**
 * 渲染行内 Markdown 内容（不添加 <p> 标签）
 * 用于题目、选项等需要在同一行显示的场景
 */
export function renderInlineMarkdown(content: string): string {
  if (!content || typeof content !== 'string') return ''
  if (!content.trim()) return ''

  // 移除换行符，确保内容在同一行显示
  const singleLineContent = content.replace(/[\r\n]+/g, ' ')

  // 保护数学内容
  const { content: protectedContent, placeholders } = protectMath(singleLineContent)

  // 处理特殊格式
  let processed = processSpecialFormats(protectedContent)

  // 使用 renderInline 避免添加 <p> 标签
  processed = md.renderInline(processed)

  // 恢复数学内容
  return restoreMath(processed, placeholders)
}
