import { fetchWithAdminAuth } from '../auth'

const API_BASE = '/api/admin'

// ========== 认证 ==========

export async function adminLogin(password: string): Promise<{ access_token: string; expires_in: number }> {
  const response = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ password }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '登录失败' }))
    throw new Error(error.detail || '登录失败')
  }

  return response.json()
}

export async function getAdminMe(): Promise<{ role: string; authenticated: boolean }> {
  const response = await fetchWithAdminAuth(`${API_BASE}/me`)
  if (!response.ok) {
    throw new Error('未登录')
  }
  return response.json()
}

// ========== 用户管理 ==========

export interface User {
  id: number
  email: string
  created_at: string
  is_disabled: boolean
}

export interface UserDetail extends User {
  total_records: number
  last_activity: string | null
}

export interface UserListResponse {
  data: User[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export async function getUsers(page: number = 1, page_size: number = 20): Promise<UserListResponse> {
  const response = await fetchWithAdminAuth(`${API_BASE}/users?page=${page}&page_size=${page_size}`)
  if (!response.ok) {
    throw new Error('获取用户列表失败')
  }
  return response.json()
}

export async function getUserDetail(user_id: number): Promise<UserDetail> {
  const response = await fetchWithAdminAuth(`${API_BASE}/users/${user_id}`)
  if (!response.ok) {
    throw new Error('获取用户详情失败')
  }
  return response.json()
}

export async function disableUser(user_id: number, is_disabled: boolean): Promise<{ message: string }> {
  const response = await fetchWithAdminAuth(`${API_BASE}/users/${user_id}/disable`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ is_disabled }),
  })

  if (!response.ok) {
    throw new Error('更新用户状态失败')
  }

  return response.json()
}

// ========== 用户记录 ==========

export interface QuestionRecord {
  id: number
  title: string
  prompt_type: string
  prompt_content: string
  image_path: string | null
  ai_response: string
  created_at: string
}

export interface UserRecordsResponse {
  data: QuestionRecord[]
  next_cursor: number | null
  has_more: boolean
}

export async function getUserRecords(
  user_id: number,
  cursor: number | null = null,
  limit: number = 20
): Promise<UserRecordsResponse> {
  const params = new URLSearchParams()
  params.set('limit', limit.toString())
  if (cursor !== null) {
    params.set('cursor', cursor.toString())
  }

  const response = await fetchWithAdminAuth(`${API_BASE}/users/${user_id}/records?${params}`)
  if (!response.ok) {
    throw new Error('获取用户记录失败')
  }
  return response.json()
}

export async function getUserRecordDetail(record_id: number): Promise<{
  id: number
  title: string
  prompt_type: string
  prompt_content: string
  ai_response: string
  created_at: string
}> {
  const response = await fetchWithAdminAuth(`${API_BASE}/user-records/${record_id}`)
  if (!response.ok) {
    throw new Error('获取用户记录详情失败')
  }
  return response.json()
}

// ========== 操作日志 ==========

export interface OperationLog {
  id: number
  operator: string
  action: string
  target_type: string | null
  target_id: number | null
  ip: string | null
  created_at: string
}

