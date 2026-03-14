/**
 * StructuredPreview - 结构化题目预览页面
 * 在此页面输入提示词生成题目并渲染
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getToken } from '@/auth'
import { handlePrint } from '@/utils/printUtils'
import QuestionRenderer from '@/components/QuestionRenderer'
import { generateStructuredQuestions } from '@/api/history'
import { renderInlineMarkdown } from '@/utils/markdownProcessor'
import './StructuredPreview.css'
import type { StructuredGenerateResponse, Question } from '@/types/structured'

export default function StructuredPreview() {
  const navigate = useNavigate()
  const [prompt, setPrompt] = useState('')
  const [questions, setQuestions] = useState<Question[]>([])
  const [title, setTitle] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 加载 MathJax
  useEffect(() => {
    // 如果已经加载则跳过
    if (window.MathJax) {
      // MathJax 3.x: typesetPromise(), MathJax 4.x: typeset() 返回 undefined
      if (window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([])
      } else if (window.MathJax.typeset) {
        // 4.x 版本，typeset 是同步的，使用 Promise.resolve 包装
        Promise.resolve().then(() => window.MathJax?.typeset?.([]))
      }
      return
    }

    // 配置 MathJax
    const mathJaxConfig: any = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true,
        packages: ['base', 'ams', 'require']
      },
      options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
        ignoreHtmlClass: 'tex2jax_ignore'
      },
      startup: {
        typeset: true,
        ready: () => {
          // @ts-ignore
          window.MathJax?.startup?.defaultReady?.()
        }
      }
    }
    window.MathJax = mathJaxConfig

    const script = document.createElement('script')
    script.type = 'text/javascript'
    // 使用 MathJax 3.x 最新版本，避免 4.x 的 API 不兼容
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js'
    script.async = true
    script.id = 'mathjax-script'

    script.onload = () => {
      if (window.MathJax?.typesetPromise) {
        window.MathJax.typesetPromise([])
      } else if (window.MathJax?.typeset) {
        Promise.resolve().then(() => window.MathJax?.typeset?.([]))
      }
    }

    script.onerror = () => {
      console.error('Failed to load MathJax')
    }

    document.head.appendChild(script)
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('请输入提示词')
      return
    }

    setLoading(true)
    setError(null)
    setQuestions([])

    try {
      const token = getToken()
      if (!token) {
        navigate('/')
        return
      }

      const data: StructuredGenerateResponse = await generateStructuredQuestions(prompt)
      setQuestions(data.questions || [])
      setTitle(data.meta?.title || '结构化题目')
    } catch (err: any) {
      console.error('生成题目失败:', err)
      const errorMessage = err?.message || '生成题目失败'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    navigate('/workbench')
  }

  const handlePrintWrapper = async () => {
    if (questions.length === 0) {
      alert('没有可打印的内容')
      return
    }
    // 使用 printUtils 中的 handlePrint，传入结构化题目数据
    await handlePrint(undefined, title || '结构化题目', questions as any, null)
  }

  if (loading) {
    return (
      <div className="preview-page">
        <div className="loading">生成题目中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="preview-page">
        <div className="error">
          {error}
          <button onClick={() => setError(null)} className="btn-back" style={{ marginTop: '12px' }}>
            确定
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="preview-page">
      {/* 顶部栏 */}
      <div className="preview-header">
        <h2>{title || '结构化题目生成'}</h2>
        <div className="preview-actions">
          <button onClick={handlePrintWrapper} className="btn-print">打印</button>
          <button onClick={handleBack} className="btn-back">返回</button>
        </div>
      </div>

      {/* 提示词输入区域 */}
      <div className="preview-content">
        <div className="prompt-input-container">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="请输入题目提示词，例如：请生成5道初一数学有理数综合练习题..."
            className="prompt-input"
            rows={6}
          />
          <button onClick={handleGenerate} className="btn-generate">
            生成题目
          </button>
        </div>
      </div>

      {/* 打印测试内容 - 仅用于调试 */}
      <div className="print-test" style={{ display: 'none' }}>
        PRINT TEST: 题目数量 {questions.length}
      </div>

      {/* 题目列表 */}
      {questions.length > 0 && (
        <div className="preview-content" id="printable-content">
          <div className="questions-container">
            {questions.map((question, index) => (
              <div key={index} className="question-wrapper">
                <QuestionRenderer question={question} index={index + 1} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
