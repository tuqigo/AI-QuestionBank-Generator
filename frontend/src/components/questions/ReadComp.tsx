/**
 * 阅读理解组件
 */
import { useMemo } from 'react'
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'
import SingleChoice from './SingleChoice'
import FillBlank from './FillBlank'

interface ReadCompProps extends QuestionRendererProps {
  mode?: 'render' | 'print'
}

export default function ReadComp({ question, index, mode = 'render' }: ReadCompProps) {
  const passage = question.passage || ''
  const subQuestions = question.sub_questions || []

  // 提取阅读材料正文（去除【阅读材料】等前缀）
  const passageText = useMemo(() => {
    let text = passage.replace(/【阅读材料】/, '').replace(/【材料】/, '').trim()
    // 分离题目指引
    const parts = text.split(/完成题目？|完成下列题目？|回答下列问题？|完成后回答/)
    if (parts.length > 1) {
      return parts[0].trim()
    }
    return text
  }, [passage])

  const modeClass = mode === 'print' ? 'question-print-mode' : 'question-render-mode'

  return (
    <div className={`question-item question-read-comp ${modeClass}`}>
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>

      {/* 阅读材料区域 */}
      <div className="passage-section">
        <div className="passage-title">阅读材料：</div>
        <div className="passage-content" dangerouslySetInnerHTML={{ __html: renderMarkdown(passageText) }} />
      </div>

      {/* 子题目 */}
      <div className="sub-questions">
        {subQuestions.map((subQ, subIdx) => {
          const subQuestionProps = {
            question: subQ,
            index: subIdx + 1,
            mode
          }

          switch (subQ.type) {
            case 'SINGLE_CHOICE':
              return <SingleChoice key={subIdx} {...subQuestionProps as any} />
            case 'FILL_BLANK':
              return <FillBlank key={subIdx} {...subQuestionProps as any} />
            default:
              return (
                <div key={subIdx} className="question-item question-sub">
                  <div className="question-header">
                    <span className="question-number">{subIdx + 1}. </span>
                    <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(subQ.stem) }} />
                  </div>
                </div>
              )
          }
        })}
      </div>
    </div>
  )
}