export interface OperationLogListResponse {
  data: OperationLog[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export async function getOperationLogs(
  page: number = 1,
  page_size: number = 20
): Promise<OperationLogListResponse> {
  const response = await fetchWithAdminAuth(`${API_BASE}/operation-logs?page=${page}&page_size=${page_size}`)
  if (!response.ok) {
    throw new Error('获取操作日志失败')
  }
  return response.json()
}

// ========== AI 生成记录 ==========

export interface AiGenerationRecord {
  id: number
  user_id: number
  user_email: string
  prompt: string
  prompt_type: 'text' | 'vision'
  success: boolean
  duration: number
  error_message: string | null
  created_at: string
}

export interface AiRecordListResponse {
  data: AiGenerationRecord[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface AiRecordFilter {
  user_id?: number
  success?: boolean
  prompt_type?: string
  date_from?: string
  date_to?: string
}

export async function getAiRecords(
  page: number = 1,
  page_size: number = 20,
  filter?: AiRecordFilter
): Promise<AiRecordListResponse> {
  const params = new URLSearchParams()
  params.set('page', page.toString())
  params.set('page_size', page_size.toString())

  if (filter) {
    if (filter.user_id) params.set('user_id', filter.user_id.toString())
    if (filter.success !== undefined) params.set('success', filter.success.toString())
    if (filter.prompt_type) params.set('prompt_type', filter.prompt_type)
    if (filter.date_from) params.set('date_from', filter.date_from)
    if (filter.date_to) params.set('date_to', filter.date_to)
  }

  const response = await fetchWithAdminAuth(`${API_BASE}/ai-records?${params}`)
  if (!response.ok) {
    throw new Error('获取 AI 记录失败')
  }
  return response.json()
}

export async function getAiRecordDetail(record_id: number): Promise<AiGenerationRecord> {
  const response = await fetchWithAdminAuth(`${API_BASE}/ai-records/${record_id}`)
  if (!response.ok) {
    throw new Error('获取 AI 记录详情失败')
  }
  return response.json()
}

// ========== 模板管理 ==========

export interface QuestionTemplate {
  id: number
  name: string
  subject: string
  grade: string
  semester: string
  textbook_version: string
  question_type: string
  template_pattern: string
  variables_config: string
  example: string | null
  generator_module: string | null
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TemplateListResponse {
  templates: TemplateListItem[]
}

export interface TemplateListItem {
  id: number
  name: string
  subject: string
  grade: string
  semester: string
  textbook_version: string
  example: string | null
}

export interface TemplateCreateInput {
  name: string
  subject: string
  grade: string
  semester: string
  textbook_version: string
  question_type: string
  template_pattern: string
  variables_config: string
  example?: string
  sort_order?: number
  is_active?: boolean
  generator_module?: string
}

export interface TemplateUpdateInput {
  name?: string
  template_pattern?: string
  variables_config?: string
  example?: string
  sort_order?: number
  is_active?: boolean
}

export interface TemplateGenerateInput {
  template_id: number
  quantity: number
}

export async function getTemplates(): Promise<TemplateListResponse> {
  const response = await fetchWithAdminAuth('/api/templates/list')
  if (!response.ok) {
    throw new Error('获取模板列表失败')
  }
  return response.json()
}

export async function getAllTemplates(): Promise<{ templates: QuestionTemplate[] }> {
  const response = await fetchWithAdminAuth('/api/templates/admin/all')
  if (!response.ok) {
    throw new Error('获取所有模板失败')
  }
  return response.json()
}

export async function createTemplate(input: TemplateCreateInput): Promise<{ id: number }> {
  const response = await fetchWithAdminAuth('/api/templates/admin/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '创建失败' }))
    throw new Error(error.detail || '创建失败')
  }
  return response.json()
}

export async function updateTemplate(template_id: number, input: TemplateUpdateInput): Promise<{ message: string }> {
  const response = await fetchWithAdminAuth(`/api/templates/admin/${template_id}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '更新失败' }))
    throw new Error(error.detail || '更新失败')
  }
  return response.json()
}

export async function deleteTemplate(template_id: number): Promise<{ message: string }> {
  const response = await fetchWithAdminAuth(`/api/templates/admin/${template_id}/delete`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '删除失败' }))
    throw new Error(error.detail || '删除失败')
  }
  return response.json()
}

export async function toggleTemplate(template_id: number, is_active: boolean): Promise<{ message: string }> {
  const response = await fetchWithAdminAuth(`/api/templates/admin/${template_id}/toggle?is_active=${is_active}`, {
    method: 'POST',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '操作失败' }))
    throw new Error(error.detail || '操作失败')
  }
  return response.json()
}

export async function testTemplate(
  template_id: number,
  quantity: number
): Promise<{ meta: { subject: string; grade: string; title: string }; questions: any[] }> {
  const response = await fetchWithAdminAuth(`/api/templates/admin/${template_id}/test`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ template_id, quantity }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '测试失败' }))
    throw new Error(error.detail || '测试失败')
  }
  return response.json()
}

export async function generateFromTemplate(
  input: TemplateGenerateInput
): Promise<{ meta: { subject: string; grade: string; title: string }; questions: any[] }> {
  const response = await fetchWithAdminAuth('/api/templates/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '生成失败' }))
    throw new Error(error.detail || '生成失败')
  }
  return response.json()
}
