import { useState, useEffect, useRef, useMemo } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { renderMarkdown } from '@/utils/markdownProcessor'
import { getHistoryDetail, createShareUrl } from '@/api/history'
import { handlePrint as printUtilsHandlePrint, splitQuestionsAndAnswers } from '@/utils/printUtils'
import type { QuestionRecord } from '@/types'

// 加载 MathJax SVG 脚本
const loadMathJax = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (window.MathJax) {
      resolve()
      return
    }
    // 先设置配置
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: false,
        processEnvironments: true,
        packages: ['base', 'ams', 'require']
      },
      options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
        ignoreHtmlClass: 'tex2jax_ignore'
      },
      svg: {
        fontCache: 'global'
      }
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load MathJax SVG'))
    document.head.appendChild(script)
  })
}

// 清理答案标题文本
function cleanAnswerText(text: string) {
  if (!text) return ''
  return text.replace(/\s*## 答案\s*/g, '')
}

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [record, setRecord] = useState<QuestionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const questionsRef = useRef<HTMLDivElement>(null)
  const answersRef = useRef<HTMLDivElement>(null)

  // 分割题目和答案，分别渲染
  const { questions, answers } = useMemo(() =>
    record ? splitQuestionsAndAnswers(record.ai_response) : { questions: '', answers: null },
    [record]
  )

  // 分别渲染题目和答案的 HTML
  const questionsHtml = useMemo(() =>
    record ? renderMarkdown(questions) : '',
    [record, questions]
  )

  const answersHtml = useMemo(() =>
    answers ? renderMarkdown(cleanAnswerText(answers)) : '',
    [answers]
  )

  // 缓存 dangerouslySetInnerHTML 对象
  const questionsProps = useMemo(() => ({ __html: questionsHtml }), [questionsHtml])
  const answersProps = useMemo(() => ({ __html: answersHtml }), [answersHtml])

  useEffect(() => {
    if (!id) return
    getHistoryDetail(parseInt(id))
      .then((data: QuestionRecord) => setRecord(data))
      .catch((err: unknown) => {
        console.error('加载失败:', err)
        alert('加载失败')
        navigate('/history')
      })
      .finally(() => setLoading(false))
  }, [id, navigate])

  // 加载 MathJax 并渲染公式
  useEffect(() => {
    let mounted = true

    const initAndRenderMathJax = async () => {
      if (!record) return

      try {
        await loadMathJax()
        if (mounted && window.MathJax) {
          // 等待 DOM 更新
          await new Promise(resolve => setTimeout(resolve, 100))

          // 收集需要渲染的元素（排除 null）
          const elements = [questionsRef.current, answersRef.current].filter(Boolean) as HTMLElement[]

          if (elements.length > 0 && window.MathJax.typesetPromise) {
            await window.MathJax.typesetPromise(elements)
            console.log('HistoryDetail MathJax rendered', { elementsCount: elements.length })
          }
        }
      } catch (error) {
        console.error('Failed to process MathJax in HistoryDetail:', error)
      }
    }

    initAndRenderMathJax()

    return () => {
      mounted = false
    }
  }, [record])

  const handleShare = async () => {
    if (!id) return
    try {
      const url = await createShareUrl(parseInt(id))
      setShareUrl(url)
      // 复制到剪贴板
      const fullUrl = window.location.origin + url
      await navigator.clipboard.writeText(fullUrl)
    } catch (err) {
      alert('生成分享链接失败')
    }
  }

  /**
   * 打印功能 - 使用统一打印工具
   */
  const handlePrint = async () => {
    if (!record) return
    await printUtilsHandlePrint(record.ai_response)
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

  return (
    <div className="detail-page">
      <div className="detail-header">
        <h2>{record.title}</h2>
        <div className="detail-actions">
          <button onClick={handlePrint} className="btn-action">打印</button>
          <button onClick={handleShare} className="btn-action">分享</button>
          <Link to="/" className="btn-back">返回首页</Link>
        </div>
      </div>

      {shareUrl && (
        <div className="share-link-display">
          <span>分享链接：</span>
          <a href={shareUrl} target="_blank" rel="noopener noreferrer">{window.location.origin}{shareUrl}</a>
          <button
            onClick={async () => {
              await navigator.clipboard.writeText(window.location.origin + shareUrl)
              alert('链接已复制到剪贴板')
            }}
            className="btn-copy"
          >
            复制链接
          </button>
        </div>
      )}

      <div className="detail-meta">
        <span>类型：{record.prompt_type === 'image' ? '图片' : '文字'}</span>
        <span>创建时间：{new Date(record.created_at).toLocaleString('zh-CN')}</span>
      </div>

      <div className="detail-prompt">
        <strong>提示词：</strong>
        <p>{record.prompt_content}</p>
      </div>

      <div className="detail-content markdown-body">
        <div ref={questionsRef} dangerouslySetInnerHTML={questionsProps} />
        {answersHtml && (
          <div ref={answersRef} className="answer-section" dangerouslySetInnerHTML={answersProps} />
        )}
      </div>
    </div>
  )
}
