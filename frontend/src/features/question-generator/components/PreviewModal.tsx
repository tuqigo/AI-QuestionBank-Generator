import type { StructuredQuestion, MetaData } from '@/types/question'
import PrintPreview from '@/components/PrintPreview'
// CSS is imported from MainContent.tsx

interface PreviewModalProps {
  isOpen: boolean
  onClose: () => void
  questions: StructuredQuestion[]
  meta: MetaData | null
  downloadingPDF: boolean
  onDownload: () => void
}

export default function PreviewModal({
  isOpen,
  onClose,
  questions,
  meta,
  downloadingPDF,
  onDownload
}: PreviewModalProps) {
  if (!isOpen || !meta) return null

  return (
    <div className="preview-modal-overlay" onClick={onClose}>
      <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
        <div className="preview-modal-header">
          <h3>打印预览</h3>
          <button className="preview-modal-close" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        <div className="preview-modal-body">
          <PrintPreview
            questions={questions}
            meta={meta}
          />
        </div>
        <div className="preview-modal-footer">
          <button
            type="button"
            className="btn-download-pdf-modal"
            onClick={onDownload}
            disabled={downloadingPDF}
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
        </div>
      </div>
    </div>
  )
}
