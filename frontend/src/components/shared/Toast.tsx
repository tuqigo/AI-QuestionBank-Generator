import { useEffect, useState, useCallback, useRef } from 'react'
import './Toast.css'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastMessage {
  id: string
  type: ToastType
  message: string
  duration?: number
}

export interface ToastOptions {
  duration?: number
}

/**
 * Toast 消息类型图标
 */
const toastIcons: Record<ToastType, React.ReactNode> = {
  success: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
      <path strokeLinecap="round" strokeLinejoin="round" d="M20 6L9 17l-5-5" />
    </svg>
  ),
  error: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
      <path strokeLinecap="round" strokeLinejoin="round" d="M18 6L6 18M6 6l12 12" />
    </svg>
  ),
  warning: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  info: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
      <circle cx="12" cy="12" r="10" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16v-4m0-4h.01" />
    </svg>
  ),
}

/**
 * 生成唯一 ID
 */
const generateId = () => `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

/**
 * Toast 队列管理 - 使用单例模式
 */
class ToastQueue {
  private static instance: ToastQueue
  private listeners: Set<(toasts: ToastMessage[]) => void> = new Set()
  private toasts: ToastMessage[] = []

  private constructor() {}

  static getInstance(): ToastQueue {
    if (!ToastQueue.instance) {
      ToastQueue.instance = new ToastQueue()
    }
    return ToastQueue.instance
  }

  subscribe(callback: (toasts: ToastMessage[]) => void): () => void {
    this.listeners.add(callback)
    return () => this.listeners.delete(callback)
  }

  private notify() {
    this.listeners.forEach((cb) => cb([...this.toasts]))
  }

  add(toast: Omit<ToastMessage, 'id'>): string {
    const id = generateId()
    const newToast: ToastMessage = { id, ...toast }
    this.toasts = [...this.toasts, newToast]
    this.notify()
    return id
  }

  remove(id: string) {
    this.toasts = this.toasts.filter((t) => t.id !== id)
    this.notify()
  }

  clear() {
    this.toasts = []
    this.notify()
  }

  getToasts(): ToastMessage[] {
    return [...this.toasts]
  }
}

/**
 * Toast 组件 Props
 */
export interface ToastContainerProps {
  position?: 'top-center' | 'top-right' | 'top-left'
  maxToasts?: number
  duration?: number
}

/**
 * Toast 容器组件
 */
export default function ToastContainer({
  position = 'top-center',
  maxToasts = 3,
  duration = 3000,
}: ToastContainerProps) {
  const [toasts, setToasts] = useState<ToastMessage[]>([])
  const queueRef = useRef<ToastQueue>(ToastQueue.getInstance())
  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map())

  const removeToast = useCallback((id: string) => {
    const timer = timersRef.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timersRef.current.delete(id)
    }
    queueRef.current.remove(id)
  }, [])

  const addToast = useCallback(
    (type: ToastType, message: string, options?: ToastOptions): string => {
      const toastDuration = options?.duration ?? duration
      const id = queueRef.current.add({ type, message, duration: toastDuration })

      if (toastDuration > 0) {
        const timer = setTimeout(() => {
          removeToast(id)
        }, toastDuration)
        timersRef.current.set(id, timer)
      }

      return id
    },
    [duration, removeToast]
  )

  useEffect(() => {
    const api = {
      success: (message: string, options?: ToastOptions) => addToast('success', message, options),
      error: (message: string, options?: ToastOptions) => addToast('error', message, options),
      warning: (message: string, options?: ToastOptions) => addToast('warning', message, options),
      info: (message: string, options?: ToastOptions) => addToast('info', message, options),
      remove: removeToast,
      clear: () => queueRef.current.clear(),
    }

    // @ts-ignore - 全局 toast 对象
    window.toast = api

    return () => {
      // @ts-ignore
      delete window.toast
      timersRef.current.forEach((timer) => clearTimeout(timer))
    }
  }, [addToast, removeToast])

  useEffect(() => {
    const unsubscribe = queueRef.current.subscribe(setToasts)
    setToasts(queueRef.current.getToasts())
    return unsubscribe
  }, [])

  // 只显示最新的 maxToasts 条
  const displayToasts = toasts.slice(-maxToasts)

  const positionClass = {
    'top-center': 'toast-top-center',
    'top-right': 'toast-top-right',
    'top-left': 'toast-top-left',
  }[position]

  return (
    <div className={`toast-container ${positionClass}`} role="alert" aria-live="polite">
      {displayToasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          role="alert"
        >
          <span className="toast-icon">{toastIcons[toast.type]}</span>
          <span className="toast-message">{toast.message}</span>
        </div>
      ))}
    </div>
  )
}

// 导出单例和类型
export type { ToastQueue }
export { ToastQueue as ToastQueueSingleton }
