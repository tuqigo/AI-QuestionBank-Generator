import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { toast } from '@/hooks'
import { getToken } from '@/core/auth/userAuth'
import { getHistoryDetail, createShareUrl, getHistoryQuestions, getHistoryAnswers } from '@/core/api/history'
import { handlePrint } from '@/utils/printUtils'
import { renderMarkdown } from '@/utils/markdownProcessor'
import type { QuestionRecord } from '@/types'
import type { StructuredQuestion, RecordMeta } from '@/types/question'
import PrintPreview from '@/components/PrintPreview'
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
  const hasLoadedRef = useRef(false)
  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const shareUrlRef = useRef<string | null>(null)
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
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareFullUrl, setShareFullUrl] = useState('')

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
        toast.error('加载失败')
        window.location.href = '/history' // 直接使用 window.location 避免依赖 navigate
      })
      .finally(() => setLoading(false))
  }, [id]) // 移除 navigate 依赖

  const handleShare = async () => {
    if (!id) return
    try {
      const token = getToken()
      if (!token) {
        toast.warning('请先登录')
        window.location.href = '/'
        return
      }
      // 生成分享链接
      const url = await createShareUrl(id)
      const fullUrl = window.location.origin + url
      setShareFullUrl(fullUrl)
      shareUrlRef.current = url

      // 检测是否为移动浏览器（微信、Safari 等）
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
      const isWeChat = /MicroMessenger/i.test(navigator.userAgent)

      // 移动端直接显示模态框，不尝试自动复制
      if (isMobile || isWeChat) {
        setShowShareModal(true)
        return
      }

      // PC 端尝试自动复制
      await copyToClipboard(fullUrl)
      toast.success('链接已复制')
    } catch (err) {
      console.error('生成分享链接失败:', err)
      toast.error('生成分享链接失败，请稍后重试')
    }
  }

  // 复制到剪贴板（PC 端使用）
  const copyToClipboard = async (text: string) => {
    // 优先使用 Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text)
        return
      } catch (e) {
        // Clipboard API 失败，降级到 execCommand
      }
    }

    // 降级方案：execCommand
    try {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.left = '-9999px'
      textarea.style.top = '-9999px'
      document.body.appendChild(textarea)
      textarea.select()
      textarea.setSelectionRange(0, textarea.value.length)
      const success = document.execCommand('copy')
      document.body.removeChild(textarea)
      if (!success) {
        throw new Error('execCommand failed')
      }
    } catch (e) {
      // 两种方法都失败，显示模态框让用户手动复制
      setShowShareModal(true)
    }
  }

  const handlePrintWrapper = async () => {
    if (!structuredData?.questions || structuredData.questions.length === 0) {
      toast.warning('没有可打印的内容')
      return
    }

    // 等待 MathJax 加载完成
    if (!window.MathJax || !window.MathJax.typesetPromise) {
      toast.info('MathJax 加载中，请稍后再试')
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
      toast.error('获取答案失败：' + (err?.message || '未知错误'))
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

  return (
    <div className="detail-page">
      <div className="detail-header">
        <h2>{record.title}</h2>
        <div className="detail-actions">
          <button onClick={handlePrintWrapper} className="btn-action">打印</button>
          {/* 暂时不要查看答案 后期有时间再做 接口没有返回答案 */}
          {/* <button onClick={handleToggleAnswers} className="btn-action" disabled={answersLoading}>
            {showAnswers ? '收起答案' : (answersLoading ? '加载中...' : '查看答案')}
          </button> */}
          <button onClick={handleShare} className="btn-action">分享</button>
          <Link to="/" className="btn-back">返回首页</Link>
        </div>
      </div>

      {/* 分享模态框 */}
      {showShareModal && (
        <div className="share-modal-overlay" onClick={() => setShowShareModal(false)}>
          <div className="share-modal" onClick={(e) => e.stopPropagation()}>
            <div className="share-modal-header">
              <h3>分享链接</h3>
              <button className="share-modal-close" onClick={() => setShowShareModal(false)}>×</button>
            </div>
            <div className="share-modal-body">
              <div className="share-link-box">
                <input
                  type="text"
                  className="share-link-input"
                  value={shareFullUrl}
                  readOnly
                  onClick={(e) => e.currentTarget.select()}
                />
                <button
                  className="share-link-copy-btn"
                  onClick={async () => {
                    try {
                      if (navigator.clipboard) {
                        await navigator.clipboard.writeText(shareFullUrl)
                      } else {
                        const textarea = document.createElement('textarea')
                        textarea.value = shareFullUrl
                        textarea.style.position = 'fixed'
                        textarea.style.left = '-9999px'
                        document.body.appendChild(textarea)
                        textarea.select()
                        document.execCommand('copy')
                        document.body.removeChild(textarea)
                      }
                      toast.success('链接已复制')
                    } catch (e) {
                      toast.error('复制失败，请长按链接手动复制')
                    }
                  }}
                >
                  复制
                </button>
              </div>
              {/* 微信浏览器提示 */}
              {/MicroMessenger/i.test(navigator.userAgent) && (
                <div className="wechat-hint">
                  <p>微信内无法直接复制，您可以：</p>
                  <ol>
                    <li>长按上方链接手动复制</li>
                    <li>点击右上角 <span className="icon-dots">⋮</span> 选择「在浏览器打开」</li>
                  </ol>
                </div>
              )}
              {/* Safari 提示 */}
              {/iPhone|iPad|iPod/i.test(navigator.userAgent) && !/Android/i.test(navigator.userAgent) && (
                <div className="safari-hint">
                  <p>Safari 浏览器提示：</p>
                  <ol>
                    <li>点击下方链接打开</li>
                    <li>或使用 Safari 的「分享」按钮分享给他人</li>
                  </ol>
                </div>
              )}
              <a href={shareFullUrl} target="_blank" rel="noopener noreferrer" className="share-link-direct">
                直接打开链接
              </a>
            </div>
          </div>
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
            <PrintPreview
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
