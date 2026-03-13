import { fetchWithAuth } from '../auth'
import type {
  QuestionRecord,
  QuestionRecordListResponse,
  ShareUrlResponse,
} from '../types'

import type { StructuredGenerateResponse } from '@/types/structured'

const API_BASE = '/api'

/** 获取历史记录列表（游标分页） */
export async function getHistoryList(
  cursor?: number,
  size: number = 20
): Promise<QuestionRecordListResponse> {
  const params = new URLSearchParams()
  if (cursor) params.set('cursor', String(cursor))
  params.set('size', String(size))

  const url = `${API_BASE}/history?${params.toString()}`
  const res = await fetchWithAuth(url)

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || '获取历史记录失败')
  }

  return res.json()
}

/** 获取单条历史记录详情 */
export async function getHistoryDetail(shortId: string): Promise<QuestionRecord> {
  const res = await fetchWithAuth(`${API_BASE}/history/${shortId}`)

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || '获取记录详情失败')
  }

  return res.json()
}

/** 删除历史记录 */
export async function deleteHistory(shortId: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}/history/${shortId}`, {
    method: 'DELETE',
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || '删除记录失败')
  }
}

/** 生成分享链接 */
export async function createShareUrl(shortId: string): Promise<string> {
  const res = await fetchWithAuth(`${API_BASE}/history/${shortId}/share`, {
    method: 'POST',
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || '生成分享链接失败')
  }

  const data: ShareUrlResponse = await res.json()
  return data.share_url
}

/** 通过分享 token 获取记录（无需登录） */
export async function getSharedRecord(shortId: string, token: string): Promise<QuestionRecord> {
  const url = `${API_BASE}/share/history/${shortId}?token=${encodeURIComponent(token)}`
  const res = await fetch(url)

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || '分享记录不存在或链接无效')
  }

  return res.json()
}

/** 生成结构化题目（新接口） */
export async function generateStructuredQuestions(prompt: string): Promise<StructuredGenerateResponse> {
  const res = await fetchWithAuth(`${API_BASE}/questions/structured`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(error || '生成题目失败')
  }

  return res.json()
}
