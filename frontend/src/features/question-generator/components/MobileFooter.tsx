import type { TemplateItem } from '@/types/question'
import QuantityControl from './TemplateMode/QuantityControl'
// CSS is imported from MainContent.tsx

interface MobileFooterProps {
  mode: 'prompt' | 'template'
  loading: boolean
  selectedTemplate: TemplateItem | null
  quantity: number
  onQuantityChange: (quantity: number) => void
  onGenerate: () => void
}

export default function MobileFooter({
  mode,
  loading,
  selectedTemplate,
  quantity,
  onQuantityChange,
  onGenerate
}: MobileFooterProps) {
  if (mode === 'prompt') {
    return (
      <div className="mobile-fixed-footer">
        <button
          type="button"
          className="btn-generate"
          onClick={onGenerate}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner spinner-small"></span>
              生成中...
            </>
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2V4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M12 20V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M4.92999 4.92999L6.33999 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M17.66 17.66L19.07 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M2 12H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M20 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M6.33999 17.66L4.92999 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M19.07 4.92999L17.66 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" />
              </svg>
              生成题目
            </>
          )}
        </button>
      </div>
    )
  }

  return (
    <div className="mobile-fixed-footer">
      <div className="mobile-generate-wrapper">
        {/* 题目数量控制 */}
        {selectedTemplate && (
          <QuantityControl
            quantity={quantity}
            onChange={onQuantityChange}
            variant="mobile"
          />
        )}
        <button
          type="button"
          className="btn-generate"
          onClick={onGenerate}
          disabled={loading || !selectedTemplate}
        >
          {loading ? (
            <>
              <span className="spinner spinner-small"></span>
              生成中...
            </>
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2V4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M12 20V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M4.92999 4.92999L6.33999 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M17.66 17.66L19.07 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M2 12H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M20 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M6.33999 17.66L4.92999 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M19.07 4.92999L17.66 6.33999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" />
              </svg>
              {selectedTemplate ? '生成题目' : '请选择模板'}
            </>
          )}
        </button>
      </div>
    </div>
  )
}
