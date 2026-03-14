import { renderMarkdown } from './markdownProcessor'
import type { StructuredQuestion } from '@/types/question'
import '@/types/mathjax'

// 扩展 Window 类型，支持 mathJaxReady
declare global {
  interface Window {
    mathJaxReady?: boolean
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
function getQuestionTypeClass(type: string): string {
  const typeMap: Record<string, string> = {
    SINGLE_CHOICE: 'question-single-choice',
    MULTIPLE_CHOICE: 'question-multiple-choice',
    TRUE_FALSE: 'question-true-false',
    FILL_BLANK: 'question-fill-blank',
    CALCULATION: 'question-calculation',
    WORD_PROBLEM: 'question-word-problem',
    READ_COMP: 'question-read-comp',
    CLOZE: 'question-cloze',
    ESSAY: 'question-essay',
    GEOMETRY: 'question-geometry'
  }
  return typeMap[type] || 'question-item'
}

/**
 * 渲染选项 HTML
 */
function renderOptions(options: string[], startLabel: number = 0): string {
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
function renderSubQuestions(subQuestions: any[], mode: 'print' | 'render' = 'print'): string {
  const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

  return subQuestions.map((subQ, subIdx) => {
    const subStemHtml = renderMarkdown(subQ.stem)
    let html = `<div class="question-item question-sub" style="margin-bottom: 8px; padding: 0; background: transparent; box-shadow: none;">`
    html += `<div class="question-header" style="display: flex; align-items: baseline; gap: 6px; margin-bottom: 6px; flex-wrap: nowrap;">`
    html += `<span class="question-number" style="font-weight: bold; min-width: 24px; flex-shrink: 0; white-space: nowrap; font-size: 10.5pt; line-height: 1.8;">${subIdx + 1}. </span>`
    html += `<div class="question-stem" style="font-size: 10.5pt; line-height: 1.8;">${subStemHtml}</div>`
    html += `</div>`

    if (subQ.options && subQ.options.length > 0) {
      html += `<div class="question-options" style="margin-top: 6px; padding-left: 24px;">`
      subQ.options.forEach((opt: string, optIndex: number) => {
        const optionText = opt.replace(/^[A-D]\.\s*/, '')
        const label = optionLabels[optIndex] || String.fromCharCode(65 + optIndex)
        html += `<div class="option-item" style="margin: 4px 0; padding: 4px 0; background: transparent;">`
        html += `<span class="option-label" style="font-weight: 600; margin-right: 6px; font-size: 10.5pt; line-height: 1.8;">${label}.</span>`
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
function renderStructuredQuestions(questions: StructuredQuestion[], title: string): string {
  let html = `<h1 class="print-title" style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${title}</h1>`
  html += `<div style="height: 20px;"></div>`

  questions.forEach((question, index) => {
    const typeClass = getQuestionTypeClass(question.type)
    const stemHtml = renderMarkdown(question.stem)
    const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    // 题目容器 - 使用 CSS 类名
    html += `<div class="question-item ${typeClass}" style="margin-bottom: 12px; page-break-inside: avoid;">`

    // 题目头部 - 修复题号和题目换行问题（使用 baseline 对齐）
    html += `<div class="question-header" style="display: flex; align-items: baseline; gap: 6px; margin-bottom: 6px; flex-wrap: nowrap;">`
    html += `<span class="question-number" style="font-weight: bold; min-width: 24px; flex-shrink: 0; white-space: nowrap; font-size: 10.5pt; line-height: 1.8;">${index + 1}. </span>`
    html += `<div class="question-stem" style="flex: 1; font-size: 10.5pt; line-height: 1.8;">${stemHtml}</div>`
    html += `</div>`

    // 选项
    if (question.options && question.options.length > 0) {
      html += `<div class="question-options" style="margin-top: 8px; padding-left: 36px;">`
      question.options.forEach((opt, optIndex) => {
        const optionText = opt.replace(/^[A-D]\.\s*/, '')
        const optHtml = renderMarkdown(optionText)
        html += `<div class="option-item" style="margin: 4px 0; padding: 4px 0;">`
        html += `<span class="option-label" style="font-weight: 600; margin-right: 6px; font-size: 10.5pt; line-height: 1.8;">${optionLabels[optIndex] || String.fromCharCode(65 + optIndex)}.</span>`
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
  })

  return html
}

/**
 * 获取打印所需的完整 CSS 样式
 */
function getPrintStyles(): string {
  return `
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 20mm;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.6;
      color: #000;
    }

    /* CSS 变量定义 */
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
    }

    /* 分页控制 */
    @page {
      margin: 15mm;
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
    alert('没有可打印的内容')
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
    alert('打印初始化失败')
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
        <script id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"><\/script>
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
