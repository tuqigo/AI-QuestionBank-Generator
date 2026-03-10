import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  getUserDetail,
  getUserRecords,
  disableUser,
  type UserDetail,
  type QuestionRecord
} from '../services/api'
import './UserDetailPage.css'

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [user, setUser] = useState<UserDetail | null>(null)
  const [records, setRecords] = useState<QuestionRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [recordsLoading, setRecordsLoading] = useState(true)
  const [nextCursor, setNextCursor] = useState<number | null>(null)
  const [hasMore, setHasMore] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  const userId = id ? parseInt(id, 10) : 0

  useEffect(() => {
    loadUserDetail()
  }, [userId])

  useEffect(() => {
    loadRecords()
  }, [userId])

  const loadUserDetail = async () => {
    setLoading(true)
    try {
      const data = await getUserDetail(userId)
      setUser(data)
    } catch (error) {
      console.error('加载用户详情失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRecords = async (cursor: number | null = null) => {
    setRecordsLoading(true)
    try {
      const result = await getUserRecords(userId, cursor, 20)
      if (cursor === null) {
        setRecords(result.data)
      } else {
        setRecords(prev => [...prev, ...result.data])
      }
      setNextCursor(result.next_cursor)
      setHasMore(result.has_more)
    } catch (error) {
      console.error('加载用户记录失败:', error)
    } finally {
      setRecordsLoading(false)
    }
  }

  const handleLoadMore = () => {
    if (nextCursor !== null) {
      loadRecords(nextCursor)
    }
  }

  const handleToggleStatus = async () => {
    if (!user) return

    setActionLoading(true)
    try {
      await disableUser(userId, !user.is_disabled)
      await loadUserDetail()
    } catch (error) {
      console.error('更新用户状态失败:', error)
      alert('操作失败')
    } finally {
      setActionLoading(false)
    }
  }

  const handleBack = () => {
    navigate('/admin/users')
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="user-detail-page">
        <div className="admin-loading-state">加载中...</div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="user-detail-page">
        <div className="admin-empty">
          <div className="admin-empty-icon">❌</div>
          <p>用户不存在</p>
        </div>
      </div>
    )
  }

  return (
    <div className="user-detail-page">
      <div className="user-detail-header">
        <button className="back-btn" onClick={handleBack}>
          ← 返回列表
        </button>
      </div>

      <div className="admin-card user-info-card">
        <div className="admin-card-header">
          <h3>用户信息</h3>
        </div>
        <div className="admin-card-body">
          <div className="user-info-grid">
            <div className="user-info-item">
              <span className="user-info-label">用户 ID</span>
              <span className="user-info-value">#{user.id}</span>
            </div>
            <div className="user-info-item">
              <span className="user-info-label">邮箱</span>
              <span className="user-info-value email">{user.email}</span>
            </div>
            <div className="user-info-item">
              <span className="user-info-label">注册时间</span>
              <span className="user-info-value">{formatDate(user.created_at)}</span>
            </div>
            <div className="user-info-item">
              <span className="user-info-label">状态</span>
              <span className={`admin-badge ${user.is_disabled ? 'admin-badge-error' : 'admin-badge-success'}`}>
                {user.is_disabled ? '已禁用' : '正常'}
              </span>
            </div>
            <div className="user-info-item">
              <span className="user-info-label">题目生成次数</span>
              <span className="user-info-value">{user.total_records} 次</span>
            </div>
            {user.last_activity && (
              <div className="user-info-item">
                <span className="user-info-label">最近活动</span>
                <span className="user-info-value">{formatDate(user.last_activity)}</span>
              </div>
            )}
          </div>

          <div className="user-actions">
            <button
              className={`admin-btn ${user.is_disabled ? 'admin-btn-primary' : 'admin-btn-danger'}`}
              onClick={handleToggleStatus}
              disabled={actionLoading}
            >
              {actionLoading ? '操作中...' : (user.is_disabled ? '启用用户' : '禁用用户')}
            </button>
          </div>
        </div>
      </div>

      <div className="admin-card records-section">
        <div className="admin-card-header">
          <h3>题目生成记录</h3>
        </div>
        <div className="admin-card-body">
          {recordsLoading && records.length === 0 ? (
            <div className="admin-loading-state">加载中...</div>
          ) : records.length === 0 ? (
            <div className="admin-empty">
              <div className="admin-empty-icon">📝</div>
              <p>暂无题目生成记录</p>
            </div>
          ) : (
            <>
              {records.map((record) => (
                <div key={record.id} className="record-item">
                  <div className="record-header">
                    <span className="record-id">#{record.id}</span>
                    <span className="record-date">{formatDate(record.created_at)}</span>
                  </div>
                  <h4 className="record-title">{record.title}</h4>
                  <span className="record-type">类型：{record.prompt_type}</span>
                </div>
              ))}

              {hasMore && (
                <div className="load-more-container">
                  <button
                    className="admin-btn admin-btn-secondary"
                    onClick={handleLoadMore}
                    disabled={recordsLoading}
                  >
                    {recordsLoading ? '加载中...' : '加载更多'}
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
