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

  // 小学：一年级 ~ 六年级 (grade1~grade6)
  // 初中：七年级 ~ 九年级 (grade7~grade9)
  const isPrimaryGrade = (value: string) => {
    const gradeNum = parseInt(value.replace('grade', ''))
    return gradeNum >= 1 && gradeNum <= 6
  }

  const isJuniorGrade = (value: string) => {
    const gradeNum = parseInt(value.replace('grade', ''))
    return gradeNum >= 7 && gradeNum <= 9
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="请选择年级" size="medium">
      <p className="grade-hint">便于我们为您提供更好的服务</p>
      <div className="grade-selector">
        <div className="grade-section">
          <h3 className="grade-section-title">小学</h3>
          <div className="grade-grid">
            {grades.filter(g => isPrimaryGrade(g.value)).map((g) => (
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
            {grades.filter(g => isJuniorGrade(g.value)).map((g) => (
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
