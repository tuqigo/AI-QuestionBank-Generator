import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminLogin, getAdminMe } from '../services/api'
import { getAdminToken, setAdminToken } from '../auth'
import './LoginPage.css'

export default function AdminLoginPage() {
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    // 如果已登录，跳转到首页
    const token = getAdminToken()
    if (token) {
      navigate('/admin/users')
    }
  }, [navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await adminLogin(password)
      setAdminToken(result.access_token)
      navigate('/admin/users')
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-login-page">
      <div className="admin-login-card">
        <div className="admin-login-header">
          <div className="admin-login-logo">📚</div>
          <h1>好学生 AI 题库</h1>
          <p>管理后台</p>
        </div>

        <form className="admin-login-form" onSubmit={handleSubmit}>
          <div className="admin-form-group">
            <label htmlFor="password">管理密码</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入管理密码"
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          {error && <div className="admin-form-error">{error}</div>}

          <button
            type="submit"
            className="admin-login-btn"
            disabled={loading || !password}
          >
            {loading ? (
              <>
                <span className="admin-login-spinner"></span>
                登录中...
              </>
            ) : (
              '登录'
            )}
          </button>
        </form>

        <div className="admin-login-footer">
          <p> Powered by 题小宝</p>
        </div>
      </div>
    </div>
  )
}
