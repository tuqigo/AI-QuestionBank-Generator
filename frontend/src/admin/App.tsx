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
import TemplatesPage from './pages/TemplatesPage'
import ConfigsPage from './pages/ConfigsPage'
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
  const [sidebarOpen, setSidebarOpen] = useState(() => window.innerWidth > 768)

  const handleLogout = () => {
    clearAdminToken()
    navigate('/admin/login')
  }

  const isActive = (path: string) => {
    return location.pathname.startsWith(path)
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  // 移动端点击菜单项后自动关闭侧边栏
  const handleNavClick = (path: string) => {
    if (window.innerWidth <= 768) {
      setSidebarOpen(false)
    }
    navigate(path)
  }

  // 监听窗口大小变化
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setSidebarOpen(true)
      } else {
        setSidebarOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className="admin-layout">
      {/* 侧边栏切换按钮 - 移动端显示 */}
      <button className="sidebar-toggle" onClick={toggleSidebar} title={sidebarOpen ? '收起侧边栏' : '展开侧边栏'}>
        {sidebarOpen ? '✕' : '☰'}
      </button>

      <aside className={`admin-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="admin-logo">
          <h2>好学生 AI 题库</h2>
          <span>管理后台</span>
        </div>
        <nav className="admin-nav">
          <a
            href="/admin/users"
            className={isActive('/admin/users') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); handleNavClick('/admin/users') }}
          >
            <span className="nav-icon">👥</span>
            用户管理
          </a>
          <a
            href="/admin/configs"
            className={isActive('/admin/configs') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); handleNavClick('/admin/configs') }}
          >
            <span className="nav-icon">⚙️</span>
            配置管理
          </a>
          <a
            href="/admin/templates"
            className={isActive('/admin/templates') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); handleNavClick('/admin/templates') }}
          >
            <span className="nav-icon">📝</span>
            模板管理
          </a>
          <a
            href="/admin/ai-records"
            className={isActive('/admin/ai-records') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); handleNavClick('/admin/ai-records') }}
          >
            <span className="nav-icon">📋</span>
            AI 生成记录
          </a>
          <a
            href="/admin/logs"
            className={isActive('/admin/logs') ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); handleNavClick('/admin/logs') }}
          >
            <span className="nav-icon">📜</span>
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
          <Route path="configs" element={<ConfigsPage />} />
          <Route path="templates" element={<TemplatesPage />} />
          <Route path="ai-records" element={<AiRecordsPage />} />
          <Route path="ai-records/:id" element={<AiRecordDetailPage />} />
          <Route path="user-records/:id" element={<UserRecordDetailPage />} />
          <Route path="logs" element={<OperationLogsPage />} />
        </Route>
      </Route>
    </Routes>
  )
}
