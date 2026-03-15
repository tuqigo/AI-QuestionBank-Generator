import { useState } from 'react'
import { Modal, Button } from '@/components/shared'
import './GradeSelectorModal.css'

interface GradeSelectorModalProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (grade: string) => Promise<void>
}

const PRIMARY_GRADES = [
  { value: 'grade1', label: '一年级' },
  { value: 'grade2', label: '二年级' },
  { value: 'grade3', label: '三年级' },
  { value: 'grade4', label: '四年级' },
  { value: 'grade5', label: '五年级' },
  { value: 'grade6', label: '六年级' },
]

const JUNIOR_GRADES = [
  { value: 'grade7', label: '初一' },
  { value: 'grade8', label: '初二' },
  { value: 'grade9', label: '初三' },
]

export default function GradeSelectorModal({ isOpen, onClose, onSelect }: GradeSelectorModalProps) {
  const [loading, setLoading] = useState(false)

  const handleSelect = async (grade: string) => {
    setLoading(true)
    try {
      await onSelect(grade)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="请选择年级" size="medium">
      <p className="grade-hint">便于我们为您提供更好的服务</p>
      <div className="grade-selector">
        <div className="grade-section">
          <h3 className="grade-section-title">小学</h3>
          <div className="grade-grid">
            {PRIMARY_GRADES.map((g) => (
              <Button
                key={g.value}
                variant="secondary"
                disabled={loading}
                onClick={() => handleSelect(g.value)}
                className="grade-btn"
              >
                {g.label}
              </Button>
            ))}
          </div>
        </div>

        <div className="grade-section">
          <h3 className="grade-section-title">初中</h3>
          <div className="grade-grid">
            {JUNIOR_GRADES.map((g) => (
              <Button
                key={g.value}
                variant="secondary"
                disabled={loading}
                onClick={() => handleSelect(g.value)}
                className="grade-btn"
              >
                {g.label}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {loading && (
        <div className="grade-loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}
    </Modal>
  )
}
