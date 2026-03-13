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
  const placeholders = new Map<string, string>();
  let idx = 0;

  // 保护 $$...$$ (display math) - 先处理 display math，避免被 inline 匹配
  content = content.replace(/\$\$((?:[^$]|\\\$)+?)\$\$/g, (match, math) => {
    // 使用特殊占位符格式，避免被 markdown 处理
    const placeholder = `\u0002MATH_DISPLAY_${idx++}\u0003`;
    placeholders.set(placeholder, match);
    return placeholder;
  });

  // 保护 $...$ (inline math)
  // 匹配 $...$ 内容，允许内部包含转义字符（如 \\% \\frac 等）
  // 使用 [^$] 匹配任何非$字符（包括反斜杠）
  content = content.replace(/(?<!\$)\$((?:[^$]|\$(?!\$))+?)\$(?!\$)/g, (match, math) => {
    // 使用特殊占位符格式，避免被 markdown 处理
    const placeholder = `\u0002MATH_INLINE_${idx++}\u0003`;
    placeholders.set(placeholder, `$${math}$`);
    return placeholder;
  });

  return { content, placeholders };
}

/**
 * 恢复被保护的数学内容
 */
function restoreMath(content: string, placeholders: Map<string, string>): string {
  for (const [placeholder, original] of placeholders) {
    // 转义占位符中的特殊字符，确保正则表达式正确匹配
    const escapedPlaceholder = placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escapedPlaceholder, 'g');
    content = content.replace(regex, original);
  }
  return content;
}

/**
 * 处理 markdown 中的特殊符号，将其转换为带样式的 HTML
 * 主要处理填空、分数等特殊格式
 */
export function processMarkdown(mdContent: string): string {
  if (!mdContent || typeof mdContent !== 'string') return '';

  let processed = mdContent;

  // 保护数学内容（使用局部 Map，避免多次调用冲突）
  const { content: protectedContent, placeholders } = protectMath(processed);
  processed = protectedContent;

  // 处理 [   ] 方框填空（2 个空格以上）- 在 markdown-it 之前处理
  processed = processed.replace(/\[ {2,}\]/g, '<span class="blank-box"></span>');

  // 处理带空格的括号（全角）- 将空格转为 &nbsp;
  processed = processed.replace(/（ {2,}）/g, (match) => {
    const spaces = match.slice(1, -1);
    const nbsp = '\u00a0'.repeat(spaces.length);
    return `（${nbsp}）`;
  });

  // 处理带空格的半角括号 - 将空格转为 &nbsp;
  processed = processed.replace(/\( {2,}\)/g, (match) => {
    const spaces = match.slice(1, -1);
    const nbsp = '\u00a0'.repeat(spaces.length);
    return `(${nbsp})`;
  });

  // 只处理完全空的括号（全角）
  processed = processed.replace(/（）/g, '<span class="blank-parentheses"></span>');

  // 只处理完全空的半角括号
  processed = processed.replace(/\(\)/g, '<span class="blank-parentheses"></span>');

  // 渲染 markdown
  processed = md.render(processed);

  // 恢复数学内容
  processed = restoreMath(processed, placeholders);

  return processed;
}

/**
 * 完整的 Markdown 渲染函数，包含特殊格式处理和保护数学内容
 */
export function renderMarkdown(content: string): string {
  return processMarkdown(content)
}

/**
 * 渲染用于打印的 Markdown 内容
 */
export function renderMarkdownForPrinting(content: string): string {
  return renderMarkdown(content);
}

/**
 * 渲染用于 PDF 导出的 Markdown 内容（已移除 PDF 功能，此函数保留用于兼容）
 */
export function renderMarkdownForPdf(content: string): string {
  return renderMarkdown(content);
}

/**
 * 渲染行内 Markdown 内容（不添加 <p> 标签）
 * 用于题目、选项等需要在同一行显示的场景
 */
export function renderInlineMarkdown(content: string): string {
  if (!content || typeof content !== 'string') return ''

  // 直接返回空字符串
  if (!content.trim()) return ''

  // 保护数学内容
  const { content: protectedContent, placeholders } = protectMath(content)

  // 处理特殊格式（填空、括号等）
  let processed = protectedContent
  processed = processed.replace(/\[ {2,}\]/g, '<span class="blank-box"></span>')
  processed = processed.replace(/（ {2,}）/g, (match) => {
    const spaces = match.slice(1, -1)
    const nbsp = '\u00a0'.repeat(spaces.length)
    return `（${nbsp}）`
  })
  processed = processed.replace(/\( {2,}\)/g, (match) => {
    const spaces = match.slice(1, -1)
    const nbsp = '\u00a0'.repeat(spaces.length)
    return `(${nbsp})`
  })
  processed = processed.replace(/（）/g, '<span class="blank-parentheses"></span>')
  processed = processed.replace(/\(\)/g, '<span class="blank-parentheses"></span>')

  // 使用 renderInline 避免添加 <p> 标签，但需要配置 md 实例
  // 禁用常规的包装
  processed = md.renderInline(processed)

  // 恢复数学内容
  processed = restoreMath(processed, placeholders)

  // 强制移除外层 <p> 标签（如果 renderInline 仍然添加了）
  // 使用正则移除开头的 <p> 和结尾的 </p>
  processed = processed.replace(/^<p>(.+?)<\/p>$/s, '$1')

  return processed
}
