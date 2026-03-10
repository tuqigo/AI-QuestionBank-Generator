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

// 用于存储被保护的数学内容
let mathPlaceholders: Map<string, string> = new Map();

/**
 * 保护数学内容不被 markdown-it 处理
 */
function protectMath(content: string): string {
  mathPlaceholders.clear();
  let idx = 0;

  // 保护 $$...$$ (display math)
  content = content.replace(/\$\$([\s\S]*?)\$\$/g, (match, math) => {
    const placeholder = `MATH_DISPLAY_${idx++}`;
    mathPlaceholders.set(placeholder, match);
    return placeholder;
  });

  // 保护 $...$ (inline math) - 需要确保不是已经处理过的
  content = content.replace(/(?<!\$)\$([^\$]+?)\$(?!\$)/g, (match, math) => {
    const placeholder = `MATH_INLINE_${idx++}`;
    mathPlaceholders.set(placeholder, match);
    return placeholder;
  });

  return content;
}

/**
 * 恢复被保护的数学内容
 */
function restoreMath(content: string): string {
  for (const [placeholder, original] of mathPlaceholders) {
    content = content.replace(new RegExp(placeholder, 'g'), original);
  }
  mathPlaceholders.clear();
  return content;
}

/**
 * 处理 markdown 中的特殊符号，将其转换为带样式的 HTML
 * 主要处理填空、分数等特殊格式
 */
export function processMarkdown(mdContent: string): string {
  if (!mdContent || typeof mdContent !== 'string') return '';

  let processed = mdContent;

  // 保护数学内容
  processed = protectMath(processed);

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
  processed = restoreMath(processed);

  return processed;
}

/**
 * 完整的 Markdown 渲染函数，包含特殊格式处理和保护数学内容
 */
export function renderMarkdown(content: string): string {
  return processMarkdown(content);
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
