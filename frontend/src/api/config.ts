/**
 * 配置 API 调用
 * 获取全局配置常量：学科、年级、学期、教材版本、题型等
 */

const API_BASE = '/api/configs'

export interface ConfigOption {
  value: string
  label: string
}

export interface QuestionTypeOption extends ConfigOption {
  subjects: string[]  // 适用学科列表
}

export interface ConfigData {
  subjects: ConfigOption[]
  grades: ConfigOption[]
  semesters: ConfigOption[]
  textbook_versions: string[]
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
