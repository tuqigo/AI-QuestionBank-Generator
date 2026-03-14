import { useEffect, useRef, useState } from 'react'
import type { StructuredQuestion, RecordMeta } from '@/types/question'
import QuestionRenderer from '@/components/QuestionRenderer'
import { useMathJaxSimple } from '@/hooks/useMathJax'
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
  const prevQuestionsRef = useRef<string>('')

  const questionsLength = questions.length

  // 检测题目内容变化，重置渲染状态
  useEffect(() => {
    const currentKey = questions.map(q => q.stem).join('|')
    if (prevQuestionsRef.current !== currentKey) {
      prevQuestionsRef.current = currentKey
    }
  }, [questions])

  // 使用 MathJax Hook
  useMathJaxSimple(containerRef, [questionsLength, questions])

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
