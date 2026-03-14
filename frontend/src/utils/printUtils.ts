import { renderMarkdown } from './markdownProcessor'
import type { StructuredQuestion } from '@/types/structured'

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
 * 将结构化题目转换为 HTML
 */
function renderStructuredQuestions(questions: StructuredQuestion[], title: string): string {
  let html = `<h1 style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${title}</h1>`
  html += `<div style="height: 20px;"></div>`

  questions.forEach((question, index) => {
    const stemHtml = renderMarkdown(question.stem)
    const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    html += `<div style="margin-bottom: 24px; page-break-inside: avoid; padding: 16px; border: 1px solid #f0f0f0; border-radius: 12px;">`
    html += `<div style="font-weight: bold; margin-bottom: 12px; font-size: 14pt;"><span>${index + 1}. </span>${stemHtml}</div>`

    // 选项
    if (question.options && question.options.length > 0) {
      html += `<div style="margin-top: 12px; padding-left: 36px;">`
      question.options.forEach((opt, optIndex) => {
        const optionText = opt.replace(/^[A-D]\.\s*/, '')
        const optHtml = renderMarkdown(optionText)
        html += `<div style="margin: 8px 0; padding: 8px; background: #fafafa; border-radius: 8px;">`
        html += `<span style="font-weight: 600; color: #525252; margin-right: 8px;">${optionLabels[optIndex] || String.fromCharCode(65 + optIndex)}.</span>`
        html += `<span style="color: #262626;">${optHtml}</span>`
        html += `</div>`
      })
      html += `</div>`
    }

    // 阅读材料
    if (question.passage) {
      const passageText = question.passage.replace(/【阅读材料】/, '').replace(/【材料】/, '').trim()
      html += `<div style="margin: 16px 0; padding: 16px; background: #fff7ed; border-left: 4px solid #ff6b4a; border-radius: 8px;">`
      html += `<div style="font-weight: 600; color: #c2410c; margin-bottom: 8px;">阅读材料：</div>`
      html += `<div style="font-size: 10.5pt; line-height: 1.8; color: #262626;">${renderMarkdown(passageText)}</div>`
      html += `</div>`
    }

    // 子题目
    if (question.sub_questions && question.sub_questions.length > 0) {
      html += `<div style="margin-top: 16px; padding-left: 20px; border-left: 2px solid #f0f0f0;">`
      question.sub_questions.forEach((subQ, subIdx) => {
        const subStemHtml = renderMarkdown(subQ.stem)
        html += `<div style="margin-bottom: 12px; padding: 10px;">`
        html += `<div style="font-weight: bold;"><span>${subIdx + 1}. </span>${subStemHtml}</div>`
        if (subQ.options && subQ.options.length > 0) {
          html += `<div style="margin-top: 8px; padding-left: 24px;">`
          subQ.options.forEach((opt, optIndex) => {
            const optionText = opt.replace(/^[A-D]\.\s*/, '')
            html += `<div style="margin: 4px 0;"><span style="font-weight: 600;">${optionLabels[optIndex]}.</span> ${renderMarkdown(optionText)}</div>`
          })
          html += `</div>`
        }
        html += `</div>`
      })
      html += `</div>`
    }

    html += `</div>`
  })

  return html
}

/**
 * 打印试卷 - 使用 CSS @media print 实现
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
      contentHtml += `<div style="page-break-after: always; margin-top: 30px;"></div>`
      contentHtml += `<h2 style="font-size: 14pt; font-weight: bold; margin-top: 30px;">${defaultTitleText}-答案</h2>`
      contentHtml += `<div>${answersHtml}</div>`
    }
  } else if (markdown) {
    // 传统方式：从 markdown 解析
    const { questions: qs, answers: ans } = splitQuestionsAndAnswers(markdown)
    const titleMatch = qs.match(/^#\s+(.+)$/m)
    defaultTitleText = titleText || titleMatch?.[1] || defaultTitleText

    const questionsWithoutTitle = qs.replace(/^#\s+(.+)$/gm, '').trim()
    const questionsHtml = renderMarkdown(questionsWithoutTitle)
    const answersHtml = ans ? renderMarkdown(cleanAnswerText(ans)) : ''

    const titleHtml = `<h1 style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${defaultTitleText}</h1>`
    contentHtml = ans
      ? `${titleHtml}<div style="height: 20px;"></div><div>${questionsHtml}</div><div style="page-break-after: always;"></div><h2 style="font-size: 14pt; font-weight: bold; margin-top: 30px;">${defaultTitleText}-答案</h2><div>${answersHtml}</div>`
      : `${titleHtml}<div style="height: 20px;"></div><div>${questionsHtml}</div>`
  }

  // 创建打印容器
  const printContainer = document.createElement('div')
  printContainer.id = 'print-container'
  printContainer.className = 'question-print-mode'
  printContainer.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: white;
    z-index: 10000;
    padding: 20mm;
    box-sizing: border-box;
    overflow: auto;
    display: block !important;
  `

  document.body.appendChild(printContainer)
  printContainer.innerHTML = contentHtml

  // 等待 MathJax 重新渲染打印容器中的公式
  if (window.MathJax && window.MathJax.typesetPromise) {
    try {
      await window.MathJax.typesetPromise([printContainer])
    } catch (err) {
      console.error('[MathJax] 渲染失败:', err)
    }
  }

  // 添加延迟确保 DOM 完全渲染
  await new Promise(resolve => setTimeout(resolve, 300))

  // 立即调用打印，不显示遮罩层
  window.print()

  // 打印完成后移除容器
  setTimeout(() => {
    if (printContainer.parentNode) {
      document.body.removeChild(printContainer)
    }
  }, 100)
}
