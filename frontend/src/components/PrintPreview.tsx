/**
 * PrintPreview - 打印预览专用组件
 *
 * 直接复用 printUtils 中的渲染逻辑，确保预览与打印效果完全一致
 * 后期只需维护 printUtils.ts 中的一套代码（renderStructuredQuestions + getPrintStyles）
 */
import { useEffect, useRef, useState, memo } from 'react'
import type { StructuredQuestion, RecordMeta } from '@/types/question'
import { renderStructuredQuestions, getPrintStyles } from '@/utils/printUtils'
import './PrintPreview.css'
import '@/types/mathjax'

interface PrintPreviewProps {
  questions: StructuredQuestion[]
  meta?: RecordMeta | null
  recordTitle?: string
}

// 内部组件 - 只负责渲染 HTML 内容，使用 memo 避免不必要的重新渲染
const PreviewContent = memo(({ htmlContent, containerRef }: {
  htmlContent: string
  containerRef: React.RefObject<HTMLDivElement | null>
}) => {
  return (
    <div
      className="print-preview-container question-print-mode"
      ref={containerRef}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  )
}, (prevProps, nextProps) => {
  // 只在 htmlContent 变化时才重新渲染
  return prevProps.htmlContent === nextProps.htmlContent
})

export default function PrintPreview({
  questions,
  meta,
  recordTitle
}: PrintPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const initializedRef = useRef(false)
  const [mathJaxLoaded, setMathJaxLoaded] = useState(false)
  const [htmlContent, setHtmlContent] = useState('')
  const [contentVersion, setContentVersion] = useState(0)
  const [printStyles, setPrintStyles] = useState('')
  const prevQuestionsRef = useRef<string>('')
  const hasRenderedMathJaxRef = useRef(false)

  const title = recordTitle || meta?.title || '题目练习'

  // 移动端动态缩放：根据屏幕宽度自动计算缩放比例
  const [scale, setScale] = useState(1)

  useEffect(() => {
    const updateScale = () => {
      const width = window.innerWidth
      // 基准宽度 900px，根据实际屏幕宽度动态计算缩放比例
      if (width < 900) {
        const newScale = Math.max(0.4, Math.min(1, width / 900))
        setScale(newScale)
      } else {
        setScale(1)
      }
    }

    updateScale()
    window.addEventListener('resize', updateScale)
    return () => window.removeEventListener('resize', updateScale)
  }, [])

  // 初始化时加载打印样式
  useEffect(() => {
    setPrintStyles(getPrintStyles())
  }, [])

  // 加载 MathJax
  useEffect(() => {
    if (initializedRef.current) {
      return
    }

    initializedRef.current = true

    const checkMathJaxReady = () => {
      if (window.MathJax?.typesetPromise || window.MathJax?.typeset) {
        setMathJaxLoaded(true)
      } else {
        setTimeout(checkMathJaxReady, 50)
      }
    }

    checkMathJaxReady()
  }, [])

  // 题目变化时更新 HTML 内容（只在题目真正变化时才更新）
  useEffect(() => {
    // 生成当前题目的唯一标识
    const currentKey = questions.map(q =>
      `${q.type}-${q.stem}-${q.options?.join('|') || ''}`
    ).join('###')

    // 如果题目没有变化，跳过更新
    if (prevQuestionsRef.current === currentKey) {
      return
    }

    if (questions.length === 0) {
      setHtmlContent('')
      setContentVersion(0)
      prevQuestionsRef.current = ''
      return
    }

    const html = renderStructuredQuestions(questions, title)
    setHtmlContent(html)
    // 增加版本号，触发后续的 MathJax 渲染
    setContentVersion(prev => prev + 1)
    // 记录当前题目
    prevQuestionsRef.current = currentKey
  }, [questions, title])

  // 内容更新后渲染 MathJax
  useEffect(() => {
    if (!htmlContent || !mathJaxLoaded || !containerRef.current || contentVersion === 0) {
      return
    }

    // 重置渲染标记
    hasRenderedMathJaxRef.current = false

    // 延迟 600ms 确保进度条关闭后再渲染（进度条 500ms 后关闭）
    const timer = setTimeout(() => {
      if (!containerRef.current) return

      if (window.MathJax?.typesetPromise) {
        window.MathJax.typesetPromise([containerRef.current])
          .then(() => {
            console.log('[PrintPreview] MathJax 渲染完成')
            hasRenderedMathJaxRef.current = true
          })
          .catch((err) => {
            console.error('[MathJax] 渲染失败:', err)
          })
      } else if (window.MathJax?.typeset) {
        try {
          window.MathJax.typeset([containerRef.current])
          console.log('[PrintPreview] MathJax 渲染完成')
          hasRenderedMathJaxRef.current = true
        } catch (err) {
          console.error('[MathJax] 渲染失败:', err)
        }
      }
    }, 600)

    return () => clearTimeout(timer)
  }, [htmlContent, mathJaxLoaded, contentVersion])

  // 组件重新渲染后，如果 MathJax 已渲染过但内容被重置，重新渲染 MathJax
  useEffect(() => {
    if (!htmlContent || !mathJaxLoaded || !containerRef.current || contentVersion === 0) {
      return
    }

    // 如果已经渲染过 MathJax，检查是否需要重新渲染
    if (hasRenderedMathJaxRef.current) {
      // 短暂延迟后检查 DOM 是否还存在 MathJax 渲染的内容
      const checkTimer = setTimeout(() => {
        if (!containerRef.current) return

        // 检查是否有未渲染的 LaTeX 公式（简单的检查）
        const hasUnrenderedLatex = containerRef.current.innerHTML.includes('$') ||
                                    containerRef.current.innerHTML.includes('\\(') ||
                                    containerRef.current.innerHTML.includes('$$')

        if (hasUnrenderedLatex && window.MathJax?.typesetPromise) {
          console.log('[PrintPreview] 检测到未渲染公式，重新渲染 MathJax')
          window.MathJax.typesetPromise([containerRef.current])
            .then(() => {
              console.log('[PrintPreview] MathJax 重新渲染完成')
            })
            .catch((err) => {
              console.error('[MathJax] 重新渲染失败:', err)
            })
        }
      }, 200)

      return () => clearTimeout(checkTimer)
    }
  }, [questions.length]) // 只在题目数量变化时检查

  if (questions.length === 0) {
    return null
  }

  // 移动端动态缩放样式
  const wrapperStyle: React.CSSProperties = scale < 1 ? {
    transform: `scale(${scale})`,
    transformOrigin: 'top center',
    width: `${100 / scale}%`,
    marginLeft: `${(1/scale - 1) * -50}%`
  } : {}

  return (
    <div className="print-preview-wrapper" style={wrapperStyle}>
      <style>{printStyles}</style>
      <PreviewContent htmlContent={htmlContent} containerRef={containerRef} />
    </div>
  )
}
