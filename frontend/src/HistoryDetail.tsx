import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { renderMarkdown } from '@/utils/markdownProcessor'
import { getHistoryDetail, createShareUrl } from '@/api/history'
import { handlePrint as printUtilsHandlePrint } from '@/utils/printUtils'
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
        processEnvironments: false
      },
      options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
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

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!id) return
    getHistoryDetail(parseInt(id))
      .then((data: QuestionRecord) => setRecord(data))
      .catch((err: unknown) => {
        console.error('加载失败:', err)
        alert('加载失败')
        navigate('/history')
      })
      .finally(() => setLoading(false))
  }, [id, navigate])

  // 加载 MathJax 并渲染公式
  useEffect(() => {
    let mounted = true

    const initAndRenderMathJax = async () => {
      if (!record) return

      try {
        await loadMathJax()
        if (mounted && window.MathJax) {
          await new Promise(resolve => setTimeout(resolve, 100))
          if (contentRef.current && window.MathJax.typeset) {
            window.MathJax.typeset([contentRef.current])
            console.log('HistoryDetail MathJax rendered')
          }
        }
      } catch (error) {
        console.error('Failed to process MathJax in HistoryDetail:', error)
      }
    }

    initAndRenderMathJax()

    return () => {
      mounted = false
    }
  }, [record])

  const handleShare = async () => {
    if (!id) return
    try {
      const url = await createShareUrl(parseInt(id))
      setShareUrl(url)
      // 复制到剪贴板
      const fullUrl = window.location.origin + url
      await navigator.clipboard.writeText(fullUrl)
    } catch (err) {
      alert('生成分享链接失败')
    }
  }

  /**
   * 打印功能 - 使用统一打印工具
   */
  const handlePrint = async () => {
    if (!record) return
    await printUtilsHandlePrint(record.ai_response)
  }

  if (loading) {
    return <div className="detail-page"><div className="loading">加载中...</div></div>
  }

  if (!record) {
    return (
      <div className="detail-page">
        <p>记录不存在</p>
        <Link to="/">返回首页</Link>
      </div>
    )
  }

  const questionsHtml = renderMarkdown(record.ai_response)

  return (
    <div className="detail-page">
      <div className="detail-header">
        <h2>{record.title}</h2>
        <div className="detail-actions">
          <button onClick={handlePrint} className="btn-action">打印</button>
          <button onClick={handleShare} className="btn-action">分享</button>
          <Link to="/" className="btn-back">返回首页</Link>
        </div>
      </div>

      {shareUrl && (
        <div className="share-link-display">
          <span>分享链接：</span>
          <a href={shareUrl} target="_blank" rel="noopener noreferrer">{window.location.origin}{shareUrl}</a>
          <button
            onClick={async () => {
              await navigator.clipboard.writeText(window.location.origin + shareUrl)
              alert('链接已复制到剪贴板')
            }}
            className="btn-copy"
          >
            复制链接
          </button>
        </div>
      )}

      <div className="detail-meta">
        <span>类型：{record.prompt_type === 'image' ? '图片' : '文字'}</span>
        <span>创建时间：{new Date(record.created_at).toLocaleString('zh-CN')}</span>
      </div>

      <div className="detail-prompt">
        <strong>提示词：</strong>
        <p>{record.prompt_content}</p>
      </div>

      <div className="detail-content markdown-body">
        <div ref={contentRef} dangerouslySetInnerHTML={{ __html: questionsHtml as string }} />
      </div>
    </div>
  )
}
