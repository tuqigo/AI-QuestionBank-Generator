import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getHistoryList, deleteHistory } from '@/api/history'
import type { QuestionRecord } from '@/types'

export default function HistoryList() {
  const [records, setRecords] = useState<QuestionRecord[]>([])
  const [nextCursor, setNextCursor] = useState<number | null>(null)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<number | null>(null)

  const loadHistory = async (cursor?: number) => {
    try {
      const res = await getHistoryList(cursor, 20)
      setRecords(cursor ? [...records, ...res.data] : res.data)
      setNextCursor(res.next_cursor)
      setHasMore(res.has_more)
    } catch (error) {
      console.error('加载历史记录失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这条记录吗？')) return
    setDeleting(id)
    try {
      await deleteHistory(id)
      setRecords(records.filter(r => r.id !== id))
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    } finally {
      setDeleting(null)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="history-page">
        <div className="loading">加载中...</div>
      </div>
    )
  }

  return (
    <div className="history-page">
      <div className="history-header">
        <h2>历史记录</h2>
        <Link to="/" className="btn-back">返回首页</Link>
      </div>

      {records.length === 0 ? (
        <div className="empty-state">
          <p>暂无历史记录</p>
          <Link to="/">去生成题目</Link>
        </div>
      ) : (
        <>
          <div className="history-list">
            {records.map(record => (
              <div key={record.id} className="history-card">
                <div className="card-header">
                  <h3>{record.title}</h3>
                  <span className="card-type">{record.prompt_type === 'image' ? '📷 图片' : '📝 文字'}</span>
                </div>
                <p className="card-preview">{record.prompt_content.slice(0, 100)}...</p>
                <div className="card-footer">
                  <span className="card-date">{formatDate(record.created_at)}</span>
                  <div className="card-actions">
                    <Link to={`/history/${record.id}`} className="btn-link">查看</Link>
                    <button
                      onClick={() => handleDelete(record.id)}
                      disabled={deleting === record.id}
                      className="btn-link btn-delete"
                    >
                      {deleting === record.id ? '删除中...' : '删除'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {hasMore && (
            <div className="load-more">
              <button onClick={() => loadHistory(nextCursor || undefined)}>
                加载更多
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
