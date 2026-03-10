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

/**
 * 打印试卷
 * @param markdown - 完整的 markdown 内容
 * @param titleText - 试卷标题（可选，默认为从 markdown 提取或'练习题'）
 */
export const handlePrint = async (markdown: string, titleText?: string) => {
  if (!markdown) return

  const { questions, answers } = splitQuestionsAndAnswers(markdown)

  // 提取 AI 生成的标题
  const titleMatch = questions.match(/^#\s+(.+)$/m)
  const defaultTitleText = titleText || titleMatch ? (titleMatch?.[1] || '练习题') : '练习题'

  // 移除题目中的# 标题，避免重复显示
  const questionsWithoutTitle = questions.replace(/^#\s+(.+)$/gm, '').trim()
  const questionsHtml = renderMarkdown(questionsWithoutTitle)
  const answersHtml = answers ? renderMarkdown(answers) : ''

  // 创建打印专用容器
  const printContainer = document.createElement('div')
  printContainer.id = 'print-container'
  printContainer.className = 'print-paper'

  const titleHtml = `<h1 class="print-title">${defaultTitleText}</h1>`
  const infoFields = `
    <div class="print-info-fields">
      <span>姓名：__________________</span>
      <span>班级：__________________</span>
      <span>得分：__________________</span>
    </div>
  `
  const contentHtml = answers
    ? `${titleHtml}${infoFields}<div class="print-questions">${questionsHtml}</div><div class="print-page-break"></div><h2 class="print-answers-title">答案</h2><div class="print-answers">${answersHtml}</div>`
    : `${titleHtml}${infoFields}<div class="print-questions">${questionsHtml}</div>`

  printContainer.innerHTML = contentHtml
  document.body.appendChild(printContainer)

  // 等待 MathJax 重新渲染打印容器中的公式
  if (window.MathJax && window.MathJax.typesetPromise) {
    await window.MathJax.typesetPromise([printContainer])
  }

  // 调用浏览器打印
  window.print()

  // 打印完成后移除容器
  setTimeout(() => {
    document.body.removeChild(printContainer)
  }, 500)
}
