import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { toast } from '@/hooks'
import { getHistoryList, deleteHistory } from '@/core/api/history'
import type { QuestionRecordListItem } from '@/types'

// 内联样式 - 避免 CSS 加载延迟
const inlineStyles = {
  loading: {
    padding: '32px 16px',
    textAlign: 'center' as const,
    color: '#737373',
    fontSize: '0.9375rem',
    display: 'flex' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: '12px',
  },
  spinner: {
    width: '20px',
    height: '20px',
    border: '2px solid #fed7aa',
    borderTopColor: '#f97316',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
  empty: {
    padding: '40px 16px',
    textAlign: 'center' as const,
  },
  emptyText: {
    color: '#737373',
    fontSize: '0.9375rem',
    marginBottom: '16px',
  },
  emptyLink: {
    color: '#ea580c',
    textDecoration: 'none',
    fontWeight: 500,
    fontSize: '0.9375rem',
  },
}

const loadingSpinnerKeyframes = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`

interface HistoryDropdownProps {
  isOpen: boolean
  onClose: () => void
}

export default function HistoryDropdown({ isOpen, onClose }: HistoryDropdownProps) {
  const [records, setRecords] = useState<QuestionRecordListItem[]>([])
  const [nextCursor, setNextCursor] = useState<number | null>(null)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(false)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<{ open: boolean; shortId: string; title: string } | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const loadHistory = async (cursor?: number) => {
    if (loading) return
    setLoading(true)
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

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isOpen && dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, onClose])

  // 无限滚动加载
  useEffect(() => {
    const listElement = listRef.current
    if (!listElement || !hasMore) return

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = listElement
      // 当滚动到距离底部 50px 时加载更多内容
      if (scrollHeight - scrollTop - clientHeight < 50 && !loading) {
        loadHistory(nextCursor || undefined)
      }
    }

    listElement.addEventListener('scroll', handleScroll)
    return () => {
      listElement.removeEventListener('scroll', handleScroll)
    }
  }, [hasMore, loading, nextCursor])

  const handleDeleteRequest = (shortId: string, title: string) => {
    setDeleteConfirm({ open: true, shortId, title })
  }

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return
    setDeleting(deleteConfirm.shortId as unknown as number)
    try {
      await deleteHistory(deleteConfirm.shortId)
      setRecords(records.filter(r => r.short_id !== deleteConfirm.shortId))
      setDeleteConfirm(null)
    } catch (error) {
      console.error('删除失败:', error)
      toast.error('删除失败')
    } finally {
      setDeleting(null)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteConfirm(null)
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
    <div className="history-dropdown" ref={dropdownRef}>
      {/* 内联 keyframes 动画 */}
      <style>{loadingSpinnerKeyframes}</style>
      <div className="history-dropdown-header">
        <h3>历史记录</h3>
        <button
          type="button"
          className="btn-history-close"
          onClick={onClose}
          title="关闭"
          aria-label="关闭历史记录"
        >
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      {loading && records.length === 0 ? (
        <div style={inlineStyles.loading}>
          <span style={inlineStyles.spinner}></span>
          加载中...
        </div>
      ) : records.length === 0 ? (
        <div style={inlineStyles.empty}>
          <p style={inlineStyles.emptyText}>暂无历史记录</p>
          <Link to="/" onClick={onClose} style={inlineStyles.emptyLink}>去生成题目</Link>
        </div>
      ) : (
        <>
          <div className="history-dropdown-list" ref={listRef}>
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
                    handleDeleteRequest(record.short_id, record.title)
                  }}
                  disabled={deleting === (record.short_id as unknown as number)}
                  className="btn-delete-item"
                  title="删除"
                  aria-label={`删除 ${record.title}`}
                >
                  {deleting === (record.short_id as unknown as number) ? '...' : '×'}
                </button>
              </div>
            ))}
          </div>

          {loading && (
            <div style={{
              padding: '12px 16px',
              textAlign: 'center',
              color: '#737373',
              fontSize: '0.8125rem',
              background: '#f9fafb',
            }}>加载中...</div>
          )}
        </>
      )}

      {/* 自定义删除确认对话框 */}
      {deleteConfirm && (
        <div className="delete-confirm-overlay">
          <div className="delete-confirm-dialog">
            <h4 className="delete-confirm-title">确定删除？</h4>
            <div className="delete-confirm-actions">
              <button
                className="btn-delete-confirm-cancel"
                onClick={handleDeleteCancel}
                disabled={deleting !== null}
              >
                取消
              </button>
              <button
                className="btn-delete-confirm-delete"
                onClick={handleDeleteConfirm}
                disabled={deleting !== null}
              >
                {deleting === (deleteConfirm.shortId as unknown as number) ? '删除中...' : '删除'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
