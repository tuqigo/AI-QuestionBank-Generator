import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getToken } from '@/auth'
import { getHistoryDetail, createShareUrl } from '@/api/history'
import type { QuestionRecord } from '@/types'
import type { StructuredQuestion } from '@/types/structured'
import StructuredPreviewShared from '@/components/StructuredPreviewShared'
import './HistoryDetail.css'

// 解析结构化数据
function parseStructuredData(aiResponse: string): {
  questions: StructuredQuestion[]
  meta: any | null
} {
  try {
    const data = JSON.parse(aiResponse)
    return {
      questions: data.questions || [],
      meta: data.meta || null
    }
  } catch (e) {
    console.error('解析结构化数据失败:', e)
    return {
      questions: [],
      meta: null
    }
  }
}

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const [showCopyToast, setShowCopyToast] = useState(false)
  const [structuredData, setStructuredData] = useState<{
    questions: StructuredQuestion[]
    meta: any | null
  } | null>(null)

  useEffect(() => {
    if (!id) return
    getHistoryDetail(id)
      .then((data: QuestionRecord) => {
        setRecord(data)
        // 解析结构化数据
        const parsed = parseStructuredData(data.ai_response)
        setStructuredData(parsed)
      })
      .catch((err: unknown) => {
        console.error('加载失败:', err)
        alert('加载失败')
        navigate('/history')
      })
      .finally(() => setLoading(false))
  }, [id, navigate])

  const handleShare = async () => {
    if (!id) return
    try {
      const token = getToken()
      if (!token) {
        alert('请先登录')
        navigate('/')
        return
      }
      const url = await createShareUrl(id)
      setShareUrl(url)
      // 复制到剪贴板
      const fullUrl = window.location.origin + url
      await navigator.clipboard.writeText(fullUrl)
      setShowCopyToast(true)
      setTimeout(() => setShowCopyToast(false), 2000)
    } catch (err) {
      console.error('分享失败:', err)
      alert('生成分享链接失败')
    }
  }

  /**
   * 打印功能
   */
  const handlePrint = async () => {
    if (!structuredData?.questions || structuredData.questions.length === 0) return

    console.log('Print clicked')
    console.log('Questions count:', structuredData.questions.length)

    // 创建打印专用容器
    const printContainer = document.createElement('div')
    printContainer.id = 'print-container'
    printContainer.className = 'print-paper'
    printContainer.style.cssText = `
      position: fixed;
      left: 0;
      top: 0;
      width: 210mm;
      min-height: 297mm;
      padding: 30mm 25mm;
      margin: 10mm auto;
      background: white;
      box-shadow: 0 0 10px rgba(0,0,0,0.5);
      font-family: "Microsoft YaHei", "SimSun", sans-serif;
      font-size: 14pt;
      line-height: 1.8;
      z-index: 999999;
    `

    // 构建打印内容
    const title = record?.title || structuredData.meta?.title || '题目练习'
    let contentHtml = `<h1 style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${title}</h1>`

    // 渲染每道题目
    structuredData.questions.forEach((question, index) => {
      contentHtml += `<div class="question-wrapper" style="margin-bottom: 24px; page-break-inside: avoid;">`
      contentHtml += `<div style="font-weight: bold; margin-bottom: 12px;">${index + 1}. ${question.stem}</div>`

      // 选项
      if (question.options && question.options.length > 0) {
        question.options.forEach((opt, optIndex) => {
          const optionLabel = ['A', 'B', 'C', 'D'][optIndex]
          const optionText = opt.replace(/^[A-D]\.\s*/, '')
          contentHtml += `<div style="margin-left: 32px; margin-bottom: 8px;">${optionLabel}. ${optionText}</div>`
        })
      }

      // 阅读材料
      if (question.passage) {
        contentHtml += `<div style="margin-top: 12px; margin-bottom: 12px; padding: 10px; background: #f5f5f5; border-left: 3px solid #ccc;">${question.passage}</div>`
      }

      contentHtml += `</div>`
    })

    printContainer.innerHTML = contentHtml
    document.body.appendChild(printContainer)

    // 等待 DOM 更新
    await new Promise(resolve => setTimeout(resolve, 100))

    // 等待 MathJax 渲染
    if (window.MathJax?.typesetPromise) {
      await window.MathJax.typesetPromise([printContainer])
    } else if (window.MathJax?.typeset) {
      window.MathJax.typeset([printContainer])
    }

    // 添加延迟确保 DOM 完全渲染
    await new Promise(resolve => setTimeout(resolve, 200))

    console.log('Triggering print')
    window.print()

    // 打印完成后移除容器
    setTimeout(() => {
      document.body.removeChild(printContainer)
    }, 300)
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

  const hasStructuredData = structuredData?.questions && structuredData.questions.length > 0

  return (
    <div className="detail-page">
      {/* 顶部复制成功提示 */}
      {showCopyToast && (
        <div className="copy-toast">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>已复制</span>
        </div>
      )}

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
              try {
                await navigator.clipboard.writeText(window.location.origin + shareUrl)
                setShowCopyToast(true)
                setTimeout(() => setShowCopyToast(false), 2000)
              } catch (err) {
                // 降级方案：使用传统方式复制
                const input = document.createElement('input')
                input.value = window.location.origin + shareUrl
                document.body.appendChild(input)
                input.select()
                document.execCommand('copy')
                document.body.removeChild(input)
                setShowCopyToast(true)
                setTimeout(() => setShowCopyToast(false), 2000)
              }
            }}
            className="btn-copy"
          >
            复制链接
          </button>
        </div>
      )}

      <div className="detail-meta">
        <span>类型：{record.prompt_type === 'image' ? '图片' : '文字'}</span>
        <span>创建时间：{(() => {
          const utcStr = record.created_at.endsWith('Z') ? record.created_at : record.created_at + 'Z'
          return new Date(utcStr).toLocaleString('zh-CN')
        })()}</span>
      </div>

      <div className="detail-prompt">
        <strong>提示词：</strong>
        <p>{record.prompt_content}</p>
      </div>

      <div className="detail-content">
        {hasStructuredData ? (
          <StructuredPreviewShared
            questions={structuredData.questions}
            meta={structuredData.meta}
            recordTitle={record.title}
          />
        ) : (
          <div className="error-message">
            <p>该记录使用旧数据格式，不支持查看</p>
          </div>
        )}
      </div>
    </div>
  )
}
