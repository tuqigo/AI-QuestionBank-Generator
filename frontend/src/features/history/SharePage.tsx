import { useState, useEffect, useRef } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { getToken } from '@/core/auth/userAuth'
import { getSharedRecord, getSharedQuestions } from '@/core/api/history'
import type { QuestionRecord } from '@/types'
import type { StructuredQuestion, RecordMeta } from '@/types/question'
import PrintPreview from '@/components/PrintPreview'
import './SharePage.css'

export default function SharePage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const hasLoadedRef = useRef(false) // 跟踪是否已加载数据

  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [structuredData, setStructuredData] = useState<{
    questions: StructuredQuestion[]
    meta: RecordMeta | null
  } | null>(null)

  // 检查登录状态
  useEffect(() => {
    setIsLoggedIn(!!getToken())
  }, [])

  useEffect(() => {
    if (!id || !token || hasLoadedRef.current) {
      if (!id || !token) {
        setError('无效的分享链接')
        setLoading(false)
      }
      return
    }
    hasLoadedRef.current = true

    // 并行调用两个接口：获取记录基本信息和结构化题目数据
    Promise.all([
      getSharedRecord(id, token),
      getSharedQuestions(id, token)
    ])
      .then(([recordData, questionsData]) => {
        setRecord(recordData)
        // 使用新接口返回的结构化数据
        setStructuredData({
          questions: questionsData.questions,
          meta: questionsData.meta
        })
      })
      .catch((err: unknown) => {
        console.error('加载失败:', err)
        setError('分享记录不存在或链接已失效')
      })
      .finally(() => setLoading(false))
  }, [id, token])

  if (loading) {
    return (
      <div className="share-page">
        <div className="loading">加载中...</div>
      </div>
    )
  }

  if (error || !record) {
    return (
      <div className="share-page">
        <div className="error-card">
          <h2>❌ {error || '记录不存在'}</h2>
          <p>该分享链接可能已失效或记录已被删除</p>
          <div className="auth-hint">
            <p>想生成属于自己的题目吗？</p>
            <a href="/?action=register" className="btn-primary">登录 / 注册</a>
          </div>
        </div>
      </div>
    )
  }

  const hasStructuredData = structuredData?.questions && structuredData.questions.length > 0

  return (
    <div className="share-page">
      <div className="share-header">
        <h1>{record.title}</h1>
        <span className="share-badge">分享题目</span>
      </div>

      <div className="share-meta">
        <span>创建时间：{(() => {
          const utcStr = record.created_at.endsWith('Z') ? record.created_at : record.created_at + 'Z'
          return new Date(utcStr).toLocaleString('zh-CN')
        })()}</span>
      </div>

      <div className="share-content">
        {hasStructuredData ? (
          <PrintPreview
            questions={structuredData.questions}
            meta={structuredData.meta}
            recordTitle={record.title}
          />
        ) : (
          <div className="error-message">
            <p>该记录使用旧数据格式，不支持查看</p>
          </div>
        )}
      </div>

      {!isLoggedIn && (
        <>
          <div className="share-footer">
            <p>想生成属于自己的题目吗？</p>
            <div className="share-actions">
              <a href="/?action=register" className="btn-primary">登录 / 注册</a>
              <Link to="/" className="btn-secondary">返回首页</Link>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
