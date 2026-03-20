// CSS is imported from MainContent.tsx

interface ModeTabsProps {
  mode: 'prompt' | 'template'
  onModeChange: (mode: 'prompt' | 'template') => void
}

export default function ModeTabs({ mode, onModeChange }: ModeTabsProps) {
  return (
    <div className="mode-tabs">
      <button
        type="button"
        className={`mode-tab ${mode === 'template' ? 'active' : ''}`}
        onClick={() => {
          onModeChange('template')
        }}
      >
        模板出题
      </button>
      <button
        type="button"
        className={`mode-tab ${mode === 'prompt' ? 'active' : ''}`}
        onClick={() => {
          onModeChange('prompt')
        }}
      >
        提示词出题
      </button>
    </div>
  )
}
