/**
 * 提示词校验工具函数
 * 与后端 validators.py 使用相同的校验规则
 */

// 年级关键词列表
const GRADE_KEYWORDS = [
  '一年级', '二年级', '三年级', '四年级', '五年级', '六年级',
  '七年级', '八年级', '九年级',
  '初一', '初二', '初三',
  '高一', '高二', '高三'
]

// 学科关键词列表
const SUBJECT_KEYWORDS = [
  '数学', '语文', '英语', '科学',
  '物理', '化学', '生物', '历史', '地理', '政治'
]

// 校验规则常量
const MIN_LENGTH = 5
const MAX_LENGTH = 200

export interface ValidationResult {
  valid: boolean
  error?: string
}

/**
 * 校验提示词
 * @param prompt 用户输入的提示词
 * @returns 校验结果，valid 表示是否有效，error 表示错误信息
 */
export function validatePrompt(prompt: string): ValidationResult {
  // 空值校验
  if (!prompt || !prompt.trim()) {
    return { valid: false, error: '请输入题目要求' }
  }

  const p = prompt.trim()

  // 最小长度校验
  if (p.length < MIN_LENGTH) {
    return { valid: false, error: `题目要求太短，请至少输入 ${MIN_LENGTH} 个字` }
  }

  // 最大长度校验
  if (p.length > MAX_LENGTH) {
    return { valid: false, error: `题目要求太长，请精简到 ${MAX_LENGTH} 字以内` }
  }

  // 必需元素校验：必须包含年级或学科关键词
  const hasGrade = GRADE_KEYWORDS.some(keyword => p.includes(keyword))
  const hasSubject = SUBJECT_KEYWORDS.some(keyword => p.includes(keyword))

  if (!hasGrade && !hasSubject) {
    return { valid: false, error: '请说明年级和学科（如：三年级数学）' }
  }

  return { valid: true }
}

/**
 * 检查提示词是否有效
 * @param prompt 用户输入的提示词
 * @returns True 表示有效，False 表示无效
 */
export function isValidPrompt(prompt: string): boolean {
  return validatePrompt(prompt).valid
}
