import { useState, useEffect, useRef, forwardRef } from 'react'
import { Link } from 'react-router-dom'
import { getHistoryList, deleteHistory } from '@/api/history'
import type { QuestionRecord } from '@/types'

interface HistoryDropdownProps {
  isOpen: boolean
  onClose: () => void
}

// 使用 forwardRef 暴露 dropdownRef
const HistoryDropdown = forwardRef<HTMLDivElement, HistoryDropdownProps>(function HistoryDropdown({ isOpen, onClose }, ref) {
  const [records, setRecords] = useState<QuestionRecord[]>([])
  const [nextCursor, setNextCursor] = useState<number | null>(null)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(false)
  const [deleting, setDeleting] = useState<number | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

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
    if (isOpen) {
      setLoading(true)
      loadHistory()
    }
  }, [isOpen])

  const handleDelete = async (shortId: string) => {
    if (!confirm('确定要删除这条记录吗？')) return
    setDeleting(shortId as unknown as number)
    try {
      await deleteHistory(shortId)
      setRecords(records.filter(r => r.short_id !== shortId))
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    } finally {
      setDeleting(null)
    }
  }

  const formatDate = (dateStr: string) => {
    // 确保时间字符串带 Z 后缀，让 JavaScript 知道这是 UTC 时间
    const utcStr = dateStr.endsWith('Z') ? dateStr : dateStr + 'Z'
    const date = new Date(utcStr)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!isOpen) return null

  return (
    <div className="history-dropdown history-dropdown-content" ref={dropdownRef}>
      <div className="history-dropdown-header">
        <h3>历史记录</h3>
        <button
          type="button"
          className="btn-history-close"
          onClick={onClose}
          title="关闭"
        >
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      {loading ? (
        <div className="history-dropdown-loading">加载中...</div>
      ) : records.length === 0 ? (
        <div className="history-dropdown-empty">
          <p>暂无历史记录</p>
          <Link to="/" onClick={onClose}>去生成题目</Link>
        </div>
      ) : (
        <>
          <div className="history-dropdown-list">
            {records.map(record => (
              <div key={record.short_id} className="history-dropdown-item">
                <a
                  href={`/history/${record.short_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => {
                    e.preventDefault()
                    onClose()
                    window.open(`/history/${record.short_id}`, '_blank', 'noopener,noreferrer')
                  }}
                >
                  <div className="history-item-title">{record.title}</div>
                  <div className="history-item-meta">
                    <span className="history-item-type">{record.prompt_type === 'image' ? '📷' : '📝'}</span>
                    <span className="history-item-date">{formatDate(record.created_at)}</span>
                  </div>
                </a>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    handleDelete(record.short_id)
                  }}
                  disabled={deleting === (record.short_id as unknown as number)}
                  className="btn-delete-item"
                  title="删除"
                >
                  {deleting === (record.short_id as unknown as number) ? '...' : '×'}
                </button>
              </div>
            ))}
          </div>

          {hasMore && (
            <div className="history-dropdown-more">
              <button onClick={() => loadHistory(nextCursor || undefined)}>
                加载更多
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
})

export default HistoryDropdown
