import { useState, useEffect } from 'react'
import { Modal, Button } from '@/components/shared'
import { getConfigs, type ConfigOption } from '@/api/config'
import './GradeSelectorModal.css'

interface GradeSelectorModalProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (grade: string) => Promise<void>
}

export default function GradeSelectorModal({ isOpen, onClose, onSelect }: GradeSelectorModalProps) {
  const [loading, setLoading] = useState(false)
  const [grades, setGrades] = useState<ConfigOption[]>([])

  useEffect(() => {
    if (isOpen) {
      loadGrades()
    }
  }, [isOpen])

  const loadGrades = async () => {
    try {
      const configs = await getConfigs()
      setGrades(configs.grades)
    } catch (error) {
      console.error('加载年级列表失败:', error)
    }
  }

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
            {grades.filter(g => ['grade1', 'grade2', 'grade3', 'grade4', 'grade5', 'grade6'].includes(g.value)).map((g) => (
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
            {grades.filter(g => ['grade7', 'grade8', 'grade9'].includes(g.value)).map((g) => (
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
