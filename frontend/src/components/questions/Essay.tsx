/**
 * 作文题组件
 */
import { QuestionRendererProps, StructuredQuestion } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface EssayProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function Essay({ question, index, mode = 'render' }: EssayProps) {
  // 从 rendering_meta 获取是否显示题号和作答行数
  const showQuestionNumber = (question as StructuredQuestion).rendering_meta?.show_question_number
  const rowsToAnswer = (question as StructuredQuestion).rendering_meta?.rows_to_answer || 10

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-essay ${modeClass}`}>
      <div className="question-header">
        {showQuestionNumber !== false && (
          <span className="question-number">{index}. </span>
        )}
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
      </div>
      <div className="answer-area essay-answer">
        <div className="essay-grid">
          {Array.from({ length: rowsToAnswer }).map((_, i) => (
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
