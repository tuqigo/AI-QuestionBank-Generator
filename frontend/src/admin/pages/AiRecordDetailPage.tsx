import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getAiRecordDetail, type AiGenerationRecord } from '../services/api'
import './AiRecordDetailPage.css'

export default function AiRecordDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [record, setRecord] = useState<AiGenerationRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) {
      setError('记录 ID 不能为空')
      setLoading(false)
      return
    }

    getAiRecordDetail(parseInt(id, 10))
      .then((data: AiGenerationRecord) => setRecord(data))
      .catch((err: unknown) => {
        console.error('加载失败:', err)
        setError('记录不存在或加载失败')
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleBack = () => {
    navigate('/admin/ai-records')
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

  if (loading) {
    return (
      <div className="ai-record-detail-page">
        <div className="admin-loading-state">加载中...</div>
      </div>
    )
  }

  if (error || !record) {
    return (
      <div className="ai-record-detail-page">
        <div className="admin-empty">
          <div className="admin-empty-icon">❌</div>
          <p>{error || '记录不存在'}</p>
          <button className="admin-btn admin-btn-primary" onClick={handleBack}>
            返回列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="ai-record-detail-page">
      <div className="page-header">
        <button className="back-btn" onClick={handleBack}>
          ← 返回列表
        </button>
        <h2>AI 生成记录详情</h2>
      </div>

      {/* 基本信息卡片 */}
      <div className="admin-card info-section">
        <div className="admin-card-header">
          <h3>基本信息</h3>
        </div>
        <div className="admin-card-body">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">记录 ID</span>
              <span className="info-value">#{record.id}</span>
            </div>
            <div className="info-item">
              <span className="info-label">用户</span>
              <span className="info-value email">{record.user_email}</span>
            </div>
            <div className="info-item">
              <span className="info-label">用户 ID</span>
              <span className="info-value">#{record.user_id}</span>
            </div>
            <div className="info-item">
              <span className="info-label">生成类型</span>
              <span className={`type-badge ${record.prompt_type}`}>
                {record.prompt_type === 'text' ? '文本生成' : '图片识别'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">状态</span>
              <span className={`status-badge ${record.success ? 'success' : 'failed'}`}>
                {record.success ? '✓ 成功' : '✗ 失败'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">耗时</span>
              <span className="info-value duration">{formatDuration(record.duration)}</span>
            </div>
            <div className="info-item full-width">
              <span className="info-label">创建时间</span>
              <span className="info-value">{formatDate(record.created_at)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 提示词卡片 */}
      <div className="admin-card prompt-section">
        <div className="admin-card-header">
          <h3>提示词</h3>
        </div>
        <div className="admin-card-body">
          <div className="prompt-content">{record.prompt}</div>
        </div>
      </div>

      {/* 错误信息（仅失败时显示） */}
      {record.error_message && (
        <div className="admin-card error-section">
          <div className="admin-card-header">
            <h3>❌ 错误信息</h3>
          </div>
          <div className="admin-card-body">
            <div className="error-content">{record.error_message}</div>
          </div>
        </div>
      )}
    </div>
  )
}
