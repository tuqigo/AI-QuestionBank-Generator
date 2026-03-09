import { useState, useEffect, useCallback } from 'react'
import { getToken, clearToken } from './auth'
import LoginPage from './LoginPage'
import MainContent from './MainContent'

const API_BASE = '/api'

export default function App() {
  const [user, setUser] = useState<string | null>(null)
  const [checking, setChecking] = useState(true)

  const fetchUser = useCallback(() => {
    setChecking(true)
    const token = getToken()
    if (!token) {
      setUser(null)
      setChecking(false)
      return
    }
    return fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (res.ok) return res.json()
        clearToken()
        setUser(null)
      })
      .then((data) => {
        if (data?.email) setUser(data.email)
      })
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const handleLogout = () => {
    clearToken()
    setUser(null)
  }

  if (checking) {
    return (
      <div className="loading-page">
        <div className="loading-content">
          <div className="loading-logo">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3L1 9L12 15L21 9L12 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <p>好学生 AI 题库生成器</p>
          <div className="loading-spinner"></div>
        </div>
      </div>
    )
  }

  if (!user) {
    return <LoginPage onSuccess={fetchUser} />
  }

  return <MainContent email={user} onLogout={handleLogout} />
}
