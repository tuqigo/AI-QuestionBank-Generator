/**
 * 配置 API 调用
 * 获取全局配置常量：学科、年级、学期、教材版本、题型等
 */

const API_BASE = '/api/configs'

export interface ConfigOption {
  value: string
  label: string
}

export interface TextbookVersionOption {
  id: string      // 版本 ID（如 "rjb", "bsd"）
  name: string    // 显示名称（如 "人教版"）
  sort: number    // 排序序号
}

export interface QuestionTypeOption extends ConfigOption {
  subjects: string[]  // 适用学科列表
}

export interface ConfigData {
  subjects: ConfigOption[]
  grades: ConfigOption[]
  semesters: ConfigOption[]
  textbook_versions: TextbookVersionOption[]
  question_types: QuestionTypeOption[]
  generator_modules: ConfigOption[]
}

/**
 * 获取所有配置常量
 */
export async function getConfigs(): Promise<ConfigData> {
  const response = await fetch(`${API_BASE}/configs`)
  if (!response.ok) {
    throw new Error('获取配置失败')
  }
  return response.json()
}

// ==================== 配置管理 CRUD 接口 ====================

export interface Subject {
  id: number
  code: string
  name_zh: string
  sort_order: number
  is_active: number
  created_at: string
  updated_at: string
}

export interface Grade {
  id: number
  code: string
  name_zh: string
  sort_order: number
  is_active: number
  created_at: string
  updated_at: string
}

export interface Semester {
  id: number
  code: string
  name_zh: string
  sort_order: number
  is_active: number
  created_at: string
  updated_at: string
}

export interface TextbookVersion {
  id: number
  version_code: string
  name_zh: string
  sort_order: number
  is_active: number
  created_at: string
  updated_at: string
}

export interface KnowledgePoint {
  id: number
  name: string
  subject_code: string
  grade_code: string
  semester_code: string
  textbook_version_code: string
  sort_order: number
  is_active: number
  created_at: string
  updated_at: string
}

// 创建/更新请求体
export interface SubjectCreate {
  code: string
  name_zh: string
  sort_order: number
}

export interface SubjectUpdate {
  name_zh?: string
  sort_order?: number
  is_active?: number
}

export interface GradeCreate {
  code: string
  name_zh: string
  sort_order: number
}

export interface GradeUpdate {
  name_zh?: string
  sort_order?: number
  is_active?: number
}

export interface SemesterCreate {
  code: string
  name_zh: string
  sort_order: number
}

export interface SemesterUpdate {
  name_zh?: string
  sort_order?: number
  is_active?: number
}

export interface TextbookVersionCreate {
  version_code: string
  name_zh: string
  sort_order: number
}

export interface TextbookVersionUpdate {
  name_zh?: string
  sort_order?: number
  is_active?: number
}

export interface KnowledgePointCreate {
  name: string
  subject_code: string
  grade_code: string
  semester_code: string
  textbook_version_code: string
  sort_order: number
}

export interface KnowledgePointUpdate {
  name?: string
  sort_order?: number
  is_active?: number
}

// API 函数

/**
 * 获取学科列表
 */
export async function getSubjects(active_only: boolean = true): Promise<Subject[]> {
  const response = await fetch(`${API_BASE}/subjects?active_only=${active_only}`)
  if (!response.ok) {
    throw new Error('获取学科列表失败')
  }
  return response.json()
}

/**
 * 创建学科
 */
export async function createSubject(data: SubjectCreate): Promise<Subject> {
  const response = await fetch(`${API_BASE}/admin/subjects/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建失败' }))
    throw new Error(error.detail || '创建失败')
  }
  return response.json()
}

/**
 * 更新学科
 */
export async function updateSubject(id: number, data: SubjectUpdate): Promise<Subject> {
  const response = await fetch(`${API_BASE}/admin/subjects/${id}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新失败' }))
    throw new Error(error.detail || '更新失败')
  }
  return response.json()
}

/**
 * 删除学科
 */
export async function deleteSubject(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/admin/subjects/${id}/delete`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '删除失败' }))
    throw new Error(error.detail || '删除失败')
  }
}

/**
 * 获取年级列表
 */
export async function getGrades(active_only: boolean = true): Promise<Grade[]> {
  const response = await fetch(`${API_BASE}/grades?active_only=${active_only}`)
  if (!response.ok) {
    throw new Error('获取年级列表失败')
  }
  return response.json()
}

/**
 * 创建年级
 */
export async function createGrade(data: GradeCreate): Promise<Grade> {
  const response = await fetch(`${API_BASE}/admin/grades/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建失败' }))
    throw new Error(error.detail || '创建失败')
  }
  return response.json()
}

/**
 * 更新年级
 */
export async function updateGrade(id: number, data: GradeUpdate): Promise<Grade> {
  const response = await fetch(`${API_BASE}/admin/grades/${id}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新失败' }))
    throw new Error(error.detail || '更新失败')
  }
  return response.json()
}

/**
 * 删除年级
 */
export async function deleteGrade(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/admin/grades/${id}/delete`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '删除失败' }))
    throw new Error(error.detail || '删除失败')
  }
}

/**
 * 获取学期列表
 */
