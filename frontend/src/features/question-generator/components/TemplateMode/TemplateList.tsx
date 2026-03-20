import { MathJaxText } from '@/admin/components/MathJaxText'
import type { TemplateItem } from '@/types/question'
// CSS is imported from MainContent.tsx

interface TemplateListProps {
  templates: TemplateItem[]
  loading: boolean
  selectedTemplate: TemplateItem | null
  onSelect: (template: TemplateItem) => void
}

export default function TemplateList({
  templates,
  loading,
  selectedTemplate,
  onSelect
}: TemplateListProps) {
  return (
    <div className="template-list">
      {loading && (
        <div className="template-loading">
          <span className="spinner-small"></span>
          加载中...
        </div>
      )}
      {!loading && templates.length === 0 && (
        <div className="template-empty">
          点击筛选按钮加载模板列表
        </div>
      )}
      {!loading && templates.map((template) => (
        <div
          key={template.id}
          className={`template-item ${selectedTemplate?.id === template.id ? 'selected' : ''}`}
          onClick={() => onSelect(template)}
        >
          <div className="template-name">{template.name}</div>
          {template.example && template.example.length > 0 && (
            <div className="template-example">
              <span className="example-label">例题：</span>
              <span className="example-content">
                <MathJaxText text={template.example[0]} />
              </span>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
