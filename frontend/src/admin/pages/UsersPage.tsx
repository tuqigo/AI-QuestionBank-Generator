import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUsers, type User } from '../services/api'
import './UsersPage.css'

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const navigate = useNavigate()

  const pageSize = 20

  useEffect(() => {
    loadUsers(currentPage)
  }, [currentPage])

  const loadUsers = async (page: number) => {
    setLoading(true)
    try {
      const result = await getUsers(page, pageSize)
      setUsers(result.data)
      setTotal(result.total)
      setHasMore(result.has_more)
    } catch (error) {
      console.error('加载用户列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage)
  }

  const handleUserClick = (userId: number) => {
    navigate(`./${userId}`)
  }

  const formatDate = (dateString: string) => {
    // 确保时间字符串带 Z 后缀，让 JavaScript 知道这是 UTC 时间
    const utcStr = dateString.endsWith('Z') ? dateString : dateString + 'Z'
    const date = new Date(utcStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>用户管理</h1>
        <div className="page-stats">
          共 <span>{total}</span> 个用户
        </div>
      </div>

      <div className="admin-card">
        <div className="admin-card-body">
          {loading ? (
            <div className="admin-loading-state">加载中...</div>
          ) : users.length === 0 ? (
            <div className="admin-empty">
              <div className="admin-empty-icon">👥</div>
              <p>暂无用户数据</p>
            </div>
          ) : (
            <>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>邮箱</th>
                    <th>注册时间</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>#{user.id}</td>
                      <td className="user-email">{user.email}</td>
                      <td>{formatDate(user.created_at)}</td>
                      <td>
                        <span className={`admin-badge ${user.is_disabled ? 'admin-badge-error' : 'admin-badge-success'}`}>
                          {user.is_disabled ? '已禁用' : '正常'}
                        </span>
                      </td>
                      <td>
                        <button
                          className="admin-btn admin-btn-sm admin-btn-secondary"
                          onClick={() => handleUserClick(user.id)}
                        >
                          查看详情
                        </button>
                      </td>
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
