/**
 * QuestionRenderer - 题目渲染主组件
 * 根据题型动态渲染对应的组件
 */
import { lazy, Suspense, useEffect, forwardRef } from 'react'
import type { Question } from '@/types/structured'

// 懒加载各题型组件
const SingleChoice = lazy(() => import('./questions/SingleChoice'))
const MultipleChoice = lazy(() => import('./questions/MultipleChoice'))
const TrueFalse = lazy(() => import('./questions/TrueFalse'))
const FillBlank = lazy(() => import('./questions/FillBlank'))
const Calculation = lazy(() => import('./questions/Calculation'))
const WordProblem = lazy(() => import('./questions/WordProblem'))
const Geometry = lazy(() => import('./questions/Geometry'))
const ReadComp = lazy(() => import('./questions/ReadComp'))
const PoetryApp = lazy(() => import('./questions/PoetryApp'))
const Cloze = lazy(() => import('./questions/Cloze'))
const Essay = lazy(() => import('./questions/Essay'))

// 加载中组件
const LoadingFallback = () => (
  <div className="question-loading">
    <span className="loading-spinner"></span>
    <span>加载中...</span>
  </div>
)

interface QuestionRendererProps {
  question: Question
  index?: number  // 题号
}

/**
 * QuestionRendererWithMathJax - 带 MathJax 自动渲染的题目渲染器
 * 在组件挂载/更新时自动触发 MathJax 重新渲染
 */
const QuestionRendererWithMathJax = forwardRef<HTMLDivElement, QuestionRendererProps>(
  function QuestionRendererWithMathJax({ question, index = 1 }, ref) {
    // 在组件挂载或 question 变化后触发 MathJax 渲染
    useEffect(() => {
      const timer = setTimeout(() => {
        if (window.MathJax?.typesetPromise) {
          window.MathJax.typesetPromise().catch(err => console.error('MathJax render error:', err))
        } else if (window.MathJax?.typeset) {
          window.MathJax.typeset()
        }
      }, 100)
      return () => clearTimeout(timer)
    }, [question])

    // 渲染逻辑
    if (!question?.type) {
      return (
        <div className="question-error" ref={ref}>
          <p>错误：无效的题目数据</p>
        </div>
      )
    }

    const renderQuestion = () => {
      switch (question.type) {
        case 'SINGLE_CHOICE':
          return <SingleChoice question={question} index={index} />

        case 'MULTIPLE_CHOICE':
          return <MultipleChoice question={question} index={index} />

        case 'TRUE_FALSE':
          return <TrueFalse question={question} index={index} />

        case 'FILL_BLANK':
          return <FillBlank question={question} index={index} />

        case 'CALCULATION':
          return <Calculation question={question} index={index} />

        case 'WORD_PROBLEM':
          return <WordProblem question={question} index={index} />

        case 'GEOMETRY':
          return <Geometry question={question} index={index} />

        case 'READ_COMP':
          return <ReadComp question={question} index={index} />

        case 'POETRY_APP':
          return <PoetryApp question={question} index={index} />

        case 'CLOZE':
          return <Cloze question={question} index={index} />

        case 'ESSAY':
          return <Essay question={question} index={index} />

        default:
          return (
            <div className="question-error" ref={ref}>
              <p>错误：不支持的题型 "{question.type}"</p>
            </div>
          )
      }
    }

    return (
      <div ref={ref}>
        <Suspense fallback={<LoadingFallback />}>
          {renderQuestion()}
        </Suspense>
      </div>
    )
  }
)

// 保持向后兼容
export default QuestionRendererWithMathJax
