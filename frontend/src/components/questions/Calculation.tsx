/**
 * 计算题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface CalculationProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function Calculation({ question, index, mode = 'render' }: CalculationProps) {
  const html = renderInlineMarkdown(question.stem)
  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-calculation ${modeClass}`}>
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
