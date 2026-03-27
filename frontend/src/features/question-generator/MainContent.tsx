import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { fetchWithAuth, clearToken } from '@/core/auth/userAuth'
import { validatePrompt } from '@/utils/promptValidator'
import { handleDownloadPDF, preloadPDFLibs } from '@/utils/printUtils'
import HistoryDropdown from '../history/HistoryList'
import ProgressModal from './ProgressModal'
import PrintPreview from '@/components/PrintPreview'
import { generateStructuredQuestions, getTemplates, generateFromTemplate } from '@/core/api/history'
import { getConfigs, type ConfigOption, type TextbookVersionOption } from '@/api/config'
import type { StructuredQuestion, MetaData, TemplateItem, TemplateFilter } from '@/types/question'
import { useMathJaxSimple } from '@/hooks/useMathJax'
import { useSwipeToClose } from '@/hooks/useSwipeToClose'
import { MathJaxText } from '@/admin/components/MathJaxText'
import './MainContent.css'

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
  userGrade?: string | null  // 用户的年级（从 /api/auth/me 获取）
  onLogout: () => void
  fetchUser: () => void
}

export default function MainContent({ email, userGrade, onLogout, fetchUser }: Props) {
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
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch (e) {
        console.error('解析筛选配置失败:', e)
      }
    }
    return {}
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

  // 用户年级获取后，设置为默认筛选条件并加载模板
  useEffect(() => {
    if (!userGrade) {
      // 用户年级还未获取，等待
      return
    }

    // 如果模板还未加载，使用用户年级加载模板
    if (allTemplates.length === 0 && !templateLoading) {
      const newFilter = { grade: userGrade }
      setTemplateFilter(newFilter)

      // 使用新的筛选条件加载模板
      setTemplateLoading(true)
      setError('')
      getTemplates(newFilter)
        .then((data) => {
          setAllTemplates(data)
          setFilteredTemplates(data)
          if (data.length === 0) {
            setError('没有找到符合条件的模板')
          }
        })
        .catch((e) => {
          if (e instanceof Error) {
            setError(e.message || '加载模板失败')
          } else {
            setError('加载模板失败')
          }
          setAllTemplates([])
          setFilteredTemplates([])
        })
        .finally(() => {
          setTemplateLoading(false)
        })
    }
  }, [userGrade])

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

  // 进度条状态
  const [progressStage, setProgressStage] = useState<'preparing' | 'connecting' | 'generating' | 'processing' | 'complete'>('preparing')
  const [showProgress, setShowProgress] = useState(false)

  // 预览模态框状态（仅移动端）
  const [showPreviewModal, setShowPreviewModal] = useState(false)

  // 筛选模态框状态（仅移动端）
  const [showFilterModal, setShowFilterModal] = useState(false)

  // 滑动手势关闭模态框
  useSwipeToClose({
    isOpen: showPreviewModal,
    onClose: () => setShowPreviewModal(false),
    threshold: 80
  })

  useSwipeToClose({
    isOpen: showFilterModal,
    onClose: () => setShowFilterModal(false),
    threshold: 80
  })

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

  // 计算当前筛选条件摘要
  const getFilterSummary = () => {
    const parts: string[] = []
    if (templateFilter.grade) {
      // 年级：如 "二年级"
      const gradeLabel = grades.find(g => g.value === templateFilter.grade)?.label || templateFilter.grade
      parts.push(gradeLabel)
    }
    if (templateFilter.semester) {
      // 学期：只需要括号内容，如 "(下)"
      const semesterLabel = semesters.find(s => s.value === templateFilter.semester)?.label || templateFilter.semester
      // 如果 label 是 "下学期"，转换成 "(下)"
      if (semesterLabel.includes('上')) {
        parts.push('(上)')
      } else if (semesterLabel.includes('下')) {
        parts.push('(下)')
      }
    }
    if (templateFilter.textbook_version) {
      // 版本：如 "沪教版"
      const versionName = textbookVersions.find(v => v.id === templateFilter.textbook_version)?.name ||
                         templateFilter.textbook_version
      parts.push(versionName)
    }
    return parts.length > 0 ? parts.join('') : ''
  }

  const filterSummary = getFilterSummary()

  // 加载并筛选模板（点击"查找模板"按钮时调用）
  const applyFilter = async () => {
    // 必须有年级筛选条件
    if (!templateFilter.grade) {
      setError('请先选择年级')
      return
    }

    setTemplateLoading(true)
    try {
      // 使用当前的筛选条件调用后端 API
      const data = await getTemplates(templateFilter)
      setAllTemplates(data)
      setFilteredTemplates(data)

      if (data.length === 0) {
        setError('没有找到符合条件的模板')
      } else {
        setError('')
      }
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

    // PC 端筛选后自动折叠
    if (!isMobile) {
      setFilterOpen(false)
    }
  }

  // 加载模板（带筛选条件）
  const loadAllTemplates = async () => {
    // 必须有年级筛选条件
    if (!templateFilter.grade) {
      setError('请先选择年级')
      return
    }

    setTemplateLoading(true)
    setError('')
    try {
      // 使用当前的筛选条件调用后端 API
      const data = await getTemplates(templateFilter)
      setAllTemplates(data)
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

      // 预加载 PDF 库（用户点击"生成题目"后提前加载，下载时无延迟）
      preloadPDFLibs().catch(err => {
        console.warn('[PDF] 预加载失败:', err)
      })

      setTimeout(() => {
        setShowProgress(false)
        // 移动端打开预览模态框
        if (isMobile) {
          setShowPreviewModal(true)
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

      // 预加载 PDF 库（用户点击"生成题目"后提前加载，下载时无延迟）
      preloadPDFLibs().catch(err => {
        console.warn('[PDF] 预加载失败:', err)
      })

      // 500ms 后关闭进度条并滚动到打印按钮（仅移动端）
      setTimeout(() => {
        setShowProgress(false)
        // 移动端打开预览模态框
        if (isMobile) {
          setShowPreviewModal(true)
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

  const [downloadingPDF, setDownloadingPDF] = useState(false)

  /**
   * 下载 PDF 功能
   */
  const handleDownloadPDFWrapper = async () => {
    if (!questions.length || !meta) return
    setDownloadingPDF(true)
    try {
      await handleDownloadPDF(questions, meta.title, null)
    } finally {
      setDownloadingPDF(false)
    }
  }

  /**
   * 打开预览模态框（仅移动端）
   */
  const handleOpenPreviewModal = () => {
    if (!questions.length || !meta) return
    setShowPreviewModal(true)
  }

  return (
    <div className="app">
      {/* 进度条 Modal */}
      <ProgressModal isOpen={showProgress} stage={progressStage} />

      {/* 预览模态框（仅移动端） */}
      {isMobile && showPreviewModal && (
        <div className="preview-modal-overlay" onClick={() => setShowPreviewModal(false)}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h3>打印预览</h3>
              <button className="preview-modal-close" onClick={() => setShowPreviewModal(false)}>
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
            <div className="preview-modal-body">
              <PrintPreview
                questions={questions}
                meta={meta}
              />
            </div>
            <div className="preview-modal-footer">
              <button
                type="button"
                className="btn-download-pdf-modal"
                onClick={async () => {
                  await handleDownloadPDFWrapper()
                }}
                disabled={downloadingPDF}
              >
                {downloadingPDF ? (
                  <svg className="spinner-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeDasharray="32 64" opacity="0.3" />
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <polyline points="7 10 12 15 17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                {downloadingPDF ? '生成中...' : '下载 PDF'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 筛选模态框（仅移动端） */}
      {isMobile && showFilterModal && (
        <div className="filter-modal-overlay" onClick={() => setShowFilterModal(false)}>
          <div className="filter-modal" onClick={(e) => e.stopPropagation()}>
            <div className="filter-modal-header">
              <h3>筛选模板</h3>
              <button className="filter-modal-close" onClick={() => setShowFilterModal(false)}>
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
            <div className="filter-modal-body">
              <div className="filter-modal-content">
                {/* 学科 */}
                <div className="filter-modal-section">
                  <label className="filter-modal-label">学科</label>
                  <div className="filter-modal-options">
                    {filterOptions.subjects.map(s => (
                      <button
                        key={s.value}
                        type="button"
                        className={`filter-modal-option ${templateFilter.subject === s.value ? 'selected' : ''}`}
                        onClick={() => setTemplateFilter({ ...templateFilter, subject: s.value })}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>
                {/* 年级 */}
                <div className="filter-modal-section">
                  <label className="filter-modal-label">年级</label>
                  <div className="filter-modal-options">
                    {filterOptions.grades.map(g => (
                      <button
                        key={g.value}
                        type="button"
                        className={`filter-modal-option ${templateFilter.grade === g.value ? 'selected' : ''}`}
                        onClick={() => setTemplateFilter({ ...templateFilter, grade: g.value })}
                      >
                        {g.label}
                      </button>
                    ))}
                  </div>
                </div>
                {/* 学期 */}
                <div className="filter-modal-section">
                  <label className="filter-modal-label">学期</label>
                  <div className="filter-modal-options">
                    {filterOptions.semesters.map(s => (
                      <button
                        key={s.value}
                        type="button"
                        className={`filter-modal-option ${templateFilter.semester === s.value ? 'selected' : ''}`}
                        onClick={() => setTemplateFilter({ ...templateFilter, semester: s.value })}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>
                {/* 版本 */}
                <div className="filter-modal-section">
                  <label className="filter-modal-label">版本</label>
                  <div className="filter-modal-options">
                    {filterOptions.textbook_versions.map(v => (
                      <button
                        key={v.value}
                        type="button"
                        className={`filter-modal-option ${templateFilter.textbook_version === v.value ? 'selected' : ''}`}
                        onClick={() => setTemplateFilter({ ...templateFilter, textbook_version: v.value })}
                      >
                        {v.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className="filter-modal-footer">
              <button
                type="button"
                className="btn-filter-reset"
                onClick={() => {
                  setTemplateFilter({})
                  localStorage.removeItem('question-generator-filter')
                  setFilteredTemplates(allTemplates)
                  setShowFilterModal(false)
                }}
              >
                重置
              </button>
              <button
                type="button"
                className="btn-filter-confirm"
                onClick={() => {
                  applyFilter()
                  setShowFilterModal(false)
                }}
                disabled={templateLoading}
              >
                查找模板
              </button>
            </div>
          </div>
        </div>
      )}

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
                {/* 模板列表 - 合并筛选条件和模板列表 */}
                <section className="panel-section template-section-flex">
                  <div className="section-header">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 5H7C6.46957 5 5.96086 5.21071 5.58579 5.58579C5.21071 5.96086 5 6.46957 5 7V19C5 19.5304 5.21071 20.0391 5.58579 20.4142C5.96086 20.7893 6.46957 21 7 21H17C17.5304 21 18.0391 20.7893 18.4142 20.4142C18.7893 20.0391 19 19.5304 19 19V7C19 6.46957 18.7893 5.96086 18.4142 5.58579C18.0391 5.21071 17.5304 5 17 5H15C14.4696 5 14 5.44772 14 6V8C14 8.55228 14.4696 9 15 9H17V19H7V7H9C9.53043 7 10 6.55228 10 6V4C10 3.44772 9.53043 3 9 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <label>模板列表</label>
                    {/* 筛选按钮（小箭头） */}
                    <button
                      type="button"
                      className="btn-filter-icon"
                      onClick={() => {
                        if (isMobile) {
                          setShowFilterModal(true)
                        } else {
                          setFilterOpen(!filterOpen)
                        }
                      }}
                      title="筛选模板"
                    >
                      {/* 筛选条件摘要 */}
                      {filterSummary && (
                        <span className="filter-summary">{filterSummary}</span>
                      )}
                      <svg
                        className={`filter-toggle-icon ${showFilterModal || filterOpen ? 'open' : ''}`}
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M6 15L12 9L18 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </button>
                  </div>
                  {/* PC 端筛选表单 */}
                  {!isMobile && filterOpen && (
                    <div className="template-filter">
                      <select
                        value={templateFilter.grade || filterOptions.grades[0]?.value || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, grade: e.target.value as any })}
                        className="filter-select"
                      >
                        {filterOptions.grades.map(g => (
                          <option key={g.value} value={g.value}>{g.label}</option>
                        ))}
                      </select>
                      <select
                        value={templateFilter.subject || filterOptions.subjects[0]?.value || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, subject: e.target.value as any })}
                        className="filter-select"
                      >
                        {filterOptions.subjects.map(s => (
                          <option key={s.value} value={s.value}>{s.label}</option>
                        ))}
                      </select>
                      <select
                        value={templateFilter.semester || filterOptions.semesters[0]?.value || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, semester: e.target.value as any })}
                        className="filter-select"
                      >
                        {filterOptions.semesters.map(s => (
                          <option key={s.value} value={s.value}>{s.label}</option>
                        ))}
                      </select>
                      <select
                        value={templateFilter.textbook_version || filterOptions.textbook_versions[0]?.value || ''}
                        onChange={(e) => setTemplateFilter({ ...templateFilter, textbook_version: e.target.value })}
                        className="filter-select"
                      >
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
                  {/* 模板列表 */}
                  <div className="template-list" ref={templateListRef}>
                    {templateLoading && (
                      <div className="template-loading">
                        <span className="spinner-small"></span>
                        加载中...
                      </div>
                    )}
                    {!templateLoading && filteredTemplates.length === 0 && (
                      <div className="template-empty">
                        点击筛选按钮加载模板列表
                      </div>
                    )}
                    {!templateLoading && filteredTemplates.map((template) => (
                      <div
                        key={template.id}
                        className={`template-item ${selectedTemplate?.id === template.id ? 'selected' : ''}`}
                        onClick={() => handleTemplateSelect(template)}
                      >
                        <div className="template-name">{template.name}</div>
                        {template.example && template.example.length > 0 && (
                          <div className="template-example">
                            <span className="example-label">例题：</span>
                            <span className="example-content">
                              <MathJaxText text={template.example[0]} />
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
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

            {/* 动作按钮区域（PC 端） */}
            {!isMobile && (
              <div className="action-buttons">
                {/* 题目数量控制 - 模板模式下显示 */}
                {mode === 'template' && selectedTemplate && (
                  <div className="quantity-control-inline">
                    <button
                      type="button"
                      className="quantity-btn-inline"
                      onClick={() => setTemplateQuantity(Math.max(5, templateQuantity - 5))}
                    >
                      -
                    </button>
                    <span className="quantity-value-inline">{templateQuantity} 道</span>
                    <button
                      type="button"
                      className="quantity-btn-inline"
                      onClick={() => setTemplateQuantity(Math.min(100, templateQuantity + 5))}
                    >
                      +
                    </button>
                  </div>
                )}
                {/* 下载 PDF 按钮 - 仅在生成成功后显示 */}
                {questions.length > 0 && meta && (
                  <button
                    type="button"
                    className="btn-download-pdf"
                    onClick={handleDownloadPDFWrapper}
                    disabled={downloadingPDF}
                    title={downloadingPDF ? '生成中...' : '下载 PDF'}
                    aria-label="下载 PDF"
                  >
                    {downloadingPDF ? (
                      <svg className="spinner-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeDasharray="32 64" opacity="0.3" />
                        <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <polyline points="7 10 12 15 17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                    {downloadingPDF ? '生成中...' : '下载 PDF'}
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
            )}
          </div>
        </aside>

        {/* 移动端底部固定按钮 */}
        {isMobile && (
          <div className="mobile-fixed-footer">
            {mode === 'prompt' ? (
              <button
                type="button"
                className="btn-generate"
                onClick={generate}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner spinner-small"></span>
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
              <div className="mobile-generate-wrapper">
                {/* 题目数量控制 */}
                {selectedTemplate && (
                  <div className="quantity-control-mobile">
                    <button
                      type="button"
                      className="quantity-btn-mobile"
                      onClick={() => setTemplateQuantity(Math.max(5, templateQuantity - 5))}
                    >
                      -
                    </button>
                    <span className="quantity-value-mobile">{templateQuantity} 道</span>
                    <button
                      type="button"
                      className="quantity-btn-mobile"
                      onClick={() => setTemplateQuantity(Math.min(100, templateQuantity + 5))}
                    >
                      +
                    </button>
                  </div>
                )}
                <button
                  type="button"
                  className="btn-generate"
                  onClick={generateFromTemplateWrapper}
                  disabled={loading || !selectedTemplate}
                >
                  {loading ? (
                    <>
                      <span className="spinner spinner-small"></span>
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
              </div>
            )}
          </div>
        )}

        {/* 右侧预览区 */}
        <section className={`preview ${isMobile ? 'mobile-hidden' : ''}`} ref={previewRef}>
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
