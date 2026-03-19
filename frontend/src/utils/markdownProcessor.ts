import MarkdownIt from 'markdown-it';

// 创建 markdown-it 实例，配置选项
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  typographer: false,
  xhtmlOut: false,
});

// 禁用 smartquotes 避免干扰 LaTeX
md.disable(['smartquotes']);

/**
 * 检查内容是否包含 Markdown 语法
 * 如果没有 Markdown 语法，可以直接原样返回，让 MathJax 处理公式
 */
function hasMarkdownSyntax(content: string): boolean {
  // 检查常见 Markdown 语法
  const markdownPatterns = [
    /^#{1,6}\s+/m,           // 标题 # ## ###
    /^\s*[-*+]\s+/m,         // 无序列表
    /^\s*\d+\.\s+/m,         // 有序列表
    /^\s*>\s+/m,             // 引用
    /^\s*```/m,              // 代码块
    /^\s*\|.*\|/m,           // 表格
    /\*\*[^*]+\*\*/g,        // 粗体 **text**
    /\*[^*]+\*/g,            // 斜体 *text*
    /__[^_]+__/g,            // 粗体 __text__
    /_[^_]+_/g,              // 斜体 _text_
    /\[([^\]]+)\]\([^)]+\)/g, // 链接 [text](url)
    /!\[([^\]]+)\]\([^)]+\)/g, // 图片
  ];

  return markdownPatterns.some(pattern => pattern.test(content));
}

/**
 * 保护数学内容不被 markdown-it 处理
 */
function protectMath(content: string): { content: string; placeholders: Map<string, string> } {
  const placeholders = new Map<string, string>()
  let idx = 0

  // 保护 $$...$$ (display math)
  content = content.replace(/\$\$([\s\S]*?)\$\$/g, (match, math) => {
    const processedMath = math.replace(/_{3,}/g, '\\underline{\\hspace{1.5cm}}')
    const placeholder = `MATH_DISPLAY_${idx++}`
    placeholders.set(placeholder, `$$${processedMath}$$`)
    return `@@${placeholder}@@`
  })

  // 保护 \[...\] (display math) - 竖式加减法等使用的 LaTeX 格式
  content = content.replace(/\\\s*\[([\s\S]*?)\\\s*\]/g, (match, math) => {
    const placeholder = `MATH_DISPLAY_BRACKET_${idx++}`
    placeholders.set(placeholder, `\\[${math}\\]`)
    return `@@${placeholder}@@`
  })

  // 保护 $...$ (inline math)
  content = content.replace(/(?<!\\)\$([^$\n]+?)\$/g, (match, math) => {
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
function processSpecialFormats(content: string, answerWidth?: number): string {
  let processed = content

  // 处理 [   ] 方框填空（2 个空格以上）
  processed = processed.replace(/\[ {2,}\]/g, '<span class="blank-box"></span>')

  // 处理带空格的括号（全角）- 支持 answer_width 控制宽度
  processed = processed.replace(/（ {2,}）/g, () => {
    if (answerWidth) {
      return `（<span class="answer-placeholder" style="width: ${answerWidth}px; min-width: ${answerWidth}px; display: inline-block; border-bottom: 1px dotted currentColor;"></span>）`
    }
    return '（<span class="answer-placeholder"></span>）'
  })
  // 处理带空格的半角括号 - 支持 answer_width 控制宽度
  processed = processed.replace(/\( {2,}\)/g, () => {
    if (answerWidth) {
      return `(<span class="answer-placeholder" style="width: ${answerWidth}px; min-width: ${answerWidth}px; display: inline-block; border-bottom: 1px dotted currentColor;"></span>)`
    }
    return '(<span class="answer-placeholder"></span>)'
  })
  // 处理完全空的括号
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
 * 完整的 Markdown 渲染函数
 *
 * 优化：如果没有 Markdown 语法，只处理特殊格式并保留 LaTeX 原样，
 * 让 MathJax 直接渲染公式，避免 markdown-it 干扰
 *
 * @param content 要渲染的内容
 * @param answerWidth 作答区域宽度（从 rendering_meta.answer_width 获取）
 */
export function renderMarkdown(content: string, answerWidth?: number): string {
  if (!content || typeof content !== 'string') return ''

  // 如果没有 Markdown 语法，只处理特殊格式，不经过 markdown-it
  if (!hasMarkdownSyntax(content)) {
    return processSpecialFormats(content, answerWidth)
  }

  // 有 Markdown 语法，需要完整处理
  const { content: protectedContent, placeholders } = protectMath(content)
  let processed = processSpecialFormats(protectedContent, answerWidth)
  processed = md.render(processed)
  return restoreMath(processed, placeholders)
}

/**
 * 渲染行内 Markdown 内容（不添加 <p> 标签）
 *
 * @param content 要渲染的内容
 * @param answerWidth 作答区域宽度（从 rendering_meta.answer_width 获取）
 */
export function renderInlineMarkdown(content: string, answerWidth?: number): string {
  if (!content || typeof content !== 'string') return ''
  if (!content.trim()) return ''

  // 如果没有 Markdown 语法，只处理特殊格式
  if (!hasMarkdownSyntax(content)) {
    return processSpecialFormats(content.replace(/[\r\n]+/g, ' '), answerWidth)
  }

  // 有 Markdown 语法，需要完整处理
  const singleLineContent = content.replace(/[\r\n]+/g, ' ')
  const { content: protectedContent, placeholders } = protectMath(singleLineContent)
  let processed = processSpecialFormats(protectedContent, answerWidth)
  processed = md.renderInline(processed)
  return restoreMath(processed, placeholders)
}
