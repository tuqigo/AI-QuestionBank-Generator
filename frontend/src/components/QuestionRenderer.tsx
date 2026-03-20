/**
 * QuestionRenderer - 题目渲染主组件
 * 根据题型动态渲染对应的组件
 *
 * 注意：MathJax 渲染由 StructuredPreviewShared 统一控制
 * 本组件不触发 MathJax 渲染
 */
import { useMemo } from 'react'
import type { Question, QuestionRenderingMeta, StructuredQuestion } from '@/types/question'

// 题型组件映射
import SingleChoice from './questions/SingleChoice'
import MultipleChoice from './questions/MultipleChoice'
import TrueFalse from './questions/TrueFalse'
import FillBlank from './questions/FillBlank'
import Calculation from './questions/Calculation'
import OralCalculation from './questions/OralCalculation'
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
 * 根据 rendering_meta 生成 CSS 类名和样式
 */
function getRenderingStyles(renderingMeta?: QuestionRenderingMeta): React.CSSProperties {
  const styles: React.CSSProperties = {}

  if (!renderingMeta) {
    return styles
  }

  // 字体大小（通过 CSS 变量传递）
  if (renderingMeta.font_size) {
    (styles as any)['--font-size'] = `${renderingMeta.font_size}px`
  }

  // 列数（多列布局使用）
  if (renderingMeta.columns) {
    (styles as any)['--columns'] = String(renderingMeta.columns)
  }

  // LaTeX 缩放（通过 CSS 变量传递给 MathJax 容器）
  if (renderingMeta.latex_scale) {
    (styles as any)['--latex-scale'] = String(renderingMeta.latex_scale)
  }

  // 作答宽度（填空题/口算题）
  if (renderingMeta.answer_width) {
    const widthPx = String(renderingMeta.answer_width) + 'px'
    ;(styles as any)['--answer-placeholder-width'] = widthPx
    ;(styles as any)['--answer-width'] = widthPx
  }

  return styles
}

/**
 * 根据 rendering_meta 生成 CSS 类名
 */
function getRenderingClasses(renderingMeta?: QuestionRenderingMeta): string {
  if (!renderingMeta) {
    return ''
  }

  const classes: string[] = []

  // 布局类
  if (renderingMeta.layout === 'multi') {
    classes.push('question-layout-multi')
  } else if (renderingMeta.layout === 'inline') {
    classes.push('question-layout-inline')
  } else {
    classes.push('question-layout-single')
  }

  // 保持在一起（避免分页打断）
  if (renderingMeta.keep_together === true) {
    classes.push('question-keep-together')
  }

  return classes.join(' ')
}

/**
 * QuestionRenderer - 题目渲染器
 * 不触发 MathJax 渲染（由 StructuredPreviewShared 统一控制）
 * @param mode - 渲染模式：'render'（默认）或 'print'
 */
export default function QuestionRenderer({ question, index = 1, mode = 'render' }: QuestionRendererProps) {
  // 提取 rendering_meta（如果是 StructuredQuestion）
  const renderingMeta = (question as StructuredQuestion).rendering_meta

  // 渲染样式和类名
  const renderingStyles = getRenderingStyles(renderingMeta)
  const renderingClasses = getRenderingClasses(renderingMeta)

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
    const baseProps = { question, index, mode }

    switch (question.type) {
      case 'SINGLE_CHOICE':
        return <SingleChoice {...baseProps} />

      case 'MULTIPLE_CHOICE':
        return <MultipleChoice {...baseProps} />

      case 'TRUE_FALSE':
        return <TrueFalse {...baseProps} />

      case 'FILL_BLANK':
        return <FillBlank {...baseProps} />

      case 'CALCULATION':
        return <Calculation {...baseProps} />

      case 'ORAL_CALCULATION':
        return <OralCalculation {...baseProps} />

      case 'WORD_PROBLEM':
        return <WordProblem {...baseProps} />

      case 'READ_COMP':
        return <ReadComp {...baseProps} />

      case 'CLOZE':
        return <Cloze {...baseProps} />

      case 'ESSAY':
        return <Essay {...baseProps} />

      default:
        return (
          <div className="question-error">
            <p>错误：不支持的题型 "{question.type}"</p>
          </div>
        )
    }
  }, [question, index, mode])

  // 包裹渲染容器，应用 layout 和 keep_together 类名
  return (
    <div className={`question-render-container ${renderingClasses}`} style={renderingStyles}>
      {renderedQuestion}
    </div>
  )
}
