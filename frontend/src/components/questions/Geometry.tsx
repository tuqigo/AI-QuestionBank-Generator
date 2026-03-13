/**
 * 几何题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

export default function Geometry({ question, index }: QuestionRendererProps) {
  return (
    <div className="question-item question-geometry">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>
      <div className="answer-area">
        <span className="answer-placeholder">解：________________________</span>
      </div>
    </div>
  )
}
