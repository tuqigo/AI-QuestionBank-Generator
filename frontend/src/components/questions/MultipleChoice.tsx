/**
 * 多选题组件
 */
import { useMemo } from 'react'
import { QuestionRendererProps, QuestionWithOptions } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface MultipleChoiceProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function MultipleChoice({ question, index, mode = 'render' }: MultipleChoiceProps) {
  const options = question.options || []

  // 多选题选项标签（A, B, C...）
  const optionLabels = useMemo(() => {
    const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    return options.map((opt, idx) => ({
      letter: letters[idx] || String.fromCharCode(65 + idx),
      text: opt
    }))
  }, [options])

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-multiple-choice ${modeClass}`}>
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
      </div>
      <div className="question-options">
        {optionLabels.map((opt, idx) => (
          <div key={idx} className="option-item">
            <span className="option-label">{opt.letter}. </span>
            <span className="option-text" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(opt.text) }} />
          </div>
        ))}
      </div>
    </div>
  )
}
