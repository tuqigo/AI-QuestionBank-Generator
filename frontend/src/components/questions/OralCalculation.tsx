/**
 * 口算题组件
 * 直接显示题目，无需"解："答案区
 */
import { QuestionRendererProps } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface OralCalculationProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function OralCalculation({ question, index, mode = 'render' }: OralCalculationProps) {
  const html = renderInlineMarkdown(question.stem)
  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-oral-calculation ${modeClass}`}>
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    </div>
  )
}
