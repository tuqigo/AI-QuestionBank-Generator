/**
 * 类型定义统一导出
 */

// ===================== 历史记录相关类型 =====================

export interface GenerateResponse {
  title: string
  markdown: string
  record_id?: number
  short_id?: string
}

export interface QuestionRecord {
  id: number
  short_id: string
  title: string
  prompt_type: 'text' | 'image'
  prompt_content: string
  image_path: string | null
  ai_response: string
  is_deleted: boolean
  created_at: string
}

/** 历史记录列表项（精简版） */
export interface QuestionRecordListItem {
  id: number
  short_id: string
  title: string
  prompt_type: 'text' | 'image'
  created_at: string
}

export interface QuestionRecordListResponse {
  data: QuestionRecordListItem[]
  next_cursor: number | null
  has_more: boolean
}

export interface ShareUrlResponse {
  share_url: string
}

// ===================== MathJax 类型定义 =====================

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
