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

// html2canvas 类型定义
export interface Html2CanvasOptions {
  scale?: number
  useCORS?: boolean
  letterRendering?: boolean
  allowTaint?: boolean
  logging?: boolean
  backgroundColor?: string
}

export interface Html2Canvas {
  (element: HTMLElement, options?: Html2CanvasOptions): Promise<HTMLCanvasElement>
}

// jsPDF 类型定义
export interface JsPDF {
  addImage: (imageData: string, format: string, x: number, y: number, width: number, height: number, alias?: string, compression?: string) => void
  addPage: () => void
  save: (filename: string) => void
}

export interface JsPDFConstructor {
  jsPDF: new (options: { unit: string; format: string; orientation: 'portrait' | 'landscape' }) => JsPDF
}

// html2pdf.js 类型定义
export interface Html2PdfOptions {
  margin?: number | number[]
  filename?: string
  image?: { type: string; quality: number }
  html2canvas?: Html2CanvasOptions
  jsPDF?: {
    unit: string
    format: string
    orientation: 'portrait' | 'landscape'
    compress: boolean
  }
  pagebreak?: { mode: string[] }
}

export interface Html2Pdf {
  (): {
    set: (options: Html2PdfOptions) => {
      from: (element: HTMLElement) => {
        save: () => Promise<void>
        toPdf: () => { save: () => Promise<void> }
      }
    }
  }
}

declare global {
  interface Window {
    MathJax?: MathJaxConfig
    mathJaxReady?: boolean
    html2pdf?: Html2Pdf
    html2canvas?: Html2Canvas
    jspdf?: JsPDFConstructor
  }
}
