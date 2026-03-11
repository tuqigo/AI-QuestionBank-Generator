import { useEffect, useState } from 'react'

interface ProgressModalProps {
  isOpen: boolean
  stage: 'preparing' | 'connecting' | 'generating' | 'processing' | 'complete'
}

const STAGES = {
  preparing: { label: '准备中', progress: 10 },
  connecting: { label: '连接 AI', progress: 30 },
  generating: { label: '生成中', progress: 70 },
  processing: { label: '整理中', progress: 90 },
  complete: { label: '完成', progress: 100 },
}

const TIME_HINTS = {
  preparing: '即将开始...',
  connecting: '正在连接通义千问 API',
  generating: 'AI 正在思考题目，预计需要 10-30 秒',
  processing: '正在整理题目格式',
  complete: '生成成功！',
}

export default function ProgressModal({ isOpen, stage }: ProgressModalProps) {
  const [displayProgress, setDisplayProgress] = useState(0)
  const [timeHint, setTimeHint] = useState('')

  useEffect(() => {
    if (!isOpen) {
      setDisplayProgress(0)
      return
    }

    const targetProgress = STAGES[stage].progress
    setTimeHint(TIME_HINTS[stage])

    // 平滑过渡进度
    const duration = 500
    const startTime = Date.now()
    const startProgress = displayProgress

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // 使用 ease-out 缓动
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = startProgress + (targetProgress - startProgress) * eased

      setDisplayProgress(current)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [stage, isOpen])

  if (!isOpen) return null

  return (
    <div className="progress-modal-overlay">
      <div className="progress-modal">
        <div className="progress-title">
          {stage === 'complete' ? '生成成功！' : '正在生成题目'}
        </div>
        <div className="progress-subtitle">
          {stage === 'complete'
            ? '即将为您展示题目预览'
            : '请稍候，AI 正在为您定制专属练习题'}
        </div>

        {/* 进度条 */}
        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${displayProgress}%` }}
          />
        </div>

        {/* 阶段指示器 */}
        <div className="progress-steps">
          {Object.entries(STAGES).map(([key, { label }]) => {
            const stageOrder = ['preparing', 'connecting', 'generating', 'processing', 'complete']
            const currentIndex = stageOrder.indexOf(stage)
            const thisIndex = stageOrder.indexOf(key as keyof typeof STAGES)

            let className = 'progress-step'
            if (thisIndex < currentIndex) {
              className += ' completed'
            } else if (thisIndex === currentIndex) {
              className += ' active'
            }

            return (
              <div key={key} className={className}>
                <div className="progress-step-icon">
                  {thisIndex < currentIndex ? (
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                      {key === 'preparing' && (
                        <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      )}
                      {key === 'connecting' && (
                        <path d="M12 2V4M12 20V22M2 12H4M20 12H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      )}
                      {key === 'generating' && (
                        <path d="M12 2L15 8L21 9L17 14L18 20L12 17L6 20L7 14L3 9L9 8L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      )}
                      {key === 'processing' && (
                        <path d="M9 11L12 14L15 11M12 2V4M12 20V22M2 12H4M20 12H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      )}
                      {key === 'complete' && (
                        <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      )}
                    </svg>
                  )}
                </div>
                <span className="progress-step-label">{label}</span>
              </div>
            )
          })}
        </div>

        {/* 时间提示 */}
        <div className="progress-time-hint">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
            <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          {timeHint}
        </div>
      </div>
    </div>
  )
}
