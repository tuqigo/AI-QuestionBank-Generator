/**
 * 作文题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

export default function Essay({ question, index }: QuestionRendererProps) {
  return (
    <div className="question-item question-essay">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>
      <div className="answer-area essay-answer">
        <div className="essay-grid">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="essay-line">
              <span className="line-number">{(i + 1).toString().padStart(2, '0')}</span>
              <span className="answer-placeholder">________________________________________</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
