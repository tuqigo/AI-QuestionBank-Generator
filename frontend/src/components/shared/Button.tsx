import './Button.css'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
  children: React.ReactNode
}

/**
 * 通用按钮组件
 */
export default function Button({
  variant = 'primary',
  size = 'medium',
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  const variantClass = `btn-${variant}`
  const sizeClass = `btn-${size}`
  const fullWidthClass = fullWidth ? 'btn-full-width' : ''
  const loadingClass = loading ? 'btn-loading' : ''

  return (
    <button
      className={`btn ${variantClass} ${sizeClass} ${fullWidthClass} ${loadingClass} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className="btn-spinner"></span>}
      {leftIcon && <span className="btn-icon-left">{leftIcon}</span>}
      <span className="btn-content">{children}</span>
      {rightIcon && <span className="btn-icon-right">{rightIcon}</span>}
    </button>
  )
}
