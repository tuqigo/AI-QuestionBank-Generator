/**
 * 计算题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

export default function Calculation({ question, index }: QuestionRendererProps) {
  const html = renderMarkdown(question.stem)

  return (
    <div className="question-item question-calculation">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: html }} />
      </div>
      <div className="answer-area">
        <span className="answer-placeholder">解：________________________</span>
      </div>
    </div>
  )
}
