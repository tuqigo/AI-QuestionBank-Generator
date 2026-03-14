import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getToken } from '@/core/auth/userAuth'
import { getHistoryDetail, createShareUrl, getHistoryQuestions, getHistoryAnswers } from '@/core/api/history'
import { handlePrint } from '@/utils/printUtils'
import { renderMarkdown } from '@/utils/markdownProcessor'
import type { QuestionRecord } from '@/types'
import type { StructuredQuestion, RecordMeta } from '@/types/question'
import StructuredPreviewShared from '@/components/StructuredPreviewShared'
import './HistoryDetail.css'

// 解析结构化数据
function parseStructuredData(aiResponse: string): {
  questions: StructuredQuestion[]
  meta: RecordMeta | null
} {
  try {
    const data = JSON.parse(aiResponse)
    return {
      questions: data.questions || [],
      meta: data.meta || null
    }
  } catch (e) {
    console.error('解析结构化数据失败:', e)
    return {
      questions: [],
      meta: null
    }
  }
}

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>()
  const hasLoadedRef = useRef(false) // 跟踪是否已加载数据
  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const shareUrlRef = useRef<string | null>(null) // 使用 ref 存储分享链接，避免触发重新渲染
  const [showCopyToast, setShowCopyToast] = useState(false)
  const [structuredData, setStructuredData] = useState<{
    questions: StructuredQuestion[]
    meta: RecordMeta | null
  } | null>(null)
  const [answers, setAnswers] = useState<Array<{
    question_id: number
    type: string
    answer_text: string
    rows_to_answer?: number
  }>>([])
  const [showAnswers, setShowAnswers] = useState(false)
  const [answersLoading, setAnswersLoading] = useState(false)

  useEffect(() => {
    if (!id || hasLoadedRef.current) return
    hasLoadedRef.current = true

    Promise.all([
      getHistoryDetail(id),
      getHistoryQuestions(id)
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
        alert('加载失败')
        window.location.href = '/history' // 直接使用 window.location 避免依赖 navigate
      })
      .finally(() => setLoading(false))
  }, [id]) // 移除 navigate 依赖

  const handleShare = async () => {
    if (!id) return
    try {
      const token = getToken()
      if (!token) {
        alert('请先登录')
        window.location.href = '/'
        return
      }
      const url = await createShareUrl(id)
      shareUrlRef.current = url
      // 复制到剪贴板
      const fullUrl = window.location.origin + url
      await navigator.clipboard.writeText(fullUrl)
      setShowCopyToast(true)
      setTimeout(() => setShowCopyToast(false), 2000)
    } catch (err) {
      console.error('分享失败:', err)
      alert('生成分享链接失败')
    }
  }

  const handlePrintWrapper = async () => {
    if (!structuredData?.questions || structuredData.questions.length === 0) {
      alert('没有可打印的内容')
      return
    }

    // 等待 MathJax 加载完成
    if (!window.MathJax || !window.MathJax.typesetPromise) {
      alert('MathJax 加载中，请稍后再试')
      return
    }

    // 使用 printUtils 中的 handlePrint，传入结构化题目数据
    const title = record?.title || structuredData.meta?.title || '题目练习'
    await handlePrint(undefined, title, structuredData.questions, null)
  }

  /**
   * 查看答案功能
   */
  const handleToggleAnswers = async () => {
    if (showAnswers) {
      setShowAnswers(false)
      return
    }

    if (!id) return

    setAnswersLoading(true)
    try {
      const data = await getHistoryAnswers(id)
      setAnswers(data.answers)
      setShowAnswers(true)
    } catch (err: any) {
      console.error('获取答案失败:', err)
      alert('获取答案失败：' + (err?.message || '未知错误'))
    } finally {
      setAnswersLoading(false)
    }
  }

  if (loading) {
    return <div className="detail-page"><div className="loading">加载中...</div></div>
  }

  if (!record) {
    return (
      <div className="detail-page">
        <p>记录不存在</p>
        <Link to="/">返回首页</Link>
      </div>
    )
  }

  const hasStructuredData = structuredData?.questions && structuredData.questions.length > 0
  const hasShareUrl = shareUrlRef.current

  return (
    <div className="detail-page">
      {/* 顶部复制成功提示 */}
      {showCopyToast && (
        <div className="copy-toast">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>已复制</span>
        </div>
      )}

      <div className="detail-header">
        <h2>{record.title}</h2>
        <div className="detail-actions">
          <button onClick={handlePrintWrapper} className="btn-action">打印</button>
          <button onClick={handleToggleAnswers} className="btn-action" disabled={answersLoading}>
            {showAnswers ? '收起答案' : (answersLoading ? '加载中...' : '查看答案')}
          </button>
          <button onClick={handleShare} className="btn-action">分享</button>
          <Link to="/" className="btn-back">返回首页</Link>
        </div>
      </div>

      {hasShareUrl && (
        <div className="share-link-display">
          <span>分享链接：</span>
          <a href={shareUrlRef.current!} target="_blank" rel="noopener noreferrer">{window.location.origin}{shareUrlRef.current}</a>
          <button
            onClick={async () => {
              try {
                await navigator.clipboard.writeText(window.location.origin + shareUrlRef.current)
                setShowCopyToast(true)
                setTimeout(() => setShowCopyToast(false), 2000)
              } catch (err) {
                // 降级方案：使用传统方式复制
                const input = document.createElement('input')
                input.value = window.location.origin + shareUrlRef.current
                document.body.appendChild(input)
                input.select()
                document.execCommand('copy')
                document.body.removeChild(input)
                setShowCopyToast(true)
                setTimeout(() => setShowCopyToast(false), 2000)
              }
            }}
            className="btn-copy"
          >
            复制链接
          </button>
        </div>
      )}

      <div className="detail-meta">
        <span>类型：{record.prompt_type === 'image' ? '图片' : '文字'}</span>
        <span>创建时间：{(() => {
          const utcStr = record.created_at.endsWith('Z') ? record.created_at : record.created_at + 'Z'
          return new Date(utcStr).toLocaleString('zh-CN')
        })()}</span>
      </div>

      <div className="detail-prompt">
        <strong>提示词：</strong>
        <p>{record.prompt_content}</p>
      </div>

      <div className="detail-content">
        {hasStructuredData ? (
          <>
            <StructuredPreviewShared
              questions={structuredData.questions}
              meta={structuredData.meta}
              recordTitle={record.title}
            />

            {/* 答案区域 */}
            {showAnswers && answers.length > 0 && (
              <div className="answers-section">
                <h3>参考答案</h3>
                <div className="answers-list">
                  {answers.map((answer, idx) => (
                    <div key={answer.question_id} className="answer-item">
                      <div className="answer-header">
                        <span className="answer-index">第 {idx + 1} 题</span>
                        <span className="answer-type">{answer.type}</span>
                      </div>
                      <div className="answer-content">
                        <strong>答案：</strong>
                        {answer.answer_text || '暂无答案'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="error-message">
            <p>该记录使用旧数据格式，不支持查看</p>
          </div>
        )}
      </div>
    </div>
  )
}
