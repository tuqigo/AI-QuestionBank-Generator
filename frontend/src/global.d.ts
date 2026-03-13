// 全局类型声明
export {}

declare global {
  interface Window {
    MathJax?: {
      typesetPromise?: (elements?: (HTMLElement | null)[]) => Promise<void>
      typeset?: (elements?: (HTMLElement | null)[]) => void
      hub?: any
      ajax?: any
      ready?: (callback: () => void) => void
      // MathJax 3 配置对象 - 使用索引签名允许任意属性
      tex?: {
        inlineMath?: string[][]
        displayMath?: string[][]
        processEscapes?: boolean
        processEnvironments?: boolean
        packages?: string[]
        [key: string]: any
      }
      options?: {
        skipHtmlTags?: string[]
        ignoreHtmlClass?: string
        [key: string]: any
      }
      startup?: {
        typeset?: boolean
        ready?: () => void
        defaultReady?: () => void
        [key: string]: any
      }
      svg?: {
        fontCache?: string
        [key: string]: any
      }
      [key: string]: any
    }
  }
}
