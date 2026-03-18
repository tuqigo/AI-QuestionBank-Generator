import { useEffect, useRef } from 'react'

interface UseSwipeToCloseOptions {
  isOpen: boolean
  onClose: () => void
  threshold?: number
}

/**
 * 移动端滑动手势关闭模态框
 * 支持：
 * 1. 向左滑动关闭
 * 2. 向右滑动关闭
 */
export function useSwipeToClose({ isOpen, onClose, threshold = 100 }: UseSwipeToCloseOptions) {
  const startX = useRef<number>(0)
  const currentX = useRef<number>(0)
  const isTouching = useRef<boolean>(false)

  useEffect(() => {
    if (!isOpen) return

    const handleTouchStart = (e: TouchEvent) => {
      startX.current = e.touches[0].clientX
      currentX.current = 0
      isTouching.current = true
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (!isTouching.current) return

      currentX.current = e.touches[0].clientX - startX.current
    }

    const handleTouchEnd = (e: TouchEvent) => {
      if (!isTouching.current) return
      isTouching.current = false

      const deltaX = currentX.current

      // 向左滑动超过阈值，关闭
      if (deltaX < -threshold) {
        onClose()
        return
      }

      // 向右滑动超过阈值，关闭
      if (deltaX > threshold) {
        onClose()
        return
      }
    }

    document.addEventListener('touchstart', handleTouchStart, { passive: true })
    document.addEventListener('touchmove', handleTouchMove, { passive: true })
    document.addEventListener('touchend', handleTouchEnd, { passive: true })

    return () => {
      document.removeEventListener('touchstart', handleTouchStart)
      document.removeEventListener('touchmove', handleTouchMove)
      document.removeEventListener('touchend', handleTouchEnd)
    }
  }, [isOpen, onClose, threshold])
}
