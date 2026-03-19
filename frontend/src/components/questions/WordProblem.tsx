/**
 * 应用题组件
 */
import { QuestionRendererProps, StructuredQuestion } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface WordProblemProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function WordProblem({ question, index, mode = 'render' }: WordProblemProps) {
  // 从 rendering_meta 获取是否显示题号和作答行数
  const showQuestionNumber = (question as StructuredQuestion).rendering_meta?.show_question_number
  const rowsToAnswer = (question as StructuredQuestion).rendering_meta?.rows_to_answer || 5

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-word-problem ${modeClass}`}>
      <div className="question-header">
        {showQuestionNumber !== false && (
          <span className="question-number">{index}. </span>
        )}
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
      </div>
      <div className="answer-area" style={{ minHeight: `${rowsToAnswer * 30}px` }}>
        <span className="answer-placeholder">答：________________________</span>
      </div>
    </div>
  )
}
