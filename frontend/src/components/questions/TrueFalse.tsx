/**
 * 判断题组件
 */
import type { QuestionRendererProps, StructuredQuestion } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface TrueFalseProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function TrueFalse({ question, index, mode = 'render' }: TrueFalseProps) {
  // 从 rendering_meta 获取是否显示题号
  const showQuestionNumber = (question as StructuredQuestion).rendering_meta?.show_question_number

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-true-false ${modeClass}`}>
      <div className="question-header">
        {showQuestionNumber !== false && (
          <span className="question-number">{index}. </span>
        )}
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
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
