/**
 * 应用题组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface WordProblemProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function WordProblem({ question, index, mode = 'render' }: WordProblemProps) {
  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-word-problem ${modeClass}`}>
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
      </div>
      <div className="answer-area">
        <span className="answer-placeholder">答：________________________</span>
      </div>
    </div>
  )
}
