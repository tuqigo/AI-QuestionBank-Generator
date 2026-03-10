export interface GenerateResponse {
  title: string
  markdown: string
}

// 历史记录相关类型
export interface QuestionRecord {
  id: number
  title: string
  prompt_type: 'text' | 'image'
  prompt_content: string
  image_path: string | null
  ai_response: string
  is_deleted: boolean
  created_at: string
}

export interface QuestionRecordListResponse {
  data: QuestionRecord[]
  next_cursor: number | null
  has_more: boolean
}

export interface ShareUrlResponse {
  share_url: string
}

// MathJax 类型定义
declare global {
  interface Window {
    MathJax?: {
      tex: {
        inlineMath: string[][]
        displayMath: string[][]
        processEscapes: boolean
        processEnvironments: boolean
        packages?: string[]
      }
      options: {
        skipHtmlTags: string[]
        ignoreHtmlClass?: string
      }
      svg: {
        fontCache: string
      }
      typeset?: (elements: HTMLElement[]) => void
      typesetPromise?: (elements: HTMLElement[]) => Promise<void>
    }
  }
}
