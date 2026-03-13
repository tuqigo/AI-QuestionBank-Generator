/**
 * 填空题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

export default function FillBlank({ question, index }: QuestionRendererProps) {
  return (
    <div className="question-item question-fill-blank">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>
      <div className="answer-line">
        <span className="answer-placeholder">________________________</span>
      </div>
    </div>
  )
}
