import { useEffect, useRef, useState, useLayoutEffect } from 'react'
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
  const mathJaxRenderedRef = useRef(false) // 记录 MathJax 是否已渲染
  const prevQuestionsRef = useRef<string>('') // 记录上一次的题目内容

  // 使用 key 来强制重新初始化（当题目内容变化时）
  const questionsLength = questions.length

  // 检测题目内容变化，重置渲染状态
  useEffect(() => {
    const currentKey = questions.map(q => q.stem).join('|')
    if (prevQuestionsRef.current !== currentKey) {
      // 题目内容变化，重置所有状态
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
      script.onload = () => console.log('MathJax script loaded')
      document.head.appendChild(script)
    }
  }, [])

  // 等待组件渲染完成（检测 loading 元素是否消失）
  useEffect(() => {
    if (questionsLength === 0) {
      setComponentsReady(false)
      return
    }

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

  // 使用 useLayoutEffect 确保在浏览器绘制前渲染 MathJax
  useLayoutEffect(() => {
    if (questionsLength === 0 || !containerRef.current || !componentsReady) {
      return
    }

    // 如果已经渲染过，不再重复渲染
    if (mathJaxRenderedRef.current) {
      return
    }

    console.log('[MathJax] useLayoutEffect 执行，题目数量:', questionsLength, 'componentsReady:', componentsReady)

    // 立即同步渲染
    if (window.MathJax && containerRef.current) {
      try {
        // 检查当前 DOM 是否包含 LaTeX
        const innerHTML = containerRef.current.innerHTML
        console.log('[MathJax] 渲染前 innerHTML 长度:', innerHTML.length)
        // 检查是否包含 $ 符号（LaTeX 标记）
        const hasLatex = innerHTML.includes('$') || innerHTML.includes('\\(') || innerHTML.includes('\\[')
        console.log('[MathJax] 是否包含 LaTeX:', hasLatex)

        if (window.MathJax.typesetPromise) {
          window.MathJax.typesetPromise([containerRef.current]).then(() => {
            console.log('[MathJax] 渲染完成 (Promise)')
            // 渲染完成后检查
            if (containerRef.current) {
              const hasMathJaxElements = containerRef.current.querySelectorAll('mjx-container').length
              console.log('[MathJax] mjx-container 元素数量:', hasMathJaxElements)
              // 标记已渲染
              mathJaxRenderedRef.current = true
            }
          })
        } else if (window.MathJax.typeset) {
          window.MathJax.typeset([containerRef.current])
          console.log('[MathJax] 渲染完成 (sync)')
          mathJaxRenderedRef.current = true
        }
      } catch (err) {
        console.error('[MathJax] 渲染失败:', err)
      }
    }
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
