import { useState, useEffect } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { renderMarkdown } from '@/utils/markdownProcessor'
import { getSharedRecord } from '@/api/history'
import type { QuestionRecord } from '@/types'

// 加载 MathJax SVG 脚本
const loadMathJax = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (window.MathJax) {
      resolve()
      return
    }
    // 先设置配置
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

export default function SharePage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''

  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id || !token) {
      setError('无效的分享链接')
      setLoading(false)
      return
    }

    getSharedRecord(id, token)
      .then((data: QuestionRecord) => setRecord(data))
      .catch((err: unknown) => {
        console.error('加载失败:', err)
        setError('分享记录不存在或链接已失效')
      })
      .finally(() => setLoading(false))
  }, [id, token])

  // 加载 MathJax 并渲染公式
  useEffect(() => {
    let mounted = true

    const initAndRenderMathJax = async () => {
      if (!record) return

      try {
        await loadMathJax()
        if (mounted && window.MathJax) {
          await new Promise(resolve => setTimeout(resolve, 100))
          const content = document.querySelector('.share-content')
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

  if (loading) {
    return (
      <div className="share-page">
        <div className="loading">加载中...</div>
      </div>
    )
  }

  if (error || !record) {
    return (
      <div className="share-page">
        <div className="error-card">
          <h2>❌ {error || '记录不存在'}</h2>
          <p>该分享链接可能已失效或记录已被删除</p>
          <div className="auth-hint">
            <p>想生成属于自己的题目吗？</p>
            <Link to="/login" className="btn-primary">登录 / 注册</Link>
          </div>
        </div>
      </div>
    )
  }

  const questionsHtml = renderMarkdown(record.ai_response)

  return (
    <div className="share-page">
      <div className="share-header">
        <h1>{record.title}</h1>
        <span className="share-badge">分享题目</span>
      </div>

      <div className="share-meta">
        <span>创建时间：{(() => {
          const d = new Date(record.created_at)
          return d.toLocaleString('zh-CN')
        })()}</span>
      </div>

      <div className="share-content markdown-body">
        <div dangerouslySetInnerHTML={{ __html: questionsHtml as string }} />
      </div>

      <div className="share-footer">
        <p>想生成属于自己的题目吗？</p>
        <div className="share-actions">
          <Link to="/login" className="btn-primary">登录 / 注册</Link>
          <Link to="/" className="btn-secondary">返回首页</Link>
        </div>
      </div>
    </div>
  )
}
