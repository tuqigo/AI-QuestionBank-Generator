/**
 * 计算题组件
 */
import { QuestionRendererProps, StructuredQuestion } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface CalculationProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function Calculation({ question, index, mode = 'render' }: CalculationProps) {
  // 从 rendering_meta 获取是否显示题号和作答行数
  const showQuestionNumber = (question as StructuredQuestion).rendering_meta?.show_question_number
  const rowsToAnswer = (question as StructuredQuestion).rendering_meta?.rows_to_answer || 2

  const html = renderInlineMarkdown(question.stem)
  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-calculation ${modeClass}`}>
      <div className="question-header">
        {showQuestionNumber !== false && (
          <span className="question-number">{index}. </span>
        )}
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: html }} />
      </div>
      <div className="answer-area" style={{ minHeight: `${rowsToAnswer * 30}px` }}>
        <span className="answer-placeholder">解：________________________</span>
      </div>
    </div>
  )
}
