import { useEffect, useRef, useState, useCallback } from 'react'

export interface UseMathJaxOptions {
  /** 是否自动渲染，默认为 true */
  autoRender?: boolean
  /** 延迟渲染时间（毫秒），默认为 100ms */
  renderDelay?: number
  /** 依赖变化时重新渲染，默认为 true */
  watchDependencies?: boolean
}

export interface UseMathJaxReturn {
  /** MathJax 是否已加载 */
  isLoaded: boolean
  /** 组件是否已准备好渲染 */
  isReady: boolean
  /** 是否已渲染完成 */
  hasRendered: boolean
  /** 手动触发 MathJax 渲染 */
  render: () => Promise<void>
  /** 重置渲染状态 */
  reset: () => void
}

/**
 * MathJax Hook - 用于在 React 组件中加载和渲染 MathJax
 *
 * @param containerRef - 包含数学公式的 DOM 容器引用
 * @param options - 配置选项
 * @returns UseMathJaxReturn
 *
 * @example
 * ```tsx
 * const containerRef = useRef<HTMLDivElement>(null)
 * const { isLoaded, isReady, render } = useMathJax(containerRef)
 *
 * useEffect(() => {
 *   if (isLoaded && isReady) {
 *     render()
 *   }
 * }, [isLoaded, isReady])
 * ```
 */
export function useMathJax(
  containerRef: React.RefObject<HTMLElement | null>,
  options: UseMathJaxOptions = {}
): UseMathJaxReturn {
  const {
    autoRender = true,
    renderDelay = 100,
    watchDependencies = true,
  } = options

  const initializedRef = useRef(false)
  const mathJaxRenderedRef = useRef(false)
  const prevContentRef = useRef<string>('')

  const [isLoaded, setIsLoaded] = useState(false)
  const [isReady, setIsReady] = useState(false)
  const [hasRendered, setHasRendered] = useState(false)

  // 检测 MathJax 是否加载完成
  useEffect(() => {
    if (initializedRef.current) {
      return
    }

    initializedRef.current = true

    const checkMathJaxReady = () => {
      if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        setIsLoaded(true)
      } else {
        setTimeout(checkMathJaxReady, 50)
      }
    }

    checkMathJaxReady()
  }, [])

  // 手动渲染函数
  const render = useCallback(async (): Promise<void> => {
    if (!containerRef.current || !window.MathJax) {
      return
    }

    if (mathJaxRenderedRef.current) {
      return
    }

    try {
      if (window.MathJax.typesetPromise) {
        await window.MathJax.typesetPromise([containerRef.current])
        mathJaxRenderedRef.current = true
        setHasRendered(true)
      } else if (window.MathJax.typeset) {
        window.MathJax.typeset([containerRef.current])
        mathJaxRenderedRef.current = true
        setHasRendered(true)
      }
    } catch (err) {
      console.error('[MathJax] 渲染失败:', err)
    }
  }, [containerRef])

  // 自动渲染
  useEffect(() => {
    if (!autoRender || !isLoaded || !containerRef.current) {
      return
    }

    const timer = setTimeout(() => {
      render()
    }, renderDelay)

    return () => clearTimeout(timer)
  }, [autoRender, isLoaded, render, renderDelay])

  // 重置渲染状态
  const reset = useCallback(() => {
    mathJaxRenderedRef.current = false
    setHasRendered(false)
    setIsReady(false)
  }, [])

  return {
    isLoaded,
    isReady,
    hasRendered,
    render,
    reset,
  }
}

/**
 * 简化的 MathJax Hook - 仅处理基本的加载和渲染逻辑
 * 适用于简单的使用场景
 *
 * @param containerRef - 包含数学公式的 DOM 容器引用
 * @param dependencies - 依赖数组，当这些值变化时重新渲染
 *
 * @example
 * ```tsx
 * const containerRef = useRef<HTMLDivElement>(null)
 * useMathJaxSimple(containerRef, [questions])
 * ```
 */
export function useMathJaxSimple(
  containerRef: React.RefObject<HTMLElement | null>,
  dependencies: React.DependencyList = []
): void {
  const initializedRef = useRef(false)
  const mathJaxRenderedRef = useRef(false)
  const [isLoaded, setIsLoaded] = useState(false)
  const prevDepsRef = useRef<string>('')

  // 检测 MathJax 是否加载完成
  useEffect(() => {
    if (initializedRef.current) {
      return
    }

    initializedRef.current = true

    const checkMathJaxReady = () => {
      if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        setIsLoaded(true)
      } else {
        setTimeout(checkMathJaxReady, 50)
      }
    }

    checkMathJaxReady()
  }, [])

  // 渲染 MathJax
  useEffect(() => {
    if (!isLoaded || !containerRef.current) {
      return
    }

    const timer = setTimeout(() => {
      if (window.MathJax && containerRef.current) {
        if (window.MathJax.typesetPromise) {
          window.MathJax.typesetPromise([containerRef.current])
            .then(() => {
              mathJaxRenderedRef.current = true
            })
            .catch((err) => {
              console.error('[MathJax] 渲染失败:', err)
            })
        } else if (window.MathJax.typeset) {
          window.MathJax.typeset([containerRef.current])
          mathJaxRenderedRef.current = true
        }
      }
    }, 150)

    return () => clearTimeout(timer)
  }, dependencies) // eslint-disable-line react-hooks/exhaustive-deps
}
