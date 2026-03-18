/**
 * StructuredPreview - 结构化题目预览页面
 * 在此页面输入提示词生成题目并渲染
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getToken } from '@/core/auth/userAuth'
import { toast } from '@/hooks'
import { handlePrint } from '@/utils/printUtils'
import PrintPreview from '@/components/PrintPreview'
import { generateStructuredQuestions, getHistoryAnswers } from '@/core/api/history'
import './StructuredPreview.css'
import type { StructuredGenerateResponse, Question, MetaData } from '@/types/question'

export default function StructuredPreview() {
  const navigate = useNavigate()
  const [prompt, setPrompt] = useState('')
  const [questions, setQuestions] = useState<Question[]>([])
  const [title, setTitle] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [shortId, setShortId] = useState<string | null>(null)
  const [answers, setAnswers] = useState<Array<{
    question_id: number
    type: string
    answer_text: string
    rows_to_answer?: number
  }>>([])
  const [showAnswers, setShowAnswers] = useState(false)
  const [answersLoading, setAnswersLoading] = useState(false)

  // 加载 MathJax（PrintPreview 组件内部会处理）
  useEffect(() => {
    // 如果已经加载则跳过
    if (window.MathJax) {
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
        typeset: true
      }
    }
    window.MathJax = mathJaxConfig

    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = '/mathjax@4.1.1/tex-mml-chtml.js'
    script.async = true
    script.id = 'mathjax-script'

    document.head.appendChild(script)
  }, [])

  // 题目变化时，不需要再手动渲染 MathJax（PrintPreview 组件内部会处理）

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.warning('请输入提示词')
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
      setShortId(data.short_id || null)
      setAnswers([])
      setShowAnswers(false)
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

  /**
   * 查看答案功能
   */
  const handleToggleAnswers = async () => {
    if (showAnswers) {
      setShowAnswers(false)
      return
    }

    if (!shortId) {
      toast.warning('请先生成题目')
      return
    }

    setAnswersLoading(true)
    try {
      const data = await getHistoryAnswers(shortId)
      setAnswers(data.answers)
      setShowAnswers(true)
    } catch (err: any) {
      console.error('获取答案失败:', err)
      toast.error('获取答案失败：' + (err?.message || '未知错误'))
    } finally {
      setAnswersLoading(false)
    }
  }

  const handlePrintWrapper = async () => {
    if (questions.length === 0) {
      toast.warning('没有可打印的内容')
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
          <button onClick={handleToggleAnswers} className="btn-print" disabled={!shortId || answersLoading}>
            {showAnswers ? '收起答案' : (answersLoading ? '加载中...' : '查看答案')}
          </button>
          <button onClick={handlePrintWrapper} className="btn-print" disabled={!shortId}>打印</button>
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

      {/* 题目列表 - 使用 PrintPreview 组件确保预览和打印格式完全一致 */}
      {questions.length > 0 && (
        <div className="preview-content">
          <PrintPreview questions={questions as any} meta={{ title }} recordTitle={title} />

          {/* 答案区域 */}
          {showAnswers && answers.length > 0 && (
            <div className="answers-section">
              <h3>参考答案</h3>
              <div className="answers-list">
                {answers.map((answer, idx) => (
                  <div key={answer.question_id} className="answer-item">
                    <div className="answer-header">
                      <span className="answer-index">第 {idx + 1} 题</span>
                      <span className="answer-type">{answer.type}</span>
                    </div>
                    <div className="answer-content">
                      <strong>答案：</strong>
                      {answer.answer_text || '暂无答案'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
