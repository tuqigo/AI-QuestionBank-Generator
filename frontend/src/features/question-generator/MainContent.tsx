import { useState, useEffect, useRef } from 'react'
import { fetchWithAuth, clearToken } from '@/core/auth/userAuth'
import { validatePrompt } from '@/utils/promptValidator'
import { handleDownloadPDF } from '@/utils/printUtils'
import HistoryDropdown from '../history/HistoryList'
import ProgressModal from './ProgressModal'
import PrintPreview from '@/components/PrintPreview'
import { getTemplates as apiGetTemplates } from '@/core/api/history'
import type { ConfigOption, TextbookVersionOption } from '@/api/config'
import type { StructuredQuestion, MetaData, TemplateItem, TemplateFilter } from '@/types/question'
import { useMathJaxSimple } from '@/hooks/useMathJax'
import { useSwipeToClose } from '@/hooks/useSwipeToClose'
import { useResponsive } from './hooks/useResponsive'
import { useQuestionGenerator } from './hooks/useQuestionGenerator'
import { useTemplateFilter } from './hooks/useTemplateFilter'
import Header from './components/Header'
import ModeTabs from './components/ModeTabs'
import TemplateList from './components/TemplateMode/TemplateList'
import TemplateFilterComponent from './components/TemplateMode/TemplateFilter'
import FilterModal from './components/TemplateMode/FilterModal'
import QuantityControl from './components/TemplateMode/QuantityControl'
import Shortcuts from './components/PromptMode/Shortcuts'
import PromptInput from './components/PromptMode/PromptInput'
import ActionButtons from './components/ActionButtons'
import MobileFooter from './components/MobileFooter'
import PreviewModal from './components/PreviewModal'
import PreviewPanel from './components/PreviewPanel'
import './MainContent.css'

interface Props {
  email: string
  onLogout: () => void
  fetchUser: () => void
}

