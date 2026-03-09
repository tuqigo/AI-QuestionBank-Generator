import { marked } from 'marked';

/**
 * 处理 markdown 中的特殊符号，将其转换为带样式的 HTML
 * 统一处理分数、小数、填空等特殊格式
 */
export function processMarkdown(md: string): string {
  if (!md || typeof md !== 'string') return '';

  let processed = md;

  // 处理分数格式：\frac{分子}{分母} -> <sup>分子</sup>⁄<sub>分母</sub>
  processed = processed.replace(/\\\\frac\{([^}]+)\}\{([^}]+)\}/g, '<sup>$1</sup>⁄<sub>$2</sub>');

  // 处理简单分数格式：1/2, 3/4 等 -> <sup>分子</sup>⁄<sub>分母</sub>
  processed = processed.replace(/\b(\d+)\/(\d+)\b/g, '<sup>$1</sup>⁄<sub>$2</sub>');

  // 处理小数 - 使用更精确的匹配，避免影响日期等
  processed = processed.replace(/(\d+)\.(\d+)/g, '$1.<small>$2</small>');

  // 处理 [○] 比较符号
  processed = processed.replace(/\[○\]/g, '<span class="comparison-circle">○</span>');

  // 处理 6 个或以上连续下划线作为填空横线
  processed = processed.replace(/_{6,}/g, (match) => {
    const width = Math.max(80, match.length * 8);
    return `<span class="blank-line" style="min-width: ${width}px"></span>`;
  });

  // 处理 [  ] 方框填空（2 个空格以上）
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

  // 将行首的题号（如"1. "）转换为带序号样式的格式
  // 匹配行首的数字加点号加空格，如"1. "、"10. "等
  processed = processed.replace(/^(\d+)\.\s+/gm, '<span class="question-number">$1.</span> ');

  return processed;
}

/**
 * 完整的 Markdown 渲染函数，包含特殊格式处理
 */
export function renderMarkdown(content: string): string {
  const processedContent = processMarkdown(content);
  return marked(processedContent, { async: false }) as string;
}

/**
 * 渲染用于打印的 Markdown 内容
 */
export function renderMarkdownForPrinting(content: string): string {
  return renderMarkdown(content);
}

/**
 * 渲染用于 PDF 导出的 Markdown 内容
 */
export function renderMarkdownForPdf(content: string): string {
  return renderMarkdown(content);
}