export async function getSemesters(active_only: boolean = true): Promise<Semester[]> {
  const response = await fetch(`${API_BASE}/semesters?active_only=${active_only}`)
  if (!response.ok) {
    throw new Error('获取学期列表失败')
  }
  return response.json()
}

/**
 * 创建学期
 */
export async function createSemester(data: SemesterCreate): Promise<Semester> {
  const response = await fetch(`${API_BASE}/admin/semesters/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建失败' }))
    throw new Error(error.detail || '创建失败')
  }
  return response.json()
}

/**
 * 更新学期
 */
export async function updateSemester(id: number, data: SemesterUpdate): Promise<Semester> {
  const response = await fetch(`${API_BASE}/admin/semesters/${id}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新失败' }))
    throw new Error(error.detail || '更新失败')
  }
  return response.json()
}

/**
 * 删除学期
 */
export async function deleteSemester(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/admin/semesters/${id}/delete`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '删除失败' }))
    throw new Error(error.detail || '删除失败')
  }
}

/**
 * 获取教材版本列表
 */
export async function getTextbookVersions(active_only: boolean = true): Promise<TextbookVersion[]> {
  const response = await fetch(`${API_BASE}/textbook-versions?active_only=${active_only}`)
  if (!response.ok) {
    throw new Error('获取教材版本列表失败')
  }
  return response.json()
}

/**
 * 创建教材版本
 */
export async function createTextbookVersion(data: TextbookVersionCreate): Promise<TextbookVersion> {
  const response = await fetch(`${API_BASE}/admin/textbook-versions/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建失败' }))
    throw new Error(error.detail || '创建失败')
  }
  return response.json()
}

/**
 * 更新教材版本
 */
export async function updateTextbookVersion(id: number, data: TextbookVersionUpdate): Promise<TextbookVersion> {
  const response = await fetch(`${API_BASE}/admin/textbook-versions/${id}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新失败' }))
    throw new Error(error.detail || '更新失败')
  }
  return response.json()
}

/**
 * 删除教材版本
 */
export async function deleteTextbookVersion(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/admin/textbook-versions/${id}/delete`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '删除失败' }))
    throw new Error(error.detail || '删除失败')
  }
}

/**
 * 根据条件获取知识点列表（扁平结构）
 */
export async function getKnowledgePoints(params?: {
  subject_code?: string
  grade_code?: string
  semester_code?: string
  textbook_version_code?: string
  active_only?: boolean
}): Promise<KnowledgePoint[]> {
  const searchParams = new URLSearchParams()
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.set(key, String(value))
      }
    })
  }
  const response = await fetch(`${API_BASE}/knowledge-points?${searchParams}`)
  if (!response.ok) {
    throw new Error('获取知识点列表失败')
  }
  return response.json()
}

/**
 * 创建知识点
 */
export async function createKnowledgePoint(data: KnowledgePointCreate): Promise<KnowledgePoint> {
  const response = await fetch(`${API_BASE}/admin/knowledge-points/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建失败' }))
    throw new Error(error.detail || '创建失败')
  }
  return response.json()
}

/**
 * 更新知识点
 */
export async function updateKnowledgePoint(id: number, data: KnowledgePointUpdate): Promise<KnowledgePoint> {
  const response = await fetch(`${API_BASE}/admin/knowledge-points/${id}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新失败' }))
    throw new Error(error.detail || '更新失败')
  }
  return response.json()
}

/**
 * 删除知识点
 */
export async function deleteKnowledgePoint(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/admin/knowledge-points/${id}/delete`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '删除失败' }))
    throw new Error(error.detail || '删除失败')
  }
}

// ==================== 题型管理 CRUD 接口 ====================

export interface QuestionType {
  id: number
  en_name: string
  zh_name: string
  subjects: string[]
  sort_order: number
  is_active: number
  created_at: string
  updated_at: string
}

export interface QuestionTypeCreate {
  en_name: string
  zh_name: string
  subjects?: string[]
  sort_order?: number
}

export interface QuestionTypeUpdate {
  zh_name?: string
  subjects?: string[]
  sort_order?: number
  is_active?: number
}

/**
 * 获取题型列表
 */
export async function getQuestionTypes(active_only: boolean = true, subject?: string): Promise<QuestionType[]> {
  const searchParams = new URLSearchParams()
  searchParams.set('active_only', String(active_only))
  if (subject) searchParams.set('subject', subject)
  const response = await fetch(`${API_BASE}/question-types?${searchParams}`)
  if (!response.ok) {
    throw new Error('获取题型列表失败')
  }
  return response.json()
}

/**
 * 创建题型
 */
export async function createQuestionType(data: QuestionTypeCreate): Promise<QuestionType> {
  const response = await fetch(`${API_BASE}/admin/question-types/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建失败' }))
    throw new Error(error.detail || '创建失败')
  }
  return response.json()
}

/**
 * 更新题型
 */
export async function updateQuestionType(id: number, data: QuestionTypeUpdate): Promise<QuestionType> {
  const response = await fetch(`${API_BASE}/admin/question-types/${id}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新失败' }))
    throw new Error(error.detail || '更新失败')
  }
  return response.json()
}

/**
 * 删除题型
 */
export async function deleteQuestionType(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/admin/question-types/${id}/delete`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '删除失败' }))
    throw new Error(error.detail || '删除失败')
  }
}