export default function MainContent({ email, onLogout, fetchUser }: Props) {
  // 核心状态
  const [mode, setMode] = useState<'prompt' | 'template'>(() => {
    const saved = localStorage.getItem('question-generator-mode')
    return (saved === 'prompt' || saved === 'template') ? saved : 'template'
  })
  const [prompt, setPrompt] = useState('小学六年级 数学综合练习（分数运算、百分数、圆、比例、统计）')
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(null)
  const [templateQuantity, setTemplateQuantity] = useState(15)
  const [downloadingPDF, setDownloadingPDF] = useState(false)

  // 使用自定义 hooks
  const { isMobile } = useResponsive()
  const generator = useQuestionGenerator()

  // 模板相关状态
  const [allTemplates, setAllTemplates] = useState<TemplateItem[]>([])
  const [filteredTemplates, setFilteredTemplates] = useState<TemplateItem[]>([])
  const [templateLoading, setTemplateLoading] = useState(false)
  const [filterOpen, setFilterOpen] = useState(false)
  const [showFilterModal, setShowFilterModal] = useState(false)
  const [showPreviewModal, setShowPreviewModal] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)

  // 配置常量
  const [grades, setGrades] = useState<ConfigOption[]>([])
  const [subjects, setSubjects] = useState<ConfigOption[]>([])
  const [semesters, setSemesters] = useState<ConfigOption[]>([])
  const [textbookVersions, setTextbookVersions] = useState<TextbookVersionOption[]>([])

  // 使用模板筛选 hook
  const {
    templateFilter,
    setTemplateFilter,
    filterOptions,
    filterSummary,
    applyFilter,
    resetFilter
  } = useTemplateFilter(allTemplates, grades, subjects, semesters, textbookVersions)

  // 模态框滑动手势
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

  // 模板列表 ref，用于 MathJax 渲染
  const templateListRef = useRef<HTMLDivElement>(null)
  useMathJaxSimple(templateListRef, [filteredTemplates])

  // 预览区 ref，用于自动滚动
  const previewRef = useRef<HTMLDivElement>(null)

  // 加载配置
  useEffect(() => {
    loadConfigs()
  }, [])

  // 模式切换时保存到 localStorage
  useEffect(() => {
    localStorage.setItem('question-generator-mode', mode)
  }, [mode])

  // 页面加载时，自动加载全部模板
  useEffect(() => {
    if (allTemplates.length === 0 && !templateLoading) {
      loadAllTemplates()
    }
  }, [])

  const loadConfigs = async () => {
    try {
      const data = await apiGetTemplates({})
      // 从模板数据中提取配置信息
      if (data.length > 0) {
        const gradesSet = new Set<string>()
        const subjectsSet = new Set<string>()
        const semestersSet = new Set<string>()
        const versionsSet = new Set<string>()
        data.forEach(t => {
          if (t.grade) gradesSet.add(t.grade)
          if (t.subject) subjectsSet.add(t.subject)
          if (t.semester) semestersSet.add(t.semester)
          if (t.textbook_version) versionsSet.add(t.textbook_version)
        })
        setGrades(Array.from(gradesSet).map(g => ({ value: g, label: g })))
        setSubjects(Array.from(subjectsSet).map(s => ({ value: s, label: s })))
        setSemesters(Array.from(semestersSet).map(s => ({ value: s, label: s })))
        setTextbookVersions(Array.from(versionsSet).map(v => ({ id: v, name: v, sort: 0 })))
      }
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }

  const loadAllTemplates = async () => {
    setTemplateLoading(true)
    generator.setError('')
    try {
      const data = await apiGetTemplates({})
      setAllTemplates(data)

      // 检查是否有保存的筛选配置，有的话应用过滤
      const savedFilter = localStorage.getItem('question-generator-filter')
      if (savedFilter) {
        const parsed: TemplateFilter = JSON.parse(savedFilter)
        if (parsed.grade || parsed.subject || parsed.semester || parsed.textbook_version) {
          setTemplateFilter(parsed)
          setTimeout(() => {
            let result = data
            if (parsed.grade) result = result.filter((t: TemplateItem) => t.grade === parsed.grade)
            if (parsed.subject) result = result.filter((t: TemplateItem) => t.subject === parsed.subject)
            if (parsed.semester) result = result.filter((t: TemplateItem) => t.semester === parsed.semester)
            if (parsed.textbook_version) result = result.filter((t: TemplateItem) => t.textbook_version === parsed.textbook_version)
            setFilteredTemplates(result)
            if (result.length === 0) {
              generator.setError('没有找到符合条件的模板')
            }
          }, 0)
          return
        }
      }

      setFilteredTemplates(data)
    } catch (e) {
      if (e instanceof Error) {
        generator.setError(e.message || '加载模板失败')
      } else {
        generator.setError('加载模板失败')
      }
      setAllTemplates([])
      setFilteredTemplates([])
    } finally {
      setTemplateLoading(false)
    }
  }

  // 应用筛选
  const handleApplyFilter = async () => {
    if (allTemplates.length === 0) {
      await loadAllTemplates()
    }
    const result = applyFilter(allTemplates, grades, subjects, semesters, textbookVersions)
    setFilteredTemplates(result)
    if (result.length === 0) {
      generator.setError('没有找到符合条件的模板')
    } else {
      generator.setError('')
    }
    if (!isMobile) {
      setFilterOpen(false)
    }
  }

  // 处理模板选择
  const handleTemplateSelect = (template: TemplateItem) => {
    setSelectedTemplate(template)
  }

  // 生成题目（提示词模式）
  const handleGenerateFromPrompt = async () => {
    const result = validatePrompt(prompt.trim())
    if (!result.valid) {
      generator.setError(result.error || '请输入题目要求')
      return
    }
    await generator.generateFromPrompt(prompt.trim(), isMobile)
  }

  // 生成题目（模板模式）
  const handleGenerateFromTemplate = async () => {
    if (!selectedTemplate) {
      generator.setError('请先选择一个模板')
      return
    }
    await generator.generateFromTemplate(selectedTemplate, templateQuantity, isMobile)
  }

  // 下载 PDF
  const handleDownload = async () => {
    if (!generator.questions.length || !generator.meta) return
    setDownloadingPDF(true)
    try {
      await handleDownloadPDF(generator.questions, generator.meta.title, null)
    } finally {
      setDownloadingPDF(false)
    }
  }

  // 重置筛选
  const handleResetFilter = () => {
    resetFilter()
    setFilteredTemplates(allTemplates)
    setShowFilterModal(false)
  }

  return (
    <div className="app">
      {/* 进度条 Modal */}
      <ProgressModal isOpen={generator.showProgress} stage={generator.progressStage} />

      {/* 预览模态框（仅移动端） */}
      {isMobile && (
        <PreviewModal
          isOpen={showPreviewModal}
          onClose={() => setShowPreviewModal(false)}
          questions={generator.questions}
          meta={generator.meta}
          downloadingPDF={downloadingPDF}
          onDownload={handleDownload}
        />
      )}

      {/* 筛选模态框（仅移动端） */}
      {isMobile && (
        <FilterModal
          isOpen={showFilterModal}
          onClose={() => setShowFilterModal(false)}
          filterOptions={filterOptions}
          filter={templateFilter}
          onFilterChange={setTemplateFilter}
          onApply={handleApplyFilter}
          loading={templateLoading}
        />
      )}

      {/* 顶部导航栏 */}
      <Header
        email={email}
        onLogout={onLogout}
        fetchUser={fetchUser}
        historyOpen={historyOpen}
        onHistoryToggle={() => setHistoryOpen(!historyOpen)}
      />

      {/* 主内容区 */}
      <main className="main">
        {/* 左侧控制面板 */}
        <aside className="sidebar">
          <div className="sidebar-content">
            {/* 模式切换 Tab */}
            <section className="panel-section">
              <ModeTabs mode={mode} onModeChange={(m) => { setMode(m); generator.setError('') }} />
            </section>

            {/* 模板出题模式 */}
            {mode === 'template' && (
              <>
                {/* 模板列表 */}
                <section className="panel-section">
                  <div className="section-header">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 5H7C6.46957 5 5.96086 5.21071 5.58579 5.58579C5.21071 5.96086 5 6.46957 5 7V19C5 19.5304 5.21071 20.0391 5.58579 20.4142C5.96086 20.7893 6.46957 21 7 21H17C17.5304 21 18.0391 20.7893 18.4142 20.4142C18.7893 20.0391 19 19.5304 19 19V7C19 6.46957 18.7893 5.96086 18.4142 5.58579C18.0391 5.21071 17.5304 5 17 5H15C14.4696 5 14 5.44772 14 6V8C14 8.55228 14.4696 9 15 9H17V19H7V7H9C9.53043 7 10 6.55228 10 6V4C10 3.44772 9.53043 3 9 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <label>模板列表</label>
                    <button
                      type="button"
                      className="btn-filter-icon"
                      onClick={() => isMobile ? setShowFilterModal(true) : setFilterOpen(!filterOpen)}
                      title="筛选模板"
                    >
                      {filterSummary && <span className="filter-summary">{filterSummary}</span>}
                      <svg className={`filter-toggle-icon ${showFilterModal || filterOpen ? 'open' : ''}`} viewBox="0 0 24 24" fill="none">
                        <path d="M6 15L12 9L18 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </button>
                  </div>
                  {/* PC 端筛选表单 */}
                  {!isMobile && filterOpen && (
                    <TemplateFilterComponent
                      filterOptions={filterOptions}
                      filter={templateFilter}
                      onFilterChange={setTemplateFilter}
                      onApply={handleApplyFilter}
                      loading={templateLoading}
                    />
                  )}
                  {/* 模板列表 */}
                  <TemplateList
                    templates={filteredTemplates}
                    loading={templateLoading}
                    selectedTemplate={selectedTemplate}
                    onSelect={handleTemplateSelect}
                  />
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
                  <Shortcuts onSelect={setPrompt} />
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
                  <PromptInput
                    value={prompt}
                    onChange={setPrompt}
                    error={generator.error}
                  />
                </section>
              </>
            )}

            {/* 动作按钮区域（PC 端） */}
            {!isMobile && (
              <ActionButtons
                mode={mode}
                loading={generator.loading}
                selectedTemplate={selectedTemplate}
                questions={generator.questions}
                meta={generator.meta}
                downloadingPDF={downloadingPDF}
                onDownload={handleDownload}
                onGenerate={mode === 'prompt' ? handleGenerateFromPrompt : handleGenerateFromTemplate}
                quantity={templateQuantity}
                onQuantityChange={setTemplateQuantity}
              />
            )}
          </div>
        </aside>

        {/* 移动端底部固定按钮 */}
        {isMobile && (
          <MobileFooter
            mode={mode}
            loading={generator.loading}
            selectedTemplate={selectedTemplate}
            quantity={templateQuantity}
            onQuantityChange={setTemplateQuantity}
            onGenerate={mode === 'prompt' ? handleGenerateFromPrompt : handleGenerateFromTemplate}
          />
        )}

        {/* 右侧预览区 */}
        <PreviewPanel
          questions={generator.questions}
          meta={generator.meta}
          isEmpty={generator.questions.length === 0}
        />
      </main>
    </div>
  )
}
