import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { fetchWithAuth, clearToken } from '@/core/auth/userAuth'
import { validatePrompt } from '@/utils/promptValidator'
import { handlePrint } from '@/utils/printUtils'
import HistoryDropdown from '../history/HistoryList'
import ProgressModal from './ProgressModal'
import PrintPreview from '@/components/PrintPreview'
import { generateStructuredQuestions, getTemplates, generateFromTemplate } from '@/core/api/history'
import { getConfigs, type ConfigOption, type TextbookVersionOption } from '@/api/config'
import type { StructuredQuestion, MetaData, TemplateItem, TemplateFilter } from '@/types/question'
import { useMathJaxSimple } from '@/hooks/useMathJax'
import './MainContent.css'

/**
 * 转义 LaTeX 公式中的反斜杠
 * 后端返回的 JSON 中反斜杠被转义为 \\，需要转换回 \
 */
function unescapeLatex(str: string): string {
  return str.replace(/\\\\/g, '\\')
}

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

export default function MainContent({ email, onLogout, fetchUser }: Props) {
  const [prompt, setPrompt] = useState('小学六年级 数学综合练习（分数运算、百分数、圆、比例、统计）')
  // 结构化数据
  const [questions, setQuestions] = useState<StructuredQuestion[]>([])
  const [meta, setMeta] = useState<MetaData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyOpen, setHistoryOpen] = useState(false)

  // 出题模式 - 从 localStorage 读取，默认为 'template'
  const [mode, setMode] = useState<'prompt' | 'template'>(() => {
    const saved = localStorage.getItem('question-generator-mode')
    return (saved === 'prompt' || saved === 'template') ? saved : 'template'
  })

  // 模板相关状态
  const [allTemplates, setAllTemplates] = useState<TemplateItem[]>([])
  const [filteredTemplates, setFilteredTemplates] = useState<TemplateItem[]>([])
  const [templateFilter, setTemplateFilter] = useState<TemplateFilter>(() => {
    const saved = localStorage.getItem('question-generator-filter')
    return saved ? JSON.parse(saved) : {}
  })
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(null)
  const [templateLoading, setTemplateLoading] = useState(false)
  const [templateQuantity, setTemplateQuantity] = useState(15)
  const [filterOpen, setFilterOpen] = useState(false)

  // 配置常量状态
  const [grades, setGrades] = useState<ConfigOption[]>([])
  const [subjects, setSubjects] = useState<ConfigOption[]>([])
  const [semesters, setSemesters] = useState<ConfigOption[]>([])
  const [textbookVersions, setTextbookVersions] = useState<TextbookVersionOption[]>([])

  // 加载配置
  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      const configs = await getConfigs()
      setGrades(configs.grades)
      setSubjects(configs.subjects)
      setSemesters(configs.semesters)
      setTextbookVersions(configs.textbook_versions)
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }

  // 模式切换时保存到 localStorage
  useEffect(() => {
    localStorage.setItem('question-generator-mode', mode)
  }, [mode])

  // 筛选条件变化时保存到 localStorage
  useEffect(() => {
    localStorage.setItem('question-generator-filter', JSON.stringify(templateFilter))
  }, [templateFilter])

  // 监听窗口大小变化，动态更新移动端状态
  useEffect(() => {
    const handleResize = () => {
      // 触发重新渲染，更新 isMobile 状态
      setIsMobileWidth(window.innerWidth <= 768)
    }

    handleResize() // 初始化
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // 使用状态来跟踪是否为移动端宽度
  const [isMobileWidth, setIsMobileWidth] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth <= 768 : false
  )
  const isMobile = isMobileWidth

  // 模板列表 ref，用于 MathJax 渲染
  const templateListRef = useRef<HTMLDivElement>(null)

  // MathJax 渲染 - 模板列表
  useMathJaxSimple(templateListRef, [filteredTemplates])

  // 预览区 ref，用于自动滚动
  const previewRef = useRef<HTMLDivElement>(null)

  // 打印按钮 ref，用于移动端滚动定位
  const printButtonRef = useRef<HTMLButtonElement>(null)

  // 进度条状态
  const [progressStage, setProgressStage] = useState<'preparing' | 'connecting' | 'generating' | 'processing' | 'complete'>('preparing')
  const [showProgress, setShowProgress] = useState(false)

  // 从模板列表中提取唯一的筛选选项
  const getFilterOptionsFromTemplates = (templateList: TemplateItem[]) => {
    if (templateList.length === 0) {
      return {
        grades: [],
        subjects: [],
        semesters: [],
        textbook_versions: [],
      }
    }

    const gradesSet = new Set<string>()
    const subjectsSet = new Set<string>()
    const semestersSet = new Set<string>()
    const textbookVersionsSet = new Set<string>()

    templateList.forEach((template) => {
      if (template.grade) gradesSet.add(template.grade)
      if (template.subject) subjectsSet.add(template.subject)
      if (template.semester) semestersSet.add(template.semester)
      if (template.textbook_version) textbookVersionsSet.add(template.textbook_version)
    })

    // 转换为 ConfigOption 格式
    const getOptionLabel = (type: string, value: string): string => {
      const configMap: Record<string, ConfigOption[]> = {
        grade: grades,
        subject: subjects,
        semester: semesters,
      }
      const options = configMap[type] || []
      return options.find(o => o.value === value)?.label || value
    }

    // 获取教材版本名称（从全局配置中查找）
    const getTextbookVersionName = (versionId: string): string => {
      return textbookVersions.find(v => v.id === versionId)?.name || versionId
    }

    return {
      grades: Array.from(gradesSet).map(g => ({ value: g, label: getOptionLabel('grade', g) })),
      subjects: Array.from(subjectsSet).map(s => ({ value: s, label: getOptionLabel('subject', s) })),
      semesters: Array.from(semestersSet).map(s => ({ value: s, label: getOptionLabel('semester', s) })),
      textbook_versions: Array.from(textbookVersionsSet).map(v => ({ value: v, label: getTextbookVersionName(v) })),
    }
  }

  // 使用全部模板计算筛选选项
  const filterOptions = getFilterOptionsFromTemplates(allTemplates)

  // 前端筛选模板（点击"查找模板"按钮时调用）
  const applyFilter = () => {
    let result = allTemplates

    if (templateFilter.grade) {
      result = result.filter(t => t.grade === templateFilter.grade)
    }
    if (templateFilter.subject) {
      result = result.filter(t => t.subject === templateFilter.subject)
    }
    if (templateFilter.semester) {
      result = result.filter(t => t.semester === templateFilter.semester)
    }
    if (templateFilter.textbook_version) {
      result = result.filter(t => t.textbook_version === templateFilter.textbook_version)
    }

    setFilteredTemplates(result)

    if (result.length === 0) {
      setError('没有找到符合条件的模板')
    } else {
      setError('')
      // 筛选后自动折叠
      setFilterOpen(false)
    }
  }

  // 加载全部模板
  const loadAllTemplates = async () => {
    setTemplateLoading(true)
    setError('')
    try {
      const data = await getTemplates({})
      setAllTemplates(data)

      // 检查是否有保存的筛选配置，有的话应用过滤
      const savedFilter = localStorage.getItem('question-generator-filter')
      if (savedFilter) {
        const parsed = JSON.parse(savedFilter)
        if (parsed.grade || parsed.subject || parsed.semester || parsed.textbook_version) {
          setTemplateFilter(parsed)
          // 等状态更新后应用过滤
          setTimeout(() => {
            let result = data
            if (parsed.grade) {
              result = result.filter(t => t.grade === parsed.grade)
            }
            if (parsed.subject) {
              result = result.filter(t => t.subject === parsed.subject)
            }
            if (parsed.semester) {
              result = result.filter(t => t.semester === parsed.semester)
            }
            if (parsed.textbook_version) {
              result = result.filter(t => t.textbook_version === parsed.textbook_version)
            }
            setFilteredTemplates(result)
            if (result.length === 0) {
              setError('没有找到符合条件的模板')
            }
          }, 0)
          return
        }
      }

      // 没有筛选配置或筛选条件为空，显示全部模板
      setFilteredTemplates(data)
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message || '加载模板失败')
      } else {
        setError('加载模板失败')
      }
      setAllTemplates([])
      setFilteredTemplates([])
    } finally {
      setTemplateLoading(false)
    }
  }

  // 页面加载时，自动加载全部模板
  useEffect(() => {
    if (allTemplates.length === 0 && !templateLoading) {
      loadAllTemplates()
    }
  }, [])

  // 处理模板选择
  const handleTemplateSelect = (template: TemplateItem) => {
    setSelectedTemplate(template)
  }

  // 确认出题（模板模式）
  const generateFromTemplateWrapper = async () => {
    if (!selectedTemplate) {
      setError('请先选择一个模板')
      return
    }

    setError('')
    setLoading(true)
    setShowProgress(true)
    setProgressStage('preparing')
    setQuestions([])
    setMeta(null)

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
      const data = await generateFromTemplate(selectedTemplate.id, templateQuantity)

      if (data.meta) {
        setMeta({
          subject: data.meta.subject as any,
          grade: data.meta.grade as any,
          title: data.meta.title
        })
      }

      if (data.questions) {
        setQuestions(data.questions)
      }

      setProgressStage('complete')

      setTimeout(() => {
        setShowProgress(false)
        // 滚动到打印按钮（仅移动端）- 让按钮位于屏幕中间偏上位置
        if (isMobile && printButtonRef.current) {
          const buttonRect = printButtonRef.current.getBoundingClientRect()
          const scrollTop = window.scrollY + buttonRect.top - 80 // 减去顶部导航栏和一点余量
          window.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
          })
        }
      }, 500)
    } catch (e) {
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
      stageTimers.forEach(clearTimeout)
    }
  }

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

      // 500ms 后关闭进度条并滚动到打印按钮（仅移动端）
      setTimeout(() => {
        setShowProgress(false)
        if (isMobile && printButtonRef.current) {
          printButtonRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
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
   * 打印功能 - 使用 printUtils 中的 handlePrint
   */
  const handlePrintWrapper = async () => {
    if (!questions.length || !meta) return
    // 使用 printUtils 中的 handlePrint，传入结构化题目数据
    await handlePrint(undefined, meta.title, questions, null)
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
            {/* 模式切换 Tab */}
            <section className="panel-section">
              <div className="mode-tabs">
                <button
                  type="button"
                  className={`mode-tab ${mode === 'template' ? 'active' : ''}`}
                  onClick={() => {
                    setMode('template')
                    setError('')
                  }}
                >
                  模板出题
                </button>
                <button
                  type="button"
                  className={`mode-tab ${mode === 'prompt' ? 'active' : ''}`}
                  onClick={() => {
                    setMode('prompt')
                    setError('')
                  }}
                >
                  提示词出题
                </button>
              </div>
            </section>

            {/* 模板出题模式 */}
            {mode === 'template' && (
              <>
                {/* 筛选条件标题栏（可点击展开/收起） */}
                <section className="panel-section">
                  <div
                    className="section-header filter-header"
                    onClick={() => setFilterOpen(!filterOpen)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        setFilterOpen(!filterOpen)
                      }
                    }}
                  >
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M22 3H2L8 10.46V19L10 21H14V10.46L22 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <label>筛选条件</label>
                    <svg
                      className={`filter-toggle-icon ${filterOpen ? 'open' : ''}`}
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M6 9L12 15L18 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  {/* 筛选表单 */}
                  {filterOpen && (
                    <div className="template-filter">
                      <select
                        value={templateFilter.grade || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, grade: e.target.value as any })}
                        className="filter-select"
                      >
                        <option value="">全部年级</option>
                        {filterOptions.grades.map(g => (
                          <option key={g.value} value={g.value}>{g.label}</option>
                        ))}
                      </select>
                      <select
                        value={templateFilter.subject || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, subject: e.target.value as any })}
                        className="filter-select"
                      >
                        <option value="">全部学科</option>
                        {filterOptions.subjects.map(s => (
                          <option key={s.value} value={s.value}>{s.label}</option>
                        ))}
                      </select>
                      <select
                        value={templateFilter.semester || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, semester: e.target.value as any })}
                        className="filter-select"
                      >
                        <option value="">全部学期</option>
                        {filterOptions.semesters.map(s => (
                          <option key={s.value} value={s.value}>{s.label}</option>
                        ))}
                      </select>
                      <select
                        value={templateFilter.textbook_version || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, textbook_version: e.target.value })}
                        className="filter-select"
                      >
                        <option value="">全部版本</option>
                        {filterOptions.textbook_versions.map(v => (
                          <option key={v.value} value={v.value}>{v.label}</option>
                        ))}
                      </select>
                      <button
                        type="button"
                        className="btn-search-template"
                        onClick={applyFilter}
                        disabled={templateLoading}
                      >
                        查找模板
                      </button>
                    </div>
                  )}
                </section>

                {/* 模板列表 */}
                <section className="panel-section">
                  <div className="section-header">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 5H7C6.46957 5 5.96086 5.21071 5.58579 5.58579C5.21071 5.96086 5 6.46957 5 7V19C5 19.5304 5.21071 20.0391 5.58579 20.4142C5.96086 20.7893 6.46957 21 7 21H17C17.5304 21 18.0391 20.7893 18.4142 20.4142C18.7893 20.0391 19 19.5304 19 19V7C19 6.46957 18.7893 5.96086 18.4142 5.58579C18.0391 5.21071 17.5304 5 17 5H15C14.4696 5 14 5.44772 14 6V8C14 8.55228 14.4696 9 15 9H17V19H7V7H9C9.53043 7 10 6.55228 10 6V4C10 3.44772 9.53043 3 9 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <label>模板列表</label>
                  </div>
                  <div className="template-list" ref={templateListRef}>
                    {templateLoading && (
                      <div className="template-loading">
                        <span className="spinner-small"></span>
                        加载中...
                      </div>
                    )}
                    {!templateLoading && filteredTemplates.length === 0 && (
                      <div className="template-empty">
                        点击"查找模板"加载模板列表
                      </div>
                    )}
                    {!templateLoading && filteredTemplates.map((template) => (
                      <div
                        key={template.id}
                        className={`template-item ${selectedTemplate?.id === template.id ? 'selected' : ''}`}
                        onClick={() => handleTemplateSelect(template)}
                      >
                        <div className="template-name">{template.name}</div>
                        {template.example && (
                          <div className="template-example">
                            <span className="example-label">例题：</span>
                            <span className="example-content">{unescapeLatex(template.example)}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>

                {/* 数量选择 */}
                {selectedTemplate && (
                  <section className="panel-section">
                    <div className="section-header">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 20V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M16 20V8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M8 20V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <label>题目数量</label>
                    </div>
                    <div className="quantity-selector">
                      <button
                        type="button"
                        className="quantity-btn"
                        onClick={() => setTemplateQuantity(Math.max(5, templateQuantity - 5))}
                      >
                        -
                      </button>
                      <span className="quantity-value">{templateQuantity} 道</span>
                      <button
                        type="button"
                        className="quantity-btn"
                        onClick={() => setTemplateQuantity(Math.min(100, templateQuantity + 5))}
                      >
                        +
                      </button>
                    </div>
                  </section>
                )}
              </>
            )}

            {/* 提示词出题模式 */}
            {mode === 'prompt' && (
              <>
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
              </>
            )}


            <div className="action-buttons">


              {/* 打印按钮 - 仅在生成成功后显示 */}
              {questions.length > 0 && meta && (
                <button
                  type="button"
                  className="btn-print-sidebar"
                  onClick={handlePrintWrapper}
                  title="打印题目（可另存为 PDF）"
                  aria-label="打印题目"
                  ref={printButtonRef}
                >
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="6,9 6,2 18,2 18,9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M6 18H4C3.46957 18 2.96086 17.7893 2.58579 17.4142C2.21071 17.0391 2 16.5304 2 16V10C2 9.46957 2.21071 8.96086 2.58579 8.58579C2.96086 8.21071 3.46957 8 4 8H20C20.5304 8 21.0391 8.21071 21.4142 8.58579C21.7893 8.96086 22 9.46957 22 10V16C22 16.5304 21.7893 17.0391 21.4142 17.4142C21.0391 17.7893 20.5304 18 20 18H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <rect x="6" y="14" width="12" height="8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  打印题目
                </button>
              )}
              {/* 生成按钮 */}
              {mode === 'prompt' ? (
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
              ) : (
                <button
                  type="button"
                  className="btn-generate"
                  onClick={generateFromTemplateWrapper}
                  disabled={loading || !selectedTemplate}
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
                      {selectedTemplate ? '生成题目' : '请选择模板'}
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </aside>

        {/* 右侧预览区 */}
        <section className="preview" ref={previewRef}>
          <div className="preview-card">
            {questions.length > 0 ? (
              <div className="preview-body">
                <PrintPreview
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
