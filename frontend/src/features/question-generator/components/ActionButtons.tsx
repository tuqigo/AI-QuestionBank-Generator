import type { StructuredQuestion, MetaData, TemplateItem } from '@/types/question'
// CSS is imported from MainContent.tsx

interface ActionButtonsProps {
  mode: 'prompt' | 'template'
  loading: boolean
  selectedTemplate: TemplateItem | null
  questions: StructuredQuestion[]
  meta: MetaData | null
  downloadingPDF: boolean
  onDownload: () => void
  onGenerate: () => void
  quantity: number
  onQuantityChange: (quantity: number) => void
}

export default function ActionButtons({
  mode,
  loading,
  selectedTemplate,
  questions,
  meta,
  downloadingPDF,
  onDownload,
  onGenerate,
  quantity,
  onQuantityChange
}: ActionButtonsProps) {
  return (
    <div className="action-buttons">
      {/* 题目数量控制 - 模板模式下显示 */}
      {mode === 'template' && selectedTemplate && (
        <div className="quantity-control-inline">
          <button
            type="button"
            className="quantity-btn-inline"
            onClick={() => onQuantityChange(Math.max(5, quantity - 5))}
          >
            -
          </button>
          <span className="quantity-value-inline">{quantity} 道</span>
          <button
            type="button"
            className="quantity-btn-inline"
            onClick={() => onQuantityChange(Math.min(100, quantity + 5))}
          >
            +
          </button>
        </div>
      )}
      {/* 下载 PDF 按钮 - 仅在生成成功后显示 */}
      {questions.length > 0 && meta && (
        <button
          type="button"
          className="btn-download-pdf"
          onClick={onDownload}
          disabled={downloadingPDF}
          title={downloadingPDF ? '生成中...' : '下载 PDF'}
          aria-label="下载 PDF"
        >
          {downloadingPDF ? (
            <svg className="spinner-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeDasharray="32 64" opacity="0.3" />
              <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <polyline points="7 10 12 15 17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
          {downloadingPDF ? '生成中...' : '下载 PDF'}
        </button>
      )}
      {/* 生成按钮 */}
      {mode === 'prompt' ? (
        <button
          type="button"
          className="btn-generate"
          onClick={onGenerate}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
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
      ) : (
        <button
          type="button"
          className="btn-generate"
          onClick={onGenerate}
          disabled={loading || !selectedTemplate}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
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
      )}
    </div>
  )
}
