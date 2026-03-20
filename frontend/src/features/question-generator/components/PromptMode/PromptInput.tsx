// CSS is imported from MainContent.tsx

interface PromptInputProps {
  value: string
  onChange: (value: string) => void
  error?: string
}

export default function PromptInput({ value, onChange, error }: PromptInputProps) {
  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="例如：小学六年级数学 分数小数混合运算 15 道"
        rows={4}
        className="prompt-input"
      />
      {error && (
        <div className="error-message-inline" role="alert">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
            <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <circle cx="12" cy="16" r="1" fill="currentColor" />
          </svg>
          {error}
        </div>
      )}
    </div>
  )
}
