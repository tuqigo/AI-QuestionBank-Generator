/**
 * StructuredPreviewShared - 结构化题目预览（做题模式）
 *
 * ⚠️ 注意：此组件专为未来"做题模式"设计
 * 功能特点：
 * - 支持交互操作（点击、选择、输入答案等）
 * - 支持答题功能
 * - MathJax 动态渲染
 *
 * 与 PrintPreview 的区别：
 * - PrintPreview: 纯展示模式，无交互，直接展示打印效果
 * - StructuredPreviewShared: 支持交互、答题等功能（做题模式）
 *
 * TODO: 未来实现做题模式时，需要：
 * 1. 添加答案选择/输入功能
 * 2. 添加判题功能
 * 3. 添加答题进度管理
 */
import { useEffect, useRef, useState } from 'react'
import type { StructuredQuestion, RecordMeta } from '@/types/question'
import QuestionRenderer from '@/components/QuestionRenderer'
import './StructuredPreviewShared.css'

interface StructuredPreviewSharedProps {
  questions: StructuredQuestion[]
  meta?: RecordMeta | null
  recordTitle?: string // 历史记录的标题（如果存在）
  mode?: 'render' | 'print'  // 渲染模式：render（默认）或 print
}

export default function StructuredPreviewShared({
  questions,
  meta,
  recordTitle,
  mode = 'render'
}: StructuredPreviewSharedProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const initializedRef = useRef(false)
  const [mathJaxLoaded, setMathJaxLoaded] = useState(false)
  const mathJaxRenderedRef = useRef(false)
  const prevQuestionsRef = useRef<string>('')

  const questionsLength = questions.length

  // 检测题目内容变化，重置渲染状态
  useEffect(() => {
    const currentKey = questions.map(q => q.stem).join('|')
    if (prevQuestionsRef.current !== currentKey) {
      prevQuestionsRef.current = currentKey
      mathJaxRenderedRef.current = false
    }
  }, [questions])

  // 加载 MathJax
  useEffect(() => {
    if (initializedRef.current) {
      return
    }

    initializedRef.current = true

    // 检查 MathJax 是否已经完全加载
    const checkMathJaxReady = () => {
      if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        setMathJaxLoaded(true)
      } else {
        // 等待 MathJax 加载完成
        setTimeout(checkMathJaxReady, 50)
      }
    }

    checkMathJaxReady()
  }, [])

  // MathJax 渲染
  useEffect(() => {
    if (questionsLength === 0 || !containerRef.current || !mathJaxLoaded) {
      return
    }

    // 如果已经渲染过，不再重复渲染
    if (mathJaxRenderedRef.current) {
      return
    }

    // 延迟一小段时间，确保 DOM 已经完全稳定
    const timer = setTimeout(() => {
      if (window.MathJax && containerRef.current) {
        try {
          if (window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([containerRef.current]).then(() => {
              mathJaxRenderedRef.current = true
            })
          } else if (window.MathJax.typeset) {
            window.MathJax.typeset([containerRef.current])
            mathJaxRenderedRef.current = true
          }
        } catch (err) {
          console.error('[MathJax] 渲染失败:', err)
        }
      }
    }, 150)

    return () => clearTimeout(timer)
  }, [questionsLength, mathJaxLoaded])

  if (questions.length === 0) {
    return null
  }

  const title = recordTitle || meta?.title || '题目练习'

  return (
    <div className="structured-preview-shared" ref={containerRef}>
      <div className="preview-title">
        <h2>{title}</h2>
      </div>

      <div className="questions-container">
        {questions.map((question, index) => (
          <div key={index} className="question-wrapper">
            <QuestionRenderer question={question} index={index + 1} mode={mode} />
          </div>
        ))}
      </div>
    </div>
  )
}
