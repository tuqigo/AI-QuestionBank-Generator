import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { marked } from 'marked'
import { getHistoryDetail, deleteHistory, createShareUrl } from '@/api/history'
import type { QuestionRecord } from '@/types'

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [shareUrl, setShareUrl] = useState<string | null>(null)

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

  const handleDelete = async () => {
    if (!confirm('确定要删除这条记录吗？')) return
    if (!id) return
    try {
      await deleteHistory(parseInt(id))
      navigate('/history')
    } catch (err) {
      alert('删除失败')
    }
  }

  const handleShare = async () => {
    if (!id) return
    try {
      const url = await createShareUrl(parseInt(id))
      setShareUrl(url)
      // 复制到剪贴板
      const fullUrl = window.location.origin + url
      await navigator.clipboard.writeText(fullUrl)
      alert('分享链接已复制到剪贴板')
    } catch (err) {
      alert('生成分享链接失败')
    }
  }

  if (loading) {
    return <div className="detail-page"><div className="loading">加载中...</div></div>
  }

  if (!record) {
    return (
      <div className="detail-page">
        <p>记录不存在</p>
        <Link to="/history">返回历史列表</Link>
      </div>
    )
  }

  const questionsHtml = marked(record.ai_response)

  return (
    <div className="detail-page">
      <div className="detail-header">
        <h2>{record.title}</h2>
        <div className="detail-actions">
          <button onClick={handleShare} className="btn-action">分享</button>
          <button onClick={handleDelete} className="btn-action btn-delete">删除</button>
          <Link to="/history" className="btn-back">返回列表</Link>
        </div>
      </div>

      {shareUrl && (
        <div className="share-hint">
          分享链接：{window.location.origin}{shareUrl}
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
        <div dangerouslySetInnerHTML={{ __html: questionsHtml as string }} />
      </div>
    </div>
  )
}
