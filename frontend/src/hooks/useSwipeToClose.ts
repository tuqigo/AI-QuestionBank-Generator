import { useEffect, useRef } from 'react'

interface UseSwipeToCloseOptions {
  isOpen: boolean
  onClose: () => void
  threshold?: number
}

/**
 * 移动端滑动手势关闭模态框
 * 支持：
 * 1. 向下滑动关闭（bottom sheet 样式）
 * 2. 向左滑动关闭
 */
export function useSwipeToClose({ isOpen, onClose, threshold = 100 }: UseSwipeToCloseOptions) {
  const startY = useRef<number>(0)
  const startX = useRef<number>(0)
  const currentY = useRef<number>(0)
  const currentX = useRef<number>(0)
  const isTouching = useRef<boolean>(false)

  useEffect(() => {
    if (!isOpen) return

    const handleTouchStart = (e: TouchEvent) => {
      startY.current = e.touches[0].clientY
      startX.current = e.touches[0].clientX
      currentY.current = 0
      currentX.current = 0
      isTouching.current = true
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (!isTouching.current) return

      currentY.current = e.touches[0].clientY - startY.current
      currentX.current = e.touches[0].clientX - startX.current
    }

    const handleTouchEnd = (e: TouchEvent) => {
      if (!isTouching.current) return
      isTouching.current = false

      const deltaY = currentY.current
      const deltaX = currentX.current

      // 向下滑动超过阈值，关闭
      if (deltaY > threshold) {
        onClose()
        return
      }

      // 向左滑动超过阈值，关闭
      if (deltaX < -threshold) {
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
