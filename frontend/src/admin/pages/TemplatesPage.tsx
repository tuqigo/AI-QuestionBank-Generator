import React, { useState, useEffect } from 'react'
import {
  getAllTemplates,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  toggleTemplate,
  testTemplate,
  type QuestionTemplate,
  type TemplateCreateInput,
} from '../services/api'
import { getConfigs, type ConfigOption, type QuestionTypeOption } from '@/api/config'
import './TemplatesPage.css'

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<QuestionTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [modalVisible, setModalVisible] = useState(false)
  const [modalMode, setModalMode] = useState<'create' | 'edit' | 'test' | 'view'>('create')
  const [currentTemplate, setCurrentTemplate] = useState<QuestionTemplate | null>(null)
  const [testQuantity, setTestQuantity] = useState(5)
  const [testResult, setTestResult] = useState<any[] | null>(null)
  const [formData, setFormData] = useState<TemplateCreateInput>({
    name: '',
    subject: 'math',
    grade: 'grade1',
    semester: 'upper',
    textbook_version: '人教版',
    question_type: 'CALCULATION',
    template_pattern: '',
    variables_config: '{}',
    example: '',
    sort_order: 0,
    is_active: true,
    generator_module: '',
  })

  // 配置常量状态
  const [subjects, setSubjects] = useState<ConfigOption[]>([])
  const [grades, setGrades] = useState<ConfigOption[]>([])
  const [semesters, setSemesters] = useState<ConfigOption[]>([])
  const [textbookVersions, setTextbookVersions] = useState<string[]>([])
  const [questionTypes, setQuestionTypes] = useState<QuestionTypeOption[]>([])

  useEffect(() => {
    loadConfigs()
    loadTemplates()
  }, [])

  const loadConfigs = async () => {
    try {
      const configs = await getConfigs()
      setSubjects(configs.subjects)
      setGrades(configs.grades)
      setSemesters(configs.semesters)
      setTextbookVersions(configs.textbook_versions)
      setQuestionTypes(configs.question_types)
    } catch (error) {
      console.error('加载配置失败:', error)
      alert('加载配置失败')
    }
  }

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const result = await getAllTemplates()
      setTemplates(result.templates)
    } catch (error) {
      console.error('加载模板列表失败:', error)
      alert('加载模板列表失败')
    } finally {
      setLoading(false)
    }
  }

  const openCreateModal = () => {
    setModalMode('create')
    setFormData({
      name: '',
      subject: 'math',
      grade: 'grade1',
      semester: 'upper',
      textbook_version: '人教版',
      question_type: 'CALCULATION',
      template_pattern: '',
      variables_config: '{}',
      example: '',
      sort_order: 0,
      is_active: true,
      generator_module: '',
    })
    setModalVisible(true)
  }

  const openEditModal = (template: QuestionTemplate) => {
    setModalMode('edit')
    setCurrentTemplate(template)
    setFormData({
      name: template.name,
      subject: template.subject,
      grade: template.grade,
      semester: template.semester,
      textbook_version: template.textbook_version,
      question_type: template.question_type,
      template_pattern: template.template_pattern,
      variables_config: typeof template.variables_config === 'string'
        ? template.variables_config
        : JSON.stringify(template.variables_config, null, 2),
      example: template.example || '',
      sort_order: template.sort_order,
      is_active: template.is_active,
      generator_module: template.generator_module || '',
    })
    setModalVisible(true)
  }

  const openTestModal = (template: QuestionTemplate) => {
    setModalMode('test')
    setCurrentTemplate(template)
    setTestQuantity(5)
    setTestResult(null)
    setModalVisible(true)
  }

  const openViewModal = (template: QuestionTemplate) => {
    setModalMode('view')
    setCurrentTemplate(template)
    setModalVisible(true)
  }

  const handleCloseModal = () => {
    setModalVisible(false)
    setCurrentTemplate(null)
    setTestResult(null)
  }

  const handleSave = async () => {
    // 验证必填字段
    if (!formData.name?.trim()) {
      alert('请输入模板名称')
      return
    }
    if (!formData.template_pattern?.trim()) {
      alert('请输入模板模式')
      return
    }

    try {
      let variablesConfig: object
      try {
        variablesConfig = JSON.parse(formData.variables_config || '{}')
      } catch {
        alert('变量配置必须是有效的 JSON 格式')
        return
      }

      if (modalMode === 'create') {
        await createTemplate({
          ...formData,
          variables_config: JSON.stringify(variablesConfig),
        })
        alert('创建成功')
      } else if (modalMode === 'edit' && currentTemplate) {
        await updateTemplate(currentTemplate.id, {
          name: formData.name,
          subject: formData.subject,
          grade: formData.grade,
          semester: formData.semester,
          textbook_version: formData.textbook_version,
          template_pattern: formData.template_pattern,
          variables_config: JSON.stringify(variablesConfig),
          example: formData.example,
          sort_order: formData.sort_order,
          is_active: formData.is_active,
          question_type: formData.question_type,
        })
        alert('更新成功')
      }
      handleCloseModal()
      loadTemplates()
    } catch (error) {
      console.error('保存失败:', error)
      alert(`保存失败：${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  const handleTest = async () => {
    if (!currentTemplate) return

    try {
      const result = await testTemplate(currentTemplate.id, testQuantity)
      setTestResult(result.questions)
    } catch (error) {
      console.error('测试失败:', error)
      alert(`测试失败：${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  const handleToggle = async (templateId: number, currentStatus: boolean) => {
    try {
      await toggleTemplate(templateId, !currentStatus)
      loadTemplates()
    } catch (error) {
      console.error('切换状态失败:', error)
      alert('切换状态失败')
    }
  }

  const handleDelete = async (templateId: number) => {
    if (!confirm('确定要删除这个模板吗？此操作不可恢复！')) return

    try {
      await deleteTemplate(templateId)
      loadTemplates()
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    }
  }

  const getSubjectLabel = (subject: string) => {
    return subjects.find(s => s.value === subject)?.label || subject
  }

  const getGradeLabel = (grade: string) => {
    return grades.find(g => g.value === grade)?.label || grade
  }

  const getSemesterLabel = (semester: string) => {
    return semesters.find(s => s.value === semester)?.label || semester
  }

  const getQuestionTypeLabel = (questionType: string) => {
    return questionTypes.find(t => t.value === questionType)?.label || questionType
  }

  const renderModalContent = () => {
    if (modalMode === 'create' || modalMode === 'edit') {
      return (
        <div className="form-content">
          <div className="form-row">
            <div className="form-group">
              <label>模板名称 *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：一年级 10 以内的加减法"
              />
            </div>
            <div className="form-group">
              <label>生成器模块</label>
              <input
                type="text"
                value={formData.generator_module}
                onChange={(e) => setFormData({ ...formData, generator_module: e.target.value })}
                placeholder="例如：basic_arithmetic"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>学科 *</label>
              <select
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              >
                {subjects.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>年级 *</label>
              <select
                value={formData.grade}
                onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
              >
                {grades.map(g => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>学期 *</label>
              <select
                value={formData.semester}
                onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
              >
                {semesters.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>教材版本 *</label>
              <select
                value={formData.textbook_version}
                onChange={(e) => setFormData({ ...formData, textbook_version: e.target.value })}
              >
                {textbookVersions.map(v => (
                  <option key={v} value={v}>{v}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>题型 *</label>
              <select
                value={formData.question_type}
                onChange={(e) => setFormData({ ...formData, question_type: e.target.value })}
              >
                {questionTypes.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>排序</label>
              <input
                type="number"
                value={formData.sort_order}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
              />
            </div>
          </div>

          <div className="form-group full-width">
            <label>模板模式 (template_pattern) *</label>
            <textarea
              value={formData.template_pattern}
              onChange={(e) => setFormData({ ...formData, template_pattern: e.target.value })}
              placeholder="描述模板的模式，例如：简单的加减法运算"
              rows={3}
            />
          </div>

          <div className="form-group full-width">
            <label>变量配置 (variables_config) - JSON 格式</label>
            <textarea
              value={formData.variables_config}
              onChange={(e) => setFormData({ ...formData, variables_config: e.target.value })}
              placeholder='例如：{"min": 1, "max": 10}'
              rows={5}
            />
          </div>

          <div className="form-group full-width">
            <label>示例</label>
            <textarea
              value={formData.example}
              onChange={(e) => setFormData({ ...formData, example: e.target.value })}
              placeholder="示例题目"
              rows={2}
            />
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              启用
            </label>
          </div>
        </div>
      )
    }

    if (modalMode === 'test') {
      return (
        <div className="test-content">
          <div className="test-info">
            <h4>测试模板：{currentTemplate?.name}</h4>
            <div className="test-settings">
              <label>
                生成数量：
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={testQuantity}
                  onChange={(e) => setTestQuantity(parseInt(e.target.value) || 5)}
                />
              </label>
              <button className="admin-btn admin-btn-primary" onClick={handleTest}>
                开始测试
              </button>
            </div>
          </div>

          {testResult && (
            <div className="test-result">
              <h4>生成结果 ({testResult.length} 题)</h4>
              <div className="json-viewer">
                <pre>{JSON.stringify(testResult, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      )
    }

    if (modalMode === 'view') {
      return (
        <div className="view-content">
          <div className="view-row">
            <strong>ID:</strong> {currentTemplate?.id}
          </div>
          <div className="view-row">
            <strong>名称:</strong> {currentTemplate?.name}
          </div>
          <div className="view-row">
            <strong>学科:</strong> {getSubjectLabel(currentTemplate?.subject || '')}
          </div>
          <div className="view-row">
            <strong>年级:</strong> {getGradeLabel(currentTemplate?.grade || '')}
          </div>
          <div className="view-row">
            <strong>学期:</strong> {getSemesterLabel(currentTemplate?.semester || '')}
          </div>
          <div className="view-row">
            <strong>教材版本:</strong> {currentTemplate?.textbook_version}
          </div>
          <div className="view-row">
            <strong>题型:</strong> {currentTemplate?.question_type && getQuestionTypeLabel(currentTemplate.question_type)}
          </div>
          <div className="view-row">
            <strong>模板模式:</strong>
            <pre className="json-viewer">{currentTemplate?.template_pattern}</pre>
          </div>
          <div className="view-row">
            <strong>变量配置:</strong>
            <pre className="json-viewer">
              {typeof currentTemplate?.variables_config === 'string'
                ? currentTemplate.variables_config
                : JSON.stringify(currentTemplate?.variables_config, null, 2)}
            </pre>
          </div>
          <div className="view-row">
            <strong>生成器模块:</strong> {currentTemplate?.generator_module || '-'}
          </div>
          <div className="view-row">
            <strong>示例:</strong> {currentTemplate?.example || '-'}
          </div>
          <div className="view-row">
            <strong>状态:</strong> {currentTemplate?.is_active ? '启用' : '禁用'}
          </div>
          <div className="view-row">
            <strong>排序:</strong> {currentTemplate?.sort_order}
          </div>
          <div className="view-row">
            <strong>创建时间:</strong> {currentTemplate?.created_at}
          </div>
          <div className="view-row">
            <strong>更新时间:</strong> {currentTemplate?.updated_at}
          </div>
        </div>
      )
    }

    return null
  }

  return (
    <div className="templates-page">
      <div className="page-header">
        <h1>模板管理</h1>
        <div className="page-actions">
          <div className="page-stats">
            共 <span>{templates.length}</span> 个模板
          </div>
          <button className="admin-btn admin-btn-primary" onClick={openCreateModal}>
            + 添加模板
          </button>
        </div>
      </div>

      <div className="admin-card">
        <div className="admin-card-body">
          {loading ? (
            <div className="admin-loading-state">加载中...</div>
          ) : templates.length === 0 ? (
            <div className="admin-empty">
              <div className="admin-empty-icon">📝</div>
              <p>暂无模板数据</p>
            </div>
          ) : (
            <>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>模板名称</th>
                    <th>学科</th>
                    <th>年级</th>
                    <th>学期</th>
                    <th>教材版本</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {templates.map((template) => (
                    <tr key={template.id}>
                      <td>#{template.id}</td>
                      <td className="template-name">{template.name}</td>
                      <td>{getSubjectLabel(template.subject)}</td>
                      <td>{getGradeLabel(template.grade)}</td>
                      <td>{getSemesterLabel(template.semester)}</td>
                      <td>{template.textbook_version}</td>
                      <td>
                        <span className={`admin-badge ${template.is_active ? 'admin-badge-success' : 'admin-badge-error'}`}>
                          {template.is_active ? '启用' : '禁用'}
                        </span>
                      </td>
                      <td className="action-buttons">
                        <button
                          className="admin-btn admin-btn-sm admin-btn-primary"
                          onClick={() => openTestModal(template)}
                        >
                          测试
                        </button>
                        <button
                          className="admin-btn admin-btn-sm admin-btn-secondary"
                          onClick={() => openEditModal(template)}
                        >
                          编辑
                        </button>
                        <button
                          className="admin-btn admin-btn-sm"
                          onClick={() => openViewModal(template)}
                        >
                          查看
                        </button>
                        <button
                          className={`admin-btn admin-btn-sm ${template.is_active ? 'admin-btn-secondary' : 'admin-btn-primary'}`}
                          onClick={() => handleToggle(template.id, template.is_active)}
                        >
                          {template.is_active ? '禁用' : '启用'}
                        </button>
                        <button
                          className="admin-btn admin-btn-sm admin-btn-danger"
                          onClick={() => handleDelete(template.id)}
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      </div>

      {/* 弹窗 */}
      {modalVisible && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                {modalMode === 'create' && '添加模板'}
                {modalMode === 'edit' && '编辑模板'}
                {modalMode === 'test' && '测试模板'}
                {modalMode === 'view' && '模板详情'}
              </h2>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>
            {renderModalContent()}
            <div className="modal-footer">
              {(modalMode === 'create' || modalMode === 'edit') && (
                <>
                  <button className="admin-btn" onClick={handleCloseModal}>取消</button>
                  <button className="admin-btn admin-btn-primary" onClick={handleSave}>
                    {modalMode === 'create' ? '创建' : '保存'}
                  </button>
                </>
              )}
              {modalMode === 'test' && (
                <button className="admin-btn" onClick={handleCloseModal}>关闭</button>
              )}
              {modalMode === 'view' && (
                <button className="admin-btn" onClick={handleCloseModal}>关闭</button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
