import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { fetchWithAuth, clearToken } from './auth'
import { validatePrompt } from './utils/promptValidator'
import HistoryDropdown from './HistoryList'
import ProgressModal from './components/ProgressModal'
import StructuredPreviewShared from './components/StructuredPreviewShared'
import { generateStructuredQuestions } from './api/history'
import type { StructuredQuestion } from './types/structured'
import './App.css'

const SHORTCUTS = [
  { label: '口算题', prompt: '小学一年级数学 数的组成，比大小、多少、长短、高矮、轻重、简单分类、统计', icon: '🔢' },
  { label: '综合题', prompt: '小学六年级 数学综合练习（分数运算、百分数、圆、比例、统计）', icon: '📝' },
  { label: '应用题', prompt: '小学二年级语文，多音字、形近字、同音字辨析、陈述句、疑问句、感叹句', icon: '📚' },
  { label: '选择题', prompt: '上海人沪教牛津版小学三年级英语选择题', icon: '✅' },
  { label: '阅读理解', prompt: '小学四年级语文 阅读理解 2 篇，每篇 3 道题', icon: '📖' },
  { label: '英语题', prompt: '小学6年级英语综合题，题型丰富', icon: '🔤' },
]

interface Props {
  email: string
  onLogout: () => void
  fetchUser: () => void
}

