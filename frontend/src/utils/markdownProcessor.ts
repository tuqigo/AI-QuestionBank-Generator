import MarkdownIt from 'markdown-it';

// 创建 markdown-it 实例，配置选项
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
});

/**
 * 处理 markdown 中的特殊符号，将其转换为带样式的 HTML
 * 主要处理填空、分数等特殊格式
 */
export function processMarkdown(mdContent: string): string {
  if (!mdContent || typeof mdContent !== 'string') return '';

  let processed = mdContent;

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

  return processed;
}

/**
 * 完整的 Markdown 渲染函数，包含特殊格式处理
 */
export function renderMarkdown(content: string): string {
  const processedContent = processMarkdown(content);
  return md.render(processedContent);
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
