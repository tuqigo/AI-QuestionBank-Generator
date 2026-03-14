/**
 * 填空题组件
 */
import type { QuestionRendererProps } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface FillBlankProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function FillBlank({ question, index, mode = 'render' }: FillBlankProps) {
  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-fill-blank ${modeClass}`}>
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
      </div>
      <div className="answer-line">
        <span className="answer-placeholder">________________________</span>
      </div>
    </div>
  )
}
