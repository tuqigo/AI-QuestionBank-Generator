import { useState, useEffect } from 'react'

interface UseResponsiveReturn {
  isMobile: boolean
  isMobileWidth: boolean
  setIsMobileWidth: (value: boolean) => void
}

/**
 * 管理响应式状态，监听窗口大小变化
 * @param breakpoint 移动端断点，默认 768px
 */
export function useResponsive(breakpoint: number = 768): UseResponsiveReturn {
  const [isMobileWidth, setIsMobileWidth] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth <= breakpoint : false
  )

  useEffect(() => {
    const handleResize = () => {
      setIsMobileWidth(window.innerWidth <= breakpoint)
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [breakpoint])

  return {
    isMobile: isMobileWidth,
    isMobileWidth,
    setIsMobileWidth,
  }
}
