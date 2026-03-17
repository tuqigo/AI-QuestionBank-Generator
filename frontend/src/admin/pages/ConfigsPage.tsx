/**
 * 配置管理页面
 * 管理学科、年级、学期、教材版本、知识点等配置数据
 */
import React, { useState, useEffect } from 'react'
import {
  getSubjects,
  getGrades,
  getSemesters,
  getTextbookVersions,
  getKnowledgePoints,
  createSubject,
  updateSubject,
  deleteSubject,
  createGrade,
  updateGrade,
  deleteGrade,
  createSemester,
  updateSemester,
  deleteSemester,
  createTextbookVersion,
  updateTextbookVersion,
  deleteTextbookVersion,
  createKnowledgePoint,
  updateKnowledgePoint,
  deleteKnowledgePoint,
  type Subject,
  type Grade,
  type Semester,
  type TextbookVersion,
  type KnowledgePoint,
} from '@/api/config'
import './ConfigsPage.css'

type ConfigTab = 'subject' | 'grade' | 'semester' | 'textbook' | 'knowledge'

export default function ConfigsPage() {
  const [activeTab, setActiveTab] = useState<ConfigTab>('subject')
  const [loading, setLoading] = useState(false)

  // 数据状态
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [grades, setGrades] = useState<Grade[]>([])
  const [semesters, setSemesters] = useState<Semester[]>([])
  const [textbookVersions, setTextbookVersions] = useState<TextbookVersion[]>([])
  const [knowledgePoints, setKnowledgePoints] = useState<KnowledgePoint[]>([])

  // 弹窗状态
  const [modalVisible, setModalVisible] = useState(false)
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create')
  const [currentItem, setCurrentItem] = useState<Subject | Grade | Semester | TextbookVersion | KnowledgePoint | null>(null)

  // 表单数据
  const [formData, setFormData] = useState<Record<string, any>>({})

  useEffect(() => {
    loadConfigData()
  }, [activeTab])

  const loadConfigData = async () => {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'subject':
          setSubjects(await getSubjects(false))
          break
        case 'grade':
          setGrades(await getGrades(false))
          break
        case 'semester':
          setSemesters(await getSemesters(false))
          break
        case 'textbook':
          setTextbookVersions(await getTextbookVersions(false))
          break
        case 'knowledge':
          setKnowledgePoints(await getKnowledgePoints())
          break
      }
    } catch (error) {
      console.error('加载配置数据失败:', error)
      alert('加载配置数据失败')
    } finally {
      setLoading(false)
    }
  }

  const openCreateModal = () => {
    setModalMode('create')
    setCurrentItem(null)
    setFormData(getDefaultFormData())
    setModalVisible(true)
  }

  const openEditModal = (item: any) => {
    setModalMode('edit')
    setCurrentItem(item)
    setFormData({ ...item })
    setModalVisible(true)
  }

  const handleCloseModal = () => {
    setModalVisible(false)
    setCurrentItem(null)
  }

  const getDefaultFormData = () => {
    switch (activeTab) {
      case 'subject':
        return { code: '', name_zh: '', sort_order: 0 }
      case 'grade':
        return { code: '', name_zh: '', sort_order: 0 }
      case 'semester':
        return { code: '', name_zh: '', sort_order: 0 }
      case 'textbook':
        return { version_code: '', name_zh: '', sort_order: 0 }
      case 'knowledge':
        return {
          subject_code: 'math',
          grade_code: 'grade1',
          semester_code: 'upper',
          textbook_version_code: 'rjb',
          name: '',
          sort_order: 0,
        }
    }
  }

  const handleSave = async () => {
    try {
      if (activeTab === 'subject') {
        if (modalMode === 'create') {
          await createSubject({
            code: formData.code,
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
          })
        } else {
          await updateSubject((currentItem as Subject).id, {
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
            is_active: formData.is_active,
          })
        }
      } else if (activeTab === 'grade') {
        if (modalMode === 'create') {
          await createGrade({
            code: formData.code,
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
          })
        } else {
          await updateGrade((currentItem as Grade).id, {
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
            is_active: formData.is_active,
          })
        }
      } else if (activeTab === 'semester') {
        if (modalMode === 'create') {
          await createSemester({
            code: formData.code,
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
          })
        } else {
          await updateSemester((currentItem as Semester).id, {
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
            is_active: formData.is_active,
          })
        }
      } else if (activeTab === 'textbook') {
        if (modalMode === 'create') {
          await createTextbookVersion({
            version_code: formData.version_code,
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
          })
        } else {
          await updateTextbookVersion((currentItem as TextbookVersion).id, {
            name_zh: formData.name_zh,
            sort_order: formData.sort_order || 0,
            is_active: formData.is_active,
          })
        }
      } else if (activeTab === 'knowledge') {
        if (modalMode === 'create') {
          await createKnowledgePoint({
            name: formData.name,
            subject_code: formData.subject_code,
            grade_code: formData.grade_code,
            semester_code: formData.semester_code,
            textbook_version_code: formData.textbook_version_code,
            sort_order: formData.sort_order || 0,
          })
        } else {
          await updateKnowledgePoint((currentItem as KnowledgePoint).id, {
            name: formData.name,
            sort_order: formData.sort_order || 0,
            is_active: formData.is_active,
          })
        }
      }
      alert('保存成功')
      handleCloseModal()
      loadConfigData()
    } catch (error) {
      console.error('保存失败:', error)
      alert(`保存失败：${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除吗？此操作不可恢复！')) return

    try {
      switch (activeTab) {
        case 'subject':
          await deleteSubject(id)
          break
        case 'grade':
          await deleteGrade(id)
          break
        case 'semester':
          await deleteSemester(id)
          break
        case 'textbook':
          await deleteTextbookVersion(id)
          break
        case 'knowledge':
          await deleteKnowledgePoint(id)
          break
      }
      alert('删除成功')
      loadConfigData()
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    }
  }

  const handleToggleActive = async (item: any) => {
    try {
      const newStatus = item.is_active === 1 ? 0 : 1
      switch (activeTab) {
        case 'subject':
          await updateSubject(item.id, { is_active: newStatus })
          break
        case 'grade':
          await updateGrade(item.id, { is_active: newStatus })
          break
        case 'semester':
          await updateSemester(item.id, { is_active: newStatus })
          break
        case 'textbook':
          await updateTextbookVersion(item.id, { is_active: newStatus })
          break
        case 'knowledge':
          await updateKnowledgePoint(item.id, { is_active: newStatus })
          break
      }
      loadConfigData()
    } catch (error) {
      console.error('切换状态失败:', error)
      alert('切换状态失败')
    }
  }

  const renderTable = () => {
    switch (activeTab) {
      case 'subject':
        return (
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>代码</th>
                <th>名称</th>
                <th>排序</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((item) => (
                <tr key={item.id}>
                  <td>#{item.id}</td>
                  <td>{item.code}</td>
                  <td>{item.name_zh}</td>
                  <td>{item.sort_order}</td>
                  <td>
                    <span className={`admin-badge ${item.is_active ? 'admin-badge-success' : 'admin-badge-error'}`}>
                      {item.is_active ? '启用' : '禁用'}
                    </span>
                  </td>
                  <td className="action-buttons">
                    <button
                      className="admin-btn admin-btn-sm admin-btn-secondary"
                      onClick={() => openEditModal(item)}
                    >
                      编辑
                    </button>
                    <button
                      className="admin-btn admin-btn-sm"
                      onClick={() => handleToggleActive(item)}
                    >
                      {item.is_active ? '禁用' : '启用'}
                    </button>
                    <button
                      className="admin-btn admin-btn-sm admin-btn-danger"
                      onClick={() => handleDelete(item.id)}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      case 'grade':
        return (
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>代码</th>
                <th>名称</th>
                <th>排序</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {grades.map((item) => (
                <tr key={item.id}>
                  <td>#{item.id}</td>
                  <td>{item.code}</td>
                  <td>{item.name_zh}</td>
                  <td>{item.sort_order}</td>
                  <td>
                    <span className={`admin-badge ${item.is_active ? 'admin-badge-success' : 'admin-badge-error'}`}>
                      {item.is_active ? '启用' : '禁用'}
                    </span>
                  </td>
                  <td className="action-buttons">
                    <button
                      className="admin-btn admin-btn-sm admin-btn-secondary"
                      onClick={() => openEditModal(item)}
                    >
                      编辑
                    </button>
                    <button
                      className="admin-btn admin-btn-sm"
                      onClick={() => handleToggleActive(item)}
                    >
                      {item.is_active ? '禁用' : '启用'}
                    </button>
                    <button
                      className="admin-btn admin-btn-sm admin-btn-danger"
                      onClick={() => handleDelete(item.id)}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      case 'semester':
        return (
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>代码</th>
                <th>名称</th>
                <th>排序</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {semesters.map((item) => (
                <tr key={item.id}>
                  <td>#{item.id}</td>
                  <td>{item.code}</td>
                  <td>{item.name_zh}</td>
                  <td>{item.sort_order}</td>
                  <td>
                    <span className={`admin-badge ${item.is_active ? 'admin-badge-success' : 'admin-badge-error'}`}>
                      {item.is_active ? '启用' : '禁用'}
                    </span>
                  </td>
                  <td className="action-buttons">
                    <button
                      className="admin-btn admin-btn-sm admin-btn-secondary"
                      onClick={() => openEditModal(item)}
                    >
                      编辑
                    </button>
                    <button
                      className="admin-btn admin-btn-sm"
                      onClick={() => handleToggleActive(item)}
                    >
                      {item.is_active ? '禁用' : '启用'}
                    </button>
                    <button
                      className="admin-btn admin-btn-sm admin-btn-danger"
                      onClick={() => handleDelete(item.id)}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      case 'textbook':
        return (
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>代码</th>
                <th>名称</th>
                <th>排序</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {textbookVersions.map((item) => (
                <tr key={item.id}>
                  <td>#{item.id}</td>
                  <td>{item.version_code}</td>
                  <td>{item.name_zh}</td>
                  <td>{item.sort_order}</td>
                  <td>
                    <span className={`admin-badge ${item.is_active ? 'admin-badge-success' : 'admin-badge-error'}`}>
                      {item.is_active ? '启用' : '禁用'}
                    </span>
                  </td>
                  <td className="action-buttons">
                    <button
                      className="admin-btn admin-btn-sm admin-btn-secondary"
                      onClick={() => openEditModal(item)}
                    >
                      编辑
                    </button>
                    <button
                      className="admin-btn admin-btn-sm"
                      onClick={() => handleToggleActive(item)}
                    >
                      {item.is_active ? '禁用' : '启用'}
                    </button>
                    <button
                      className="admin-btn admin-btn-sm admin-btn-danger"
                      onClick={() => handleDelete(item.id)}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      case 'knowledge':
        return (
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>知识点名称</th>
                <th>学科</th>
                <th>年级</th>
                <th>学期</th>
                <th>教材版本</th>
                <th>排序</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {knowledgePoints.map((point) => (
                <tr key={point.id}>
                  <td>#{point.id}</td>
                  <td>{point.name}</td>
                  <td>{point.subject_code}</td>
                  <td>{point.grade_code}</td>
                  <td>{point.semester_code}</td>
                  <td>{point.textbook_version_code}</td>
                  <td>{point.sort_order}</td>
                  <td>
                    <span className={`admin-badge ${point.is_active ? 'admin-badge-success' : 'admin-badge-error'}`}>
                      {point.is_active ? '启用' : '禁用'}
                    </span>
                  </td>
                  <td className="action-buttons">
                    <button
                      className="admin-btn admin-btn-sm admin-btn-secondary"
                      onClick={() => openEditModal(point)}
                    >
                      编辑
                    </button>
                    <button
                      className="admin-btn admin-btn-sm"
                      onClick={() => handleToggleActive(point)}
                    >
                      {point.is_active ? '禁用' : '启用'}
                    </button>
                    <button
                      className="admin-btn admin-btn-sm admin-btn-danger"
                      onClick={() => handleDelete(point.id)}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      default:
        return null
    }
  }

  const renderModalForm = () => {
    switch (activeTab) {
      case 'subject':
        return (
          <>
            <div className="form-group">
              <label>代码 *</label>
              <input
                type="text"
                value={formData.code || ''}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                placeholder="例如：math"
                disabled={modalMode === 'edit'}
              />
            </div>
            <div className="form-group">
              <label>名称 *</label>
              <input
                type="text"
                value={formData.name_zh || ''}
                onChange={(e) => setFormData({ ...formData, name_zh: e.target.value })}
                placeholder="例如：数学"
              />
            </div>
            <div className="form-group">
              <label>排序</label>
              <input
                type="number"
                value={formData.sort_order || 0}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
              />
            </div>
          </>
        )
      case 'grade':
        return (
          <>
            <div className="form-group">
              <label>代码 *</label>
              <input
                type="text"
                value={formData.code || ''}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                placeholder="例如：grade1"
                disabled={modalMode === 'edit'}
              />
            </div>
            <div className="form-group">
              <label>名称 *</label>
              <input
                type="text"
                value={formData.name_zh || ''}
                onChange={(e) => setFormData({ ...formData, name_zh: e.target.value })}
                placeholder="例如：一年级"
              />
            </div>
            <div className="form-group">
              <label>排序</label>
              <input
                type="number"
                value={formData.sort_order || 0}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
              />
            </div>
          </>
        )
      case 'semester':
        return (
          <>
            <div className="form-group">
              <label>代码 *</label>
              <input
                type="text"
                value={formData.code || ''}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                placeholder="例如：upper"
                disabled={modalMode === 'edit'}
              />
            </div>
            <div className="form-group">
              <label>名称 *</label>
              <input
                type="text"
                value={formData.name_zh || ''}
                onChange={(e) => setFormData({ ...formData, name_zh: e.target.value })}
                placeholder="例如：上学期"
              />
            </div>
            <div className="form-group">
              <label>排序</label>
              <input
                type="number"
                value={formData.sort_order || 0}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
              />
            </div>
          </>
        )
      case 'textbook':
        return (
          <>
            <div className="form-group">
              <label>代码 *</label>
              <input
                type="text"
                value={formData.version_code || ''}
                onChange={(e) => setFormData({ ...formData, version_code: e.target.value })}
                placeholder="例如：rjb"
                disabled={modalMode === 'edit'}
              />
            </div>
            <div className="form-group">
              <label>名称 *</label>
              <input
                type="text"
                value={formData.name_zh || ''}
                onChange={(e) => setFormData({ ...formData, name_zh: e.target.value })}
                placeholder="例如：人教版"
              />
            </div>
            <div className="form-group">
              <label>排序</label>
              <input
                type="number"
                value={formData.sort_order || 0}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
              />
            </div>
          </>
        )
      case 'knowledge':
        return (
          <>
            <div className="form-group">
              <label>学科 *</label>
              <select
                value={formData.subject_code || 'math'}
                onChange={(e) => setFormData({ ...formData, subject_code: e.target.value })}
                disabled={modalMode === 'edit'}
              >
                <option value="math">数学</option>
                <option value="chinese">语文</option>
                <option value="english">英语</option>
              </select>
            </div>
            <div className="form-group">
              <label>年级 *</label>
              <select
                value={formData.grade_code || 'grade1'}
                onChange={(e) => setFormData({ ...formData, grade_code: e.target.value })}
                disabled={modalMode === 'edit'}
              >
                <option value="grade1">一年级</option>
                <option value="grade2">二年级</option>
                <option value="grade3">三年级</option>
                <option value="grade4">四年级</option>
                <option value="grade5">五年级</option>
                <option value="grade6">六年级</option>
                <option value="grade7">七年级</option>
                <option value="grade8">八年级</option>
                <option value="grade9">九年级</option>
              </select>
            </div>
            <div className="form-group">
              <label>学期 *</label>
              <select
                value={formData.semester_code || 'upper'}
                onChange={(e) => setFormData({ ...formData, semester_code: e.target.value })}
                disabled={modalMode === 'edit'}
              >
                <option value="upper">上学期</option>
                <option value="lower">下学期</option>
              </select>
            </div>
            <div className="form-group">
              <label>教材版本 *</label>
              <select
                value={formData.textbook_version_code || 'rjb'}
                onChange={(e) => setFormData({ ...formData, textbook_version_code: e.target.value })}
                disabled={modalMode === 'edit'}
              >
                <option value="rjb">人教版</option>
                <option value="rjb_2024">人教版（2024 新版）</option>
                <option value="bsd">北师大版</option>
                <option value="sj">苏教版</option>
                <option value="xs">西师版</option>
                <option value="hj">沪教版</option>
              </select>
            </div>
            <div className="form-group">
              <label>知识点名称 *</label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：5 以内数的认识"
              />
            </div>
            <div className="form-group">
              <label>排序</label>
              <input
                type="number"
                value={formData.sort_order || 0}
                onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
              />
            </div>
          </>
        )
      default:
        return null
    }
  }

  const getModalTitle = () => {
    if (activeTab === 'knowledge') {
      return modalMode === 'create' ? '添加知识点' : '编辑知识点'
    }
    const titles: Record<ConfigTab, string> = {
      subject: '学科',
      grade: '年级',
      semester: '学期',
      textbook: '教材版本',
      knowledge: '知识点',
    }
    return modalMode === 'create' ? `添加${titles[activeTab]}` : `编辑${titles[activeTab]}`
  }

  return (
    <div className="configs-page">
      <div className="page-header">
        <h1>配置管理</h1>
        <button className="admin-btn admin-btn-primary" onClick={openCreateModal}>
          + 添加{activeTab === 'knowledge' ? '知识点' : activeTab === 'subject' ? '学科' : activeTab === 'grade' ? '年级' : activeTab === 'semester' ? '学期' : '教材版本'}
        </button>
      </div>

      <div className="config-tabs">
        <button
          className={`config-tab ${activeTab === 'subject' ? 'active' : ''}`}
          onClick={() => setActiveTab('subject')}
        >
          学科配置
        </button>
        <button
          className={`config-tab ${activeTab === 'grade' ? 'active' : ''}`}
          onClick={() => setActiveTab('grade')}
        >
          年级配置
        </button>
        <button
          className={`config-tab ${activeTab === 'semester' ? 'active' : ''}`}
          onClick={() => setActiveTab('semester')}
        >
          学期配置
        </button>
        <button
          className={`config-tab ${activeTab === 'textbook' ? 'active' : ''}`}
          onClick={() => setActiveTab('textbook')}
        >
          教材版本
        </button>
        <button
          className={`config-tab ${activeTab === 'knowledge' ? 'active' : ''}`}
          onClick={() => setActiveTab('knowledge')}
        >
          知识点配置
        </button>
      </div>

      <div className="admin-card">
        <div className="admin-card-body">
          {loading ? (
            <div className="admin-loading-state">加载中...</div>
          ) : activeTab === 'knowledge' && knowledgePoints.length === 0 ? (
            <div className="admin-empty">
              <div className="admin-empty-icon">📚</div>
              <p>暂无知识点数据</p>
              <p className="admin-empty-hint">点击"添加知识点"按钮创建新的知识点</p>
            </div>
          ) : (
            renderTable()
          )}
        </div>
      </div>

      {/* 弹窗 */}
      {modalVisible && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{getModalTitle()}</h2>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>
            <div className="form-content">
              {renderModalForm()}
            </div>
            <div className="modal-footer">
              <button className="admin-btn" onClick={handleCloseModal}>取消</button>
              <button className="admin-btn admin-btn-primary" onClick={handleSave}>
                {modalMode === 'create' ? '创建' : '保存'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
