/**
 * QuestionRenderer - 题目渲染主组件
 * 根据题型动态渲染对应的组件
 *
 * 注意：MathJax 渲染由 StructuredPreviewShared 统一控制
 * 本组件不触发 MathJax 渲染
 */
import { useMemo } from 'react'
import type { Question } from '@/types/structured'

// 题型组件映射
import SingleChoice from './questions/SingleChoice'
import MultipleChoice from './questions/MultipleChoice'
import TrueFalse from './questions/TrueFalse'
import FillBlank from './questions/FillBlank'
import Calculation from './questions/Calculation'
import WordProblem from './questions/WordProblem'
import ReadComp from './questions/ReadComp'
import Cloze from './questions/Cloze'
import Essay from './questions/Essay'

interface QuestionRendererProps {
  question: Question
  index?: number  // 题号
  mode?: 'render' | 'print'  // 渲染模式：render（屏幕显示）或 print（打印）
}

/**
 * QuestionRenderer - 题目渲染器
 * 不触发 MathJax 渲染（由 StructuredPreviewShared 统一控制）
 * @param mode - 渲染模式：'render'（默认）或 'print'
 */
export default function QuestionRenderer({ question, index = 1, mode = 'render' }: QuestionRendererProps) {
  // 渲染逻辑
  if (!question?.type) {
    return (
      <div className="question-error">
        <p>错误：无效的题目数据</p>
      </div>
    )
  }

  // 使用 useMemo 缓存渲染结果，避免不必要的重新渲染
  const renderedQuestion = useMemo(() => {
    switch (question.type) {
      case 'SINGLE_CHOICE':
        return <SingleChoice question={question} index={index} mode={mode} />

      case 'MULTIPLE_CHOICE':
        return <MultipleChoice question={question} index={index} mode={mode} />

      case 'TRUE_FALSE':
        return <TrueFalse question={question} index={index} mode={mode} />

      case 'FILL_BLANK':
        return <FillBlank question={question} index={index} mode={mode} />

      case 'CALCULATION':
        return <Calculation question={question} index={index} mode={mode} />

      case 'WORD_PROBLEM':
        return <WordProblem question={question} index={index} mode={mode} />

      case 'READ_COMP':
        return <ReadComp question={question} index={index} mode={mode} />

      case 'CLOZE':
        return <Cloze question={question} index={index} mode={mode} />

      case 'ESSAY':
        return <Essay question={question} index={index} mode={mode} />

      default:
        return (
          <div className="question-error">
            <p>错误：不支持的题型 "{question.type}"</p>
          </div>
        )
    }
  }, [question, index, mode])

  return renderedQuestion
}
