/**
 * 完形填空组件
 */
import { useMemo } from 'react'
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'
import FillBlank from './FillBlank'

export default function Cloze({ question, index }: QuestionRendererProps) {
  const passage = question.passage || ''
  const subQuestions = question.sub_questions || []

  // 提取完形填空原文
  const passageText = useMemo(() => {
    let text = passage.replace(/【原文】/, '').replace(/【完形填空】/, '').trim()
    return text
  }, [passage])

  return (
    <div className="question-item question-cloze">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>

      {/* 完形填空原文 */}
      <div className="passage-section">
        <div className="passage-title">完形填空原文：</div>
        <div className="passage-content" dangerouslySetInnerHTML={{ __html: renderMarkdown(passageText) }} />
      </div>

      {/* 子题目 */}
      <div className="sub-questions">
        {subQuestions.map((subQ, subIdx) => (
          <FillBlank
            key={subIdx}
            question={subQ}
            index={subIdx + 1}
          />
        ))}
      </div>
    </div>
  )
}