export default function MainContent({ email, onLogout }: Props) {
  const [prompt, setPrompt] = useState('小学六年级 数学综合练习（分数运算、百分数、圆、比例、统计）')
  // 结构化数据
  const [questions, setQuestions] = useState<StructuredQuestion[]>([])
  const [meta, setMeta] = useState<{ subject: string; grade: string; title: string } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyOpen, setHistoryOpen] = useState(false)

  // 进度条状态
  const [progressStage, setProgressStage] = useState<'preparing' | 'connecting' | 'generating' | 'processing' | 'complete'>('preparing')
  const [showProgress, setShowProgress] = useState(false)

  // 预览区 ref，用于自动滚动
  const previewRef = useRef<HTMLDivElement>(null)

  const generate = async () => {
    const p = prompt.trim()

    // 使用统一的校验函数
    const result = validatePrompt(p)
    if (!result.valid) {
      setError(result.error || '请输入题目要求')
      return
    }

    setError('')
    setLoading(true)
    setShowProgress(true)
    setProgressStage('preparing')
    setQuestions([])
    setMeta(null)

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
      // 调用新结构化接口
      const data = await generateStructuredQuestions(p)

      if (data.meta) {
        setMeta({
          subject: data.meta.subject,
          grade: data.meta.grade,
          title: data.meta.title
        })
      }

      if (data.questions) {
        setQuestions(data.questions)
      }

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
      // 友好的错误提示
      let errorMessage = '生成失败，请稍后重试'
      if (e instanceof Error) {
        if (e.message.includes('超时')) {
          errorMessage = '题目生成时间过长，请减少题目数量或简化要求后重试'
        } else if (e.message.includes('网络')) {
          errorMessage = '网络连接失败，请检查网络后重试'
        } else {
          errorMessage = e.message || '系统内部错误，稍后再试！'
        }
      }
      setError(errorMessage)
      setShowProgress(false)
    } finally {
      setLoading(false)
      // 清除所有定时器
      stageTimers.forEach(clearTimeout)
    }
  }

  /**
   * 打印功能 - 使用新的结构化数据打印
   */
  const handlePrint = async () => {
    if (!questions.length || !meta) return

    console.log('Print clicked')
    console.log('Questions count:', questions.length)

    // 创建打印专用容器
    const printContainer = document.createElement('div')
    printContainer.id = 'print-container'
    printContainer.className = 'print-paper'
    printContainer.style.cssText = `
      position: fixed;
      left: 0;
      top: 0;
      width: 210mm;
      min-height: 297mm;
      padding: 30mm 25mm;
      margin: 10mm auto;
      background: white;
      box-shadow: 0 0 10px rgba(0,0,0,0.5);
      font-family: "Microsoft YaHei", "SimSun", sans-serif;
      font-size: 14pt;
      line-height: 1.8;
      z-index: 999999;
    `

    // 构建打印内容
    let contentHtml = `<h1 style="text-align: center; margin-bottom: 30px; font-size: 18pt; font-weight: bold;">${meta.title || '题目练习'}</h1>`

    // 渲染每道题目
    questions.forEach((question, index) => {
      contentHtml += `<div class="question-wrapper" style="margin-bottom: 24px; page-break-inside: avoid;">`
      contentHtml += `<div style="font-weight: bold; margin-bottom: 12px;">${index + 1}. ${question.stem}</div>`

      // 选项
      if (question.options && question.options.length > 0) {
        question.options.forEach((opt, optIndex) => {
          const optionLabel = ['A', 'B', 'C', 'D'][optIndex]
          const optionText = opt.replace(/^[A-D]\.\s*/, '')
          contentHtml += `<div style="margin-left: 32px; margin-bottom: 8px;">${optionLabel}. ${optionText}</div>`
        })
      }

      // 阅读材料
      if (question.passage) {
        contentHtml += `<div style="margin-top: 12px; margin-bottom: 12px; padding: 10px; background: #f5f5f5; border-left: 3px solid #ccc;">${question.passage}</div>`
      }

      contentHtml += `</div>`
    })

    printContainer.innerHTML = contentHtml
    document.body.appendChild(printContainer)

    // 等待 DOM 更新
    await new Promise(resolve => setTimeout(resolve, 100))

    // 等待 MathJax 渲染
    if (window.MathJax?.typesetPromise) {
      await window.MathJax.typesetPromise([printContainer])
    } else if (window.MathJax?.typeset) {
      window.MathJax.typeset([printContainer])
    }

    // 添加延迟确保 DOM 完全渲染
    await new Promise(resolve => setTimeout(resolve, 200))

    console.log('Triggering print')
    window.print()

    // 打印完成后移除容器
    setTimeout(() => {
      document.body.removeChild(printContainer)
    }, 300)
  }

  return (
    <div className="app">
      {/* 进度条 Modal */}
      <ProgressModal isOpen={showProgress} stage={progressStage} />

      {/* 顶部导航栏 */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo-small">
              <img src="/icon64.svg" alt="logo" width="24" height="24" />
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
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                  <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
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
                <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M16 17L21 12L16 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
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
                  <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
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
                  <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M18.5 2.5C18.8978 2.10217 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10217 21.4999 2.5C21.8977 2.89782 22.1212 3.43739 22.1212 4C22.1212 4.56261 21.8977 5.10217 21.4999 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
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
              {/* 错误提示 - 输入框下方 */}
              {error && (
                <div className="error-message-inline" role="alert">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                    <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    <circle cx="12" cy="16" r="1" fill="currentColor" />
                  </svg>
                  {error}
                </div>
              )}
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
                      <path d="M12 2V4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M12 20V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M4.92999 4.92999L6.33999 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M17.66 17.66L19.07 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M2 12H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M20 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M6.33999 17.66L4.92999 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M19.07 4.92999L17.66 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" />
                    </svg>
                    生成题目
                  </>
                )}
              </button>
            </div>
          </div>
        </aside>

        {/* 右侧预览区 */}
        <section className="preview" ref={previewRef}>
          <div className="preview-header">
            {questions.length > 0 && (
              <>
                <span className="question-count">
                  {questions.length} 道题
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
                      <path d="M23 4V10H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M1 20V14H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M3.51 9.00001C4.01717 7.56678 4.87913 6.2854 6.01547 5.27542C7.1518 4.26543 8.52547 3.55977 10.0083 3.22426C11.4911 2.88875 13.0348 2.93434 14.4952 3.35677C15.9556 3.77921 17.2853 4.56506 18.36 5.64001L23 10.0001M1 14.0001L5.64 18.3601C6.71475 19.435 8.04437 20.2209 9.5048 20.6433C10.9652 21.0658 12.5089 21.1114 13.9917 20.7758C15.4745 20.4403 16.8482 19.7347 17.9845 18.7247C19.1209 17.7147 19.9828 16.4333 20.49 15.0001" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
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
                      <polyline points="6,9 6,2 18,2 18,9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M6 18H4C3.46957 18 2.96086 17.7893 2.58579 17.4142C2.21071 17.0391 2 16.5304 2 16V10C2 9.46957 2.21071 8.96086 2.58579 8.58579C2.96086 8.21071 3.46957 8 4 8H20C20.5304 8 21.0391 8.21071 21.4142 8.58579C21.7893 8.96086 22 9.46957 22 10V16C22 16.5304 21.7893 17.0391 21.4142 17.4142C21.0391 17.7893 20.5304 18 20 18H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      <rect x="6" y="14" width="12" height="8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </button>
                </div>
              </>
            )}
          </div>
          <div className="preview-card">
            {questions.length > 0 ? (
              <div className="preview-body">
                <StructuredPreviewShared
                  questions={questions}
                  meta={meta}
                />
              </div>
            ) : (
              <div className="placeholder">
                <div className="placeholder-icon">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 6V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
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
