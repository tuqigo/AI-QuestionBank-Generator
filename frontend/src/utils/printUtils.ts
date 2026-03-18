import { renderMarkdown } from './markdownProcessor'
import { toast } from '../hooks'
import type { StructuredQuestion } from '@/types/question'
import '@/types/mathjax'
import type { LayoutConfig } from '@/config/questionConfig'
import { QUESTION_TYPE_CONFIGS } from '@/config/questionConfig'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

// 挂载到 window 供后续使用
if (typeof window !== 'undefined') {
  ;(window as any).html2canvas = html2canvas
  ;(window as any).jspdf = { jsPDF }
}

/**
 * 检测是否为移动设备
 */
function isMobileDevice(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

/**
 * 移动端分享文件
 * @returns 'shared' 分享成功，'cancelled' 用户取消，'unsupported' 不支持
 */
async function shareFileOnMobile(file: Blob, filename: string): Promise<'shared' | 'cancelled' | 'unsupported'> {
  if (!isMobileDevice()) return 'unsupported'

  // 检查是否支持 Web Share API Level 2
  if (!navigator.share || !navigator.canShare) return 'unsupported'

  const fileToShare = new File([file], filename, { type: file.type })
  const shareData: ShareData = { files: [fileToShare] }

  // 检查是否可以分享
  if (!navigator.canShare(shareData)) return 'unsupported'

  try {
    await navigator.share(shareData)
    return 'shared'
  } catch (err) {
    // 用户取消分享
    if ((err as Error).name === 'AbortError') {
      console.log('[Share] 用户取消分享')
      return 'cancelled'
    }
    // 其他错误
    console.log('[Share] 分享失败:', err)
    return 'unsupported'
  }
}

/**
 * 分割题目和答案
 */
export function splitQuestionsAndAnswers(md: string): { questions: string; answers: string | null } {
  const idx = md.indexOf('## 答案')
  if (idx === -1) return { questions: md, answers: null }
  const questions = md.slice(0, idx).trim().replace(/<!--\s*PAGE_BREAK\s*-->/g, '')
  const answers = md.slice(idx).trim().replace(/<!--\s*PAGE_BREAK\s*-->/g, '')
  return { questions, answers }
}

/**
 * 计算题目数量 - 匹配行首数字加点号的格式
 */
export function countQuestions(questions: string): number {
  if (!questions || typeof questions !== 'string') return 0
  const matches = questions.match(/^\d+\./gm)
  return matches ? matches.length : 0
}

// 定义一个辅助函数来清理答案文本
function cleanAnswerText(text: string) {
  if (!text) return ''
  return text.replace(/\s*## 答案\s*/g, '')
}

/**
 * 获取题型对应的 CSS 类名
 */
export function getQuestionTypeClass(type: string): string {
  const typeMap: Record<string, string> = {
    SINGLE_CHOICE: 'question-single-choice',
    MULTIPLE_CHOICE: 'question-multiple-choice',
    TRUE_FALSE: 'question-true-false',
    FILL_BLANK: 'question-fill-blank',
    CALCULATION: 'question-calculation',
    ORAL_CALCULATION: 'question-oral-calculation',
    WORD_PROBLEM: 'question-word-problem',
    READ_COMP: 'question-read-comp',
    CLOZE: 'question-cloze',
    ESSAY: 'question-essay',
    GEOMETRY: 'question-geometry'
  }
  return typeMap[type] || 'question-item'
}

/**
 * 将题目按题型分组，连续相同题型归为一组
 */
function groupQuestionsByType(questions: StructuredQuestion[]): {
  type: string
  questions: StructuredQuestion[]
}[] {
  const groups: { type: string; questions: StructuredQuestion[] }[] = []

  for (const question of questions) {
    const lastGroup = groups[groups.length - 1]
    if (lastGroup && lastGroup.type === question.type) {
      lastGroup.questions.push(question)
    } else {
      groups.push({ type: question.type, questions: [question] })
    }
  }

  return groups
}

/**
 * 渲染单个题目 HTML
 */
function renderSingleQuestion(question: StructuredQuestion, index: number): string {
  const typeClass = getQuestionTypeClass(question.type)
  const stemHtml = renderMarkdown(question.stem)
  const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

  let html = `<div class="question-item ${typeClass}" style="margin-bottom: 12px; page-break-inside: avoid;">`

  // 题目头部
  html += `<div class="question-header" style="display: flex; align-items: baseline; gap: 4px; margin-bottom: 6px; flex-wrap: nowrap;">`
  html += `<span class="question-number" style="font-weight: bold; min-width: 20px; flex-shrink: 0; white-space: nowrap; font-size: 10.5pt; line-height: 1.8;">${index + 1}.</span>`
  html += `<div class="question-stem" style="flex: 1; font-size: 10.5pt; line-height: 1.8;">${stemHtml}</div>`
  html += `</div>`

  // 选项
  if (question.options && question.options.length > 0) {
    html += `<div class="question-options" style="margin-top: 8px; padding-left: 36px;">`
    question.options.forEach((opt, optIndex) => {
      const optionText = opt.replace(/^[A-D]\.\s*/, '')
      const optHtml = renderMarkdown(optionText)
      html += `<div class="option-item" style="margin: 4px 0; padding: 4px 0;">`
      html += `<span class="option-label" style="font-weight: 600; font-size: 10.5pt; line-height: 1.8;">${optionLabels[optIndex] || String.fromCharCode(65 + optIndex)}.</span>`
      html += `<span class="option-text" style="font-size: 10.5pt; line-height: 1.8;">${optHtml}</span>`
      html += `</div>`
    })
    html += `</div>`
  }

  // 阅读材料
  if (question.passage) {
    const passageText = question.passage.replace(/【阅读材料】/, '').replace(/【材料】/, '').trim()
    html += `<div class="passage-section" style="margin: 8px 0; padding: 8px; background: #fff7ed; border-left: 3px solid #ff6b4a; border-radius: 4px;">`
    html += `<div class="passage-content" style="font-size: 10.5pt; line-height: 1.8; color: #262626;">${renderMarkdown(passageText)}</div>`
    html += `</div>`
  }

  // 子题目
  if (question.sub_questions && question.sub_questions.length > 0) {
    html += `<div class="sub-questions" style="margin-top: 8px; padding-left: 20px; border-left: 2px solid #f0f0f0;">`
    html += renderSubQuestions(question.sub_questions)
    html += `</div>`
  }

  html += `</div>`
  return html
}

/**
 * 渲染网格布局的题目组
 */
function renderGridGroup(
  questions: StructuredQuestion[],
  startIndex: number,
  layout: LayoutConfig,
  mode: 'render' | 'print'
): string {
  const columns = layout.columns || 3
  const gap = layout.gap || '12px'
  const itemPadding = layout.itemPadding || '0'
  const itemBorder = layout.itemBorder || 'none'

  let html = `<div class="question-grid-container" style="display: grid; grid-template-columns: repeat(${columns}, 1fr); gap: ${gap}; margin-bottom: 12px;">`

  questions.forEach((question, i) => {
    const typeClass = getQuestionTypeClass(question.type)
    const stemHtml = renderMarkdown(question.stem)
    const globalIndex = startIndex + i

    html += `<div class="question-grid-item ${typeClass}" style="padding: ${itemPadding}; border: ${itemBorder}; page-break-inside: avoid;">`

    // 题目头部（网格模式下题号与题目在同一行）
    html += `<div class="question-header" style="display: flex; align-items: baseline; gap: 4px; margin-bottom: 6px; flex-wrap: nowrap;">`
    html += `<span class="question-number" style="font-weight: bold; min-width: 20px; flex-shrink: 0; white-space: nowrap; font-size: 10.5pt; line-height: 1.8;">${globalIndex + 1}.</span>`
    html += `<div class="question-stem" style="flex: 1; font-size: 10.5pt; line-height: 1.8;">${stemHtml}</div>`
    html += `</div>`

    // 选项（如果有）
    if (question.options && question.options.length > 0) {
      html += `<div class="question-options" style="margin-top: 8px; padding-left: 24px;">`
      const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
      question.options.forEach((opt, optIndex) => {
        const optionText = opt.replace(/^[A-D]\.\s*/, '')
        const optHtml = renderMarkdown(optionText)
        html += `<div class="option-item" style="margin: 4px 0; padding: 4px 0;">`
        html += `<span class="option-label" style="font-weight: 600; font-size: 10.5pt; line-height: 1.8;">${optionLabels[optIndex] || String.fromCharCode(65 + optIndex)}.</span>`
        html += `<span class="option-text" style="font-size: 10.5pt; line-height: 1.8;">${optHtml}</span>`
        html += `</div>`
      })
      html += `</div>`
    }

    html += `</div>`
  })

  html += `</div>`
  return html
}

/**
 * 渲染选项 HTML
 */
export function renderOptions(options: string[], startLabel: number = 0): string {
  const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
  return options.map((opt, idx) => {
    const optionText = opt.replace(/^[A-D]\.\s*/, '')
    const optHtml = renderMarkdown(optionText)
    const label = optionLabels[startLabel + idx] || String.fromCharCode(65 + startLabel + idx)
    return `<div class="option-item">` +
      `<span class="option-label">${label}. </span>` +
      `<span class="option-text">${optHtml}</span>` +
      `</div>`
  }).join('')
}

/**
 * 渲染子题目 HTML
 */
export function renderSubQuestions(subQuestions: any[], mode: 'print' | 'render' = 'print'): string {
  const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

  return subQuestions.map((subQ, subIdx) => {
    const subStemHtml = renderMarkdown(subQ.stem)
    let html = `<div class="question-item question-sub" style="margin-bottom: 8px; padding: 0; background: transparent; box-shadow: none;">`
    html += `<div class="question-header" style="display: flex; align-items: baseline; gap: 4px; margin-bottom: 6px; flex-wrap: nowrap;">`
    html += `<span class="question-number" style="font-weight: bold; min-width: 20px; flex-shrink: 0; white-space: nowrap; font-size: 10.5pt; line-height: 1.8;">${subIdx + 1}.</span>`
    html += `<div class="question-stem" style="font-size: 10.5pt; line-height: 1.8;">${subStemHtml}</div>`
    html += `</div>`

    if (subQ.options && subQ.options.length > 0) {
      html += `<div class="question-options" style="margin-top: 6px; padding-left: 24px;">`
      subQ.options.forEach((opt: string, optIndex: number) => {
        const optionText = opt.replace(/^[A-D]\.\s*/, '')
        const label = optionLabels[optIndex] || String.fromCharCode(65 + optIndex)
        html += `<div class="option-item" style="margin: 4px 0; padding: 4px 0; background: transparent;">`
        html += `<span class="option-label" style="font-weight: 600; font-size: 10.5pt; line-height: 1.8;">${label}.</span>`
        html += `<span class="option-text" style="font-size: 10.5pt; line-height: 1.8;">${renderMarkdown(optionText)}</span>`
        html += `</div>`
      })
      html += `</div>`
    }

    html += `</div>`
    return html
  }).join('')
}

/**
 * 将结构化题目转换为 HTML（打印优化版本）
 */
export function renderStructuredQuestions(questions: StructuredQuestion[], title: string): string {
  let html = `<h1 class="print-title" style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${title}</h1>`
  html += `<div style="height: 20px;"></div>`

  // 1. 按题型分组
  const groups = groupQuestionsByType(questions)
  let globalIndex = 0

  groups.forEach(group => {
    // 获取题型配置
    const config = QUESTION_TYPE_CONFIGS[group.type as keyof typeof QUESTION_TYPE_CONFIGS]
    const printConfig = config?.print
    const layout = printConfig?.layout

    if (layout?.type === 'grid') {
      // 2. 有 grid 配置，使用网格布局
      html += renderGridGroup(group.questions, globalIndex, layout, 'print')
    } else {
      // 3. 无配置，使用默认渲染
      group.questions.forEach((q, i) => {
        html += renderSingleQuestion(q, globalIndex + i)
      })
    }

    globalIndex += group.questions.length
  })

  return html
}

/**
 * 获取打印所需的完整 CSS 样式
 */
export function getPrintStyles(): string {
  return `
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.6;
      color: #000;
    }

    /* 打印预览容器 - 屏幕预览时的内边距 */
    .print-preview-container {
      padding: 12px;
      max-width: 100%;
    }

    /* CSS 变量定义 - 统一预览和打印的样式 */
    .question-print-mode {
      --question-padding: 0;
      --question-margin-bottom: 12px;
      --question-background: transparent;
      --question-border: none;
      --question-box-shadow: none;
      --question-border-radius: 0;
      --question-number-font-weight: bold;
      --question-number-color: #000;
      --question-number-min-width: 24px;
      --question-stem-font-size: 10.5pt;
      --question-stem-line-height: 1.8;
      --question-stem-color: #000;
      --option-background: transparent;
      --option-border-radius: 0;
      --option-padding: 0;
      --option-margin: 4px 0;
      --option-label-font-weight: bold;
      --option-text-color: #000;
      --answer-area-background: transparent;
      --answer-area-min-height: 40px;
      --answer-area-border-radius: 0;
      --answer-area-margin-top: 8px;
      --answer-placeholder-color: #000;
      --answer-placeholder-style: solid;
      --answer-placeholder-width: 200px;
      --passage-background: transparent;
      --passage-border-left: 2px solid #000;
      --passage-padding: 8px 0;
      --passage-title-color: #000;
      --passage-title-font-size: 10.5pt;
      --essay-line-height: 28px;
      --essay-line-border: 1px dashed #999;
      --essay-line-number-width: 20px;
      --essay-line-number-font-size: 6pt;
    }

    /* 题目容器 */
    .question-item {
      margin-bottom: var(--question-margin-bottom);
      padding: var(--question-padding);
      background: var(--question-background);
      border: var(--question-border);
      box-shadow: var(--question-box-shadow);
      border-radius: var(--question-border-radius);
      page-break-inside: avoid;
    }

    .question-header {
      display: flex;
      align-items: baseline;
      gap: 6px;
      margin-bottom: 6px;
      flex-wrap: nowrap;
    }

    .question-number {
      font-weight: var(--question-number-font-weight);
      color: var(--question-number-color);
      min-width: var(--question-number-min-width);
      flex-shrink: 0;
      white-space: nowrap;
      font-size: 10.5pt;
      line-height: 1.8;
    }

    .question-stem {
      flex: 1;
      font-size: 10.5pt;
      line-height: 1.8;
      color: var(--question-stem-color);
      display: inline;
    }

    .question-stem > p {
      display: inline !important;
      margin: 0 !important;
    }

    .question-stem > * {
      display: inline !important;
      margin: 0 !important;
    }

    .question-options {
      padding-left: 36px;
    }

    .option-item {
      margin: 4px 0;
      padding: 4px 0;
      background: var(--option-background);
      border-radius: var(--option-border-radius);
      display: flex;
      align-items: baseline;
      gap: 6px;
    }

    .option-label {
      font-weight: var(--option-label-font-weight);
      min-width: 24px;
      font-size: 10.5pt;
      line-height: 1.8;
    }

    .option-text {
      flex: 1;
      color: var(--option-text-color);
      line-height: 1.6;
      display: inline;
    }

    .option-text > p {
      display: inline !important;
      margin: 0 !important;
    }

    .option-text > * {
      display: inline !important;
      margin: 0 !important;
    }

    /* 填空题 */
    .question-fill-blank .answer-line {
      margin-top: 8px;
    }

    .answer-placeholder {
      display: inline-block;
      min-width: var(--answer-placeholder-width);
      border-bottom: 1px var(--answer-placeholder-style) var(--answer-placeholder-color);
    }

    /* 口算题作答区域 - 括号中间的空白区域 */
    .answer-blank {
      display: inline-block;
      min-width: 40px;
    }

    /* 答案区域 */
    .answer-area {
      margin-top: var(--answer-area-margin-top);
      min-height: var(--answer-area-min-height);
    }

    /* 阅读材料 */
    .passage-section {
      margin: 12px 0;
      padding: 8px 0;
      background: var(--passage-background);
      border-left: var(--passage-border-left);
    }

    .passage-content {
      font-size: 10.5pt;
      line-height: 1.8;
    }

    .sub-questions {
      padding-left: 20px;
      border-left: 1px solid #ddd;
    }

    /* 网格布局样式 */
    .question-grid-container {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .question-grid-item {
      padding: 8px;
      border: 1px solid #000;
      page-break-inside: avoid;
    }

    /* 判断题选项横向排列 */
    .question-print-mode.question-true-false .question-options {
      display: flex;
      gap: 24px;
    }

    /* 作文格子 */
    .essay-grid {
      margin-top: 12px;
    }

    .essay-line {
      height: var(--essay-line-height);
      border-bottom: var(--essay-line-border);
      display: flex;
    }

    .line-number {
      width: var(--essay-line-number-width);
      font-size: var(--essay-line-number-font-size);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* 打印标题 */
    .print-title {
      text-align: center;
      margin-bottom: 30px;
      font-size: 18pt;
      font-weight: bold;
    }

    /* 答案部分 */
    .answers-section {
      page-break-before: always;
      margin-top: 30px;
    }

    .answers-title {
      font-size: 14pt;
      font-weight: bold;
      margin-top: 30px;
      margin-bottom: 16px;
    }

    .answers-content {
      font-size: 10.5pt;
      line-height: 1.8;
    }

    .answers-content > p {
      display: inline !important;
      margin: 0 !important;
    }

    .answers-content > * {
      display: inline !important;
      margin: 0 !important;
    }

    /* 数学公式 */
    mjx-container {
      display: inline !important;
      font-size: 1em !important;
      break-inside: avoid !important; /* 避免公式在分页时被切断（如分数） */
    }

    /* 分页控制 */
    @page {
      margin: 15mm 20mm;
      margin-bottom: 25mm; /* 增加底部边距，避免 Safari 页脚切断页码 */
    }

    @page :first {
      margin-top: 20mm; /* 第一页顶部增加边距，避开浏览器页眉 */
    }

    @media print {
      body {
        padding: 0;
      }

      .question-item {
        page-break-inside: avoid;
      }

      .essay-line {
        break-inside: avoid;
      }
    }
  `
}

/**
 * 打印试卷 - 使用 iframe 实现隔离的打印环境
 *
 * @param markdown - 完整的 markdown 内容（向后兼容，可选）
 * @param titleText - 试卷标题（可选）
 * @param questions - 结构化题目数据（新方式）
 * @param answers - 答案 markdown（可选）
 */
export const handlePrint = async (
  markdown?: string,
  titleText?: string,
  questions?: StructuredQuestion[],
  answers?: string | null
) => {
  // 验证输入
  if (!markdown && (!questions || questions.length === 0)) {
    console.error('[handlePrint] 没有可打印的内容')
    toast.error('没有可打印的内容')
    return
  }

  let defaultTitleText = titleText || '练习题'
  let contentHtml = ''

  // 优先使用结构化数据
  if (questions && questions.length > 0) {
    contentHtml = renderStructuredQuestions(questions, defaultTitleText)

    // 如果有答案，添加到后面
    if (answers) {
      const answersHtml = renderMarkdown(cleanAnswerText(answers))
      contentHtml += `<div class="answers-section" style="page-break-before: always; margin-top: 30px;"></div>`
      contentHtml += `<h2 class="answers-title" style="font-size: 14pt; font-weight: bold; margin-top: 30px;">${defaultTitleText}-答案</h2>`
      contentHtml += `<div class="answers-content">${answersHtml}</div>`
    }
  } else if (markdown) {
    // 传统方式：从 markdown 解析
    const { questions: qs, answers: ans } = splitQuestionsAndAnswers(markdown)
    const titleMatch = qs.match(/^#\s+(.+)$/m)
    defaultTitleText = titleText || titleMatch?.[1] || defaultTitleText

    const questionsWithoutTitle = qs.replace(/^#\s+(.+)$/gm, '').trim()
    const questionsHtml = renderMarkdown(questionsWithoutTitle)
    const answersHtml = ans ? renderMarkdown(cleanAnswerText(ans)) : ''

    const titleHtml = `<h1 class="print-title" style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${defaultTitleText}</h1>`
    contentHtml = ans
      ? `${titleHtml}<div style="height: 20px;"></div><div>${questionsHtml}</div><div style="page-break-after: always;"></div><h2 class="answers-title" style="font-size: 14pt; font-weight: bold; margin-top: 30px;">${defaultTitleText}-答案</h2><div class="answers-content">${answersHtml}</div>`
      : `${titleHtml}<div style="height: 20px;"></div><div>${questionsHtml}</div>`
  }

  // 创建 iframe 用于打印
  const printFrame = document.createElement('iframe')
  printFrame.style.cssText = 'position:absolute;width:0;height:0;border:none;visibility:hidden;'
  document.body.appendChild(printFrame)

  const printDoc = printFrame.contentDocument || printFrame.contentWindow?.document
  if (!printDoc) {
    console.error('[handlePrint] 无法创建打印文档')
    document.body.removeChild(printFrame)
    toast.error('打印初始化失败')
    return
  }

  // 写入完整的 HTML 文档（包含 MathJax 配置）
  printDoc.open()
  printDoc.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>打印 - ${defaultTitleText}</title>
        <style>${getPrintStyles()}</style>
        <script>
          window.MathJax = {
            tex: {
              inlineMath: [['$', '$'], ['\\(', '\\)']],
              displayMath: [['$$', '$$'], ['\\[', '\\]']],
              processEscapes: true,
              processEnvironments: true,
              packages: ['base', 'ams', 'require']
            },
            options: {
              skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
              ignoreHtmlClass: 'tex2jax_ignore'
            },
            startup: {
              typeset: false,
              ready: function() {
                // MathJax 加载完成后回调
                window.MathJax.startup.defaultReady();
                // 标记 MathJax 已就绪
                window.mathJaxReady = true;
              }
            }
          };
        <\/script>
        <script id="MathJax-script" src="/mathjax@4.1.1/tex-mml-chtml.js"><\/script>
      </head>
      <body class="question-print-mode">
        ${contentHtml}
      </body>
    </html>
  `)
  printDoc.close()

  // 等待 iframe 内容加载完成
  await new Promise<void>((resolve) => {
    if (printFrame.onload) {
      printFrame.onload = () => resolve()
    } else {
      // 如果没有 onload 事件，使用延迟
      setTimeout(resolve, 100)
    }
  })

  // 等待 MathJax 渲染 - 使用更可靠的等待方式
  const printWindow = printFrame.contentWindow
  await new Promise<void>((resolve) => {
    // 等待 mathJaxReady 标志
    const checkMathJax = () => {
      if (printWindow?.mathJaxReady && printWindow?.MathJax?.typesetPromise) {
        // MathJax 已就绪，开始渲染
        printWindow.MathJax.typesetPromise([printDoc.body])
          .then(() => {
            console.log('[Print] MathJax 渲染完成')
            resolve()
          })
          .catch((err) => {
            console.error('[Print] MathJax 渲染失败:', err)
            resolve() // 即使失败也继续
          })
      } else {
        // 还未就绪，继续等待
        setTimeout(checkMathJax, 50)
      }
    }
    // 最多等待 10 秒
    const timeout = setTimeout(() => {
      console.warn('[Print] MathJax 等待超时')
      resolve()
    }, 10000)

    checkMathJax()
  })

  // 额外延迟确保内容完全渲染
  await new Promise(resolve => setTimeout(resolve, 300))

  // 调用打印
  printWindow?.print()

  // 打印完成后清理
  setTimeout(() => {
    if (printFrame.parentNode) {
      document.body.removeChild(printFrame)
    }
  }, 500)
}

/**
 * 下载 PDF - 使用 html2canvas + jsPDF 将渲染后的 HTML 转换为 PDF
 *
 * @param questions - 结构化题目数据
 * @param titleText - 试卷标题
 * @param answers - 答案 markdown（可选）
 * @returns 是否成功
 */
export const handleDownloadPDF = async (
  questions: StructuredQuestion[],
  titleText?: string,
  answers?: string | null
): Promise<boolean> => {
  if (!questions || questions.length === 0) {
    toast.error('没有可下载的内容')
    return false
  }

  try {
    const defaultTitleText = titleText || '练习题'

    // 2. 生成 HTML 内容
    let contentHtml = renderStructuredQuestions(questions, defaultTitleText)

    // 如果有答案，添加到后面
    if (answers) {
      const answersHtml = renderMarkdown(cleanAnswerText(answers))
      contentHtml += `<div class="answers-section" style="page-break-before: always; margin-top: 30px;"></div>`
      contentHtml += `<h2 class="answers-title" style="font-size: 14pt; font-weight: bold; margin-top: 30px;">${defaultTitleText}-答案</h2>`
      contentHtml += `<div class="answers-content">${answersHtml}</div>`
    }

    // 3. 创建临时容器 - 隐藏在视口之外
    const container = document.createElement('div')
    container.className = 'question-print-mode pdf-container'
    container.innerHTML = contentHtml
    // 隐藏在视口外，避免闪烁
    container.style.cssText = 'position: absolute; left: -9999px; top: -9999px; width: 794px; padding: 20px; background: white;'
    document.body.appendChild(container)

    console.log('[PDF] 容器已创建，innerHTML length:', container.innerHTML.length)
    console.log('[PDF] 题目数量:', questions.length)

    // 4. 等待 MathJax 渲染
    await new Promise<void>((resolve) => {
      const checkMathJax = () => {
        if (window.MathJax?.typesetPromise) {
          window.MathJax.typesetPromise([container])
            .then(() => {
              console.log('[PDF] MathJax 渲染完成')
              resolve()
            })
            .catch((err) => {
              console.error('[PDF] MathJax 渲染失败:', err)
              resolve()
            })
        } else {
          setTimeout(checkMathJax, 50)
        }
      }
      // 最多等待 10 秒
      const timeout = setTimeout(() => {
        console.warn('[PDF] MathJax 等待超时')
        resolve()
      }, 10000)
      checkMathJax()
    })

    // 额外延迟确保内容完全渲染
    await new Promise(resolve => setTimeout(resolve, 1500))

    // 检查容器内容
    console.log('[PDF] 渲染后容器内容:', container.innerHTML.substring(0, 200))
    console.log('[PDF] 容器子元素数量:', container.children.length)

    // 5. 使用 html2canvas 捕获容器 - 提升清晰度
    console.log('[PDF] 开始 html2canvas 捕获...')

    if (!window.html2canvas) {
      throw new Error('html2canvas 未加载')
    }

    // 提升清晰度：scale = Math.min(3, devicePixelRatio * 2)
    const scale = Math.min(3, (window.devicePixelRatio || 1) * 2)
    console.log('[PDF] 使用 scale:', scale)

    const canvas = await window.html2canvas(container, {
      scale: scale,
      useCORS: true,
      letterRendering: true,
      allowTaint: false,
      logging: false,
      backgroundColor: '#ffffff'
    })

    console.log('[PDF] html2canvas 完成，canvas 尺寸:', canvas.width, 'x', canvas.height)

    // 6. 创建 PDF
    const imgData = canvas.toDataURL('image/jpeg', 0.95)

    if (!window.jspdf) {
      throw new Error('jsPDF 未加载')
    }

    const pdf = new window.jspdf.jsPDF({
      unit: 'mm',
      format: 'a4',
      orientation: 'portrait'
    })

    const pdfWidth = 210 // A4 宽度 (mm)
    const pdfHeight = 297 // A4 高度 (mm)
    const imgWidth = pdfWidth - 20 // 减去左右各 10mm 边距
    const imgHeight = (canvas.height / canvas.width) * imgWidth

    let heightLeft = imgHeight
    let position = 10 // 从顶部 10mm 开始（留出页眉位置）

    // 第一页 - 添加 10mm 左边距
    pdf.addImage(imgData, 'JPEG', 10, position, imgWidth, imgHeight, undefined, 'FAST')
    heightLeft -= pdfHeight

    // 如果内容超出一页，添加更多页面
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'JPEG', 10, position, imgWidth, imgHeight, undefined, 'FAST')
      heightLeft -= pdfHeight
    }

    // 7. 转换为 PDF 二进制数据
    const pdfData = (pdf as any).output('arraybuffer') as ArrayBuffer
    const filename = `${defaultTitleText}.pdf`

    // 8. 尝试移动端分享
    const pdfBlob = new Blob([pdfData], { type: 'application/pdf' })
    const shareResult = await shareFileOnMobile(pdfBlob, filename)

    if (shareResult === 'shared') {
      console.log('[PDF] 已通过系统分享')
      return true  // 分享成功后直接返回，不再执行下载
    }

    if (shareResult === 'cancelled') {
      console.log('[PDF] 用户取消分享')
      return false  // 用户取消，不执行下载
    }

    // unsupported: 桌面端或不支持分享，执行下载
    pdf.save(filename)
    console.log('[PDF] PDF 保存完成')

    return true
  } catch (error) {
    console.error('[PDF] 下载失败:', error)
    toast.error('PDF 下载失败：' + (error as Error).message)
    return false
  } finally {
    // 9. 清理临时容器
    const container = document.querySelector('.pdf-container')
    if (container) {
      document.body.removeChild(container)
    }
  }
}
