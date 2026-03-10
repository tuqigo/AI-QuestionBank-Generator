import React, { useState, useEffect } from 'react'
import { getOperationLogs, type OperationLog } from '../services/api'
import './OperationLogsPage.css'

export default function OperationLogsPage() {
  const [logs, setLogs] = useState<OperationLog[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)

  const pageSize = 20

  useEffect(() => {
    loadLogs(currentPage)
  }, [currentPage])

  const loadLogs = async (page: number) => {
    setLoading(true)
    try {
      const result = await getOperationLogs(page, pageSize)
      setLogs(result.data)
      setTotal(result.total)
      setHasMore(result.has_more)
    } catch (error) {
      console.error('加载操作日志失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getActionLabel = (action: string): string => {
    const actionMap: Record<string, string> = {
      'login_success': '登录成功',
      'login_failed': '登录失败',
      'view_user': '查看用户',
      'view_user_records': '查看用户记录',
      'disable_user': '禁用用户',
      'enable_user': '启用用户'
    }
    return actionMap[action] || action
  }

  const getActionColor = (action: string): string => {
    if (action.includes('login')) return 'blue'
    if (action.includes('disable')) return 'red'
    if (action.includes('enable')) return 'green'
    return 'gray'
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="operation-logs-page">
      <div className="page-header">
        <h1>操作日志</h1>
        <div className="page-stats">
          共 <span>{total}</span> 条记录
        </div>
      </div>

      <div className="admin-card">
        <div className="admin-card-body">
          {loading ? (
            <div className="admin-loading-state">加载中...</div>
          ) : logs.length === 0 ? (
            <div className="admin-empty">
              <div className="admin-empty-icon">📋</div>
              <p>暂无操作日志</p>
            </div>
          ) : (
            <>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>操作类型</th>
                    <th>操作员</th>
                    <th>操作对象</th>
                    <th>IP 地址</th>
                    <th>操作时间</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td>#{log.id}</td>
                      <td>
                        <span className={`action-badge action-${getActionColor(log.action)}`}>
                          {getActionLabel(log.action)}
                        </span>
                      </td>
                      <td>{log.operator}</td>
                      <td>
                        {log.target_type && log.target_id ? (
                          <span className="target-info">
                            {log.target_type}: #{log.target_id}
                          </span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td className="ip-address">{log.ip || '-'}</td>
                      <td>{formatDate(log.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {totalPages > 1 && (
                <div className="admin-pagination">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    上一页
                  </button>

                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum
                    if (totalPages <= 5) {
                      pageNum = i + 1
                    } else if (currentPage <= 3) {
                      pageNum = i + 1
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i
                    } else {
                      pageNum = currentPage - 2 + i
                    }
                    return (
                      <button
                        key={pageNum}
                        className={pageNum === currentPage ? 'active' : ''}
                        onClick={() => handlePageChange(pageNum)}
                      >
                        {pageNum}
                      </button>
                    )
                  })}

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages || !hasMore}
                  >
                    下一页
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
