import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getUserRecordDetail } from '../services/api'
import { renderMarkdown } from '@/utils/markdownProcessor'
import './UserRecordDetailPage.css'

// 加载 MathJax SVG 脚本
const loadMathJax = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (window.MathJax) {
      resolve()
      return
    }
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
      svg: {
        fontCache: 'global'
      }
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load MathJax SVG'))
    document.head.appendChild(script)
  })
}

export default function UserRecordDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [record, setRecord] = useState<{
    id: number
    title: string
    prompt_type: string
    prompt_content: string
    ai_response: string
    created_at: string
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) {
      setError('记录 ID 不能为空')
      setLoading(false)
      return
    }

    getUserRecordDetail(parseInt(id, 10))
      .then((data) => setRecord(data))
      .catch((err: unknown) => {
        console.error('加载失败:', err)
        setError('记录不存在或加载失败')
      })
      .finally(() => setLoading(false))
  }, [id])

  // 加载 MathJax 并渲染公式
  useEffect(() => {
    let mounted = true

    const initAndRenderMathJax = async () => {
      if (!record) return

      try {
        await loadMathJax()
        if (mounted && window.MathJax) {
          await new Promise(resolve => setTimeout(resolve, 100))
          const content = document.querySelector('.record-content')
          if (content && window.MathJax.typeset) {
            window.MathJax.typeset([content as HTMLElement])
          }
        }
      } catch (error) {
        console.error('Failed to process MathJax:', error)
      }
    }

    initAndRenderMathJax()

    return () => {
      mounted = false
    }
  }, [record])

  const handleBack = () => {
    navigate(-1)
  }

  const formatDate = (dateString: string) => {
    const utcStr = dateString.endsWith('Z') ? dateString : dateString + 'Z'
    const date = new Date(utcStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // 尝试从 AI 响应中提取题目内容（去掉答案部分）
  const getQuestionsContent = () => {
    const content = record?.ai_response || ''
    // 如果有 PAGE_BREAK 标记，只取前面的题目部分
    const breakIndex = content.indexOf('<!-- PAGE_BREAK -->')
    if (breakIndex !== -1) {
      return content.slice(0, breakIndex).trim()
    }
    return content
  }

  const questionsHtml = renderMarkdown(getQuestionsContent())

  if (loading) {
    return (
      <div className="user-record-detail-page">
        <div className="admin-loading-state">加载中...</div>
      </div>
    )
  }

  if (error || !record) {
    return (
      <div className="user-record-detail-page">
        <div className="admin-empty">
          <div className="admin-empty-icon">❌</div>
          <p>{error || '记录不存在'}</p>
          <button className="admin-btn admin-btn-primary" onClick={handleBack}>
            返回列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="user-record-detail-page">
      <div className="page-header">
        <button className="back-btn" onClick={handleBack}>
          ← 返回列表
        </button>
        <h2>题目详情</h2>
      </div>

      <div className="admin-card info-section">
        <div className="admin-card-header">
          <h3>基本信息</h3>
        </div>
        <div className="admin-card-body">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">记录 ID</span>
              <span className="info-value">#{record.id}</span>
            </div>
            <div className="info-item">
              <span className="info-label">标题</span>
              <span className="info-value">{record.title}</span>
            </div>
            <div className="info-item">
              <span className="info-label">类型</span>
              <span className={`type-badge ${record.prompt_type}`}>
                {record.prompt_type === 'text' ? '文本生成' : '图片识别'}
              </span>
            </div>
            <div className="info-item full-width">
              <span className="info-label">创建时间</span>
              <span className="info-value">{formatDate(record.created_at)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="admin-card prompt-section">
        <div className="admin-card-header">
          <h3>提示词</h3>
        </div>
        <div className="admin-card-body">
          <div className="prompt-content">{record.prompt_content}</div>
        </div>
      </div>

      <div className="admin-card content-section">
        <div className="admin-card-header">
          <h3>生成的题目</h3>
        </div>
        <div className="admin-card-body">
          <div className="record-content markdown-body">
            <div dangerouslySetInnerHTML={{ __html: questionsHtml as string }} />
          </div>
        </div>
      </div>
    </div>
  )
}
