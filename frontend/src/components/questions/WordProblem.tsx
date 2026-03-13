/**
 * 应用题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

export default function WordProblem({ question, index }: QuestionRendererProps) {
  return (
    <div className="question-item question-word-problem">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>
      <div className="answer-area">
        <span className="answer-placeholder">答：________________________</span>
      </div>
    </div>
  )
}
