/**
 * 单选题组件
 */
import { useMemo } from 'react'
import type { QuestionRendererProps, QuestionWithOptions } from '@/types/question'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'

interface SingleChoiceProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function SingleChoice({ question, index, mode = 'render' }: SingleChoiceProps) {
  const options = question.options || []

  // 处理选项：移除可能存在的 A. B. C. D. 前缀（如果 AI 返回了前缀）
  const normalizedOptions = useMemo(() => {
    return options.map((opt) => {
      // 移除任何已存在的 A-D 前缀
      const text = opt.replace(/^[A-D]\.\s*/, '')
      return { text }
    })
  }, [options])

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-single-choice ${modeClass}`}>
      <div className="question-header">
        <span className="question-number">{index}.</span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
      </div>
      <div className="question-options">
        {normalizedOptions.map((opt, idx) => (
          <div key={idx} className="option-item">
            <span className="option-label">{['A', 'B', 'C', 'D'][idx]}. </span>
            <span className="option-text" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(opt.text) }} />
          </div>
        ))}
      </div>
    </div>
  )
}
