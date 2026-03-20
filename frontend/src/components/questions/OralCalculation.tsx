/**
 * 口算题组件
 * 直接显示题目，无需"解："答案区
 */
import { QuestionRendererProps, StructuredQuestion } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface OralCalculationProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function OralCalculation({ question, index, mode = 'render' }: OralCalculationProps) {
  // 从 rendering_meta 获取作答区域宽度和样式
  const renderingMeta = (question as StructuredQuestion).rendering_meta
  const answerWidth = renderingMeta?.answer_width
  const answerStyle = renderingMeta?.answer_style
  const showQuestionNumber = renderingMeta?.show_question_number

  const html = renderInlineMarkdown(question.stem, answerWidth, answerStyle)

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-oral-calculation ${modeClass}`}>
      <div className="question-header">
        {showQuestionNumber !== false && (
          <span className="question-number">{index}. </span>
        )}
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    </div>
  )
}
