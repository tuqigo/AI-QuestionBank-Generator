/**
 * 古诗文鉴赏/默写组件
 */
import { QuestionRendererProps } from '@/types/structured'
import { renderMarkdown } from '@/utils/markdownProcessor'

export default function PoetryApp({ question, index }: QuestionRendererProps) {
  return (
    <div className="question-item question-poetry-app">
      <div className="question-header">
        <span className="question-number">{index}. </span>
        <div className="question-stem" dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
      </div>
      <div className="answer-area">
        <span className="answer-placeholder">答：________________________</span>
      </div>
    </div>
  )
}
