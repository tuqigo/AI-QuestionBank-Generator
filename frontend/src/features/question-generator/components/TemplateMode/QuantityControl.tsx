// CSS is imported from MainContent.tsx

interface QuantityControlProps {
  quantity: number
  onChange: (quantity: number) => void
  variant?: 'inline' | 'mobile'
}

export default function QuantityControl({
  quantity,
  onChange,
  variant = 'inline'
}: QuantityControlProps) {
  const wrapperClass = variant === 'inline'
    ? 'quantity-control-inline'
    : 'quantity-control-mobile'
  const buttonClass = variant === 'inline'
    ? 'quantity-btn-inline'
    : 'quantity-btn-mobile'
  const valueClass = variant === 'inline'
    ? 'quantity-value-inline'
    : 'quantity-value-mobile'

  return (
    <div className={wrapperClass}>
      <button
        type="button"
        className={buttonClass}
        onClick={() => onChange(Math.max(5, quantity - 5))}
      >
        -
      </button>
      <span className={valueClass}>{quantity} 道</span>
      <button
        type="button"
        className={buttonClass}
        onClick={() => onChange(Math.min(100, quantity + 5))}
      >
        +
      </button>
    </div>
  )
}
