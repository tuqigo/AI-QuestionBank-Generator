import type { StructuredQuestion, MetaData } from '@/types/question'
import PrintPreview from '@/components/PrintPreview'
// CSS is imported from MainContent.tsx

interface PreviewPanelProps {
  questions: StructuredQuestion[]
  meta: MetaData | null
  isEmpty: boolean
}

export default function PreviewPanel({
  questions,
  meta,
  isEmpty
}: PreviewPanelProps) {
  return (
    <section className="preview">
      <div className="preview-card">
        {questions.length > 0 && meta ? (
          <div className="preview-body">
            <PrintPreview
              questions={questions}
              meta={meta}
            />
          </div>
        ) : (
          <div className="placeholder">
            <div className="placeholder-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 6V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <p>输入提示词并点击「生成题目」</p>
            <p className="placeholder-hint">题目和答案将在此处预览，支持直接打印或另存为 PDF</p>
          </div>
        )}
      </div>
    </section>
  )
}
