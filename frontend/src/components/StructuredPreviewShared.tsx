import { useEffect, useRef, useState } from 'react'
import type { StructuredQuestion } from '@/types/structured'
import QuestionRenderer from '@/components/QuestionRenderer'
import './StructuredPreviewShared.css'

interface StructuredPreviewSharedProps {
  questions: StructuredQuestion[]
  meta?: { record_id?: number; short_id?: string; title?: string; created_at?: string } | null
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
  const [componentsReady, setComponentsReady] = useState(false)
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
      setComponentsReady(false)
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

  // 等待组件渲染完成（题目内容渲染到 DOM）
  useEffect(() => {
    if (questionsLength === 0) {
      setComponentsReady(false)
      return
    }

    // 等待一小段时间确保 DOM 已经渲染完成
    const timeout = setTimeout(() => {
      setComponentsReady(true)
    }, 150)

    return () => clearTimeout(timeout)
  }, [questionsLength])

  // MathJax 渲染
  useEffect(() => {
    if (questionsLength === 0 || !containerRef.current || !componentsReady || !mathJaxLoaded) {
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
    }, 100)

    return () => clearTimeout(timer)
  }, [questionsLength, componentsReady, mathJaxLoaded])

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
