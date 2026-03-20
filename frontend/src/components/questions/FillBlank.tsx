/**
 * 填空题组件
 */
import type { QuestionRendererProps, StructuredQuestion } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface FillBlankProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function FillBlank({ question, index, mode = 'render' }: FillBlankProps) {
  // 从 rendering_meta 获取作答区域宽度、样式和是否显示题号
  const answerWidth = (question as StructuredQuestion).rendering_meta?.answer_width
  const answerStyle = (question as StructuredQuestion).rendering_meta?.answer_style
  const showQuestionNumber = (question as StructuredQuestion).rendering_meta?.show_question_number

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-fill-blank ${modeClass}`}>
      <div className="question-header">
        {showQuestionNumber !== false && (
          <span className="question-number">{index}. </span>
        )}
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem, answerWidth, answerStyle) }} />
      </div>
    </div>
  )
}
