import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAiRecords, type AiGenerationRecord } from '../services/api'
import './AiRecordsPage.css'

export default function AiRecordsPage() {
  const navigate = useNavigate()
  const [records, setRecords] = useState<AiGenerationRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)

  // 筛选条件
  const [filterSuccess, setFilterSuccess] = useState<string>('')
  const [filterType, setFilterType] = useState<string>('')
  const [filterDateFrom, setFilterDateFrom] = useState<string>('')
  const [filterDateTo, setFilterDateTo] = useState<string>('')

  useEffect(() => {
    loadRecords(1)
  }, [])

  const loadRecords = async (pageNum: number) => {
    setLoading(true)
    try {
      const filter: Record<string, string | boolean | number> = {}
      if (filterSuccess === 'true') filter.success = true
      if (filterSuccess === 'false') filter.success = false
      if (filterType) filter.prompt_type = filterType
      if (filterDateFrom) filter.date_from = filterDateFrom
      if (filterDateTo) filter.date_to = filterDateTo

      const result = await getAiRecords(pageNum, pageSize, filter as any)
      setRecords(result.data)
      setTotal(result.total)
      setHasMore(result.has_more)
      setPage(pageNum)
    } catch (error) {
      console.error('加载 AI 记录失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApplyFilter = () => {
    setPage(1)
    loadRecords(1)
  }

  const handleResetFilter = () => {
    setFilterSuccess('')
    setFilterType('')
    setFilterDateFrom('')
    setFilterDateTo('')
    setPage(1)
    loadRecords(1)
  }

  const handleLoadMore = () => {
    if (hasMore) {
      loadRecords(page + 1)
    }
  }

  const handleViewDetail = (recordId: number) => {
    navigate(`/admin/ai-records/${recordId}`)
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

  const formatDuration = (seconds: number) => {
    if (seconds < 1) {
      return `${(seconds * 1000).toFixed(0)}ms`
    }
    return `${seconds.toFixed(1)}s`
  }

  return (
    <div className="ai-records-page">
      <div className="page-header">
        <h2>AI 生成记录</h2>
      </div>

      {/* 筛选区域 */}
      <div className="filter-section admin-card">
        <div className="admin-card-body">
          <div className="filter-grid">
            <div className="filter-item">
              <label>成功状态</label>
              <select
                value={filterSuccess}
                onChange={(e) => setFilterSuccess(e.target.value)}
              >
                <option value="">全部</option>
                <option value="true">成功</option>
                <option value="false">失败</option>
              </select>
            </div>

            <div className="filter-item">
              <label>类型</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="">全部</option>
                <option value="text">文本生成</option>
                <option value="vision">图片识别</option>
              </select>
            </div>

            <div className="filter-item">
              <label>开始日期</label>
              <input
                type="date"
                value={filterDateFrom}
                onChange={(e) => setFilterDateFrom(e.target.value)}
              />
            </div>

            <div className="filter-item">
              <label>结束日期</label>
              <input
                type="date"
                value={filterDateTo}
                onChange={(e) => setFilterDateTo(e.target.value)}
              />
            </div>

            <div className="filter-actions">
              <button
                className="admin-btn admin-btn-primary"
                onClick={handleApplyFilter}
              >
                筛选
              </button>
              <button
                className="admin-btn admin-btn-secondary"
                onClick={handleResetFilter}
              >
                重置
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 记录列表 */}
      <div className="admin-card">
        <div className="admin-card-body">
          {loading && records.length === 0 ? (
            <div className="admin-loading-state">加载中...</div>
          ) : records.length === 0 ? (
            <div className="admin-empty">
              <div className="admin-empty-icon">📝</div>
              <p>暂无 AI 生成记录</p>
            </div>
          ) : (
            <>
              <div className="records-table-container">
                <table className="records-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>用户</th>
                      <th>类型</th>
                      <th>提示词</th>
                      <th>状态</th>
                      <th>耗时</th>
                      <th>时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((record) => (
                      <tr key={record.id}>
                        <td className="record-id">#{record.id}</td>
                        <td>{record.user_email}</td>
                        <td>
                          <span className={`type-badge ${record.prompt_type}`}>
                            {record.prompt_type === 'text' ? '文本' : '视觉'}
                          </span>
                        </td>
                        <td className="prompt-cell">
                          <span title={record.prompt}>
                            {record.prompt.length > 50
                              ? `${record.prompt.slice(0, 50)}...`
                              : record.prompt}
                          </span>
                        </td>
                        <td>
                          <span className={`status-badge ${record.success ? 'success' : 'failed'}`}>
                            {record.success ? '✓ 成功' : '✗ 失败'}
                          </span>
                        </td>
                        <td className="duration-cell">{formatDuration(record.duration)}</td>
                        <td className="time-cell">{formatDate(record.created_at)}</td>
                        <td>
                          <button
                            className="btn-link"
                            onClick={() => handleViewDetail(record.id)}
                          >
                            详情
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {hasMore && (
                <div className="load-more-container">
                  <button
                    className="admin-btn admin-btn-secondary"
                    onClick={handleLoadMore}
                    disabled={loading}
                  >
                    {loading ? '加载中...' : '加载更多'}
                  </button>
                </div>
              )}

              <div className="pagination-info">
                共 {total} 条记录，当前第 {page} 页
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
