import { useEffect, useRef } from 'react'
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
  const renderingRef = useRef(false)

  // 加载 MathJax 并渲染公式
  useEffect(() => {
    let mounted = true

    const initAndRenderMathJax = async () => {
      if (questions.length === 0 || !mounted) {
        console.log('MathJax: 跳过渲染，无题目或未挂载')
        return
      }

      // 防止重复渲染
      if (renderingRef.current) {
        console.log('MathJax: 渲染中，跳过')
        return
      }

      console.log('MathJax: 开始渲染', {
        questionsCount: questions.length,
        hasWindowMathJax: !!window.MathJax,
        hasContainer: !!containerRef.current
      })

      try {
        renderingRef.current = true

        // 检查 MathJax 是否已经加载到 window
        const mathJaxLoaded = !!window.MathJax

        if (!mathJaxLoaded) {
          console.log('MathJax: 首次初始化')
          window.MathJax = {
            tex: {
              inlineMath: [['$', '$'], ['\\(', '\\)']],
              displayMath: [['$$', '$$'], ['\\[', '\\]']],
              processEscapes: false,
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
                console.log('MathJax startup ready callback')
                // @ts-ignore
                window.MathJax.startup.defaultReady()
              }
            }
          }

          const script = document.createElement('script')
          script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
          script.async = true

          await new Promise<void>((resolve) => {
            script.onload = () => {
              console.log('MathJax: 脚本加载成功，window.MathJax =', window.MathJax)
              resolve()
            }
            script.onerror = () => {
              console.error('Failed to load MathJax')
              resolve()
            }
            document.head.appendChild(script)
          })
        } else {
          console.log('MathJax: 已加载')
        }

        // 等待 DOM 完全渲染
        await new Promise(resolve => setTimeout(resolve, 150))

        // 触发 MathJax 渲染
        if (window.MathJax && containerRef.current) {
          console.log('MathJax: 开始渲染容器')
          try {
            if (window.MathJax.typesetPromise) {
              await window.MathJax.typesetPromise([containerRef.current])
              console.log('MathJax: typesetPromise 渲染完成')
            } else if (window.MathJax.typeset) {
              window.MathJax.typeset([containerRef.current])
              console.log('MathJax: typeset 渲染完成')
            }
          } catch (err) {
            console.error('MathJax render error:', err)
          }
        } else {
          console.warn('MathJax: 缺少必要条件', {
            hasMathJax: !!window.MathJax,
            hasContainer: !!containerRef.current
          })
        }
      } catch (error) {
        console.error('Failed to process MathJax:', error)
      } finally {
        renderingRef.current = false
      }
    }

    initAndRenderMathJax()

    return () => {
      mounted = false
    }
    // 只在 questions.length 变化时触发
  }, [questions.length])

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
          <div key={question.id || index} className="question-wrapper">
            <QuestionRenderer question={question} index={index + 1} />
          </div>
        ))}
      </div>
    </div>
  )
}
