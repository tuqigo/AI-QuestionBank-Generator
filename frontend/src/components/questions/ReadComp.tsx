/**
 * 阅读理解组件
 * 支持所有题型的子题目
 */
import { useMemo } from 'react'
import { QuestionRendererProps, QuestionWithPassage, QuestionWithSubQuestions } from '@/types/question'
import { renderMarkdown, renderInlineMarkdown } from '@/utils/markdownProcessor'
import SingleChoice from './SingleChoice'
import MultipleChoice from './MultipleChoice'
import TrueFalse from './TrueFalse'
import FillBlank from './FillBlank'
import Calculation from './Calculation'
import WordProblem from './WordProblem'
import Cloze from './Cloze'
import Essay from './Essay'

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
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(question.stem) }} />
      </div>

      {/* 阅读材料区域 */}
      <div className="passage-section">
        <div className="passage-content" dangerouslySetInnerHTML={{ __html: renderMarkdown(passageText) }} />
      </div>

      {/* 子题目 */}
      <div className="sub-questions">
        {subQuestions.map((subQ, subIdx) => {
          const subQuestionProps = {
            question: subQ,
            index: `${index}.${subIdx + 1}`,
            mode
          }

          switch (subQ.type) {
            case 'SINGLE_CHOICE':
              return <SingleChoice key={subIdx} {...subQuestionProps as any} />
            case 'MULTIPLE_CHOICE':
              return <MultipleChoice key={subIdx} {...subQuestionProps as any} />
            case 'TRUE_FALSE':
              return <TrueFalse key={subIdx} {...subQuestionProps as any} />
            case 'FILL_BLANK':
              return <FillBlank key={subIdx} {...subQuestionProps as any} />
            case 'CALCULATION':
              return <Calculation key={subIdx} {...subQuestionProps as any} />
            case 'WORD_PROBLEM':
              return <WordProblem key={subIdx} {...subQuestionProps as any} />
            case 'CLOZE':
              return <Cloze key={subIdx} {...subQuestionProps as any} />
            case 'ESSAY':
              return <Essay key={subIdx} {...subQuestionProps as any} />
            case 'POETRY_APP':
              // 古诗文鉴赏/默写，使用默认渲染
            default:
              return (
                <div key={subIdx} className="question-item question-sub">
                  <div className="question-header">
                    <span className="question-number">{subIdx + 1}. </span>
                    <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(subQ.stem) }} />
                  </div>
                  {subQ.options && subQ.options.length > 0 && (
                    <div className="question-options">
                      {subQ.options.map((opt, optIdx) => {
                        const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
                        return (
                          <div key={optIdx} className="option-item">
                            <span className="option-label">{letters[optIdx] || String.fromCharCode(65 + optIdx)}. </span>
                            <span className="option-text" dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(opt) }} />
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
          }
        })}
      </div>
    </div>
  )
}
