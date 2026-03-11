import React, { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation, useNavigate, Outlet } from 'react-router-dom'
import { getAdminToken, clearAdminToken } from './auth'
import { getAdminMe } from './services/api'
import LoginPage from './pages/LoginPage'
import UsersPage from './pages/UsersPage'
import UserDetailPage from './pages/UserDetailPage'
import OperationLogsPage from './pages/OperationLogsPage'
import AiRecordsPage from './pages/AiRecordsPage'
import AiRecordDetailPage from './pages/AiRecordDetailPage'
import UserRecordDetailPage from './pages/UserRecordDetailPage'
import './App.css'

// 受保护的路由组件
function ProtectedRoute() {
  const navigate = useNavigate()
  const [isChecking, setIsChecking] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      const token = getAdminToken()
      if (!token) {
        navigate('/admin/login')
        return
      }

      try {
        await getAdminMe()
        setIsAuthenticated(true)
      } catch {
        clearAdminToken()
        navigate('/admin/login')
        return
      } finally {
        setIsChecking(false)
      }
    }

    checkAuth()
  }, [navigate])

  if (isChecking) {
    return (
      <div className="admin-loading">
        <div className="admin-loading-spinner"></div>
        <p>验证中...</p>
      </div>
    )
  }

  return isAuthenticated ? <Outlet /> : null
}

// 管理后台布局
function AdminLayout() {
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAdminToken()
    navigate('/admin/login')
  }

  const isActive = (path: string) => {
    return location.pathname.startsWith(path)
  }

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-logo">
          <h2>好学生 AI 题库</h2>
          <span>管理后台</span>
        </div>
        <nav className="admin-nav">
          <a
            href="/admin/users"
            className={isActive('/admin/users') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); navigate('/admin/users') }}
          >
            <span className="nav-icon">👥</span>
            用户管理
          </a>
          <a
            href="/admin/ai-records"
            className={isActive('/admin/ai-records') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); navigate('/admin/ai-records') }}
          >
            <span className="nav-icon">📝</span>
            AI 生成记录
          </a>
          <a
            href="/admin/logs"
            className={isActive('/admin/logs') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); navigate('/admin/logs') }}
          >
            <span className="nav-icon">📋</span>
            操作日志
          </a>
        </nav>
        <div className="admin-logout">
          <button onClick={handleLogout}>
            <span className="nav-icon">🚪</span>
            退出登录
          </button>
        </div>
      </aside>
      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  )
}

// 管理后台主应用
export default function AdminApp() {
  return (
    <Routes>
      {/* 登录页面 - 公开 */}
      <Route path="login" element={<LoginPage />} />

      {/* 需要认证的页面 */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AdminLayout />}>
          <Route path="" element={<Navigate to="users" replace />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="users/:id" element={<UserDetailPage />} />
          <Route path="ai-records" element={<AiRecordsPage />} />
          <Route path="ai-records/:id" element={<AiRecordDetailPage />} />
          <Route path="user-records/:id" element={<UserRecordDetailPage />} />
          <Route path="logs" element={<OperationLogsPage />} />
        </Route>
      </Route>
    </Routes>
  )
}
