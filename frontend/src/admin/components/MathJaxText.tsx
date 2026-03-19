import React, { useEffect, useRef } from 'react'

interface MathJaxTextProps {
  text: string
  className?: string
  style?: React.CSSProperties
}

/**
 * 支持 LaTeX 数学公式渲染的文本组件
 * 自动识别并渲染 $...$ 和 $$...$$ 公式
 *
 * 注意：MathJax 需要原始的 LaTeX 文本在 DOM 中，它会查找并渲染这些公式
 */
export const MathJaxText: React.FC<MathJaxTextProps> = ({ text, className = '', style }) => {
  const containerRef = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (!containerRef.current || !window.MathJax) {
      return
    }

    const element = containerRef.current

    // 使用 requestAnimationFrame 确保 DOM 已更新
    requestAnimationFrame(() => {
      if (window.MathJax?.typesetPromise) {
        window.MathJax.typesetPromise([element]).catch((err) => {
          console.error('[MathJax] 渲染失败:', err)
        })
      } else if (window.MathJax?.typeset) {
        window.MathJax.typeset([element])
      }
    })
  }, [text])

  return (
    <span
      ref={containerRef}
      className={className}
      style={style}
    >
      {text}
    </span>
  )
}
