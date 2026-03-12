import { useState, useEffect, useRef, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { renderMarkdown } from './utils/markdownProcessor'
import { handlePrint as printUtilsHandlePrint, countQuestions, splitQuestionsAndAnswers } from './utils/printUtils'
import type { GenerateResponse } from './types'
import { fetchWithAuth, clearToken } from './auth'
import HistoryDropdown from './HistoryList'
import ProgressModal from './components/ProgressModal'
import './App.css'

// 加载 MathJax SVG 脚本（用于打印质量最高的公式渲染）
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

const API_BASE = '/api'

const SHORTCUTS = [
  { label: '口算题', prompt: '小学一年级数学 30 以内加减法 10 道', icon: '🔢' },
  { label: '综合题', prompt: '小学六年级 数学综合练习（分数运算、百分数、圆、比例、统计）', icon: '📝' },
  { label: '应用题', prompt: '小学二年级数学 简单应用题 10 道', icon: '📚' },
  { label: '选择题', prompt: '小学三年级数学 选择题 10 道', icon: '✅' },
  { label: '阅读理解', prompt: '小学四年级语文 阅读理解 2 篇，每篇 3 道题', icon: '📖' },
  { label: '英语题', prompt: '小学三年级英语 单词翻译选择题 10 道', icon: '🔤' },
]

interface Props {
  email: string
  onLogout: () => void
  fetchUser: () => void
}

export default function MainContent({ email, onLogout }: Props) {
  const [prompt, setPrompt] = useState('小学一年级数学 10 以内加减法 20 道，带答案')
  const [markdown, setMarkdown] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [imageHint, setImageHint] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [extendLoading, setExtendLoading] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // 进度条状态
  const [progressStage, setProgressStage] = useState<'preparing' | 'connecting' | 'generating' | 'processing' | 'complete'>('preparing')
  const [showProgress, setShowProgress] = useState(false)

  // 预览区 ref，用于自动滚动
  const previewRef = useRef<HTMLDivElement>(null)

  const generate = async () => {
    const p = prompt.trim()
    if (!p) {
      setError('请输入提示词')
      return
    }
    setError('')
    setLoading(true)
    setShowProgress(true)
    setProgressStage('preparing')

    // 模拟阶段推进（因为无法获取后端真实进度）
    const stageTimers: ReturnType<typeof setTimeout>[] = []

    // 200ms 后进入"连接 AI"阶段
    stageTimers.push(setTimeout(() => {
      setProgressStage('connecting')
    }, 200))

    // 800ms 后进入"生成中"阶段
    stageTimers.push(setTimeout(() => {
      setProgressStage('generating')
    }, 800))

    // 8 秒后如果还在生成中，显示"整理中"
    stageTimers.push(setTimeout(() => {
      if (progressStage === 'generating') {
        setProgressStage('processing')
      }
    }, 8000))

    try {
      const res = await fetchWithAuth(`${API_BASE}/questions/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: p }),
      })
      const data = await res.json()
      if (res.status === 401) {
        clearToken()
        onLogout()
        return
      }
      if (!res.ok) throw new Error((data as { detail?: string }).detail || '生成失败')
      const genRes = data as GenerateResponse
      setMarkdown(genRes.markdown)

      // 完成后显示完成状态
      setProgressStage('complete')

      // 500ms 后关闭进度条并滚动到预览区
      setTimeout(() => {
        setShowProgress(false)
        // 滚动到预览区（移动端）
        if (previewRef.current) {
          previewRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          })
        }
      }, 500)
    } catch (e) {
      setError(e instanceof Error ? e.message : '生成失败')
      setShowProgress(false)
    } finally {
      setLoading(false)
      // 清除所有定时器
      stageTimers.forEach(clearTimeout)
    }
  }

  const handleExtendFromImage = async () => {
    if (!imageFile) {
      setError('请先选择一张题目图片')
      return
    }
    setError('')
    setExtendLoading(true)
    setShowProgress(true)
    setProgressStage('preparing')

    // 模拟阶段推进
    const stageTimers: ReturnType<typeof setTimeout>[] = []

    stageTimers.push(setTimeout(() => {
      setProgressStage('connecting')
    }, 200))

    stageTimers.push(setTimeout(() => {
      setProgressStage('generating')
    }, 800))

    stageTimers.push(setTimeout(() => {
      if (progressStage === 'generating') {
        setProgressStage('processing')
      }
    }, 8000))

    try {
      const formData = new FormData()
      formData.append('file', imageFile)
      formData.append('hint', imageHint)
      const res = await fetchWithAuth(`${API_BASE}/questions/extend-from-image`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (res.status === 401) {
        clearToken()
        onLogout()
        return
      }
      if (!res.ok) throw new Error((data as { detail?: string }).detail || '生成失败')
      setMarkdown((data as { markdown: string }).markdown)

      setProgressStage('complete')

      // 500ms 后关闭进度条并滚动到预览区
      setTimeout(() => {
        setShowProgress(false)
        if (previewRef.current) {
          previewRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          })
        }
      }, 500)
      setImageFile(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : '生成失败')
      setShowProgress(false)
    } finally {
      setExtendLoading(false)
      stageTimers.forEach(clearTimeout)
    }
  }

  /**
   * 打印功能 - 使用统一打印工具
   */
  const handlePrint = async () => {
    if (!markdown) return
    await printUtilsHandlePrint(markdown)
  }

  // 使用 useMemo 缓存分割结果，避免每次渲染都重新计算导致引用变化
  const { questions, answers } = useMemo(() =>
    markdown ? splitQuestionsAndAnswers(markdown) : { questions: '', answers: null },
    [markdown]
  )

  // 使用 useMemo 缓存 HTML 内容，避免不必要的重新渲染导致 MathJax 渲染丢失
  const questionsHtml = useMemo(() =>
    markdown ? renderMarkdown(String(questions || '')) : '',
    [markdown]
  )
  const answersHtml = useMemo(() =>
    answers ? renderMarkdown(String(answers)) : '',
    [answers]
  )

  // 缓存 dangerouslySetInnerHTML 对象，避免每次渲染创建新对象导致 React 重新设置 innerHTML
  const questionsProps = useMemo(() => ({ __html: questionsHtml }), [questionsHtml])
  const answersProps = useMemo(() => ({ __html: answersHtml }), [answersHtml])

  // 引用预览容器，用于 MathJax 渲染
  const questionsRef = useRef<HTMLDivElement>(null)
  const answersRef = useRef<HTMLDivElement>(null)

  // 使用 refs 来跟踪上次渲染的 HTML，避免 React 重新渲染时覆盖 MathJax 的成果
  const prevQuestionsHtmlRef = useRef<string>('')
  const prevAnswersHtmlRef = useRef<string>('')

  // 添加一个触发器，用于在需要时强制重新渲染 MathJax
  const [mathJaxTrigger, setMathJaxTrigger] = useState(0)

  // 跟踪上一次 historyOpen 的状态
  const prevHistoryOpenRef = useRef<boolean>(false)

  // 当 historyOpen 变化时，触发 MathJax 重新渲染（因为 DOM 可能被重新创建）
  useEffect(() => {
    if (markdown && prevHistoryOpenRef.current !== historyOpen) {
      // historyOpen 状态变化，触发 MathJax 重新渲染
      setMathJaxTrigger(prev => prev + 1)
    }
    prevHistoryOpenRef.current = historyOpen
  }, [historyOpen, markdown])

  // 加载 MathJax 并在 markdown 变化时渲染公式
  useEffect(() => {
    let mounted = true

    const initAndRenderMathJax = async () => {
      if (!markdown) return

      try {
        await loadMathJax()

        if (!mounted) return

        // 等待 DOM 更新
        await new Promise(resolve => setTimeout(resolve, 100))

        // 收集需要渲染的元素（排除 null）
        const elements = [questionsRef.current, answersRef.current].filter(Boolean) as HTMLElement[]

        if (elements.length > 0 && window.MathJax) {
          if (window.MathJax.typesetPromise) {
            await window.MathJax.typesetPromise(elements)
          } else if (window.MathJax.typeset) {
            window.MathJax.typeset(elements)
          }
        }
      } catch (error) {
        console.error('Failed to process MathJax:', error)
      }
    }

    initAndRenderMathJax()

    return () => {
      mounted = false
    }
  }, [markdown, mathJaxTrigger])

  return (
    <div className="app">
      {/* 进度条 Modal */}
      <ProgressModal isOpen={showProgress} stage={progressStage} />

      {/* 顶部导航栏 */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-small">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 3L1 9L12 15L21 9L12 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h1>题小宝</h1>
          </div>
          <div className="header-right">
            <div
              className={`history-dropdown-wrapper ${historyOpen ? 'open' : ''}`}
            >
              <button
                className={`btn-history history-dropdown-trigger ${historyOpen ? 'active' : ''}`}
                onClick={() => setHistoryOpen(!historyOpen)}
                title="历史记录"
                aria-label="历史记录"
              >
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
              <HistoryDropdown isOpen={historyOpen} onClose={() => setHistoryOpen(false)} />
            </div>
            <div className="user-info">
              <div className="user-avatar">
                {email.charAt(0).toUpperCase()}
              </div>
              <span className="username">{email}</span>
            </div>
            <button type="button" className="btn-logout" onClick={onLogout} title="退出登录" aria-label="退出登录">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M16 17L21 12L16 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="main">
        {/* 左侧控制面板 */}
        <aside className="sidebar">
          <div className="sidebar-content">
            {/* 快捷按钮 */}
            <section className="panel-section">
              <div className="section-header">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <label>快捷模板</label>
              </div>
              <div className="shortcuts">
                {SHORTCUTS.map((s) => (
                  <button
                    key={s.label}
                    type="button"
                    className="btn-shortcut"
                    onClick={() => setPrompt(s.prompt)}
                  >
                    <span className="shortcut-icon">{s.icon}</span>
                    {s.label}
                  </button>
                ))}
              </div>
            </section>

            {/* 提示词输入 */}
            <section className="panel-section">
              <div className="section-header">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M18.5 2.5C18.8978 2.10217 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10217 21.4999 2.5C21.8977 2.89782 22.1212 3.43739 22.1212 4C22.1212 4.56261 21.8977 5.10217 21.4999 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <label>自定义提示词</label>
              </div>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="例如：小学六年级数学 分数小数混合运算 15 道"
                rows={4}
                className="prompt-input"
              />
            </section>

            {/* 生成按钮 */}
            <div className="action-buttons">
              <button
                type="button"
                className="btn-generate"
                onClick={generate}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    生成中...
                  </>
                ) : (
                  <>
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2V4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M12 20V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M4.92999 4.92999L6.33999 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M17.66 17.66L19.07 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 12H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M20 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M6.33999 17.66L4.92999 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M19.07 4.92999L17.66 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                    生成题目
                  </>
                )}
              </button>
            </div>

            {/* 图片上传 todo 先不做,后期在做 */}
         {/*    <section className="panel-section">
              <div className="section-header">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" strokeWidth="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                  <path d="M21 15L16 10L5 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <label>图片生成扩展题</label>
              </div>
              <div className="image-upload-section">
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    id="image-upload"
                    accept="image/jpeg,image/png,image/webp,image/gif"
                    onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
                    className="file-input"
                  />
                  <label htmlFor="image-upload" className="file-label">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <polyline points="17,8 12,3 7,8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <span>{imageFile ? imageFile.name : '选择图片'}</span>
                  </label>
                </div>
                <input
                  type="text"
                  placeholder="可选：补充说明"
                  value={imageHint}
                  onChange={(e) => setImageHint(e.target.value)}
                  className="hint-input"
                />
                <button
                  type="button"
                  className="btn-extend"
                  onClick={handleExtendFromImage}
                  disabled={extendLoading || !imageFile}
                >
                  {extendLoading ? (
                    <>
                      <span className="spinner-small"></span>
                      生成中...
                    </>
                  ) : (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      识别生成
                    </>
                  )}
                </button>
              </div>
            </section>
 */}
            {/* 错误提示 */}
            {error && (
              <div className="error-message" role="alert">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <circle cx="12" cy="16" r="1" fill="currentColor"/>
                </svg>
                {error}
              </div>
            )}
          </div>
        </aside>

        {/* 右侧预览区 */}
        <section className="preview" ref={previewRef}>
          <div className="preview-header">
            {markdown && (
              <>
                <span className="question-count">
                  {countQuestions(questions)} 道题
                </span>
                <div className="preview-header-actions">
                  <button
                    type="button"
                    className="btn-icon-action"
                    onClick={generate}
                    disabled={loading}
                    title="重新生成"
                    aria-label="重新生成"
                  >
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M23 4V10H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M1 20V14H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M3.51 9.00001C4.01717 7.56678 4.87913 6.2854 6.01547 5.27542C7.1518 4.26543 8.52547 3.55977 10.0083 3.22426C11.4911 2.88875 13.0348 2.93434 14.4952 3.35677C15.9556 3.77921 17.2853 4.56506 18.36 5.64001L23 10.0001M1 14.0001L5.64 18.3601C6.71475 19.435 8.04437 20.2209 9.5048 20.6433C10.9652 21.0658 12.5089 21.1114 13.9917 20.7758C15.4745 20.4403 16.8482 19.7347 17.9845 18.7247C19.1209 17.7147 19.9828 16.4333 20.49 15.0001" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                  <button
                    type="button"
                    className="btn-icon-action"
                    onClick={handlePrint}
                    title="打印题目（可另存为 PDF）"
                    aria-label="打印题目"
                  >
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polyline points="6,9 6,2 18,2 18,9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M6 18H4C3.46957 18 2.96086 17.7893 2.58579 17.4142C2.21071 17.0391 2 16.5304 2 16V10C2 9.46957 2.21071 8.96086 2.58579 8.58579C2.96086 8.21071 3.46957 8 4 8H20C20.5304 8 21.0391 8.21071 21.4142 8.58579C21.7893 8.96086 22 9.46957 22 10V16C22 16.5304 21.7893 17.0391 21.4142 17.4142C21.0391 17.7893 20.5304 18 20 18H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <rect x="6" y="14" width="12" height="8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </button>
                </div>
              </>
            )}
          </div>
          <div className="preview-card">
            {markdown ? (
              <div className="preview-body markdown-body">
                <div ref={questionsRef} dangerouslySetInnerHTML={questionsProps} />
                {answersHtml && (
                  <div ref={answersRef} className="answer-section" dangerouslySetInnerHTML={answersProps} />
                )}
              </div>
            ) : (
              <div className="placeholder">
                <div className="placeholder-icon">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 6V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <p>输入提示词并点击「生成题目」</p>
                <p className="placeholder-hint">题目和答案将在此处预览，支持直接打印或另存为 PDF</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}
