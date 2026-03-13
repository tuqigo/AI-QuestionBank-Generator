import { renderMarkdown } from './markdownProcessor'

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
  if (!text) return '';
  return text.replace(/\s*## 答案\s*/g, '');
}

/**
 * 打印试卷 - 使用 CSS @media print 实现，无需额外容器
 * @param markdown - 完整的 markdown 内容
 * @param titleText - 试卷标题（可选）
 */
export const handlePrint = async (markdown: string, titleText?: string) => {
  if (!markdown) return

  const { questions, answers } = splitQuestionsAndAnswers(markdown)

  // 提取 AI 生成的标题
  const titleMatch = questions.match(/^#\s+(.+)$/m)
  const defaultTitleText = titleText || titleMatch?.[1] || '练习题'

  // 移除题目中的# 标题，避免重复显示
  const questionsWithoutTitle = questions.replace(/^#\s+(.+)$/gm, '').trim()
  const questionsHtml = renderMarkdown(questionsWithoutTitle)
  const answersHtml = answers ? renderMarkdown(cleanAnswerText(answers)) : '';

  // 创建打印专用容器（隐藏在原页面中）
  const printContainer = document.createElement('div')
  printContainer.id = 'print-container'
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
    overflow: visible;
  `

  const titleHtml = `<h1 style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${defaultTitleText}</h1>`
  const contentHtml = answers
    ? `${titleHtml}<div style="height: 20px;"></div><div>${questionsHtml}</div><div style="page-break-after: always;"></div><h2 style="font-size: 14pt; font-weight: bold; margin-top: 30px;">${defaultTitleText}-答案</h2><div>${answersHtml}</div>`
    : `${titleHtml}<div style="height: 20px;"></div><div>${questionsHtml}</div>`

  printContainer.innerHTML = contentHtml
  document.body.appendChild(printContainer)

  // 等待 MathJax 重新渲染打印容器中的公式
  if (window.MathJax && window.MathJax.typesetPromise) {
    await window.MathJax.typesetPromise([printContainer])
  }

  // 立即调用打印，不显示遮罩层
  window.print()

  // 打印完成后移除容器
  setTimeout(() => {
    document.body.removeChild(printContainer)
  }, 100)
}
