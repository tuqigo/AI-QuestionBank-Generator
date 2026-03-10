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
              <div key={record.id} className="history-dropdown-item">
                <Link to={`/history/${record.id}`} onClick={onClose}>
                  <div className="history-item-title">{record.title}</div>
                  <div className="history-item-meta">
                    <span className="history-item-type">{record.prompt_type === 'image' ? '📷' : '📝'}</span>
                    <span className="history-item-date">{formatDate(record.created_at)}</span>
                  </div>
                </Link>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    handleDelete(record.id)
                  }}
                  disabled={deleting === record.id}
                  className="btn-delete-item"
                  title="删除"
                >
                  {deleting === record.id ? '...' : '×'}
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
