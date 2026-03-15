import { useEffect, useState, useCallback } from 'react'
import { ToastQueueSingleton, type ToastType, type ToastOptions } from '@/components/shared/Toast'

/**
 * Toast API 接口
 */
export interface ToastApi {
  success: (message: string, options?: ToastOptions) => string
  error: (message: string, options?: ToastOptions) => string
  warning: (message: string, options?: ToastOptions) => string
  info: (message: string, options?: ToastOptions) => string
  dismiss: (id: string) => void
  clear: () => void
}

const queue = ToastQueueSingleton.getInstance()
const DEFAULT_DURATION = 3000

/**
 * 全局 Toast Hook
 */
export function useToast(): ToastApi {
  const [_, setForceUpdate] = useState(0)

  const forceUpdate = useCallback(() => {
    setForceUpdate((n) => n + 1)
  }, [])

  useEffect(() => {
    const unsubscribe = queue.subscribe(() => {
      forceUpdate()
    })
    return unsubscribe
  }, [forceUpdate])

  const success = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add('success', message, options?.duration ?? DEFAULT_DURATION)
    },
    []
  )

  const error = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add('error', message, options?.duration ?? DEFAULT_DURATION)
    },
    []
  )

  const warning = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add('warning', message, options?.duration ?? DEFAULT_DURATION)
    },
    []
  )

  const info = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add('info', message, options?.duration ?? DEFAULT_DURATION)
    },
    []
  )

  const dismiss = useCallback((id: string) => {
    queue.remove(id)
  }, [])

  const clear = useCallback(() => {
    queue.clear()
  }, [])

  return { success, error, warning, info, dismiss, clear }
}

/**
 * 直接使用全局 toast 对象（非组件环境）
 */
export const toast: ToastApi = {
  success: (message, options) => queue.add('success', message, options?.duration ?? DEFAULT_DURATION),
  error: (message, options) => queue.add('error', message, options?.duration ?? DEFAULT_DURATION),
  warning: (message, options) => queue.add('warning', message, options?.duration ?? DEFAULT_DURATION),
  info: (message, options) => queue.add('info', message, options?.duration ?? DEFAULT_DURATION),
  dismiss: (id) => queue.remove(id),
  clear: () => queue.clear(),
}

export default useToast
