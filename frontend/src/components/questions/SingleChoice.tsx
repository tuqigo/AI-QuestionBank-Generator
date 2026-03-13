/**
 * 单选题组件
 */
import { useMemo } from 'react'
import type { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

// 检查选项是否已包含 A. B. C. D. 前缀
function hasOptionPrefix(text: string): boolean {
  return /^[A-D]\.\s/.test(text.trim())
}

// 移除选项前缀
function removeOptionPrefix(text: string): string {
  return text.replace(/^[A-D]\.\s*/, '')
}

export default function SingleChoice({ question, index }: QuestionRendererProps) {
  const options = question.options || []

  // 处理选项：检测是否有前缀，如果没有则添加
  const normalizedOptions = useMemo(() => {
    return options.map((opt) => {
      const hasPrefix = hasOptionPrefix(opt)
      return {
        text: hasPrefix ? removeOptionPrefix(opt) : opt,
        hasPrefix
      }
    })
  }, [options])

  return (
    <div className="question-item question-single-choice">
      <div className="question-header">
        <span className="question-number">{index}.</span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>
      <div className="question-options">
        {normalizedOptions.map((opt, idx) => (
          <div key={idx} className="option-item">
            <span className="option-label">{opt.hasPrefix ? '' : ['A', 'B', 'C', 'D'][idx]}. </span>
            <span className="option-text" dangerouslySetInnerHTML={{ __html: renderMarkdown(opt.text) }} />
          </div>
        ))}
      </div>
    </div>
  )
}
