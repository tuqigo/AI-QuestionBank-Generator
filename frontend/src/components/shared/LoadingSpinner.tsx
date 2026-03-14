import './LoadingSpinner.css'

export interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  text?: string
  className?: string
}

/**
 * 加载动画组件
 */
export default function LoadingSpinner({
  size = 'medium',
  text,
  className
}: LoadingSpinnerProps) {
  const sizeClass = `spinner-${size}`

  return (
    <div className={`loading-spinner ${sizeClass} ${className || ''}`}>
      <div className="spinner-circle"></div>
      {text && <span className="spinner-text">{text}</span>}
    </div>
  )
}
