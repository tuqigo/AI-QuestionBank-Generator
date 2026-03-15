import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect, useCallback } from 'react'
import { getToken, clearToken } from './core/auth/userAuth'
import { ToastContainer } from './components/shared'
import MainContent from './features/question-generator/MainContent'
import HistoryDetail from './features/history/HistoryDetail'
import SharePage from './features/history/SharePage'
import StructuredPreview from './features/question-generator/StructuredPreview'
import AdminApp from './admin/App'
import LandingPage from './features/landing/LandingPage'

const API_BASE = '/api'

function AppContent() {
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
          <p>题小宝</p>
          <div className="loading-spinner"></div>
        </div>
      </div>
    )
  }

  return (
    <Routes>
      {/* 管理后台 */}
      <Route path="/admin/*" element={<AdminApp />} />

      {/* 公开分享页面 - 无需登录 */}
      <Route path="/share/h/:id" element={<SharePage />} />

      {/* 【新增】首页 Landing Page - 公开访问 */}
      <Route path="/" element={<LandingPage />} />

      {/* 需要登录的页面 - 主内容 */}
      <Route path="/workbench" element={user ? <MainContent email={user} onLogout={handleLogout} fetchUser={fetchUser} /> : <Navigate to="/" />} />

      {/* 历史详情页 */}
      <Route path="/history/:id" element={user ? <HistoryDetail /> : <Navigate to="/" />} />

      {/* 【测试】结构化题目预览页 */}
      <Route path="/structured" element={user ? <StructuredPreview /> : <Navigate to="/" />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
      <ToastContainer position="top-center" duration={3000} maxToasts={3} />
    </BrowserRouter>
  )
}
