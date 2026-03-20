import { useState, useCallback } from 'react'
import type { StructuredQuestion, MetaData, TemplateItem } from '@/types/question'
import { generateStructuredQuestions, generateFromTemplate as apiGenerateFromTemplate } from '@/core/api/history'
import type { TemplateGenerateResponse } from '@/types/question'

type ProgressStage = 'preparing' | 'connecting' | 'generating' | 'processing' | 'complete'

interface UseQuestionGeneratorReturn {
  // 状态
  questions: StructuredQuestion[]
  meta: MetaData | null
  loading: boolean
  error: string
  progressStage: ProgressStage
  showProgress: boolean

  // 设置器
  setQuestions: React.Dispatch<React.SetStateAction<StructuredQuestion[]>>
  setMeta: React.Dispatch<React.SetStateAction<MetaData | null>>
  setError: React.Dispatch<React.SetStateAction<string>>
  setShowProgress: React.Dispatch<React.SetStateAction<boolean>>

  // 动作
  generateFromPrompt: (prompt: string, isMobile: boolean) => Promise<void>
  generateFromTemplate: (template: TemplateItem, quantity: number, isMobile: boolean) => Promise<void>
  resetState: () => void
}

/**
 * 管理题目生成逻辑（含进度控制）
 */
export function useQuestionGenerator(): UseQuestionGeneratorReturn {
  const [questions, setQuestions] = useState<StructuredQuestion[]>([])
  const [meta, setMeta] = useState<MetaData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [progressStage, setProgressStage] = useState<ProgressStage>('preparing')
  const [showProgress, setShowProgress] = useState(false)

  // 进度阶段推进逻辑
  const advanceProgress = useCallback((stageTimers: ReturnType<typeof setTimeout>[]) => {
    // 200ms 后进入"连接 AI"阶段
    stageTimers.push(setTimeout(() => {
      setProgressStage('connecting')
    }, 200))

    // 800ms 后进入"生成中"阶段
    stageTimers.push(setTimeout(() => {
      setProgressStage('generating')
    }, 800))

    // 8 秒后如果还在生成中，显示"整理中"
    stageTimers.push(setTimeout(() => {
      if (progressStage === 'generating') {
        setProgressStage('processing')
      }
    }, 8000))
  }, [progressStage])

  // 处理错误消息
  const formatErrorMessage = useCallback((e: unknown): string => {
    if (e instanceof Error) {
      if (e.message.includes('超时')) {
        return '题目生成时间过长，请减少题目数量或简化要求后重试'
      } else if (e.message.includes('网络')) {
        return '网络连接失败，请检查网络后重试'
      } else {
        return e.message || '系统内部错误，稍后再试！'
      }
    }
    return '生成失败，请稍后重试'
  }, [])

  // 从提示词生成题目
  const generateFromPrompt = useCallback(async (prompt: string, isMobile: boolean) => {
    setLoading(true)
    setShowProgress(true)
    setProgressStage('preparing')
    setQuestions([])
    setMeta(null)

    const stageTimers: ReturnType<typeof setTimeout>[] = []
    advanceProgress(stageTimers)

    try {
      const data = await generateStructuredQuestions(prompt)

      if (data.meta) {
        setMeta({
          subject: data.meta.subject,
          grade: data.meta.grade,
          title: data.meta.title
        })
      }

      if (data.questions) {
        setQuestions(data.questions)
      }

      setProgressStage('complete')

      setTimeout(() => {
        setShowProgress(false)
      }, 500)
    } catch (e) {
      setError(formatErrorMessage(e))
      setShowProgress(false)
    } finally {
      setLoading(false)
      stageTimers.forEach(clearTimeout)
    }
  }, [advanceProgress, formatErrorMessage])

  // 从模板生成题目
  const generateFromTemplate = useCallback(async (template: TemplateItem, quantity: number, isMobile: boolean) => {
    setLoading(true)
    setShowProgress(true)
    setProgressStage('preparing')
    setQuestions([])
    setMeta(null)

    const stageTimers: ReturnType<typeof setTimeout>[] = []
    advanceProgress(stageTimers)

    try {
      const data: TemplateGenerateResponse = await apiGenerateFromTemplate(template.id, quantity)

      if (data.meta) {
        setMeta({
          subject: data.meta.subject,
          grade: data.meta.grade,
          title: data.meta.title
        })
      }

      if (data.questions) {
        setQuestions(data.questions)
      }

      setProgressStage('complete')

      setTimeout(() => {
        setShowProgress(false)
      }, 500)
    } catch (e) {
      setError(formatErrorMessage(e))
      setShowProgress(false)
    } finally {
      setLoading(false)
      stageTimers.forEach(clearTimeout)
    }
  }, [advanceProgress, formatErrorMessage])

  // 重置状态
  const resetState = useCallback(() => {
    setQuestions([])
    setMeta(null)
    setLoading(false)
    setError('')
    setProgressStage('preparing')
    setShowProgress(false)
  }, [])

  return {
    questions,
    meta,
    loading,
    error,
    progressStage,
    showProgress,
    setQuestions,
    setMeta,
    setError,
    setShowProgress,
    generateFromPrompt,
    generateFromTemplate,
    resetState,
  }
}
