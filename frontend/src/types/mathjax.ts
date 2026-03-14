/**
 * MathJax 全局类型定义
 */

export interface MathJaxConfig {
  tex?: {
    inlineMath?: string[][]
    displayMath?: string[][]
    processEscapes?: boolean
    processEnvironments?: boolean
    packages?: string[]
  }
  options?: {
    skipHtmlTags?: string[]
    ignoreHtmlClass?: string
  }
  svg?: {
    fontCache?: string
  }
  startup?: {
    typeset?: boolean
    ready?: () => void
  }
  typeset?: (elements: HTMLElement[]) => void
  typesetPromise?: (elements: HTMLElement[]) => Promise<void>
}

declare global {
  interface Window {
    MathJax?: MathJaxConfig
    mathJaxReady?: boolean
  }
}
