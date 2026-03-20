import { useState, useEffect, useCallback } from 'react'
import type { TemplateItem, TemplateFilter } from '@/types/question'
import type { ConfigOption, TextbookVersionOption } from '@/api/config'

interface UseTemplateFilterReturn {
  // 筛选条件状态
  templateFilter: TemplateFilter
  setTemplateFilter: React.Dispatch<React.SetStateAction<TemplateFilter>>

  // 筛选选项（从模板列表提取）
  filterOptions: {
    grades: ConfigOption[]
    subjects: ConfigOption[]
    semesters: ConfigOption[]
    textbook_versions: TextbookVersionOption[]
  }

  // 筛选摘要
  filterSummary: string

  // 筛选逻辑
  applyFilter: (allTemplates: TemplateItem[], grades: ConfigOption[], subjects: ConfigOption[], semesters: ConfigOption[], textbookVersions: TextbookVersionOption[]) => TemplateItem[]

  // 重置筛选
  resetFilter: () => void
}

/**
 * 管理模板筛选逻辑
 */
export function useTemplateFilter(
  allTemplates: TemplateItem[],
  grades: ConfigOption[],
  subjects: ConfigOption[],
  semesters: ConfigOption[],
  textbookVersions: TextbookVersionOption[]
): UseTemplateFilterReturn {
  // 筛选条件状态（带 localStorage 持久化）
  const [templateFilter, setTemplateFilter] = useState<TemplateFilter>(() => {
    const saved = localStorage.getItem('question-generator-filter')
    return saved ? JSON.parse(saved) : {}
  })

  // 筛选条件变化时保存到 localStorage
  useEffect(() => {
    localStorage.setItem('question-generator-filter', JSON.stringify(templateFilter))
  }, [templateFilter])

  // 从模板列表中提取唯一的筛选选项
  const getFilterOptionsFromTemplates = useCallback((): UseTemplateFilterReturn['filterOptions'] => {
    if (allTemplates.length === 0) {
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

    allTemplates.forEach((template) => {
      if (template.grade) gradesSet.add(template.grade)
      if (template.subject) subjectsSet.add(template.subject)
      if (template.semester) semestersSet.add(template.semester)
      if (template.textbook_version) textbookVersionsSet.add(template.textbook_version)
    })

    // 获取教材版本名称
    const getTextbookVersionName = (versionId: string): string => {
      return textbookVersions.find(v => v.id === versionId)?.name || versionId
    }

    return {
      grades: Array.from(gradesSet).map(g => ({ value: g, label: g })),
      subjects: Array.from(subjectsSet).map(s => ({ value: s, label: s })),
      semesters: Array.from(semestersSet).map(s => ({ value: s, label: s })),
      textbook_versions: Array.from(textbookVersionsSet).map(v => ({
        id: v,
        name: getTextbookVersionName(v),
        sort: 0
      })),
    }
  }, [allTemplates, textbookVersions])

  const filterOptions = getFilterOptionsFromTemplates()

  // 计算筛选摘要
  const getFilterSummary = useCallback((): string => {
    const parts: string[] = []
    if (templateFilter.grade) {
      parts.push(templateFilter.grade)
    }
    if (templateFilter.semester) {
      // 学期：只需要括号内容，如 "(下)"
      if (templateFilter.semester.includes('上')) {
        parts.push('(上)')
      } else if (templateFilter.semester.includes('下')) {
        parts.push('(下)')
      }
    }
    if (templateFilter.textbook_version) {
      const versionName = textbookVersions.find(v => v.id === templateFilter.textbook_version)?.name ||
                         templateFilter.textbook_version
      parts.push(versionName)
    }
    return parts.length > 0 ? parts.join('') : ''
  }, [templateFilter, textbookVersions])

  const filterSummary = getFilterSummary()

  // 筛选逻辑
  const applyFilter = useCallback((
    allTemplates: TemplateItem[],
    grades: ConfigOption[],
    subjects: ConfigOption[],
    semesters: ConfigOption[],
    textbookVersions: TextbookVersionOption[]
  ): TemplateItem[] => {
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

    return result
  }, [templateFilter])

  // 重置筛选
  const resetFilter = useCallback(() => {
    setTemplateFilter({})
    localStorage.removeItem('question-generator-filter')
  }, [])

  return {
    templateFilter,
    setTemplateFilter,
    filterOptions,
    filterSummary,
    applyFilter,
    resetFilter,
  }
}
