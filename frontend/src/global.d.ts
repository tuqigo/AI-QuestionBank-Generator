// 全局类型声明
export {}

declare global {
  interface Window {
    MathJax?: {
      typesetPromise?: (elements?: HTMLElement[]) => Promise<void>
      typeset?: (elements?: HTMLElement[]) => void
      hub?: any
      ajax?: any
      ready?: (callback: () => void) => void
      // MathJax 3 配置对象
      tex?: {
        inlineMath?: string[][]
        displayMath?: string[][]
        processEscapes?: boolean
        processEnvironments?: boolean
        [key: string]: any
      }
      options?: {
        skipHtmlTags?: string[]
        [key: string]: any
      }
      [key: string]: any
    }
  }
}
