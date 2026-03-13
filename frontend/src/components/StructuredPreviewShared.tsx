import { useEffect, useRef, useState } from 'react'
import type { StructuredQuestion, MetaData } from '@/types/structured'
import QuestionRenderer from '@/components/QuestionRenderer'
import './StructuredPreviewShared.css'

interface StructuredPreviewSharedProps {
  questions: StructuredQuestion[]
  meta?: MetaData | null
  recordTitle?: string // 历史记录的标题（如果存在）
}

export default function StructuredPreviewShared({
  questions,
  meta,
  recordTitle
}: StructuredPreviewSharedProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const initializedRef = useRef(false)
  const [componentsReady, setComponentsReady] = useState(false)

  // 使用 key 来强制重新初始化（当题目数量从 0 变为非 0 时）
  const questionsLength = questions.length

  // 加载 MathJax
  useEffect(() => {
    if (initializedRef.current) {
      return
    }

    initializedRef.current = true
    console.log('MathJax: 初始化配置')

    if (!window.MathJax) {
      const mathJaxConfig: any = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']],
          displayMath: [['$$', '$$'], ['\\[', '\\]']],
          processEscapes: true,
          processEnvironments: true,
          packages: ['base', 'ams', 'require']
        },
        options: {
          skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
          ignoreHtmlClass: 'tex2jax_ignore'
        },
        startup: {
          typeset: true,
          ready: () => {
            console.log('MathJax startup ready')
            // @ts-ignore
            window.MathJax?.startup?.defaultReady?.()
          }
        }
      }
      window.MathJax = mathJaxConfig

      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
      script.async = true
      document.head.appendChild(script)
    }
  }, [])

  // 等待组件渲染完成（检测 loading 元素是否消失）
  useEffect(() => {
    if (questionsLength === 0) {
      setComponentsReady(false)
      return
    }

    // 重置状态
    setComponentsReady(false)

    // 使用轮询检测 loading 元素是否消失
    const checkReady = () => {
      const loadingElements = containerRef.current?.querySelectorAll('.question-loading')
      const hasLoading = loadingElements && loadingElements.length > 0

      if (!hasLoading) {
        setComponentsReady(true)
      }
    }

    // 立即检查一次
    checkReady()

    // 轮询检查
    const interval = setInterval(checkReady, 50)

    // 超时处理（5 秒后强制认为 ready）
    const timeout = setTimeout(() => {
      setComponentsReady(true)
    }, 5000)

    return () => {
      clearInterval(interval)
      clearTimeout(timeout)
    }
  }, [questionsLength])

  // 渲染公式
  useEffect(() => {
    if (questionsLength === 0 || !containerRef.current || !componentsReady) {
      return
    }

    console.log('MathJax: 组件已就绪，准备渲染公式，题目数量:', questionsLength)

    // 渲染公式
    const renderMath = async () => {
      // 使用 requestAnimationFrame 确保 DOM 已经完全更新
      await new Promise(resolve => requestAnimationFrame(resolve))
      await new Promise(resolve => setTimeout(resolve, 50))

      if (window.MathJax && containerRef.current) {
        try {
          if (window.MathJax.typesetPromise) {
            await window.MathJax.typesetPromise([containerRef.current])
          } else if (window.MathJax.typeset) {
            window.MathJax.typeset([containerRef.current])
          }
          console.log('MathJax: 渲染完成')
        } catch (err) {
          console.error('MathJax 渲染失败:', err)
        }
      }
    }

    renderMath()
  }, [questionsLength, componentsReady])

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
            <QuestionRenderer question={question} index={index + 1} />
          </div>
        ))}
      </div>
    </div>
  )
}
