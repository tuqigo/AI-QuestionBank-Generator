import type { ConfigOption, TextbookVersionOption } from '@/api/config'
import type { TemplateFilter } from '@/types/question'
// CSS is imported from MainContent.tsx

interface TemplateFilterProps {
  filterOptions: {
    grades: ConfigOption[]
    subjects: ConfigOption[]
    semesters: ConfigOption[]
    textbook_versions: TextbookVersionOption[]
  }
  filter: TemplateFilter
  onFilterChange: (filter: TemplateFilter) => void
  onApply: () => void
  loading: boolean
}

export default function TemplateFilter({
  filterOptions,
  filter,
  onFilterChange,
  onApply,
  loading
}: TemplateFilterProps) {
  return (
    <div className="template-filter">
      <select
        value={filter.grade || ''}
        onChange={(e) => onFilterChange({ ...filter, grade: e.target.value as any })}
        className="filter-select"
      >
        <option value="">全部年级</option>
        {filterOptions.grades.map(g => (
          <option key={g.value} value={g.value}>{g.label}</option>
        ))}
      </select>
      <select
        value={filter.subject || ''}
        onChange={(e) => onFilterChange({ ...filter, subject: e.target.value as any })}
        className="filter-select"
      >
        <option value="">全部学科</option>
        {filterOptions.subjects.map(s => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>
      <select
        value={filter.semester || ''}
        onChange={(e) => onFilterChange({ ...filter, semester: e.target.value as any })}
        className="filter-select"
      >
        <option value="">全部学期</option>
        {filterOptions.semesters.map(s => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>
      <select
        value={filter.textbook_version || ''}
        onChange={(e) => onFilterChange({ ...filter, textbook_version: e.target.value })}
        className="filter-select"
      >
        <option value="">全部版本</option>
        {filterOptions.textbook_versions.map(v => (
          <option key={v.id} value={v.id}>{v.name}</option>
        ))}
      </select>
      <button
        type="button"
        className="btn-search-template"
        onClick={onApply}
        disabled={loading}
      >
        查找模板
      </button>
    </div>
  )
}
