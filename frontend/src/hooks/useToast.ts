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

/**
 * 全局 Toast Hook
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const toast = useToast()
 *
 *   const handleClick = () => {
 *     toast.success('操作成功!')
 *     toast.error('出错了!')
 *   }
 * }
 * ```
 */
export function useToast(): ToastApi {
  const [_, setForceUpdate] = useState(0)

  // 强制重新渲染（虽然实际上不需要，为了保持 Hook 模式一致）
  const forceUpdate = useCallback(() => {
    setForceUpdate((n) => n + 1)
  }, [])

  useEffect(() => {
    // 订阅队列变化以触发重新渲染
    const unsubscribe = queue.subscribe(() => {
      forceUpdate()
    })
    return unsubscribe
  }, [forceUpdate])

  const success = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add({ type: 'success', message, duration: options?.duration })
    },
    []
  )

  const error = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add({ type: 'error', message, duration: options?.duration })
    },
    []
  )

  const warning = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add({ type: 'warning', message, duration: options?.duration })
    },
    []
  )

  const info = useCallback(
    (message: string, options?: ToastOptions): string => {
      return queue.add({ type: 'info', message, duration: options?.duration })
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
 *
 * @example
 * ```ts
 * // 在 API 拦截器中使用
 * toast.error('网络请求失败')
 * ```
 */
export const toast: ToastApi = {
  success: (message, options) => queue.add({ type: 'success', message, duration: options?.duration }),
  error: (message, options) => queue.add({ type: 'error', message, duration: options?.duration }),
  warning: (message, options) => queue.add({ type: 'warning', message, duration: options?.duration }),
  info: (message, options) => queue.add({ type: 'info', message, duration: options?.duration }),
  dismiss: (id) => queue.remove(id),
  clear: () => queue.clear(),
}

export default useToast
