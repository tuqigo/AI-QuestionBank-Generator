/**
 * 判断题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

export default function TrueFalse({ question, index }: QuestionRendererProps) {
  return (
    <div className="question-item question-true-false">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>
      <div className="question-options">
        <div className="option-item">
          <span className="option-label">A. </span>
          <span className="option-text">正确</span>
        </div>
        <div className="option-item">
          <span className="option-label">B. </span>
          <span className="option-text">错误</span>
        </div>
      </div>
    </div>
  )
}
