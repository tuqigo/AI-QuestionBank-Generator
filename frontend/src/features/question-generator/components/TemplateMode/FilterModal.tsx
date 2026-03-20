import type { ConfigOption, TextbookVersionOption } from '@/api/config'
import type { TemplateFilter } from '@/types/question'
// CSS is imported from MainContent.tsx

interface FilterModalProps {
  isOpen: boolean
  onClose: () => void
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

export default function FilterModal({
  isOpen,
  onClose,
  filterOptions,
  filter,
  onFilterChange,
  onApply,
  loading
}: FilterModalProps) {
  if (!isOpen) return null

  return (
    <div className="filter-modal-overlay" onClick={onClose}>
      <div className="filter-modal" onClick={(e) => e.stopPropagation()}>
        <div className="filter-modal-header">
          <h3>筛选模板</h3>
          <button className="filter-modal-close" onClick={onClose}>
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
                    className={`filter-modal-option ${filter.subject === s.value ? 'selected' : ''}`}
                    onClick={() => onFilterChange({ ...filter, subject: s.value })}
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
                    className={`filter-modal-option ${filter.grade === g.value ? 'selected' : ''}`}
                    onClick={() => onFilterChange({ ...filter, grade: g.value })}
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
                    className={`filter-modal-option ${filter.semester === s.value ? 'selected' : ''}`}
                    onClick={() => onFilterChange({ ...filter, semester: s.value })}
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
                    key={v.id}
                    type="button"
                    className={`filter-modal-option ${filter.textbook_version === v.id ? 'selected' : ''}`}
                    onClick={() => onFilterChange({ ...filter, textbook_version: v.id })}
                  >
                    {v.name}
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
              onFilterChange({})
              onApply()
            }}
          >
            重置
          </button>
          <button
            type="button"
            className="btn-filter-confirm"
            onClick={() => {
              onApply()
              onClose()
            }}
            disabled={loading}
          >
            查找模板
          </button>
        </div>
      </div>
    </div>
  )
}
