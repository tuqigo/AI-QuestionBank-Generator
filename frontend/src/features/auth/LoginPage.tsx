import { useState, useEffect, useRef } from 'react'
import { toast } from '@/hooks'
import { setToken, getToken } from '@/core/auth/userAuth'
import GradeSelectorModal from '@/components/GradeSelectorModal'
import './LoginPage.css'

const API_BASE = '/api'

type Page = 'login' | 'register' | 'forgot'

interface Props {
  onSuccess: () => void
}

export default function LoginPage({ onSuccess }: Props) {
  const [page, setPage] = useState<Page>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [sendingOtp, setSendingOtp] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [otpSent, setOtpSent] = useState(false) // 验证码是否已发送
  const [showGradeSelector, setShowGradeSelector] = useState(false)
  const timerRef = useRef<number | null>(null)

  // 倒计时逻辑
  useEffect(() => {
    if (countdown > 0) {
      timerRef.current = window.setTimeout(() => {
        setCountdown(countdown - 1)
      }, 1000)
    }
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [countdown])

  // 验证邮箱格式
  const isValidEmail = (email: string) => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return pattern.test(email)
  }

  // 验证密码强度
  const isValidPassword = (pwd: string) => {
    return pwd.length >= 6 && pwd.length <= 32
  }

  // 发送验证码
  const sendOtp = async () => {
    setError('')
    const e = email.trim().toLowerCase()
    if (!e) {
      setError('请输入邮箱')
      return
    }
    if (!isValidEmail(e)) {
      setError('邮箱格式无效')
      return
    }

    setSendingOtp(true)
    try {
      const res = await fetch(`${API_BASE}/auth/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: e,
          purpose: page === 'register' ? 'register' : 'reset_password'
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error((data as { detail?: string }).detail || '发送失败')
      }
      setCountdown(60) // 60 秒倒计时
      setOtpSent(true) // 标记验证码已发送
      toast.success('验证码已发送，请检查邮箱')
    } catch (e) {
      setError(e instanceof Error ? e.message : '发送失败')
    } finally {
      setSendingOtp(false)
    }
  }

  // 提交处理
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    const emailVal = email.trim().toLowerCase()
    const passwordVal = password
    const codeVal = code.trim()

    // 登录页面验证
    if (page === 'login') {
      if (!emailVal || !passwordVal) {
        setError('请输入邮箱和密码')
        return
      }
      if (!isValidEmail(emailVal)) {
        setError('邮箱格式无效')
        return
      }
      if (!isValidPassword(passwordVal)) {
        setError('密码至少 6 个字符')
        return
      }
    }

    // 注册页面验证
    if (page === 'register') {
      if (!emailVal || !passwordVal || !codeVal) {
        setError('请输入邮箱、密码和验证码')
        return
      }
      if (!isValidEmail(emailVal)) {
        setError('邮箱格式无效')
        return
      }
      if (!isValidPassword(passwordVal)) {
        setError('密码至少 6 个字符')
        return
      }
      if (codeVal.length !== 6 || !/^\d+$/.test(codeVal)) {
        setError('验证码为 6 位数字')
        return
      }
      if (!otpSent) {
        setError('请先获取验证码')
        return
      }
    }

    // 找回密码页面验证
    if (page === 'forgot') {
      if (!emailVal || !codeVal || !passwordVal) {
        setError('请输入邮箱、验证码和新密码')
        return
      }
      if (!isValidEmail(emailVal)) {
        setError('邮箱格式无效')
        return
      }
      if (codeVal.length !== 6 || !/^\d+$/.test(codeVal)) {
        setError('验证码为 6 位数字')
        return
      }
      if (!isValidPassword(passwordVal)) {
        setError('密码至少 6 个字符')
        return
      }
      if (!otpSent) {
        setError('请先获取验证码')
        return
      }
    }

    setLoading(true)
    try {
      let endpoint = ''
      let body: any = {}

      if (page === 'login') {
        endpoint = '/auth/login'
        body = { email: emailVal, password: passwordVal }
      } else if (page === 'register') {
        endpoint = '/auth/register'
        body = { email: emailVal, password: passwordVal, code: codeVal }
      } else if (page === 'forgot') {
        endpoint = '/auth/reset-password'
        body = { email: emailVal, code: codeVal, new_password: passwordVal }
      }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error((data as { detail?: string }).detail || '操作失败')
      }

      // 登录和注册成功后设置 token
      if (page === 'login' || page === 'register') {
        setToken((data as { access_token: string }).access_token)
        if (page === 'login') {
          onSuccess()
        } else {
          // 注册成功，显示年级选择器
          setShowGradeSelector(true)
        }
      } else {
        // 找回密码成功，提示用户登录
        toast.success('密码重置成功，请登录')
        setPage('login')
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '操作失败')
    } finally {
      setLoading(false)
    }
  }

  // 切换页面时清空错误和验证码
  const switchPage = (newPage: Page) => {
    setPage(newPage)
    setError('')
    setCode('')
    setPassword('')
    setCountdown(0)
    setOtpSent(false) // 重置验证码发送状态
  }

  // 更新用户年级
  const updateGrade = async (grade: string) => {
    const token = getToken()
    if (!token) {
      throw new Error('未登录')
    }

    const res = await fetch(`${API_BASE}/users/grade`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ grade }),
    })

    const data = await res.json()
    if (!res.ok) {
      throw new Error((data as { detail?: string }).detail || '更新失败')
    }

    toast.success('年级设置成功')
    setShowGradeSelector(false)
    onSuccess()
  }

  return (
    <div className="login-page">
      {/* 装饰性背景元素 */}
      <div className="login-background">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>

      <div className="login-card">
        <div className="login-header">
          <div className="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3L1 9L12 15L21 9L12 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h1>题小宝</h1>
          <p className="subtitle">为学生、家长、老师生成各学科练习题</p>
        </div>

        <form onSubmit={submit} className="login-form">
          {/* 页面标题 */}
          <div className="form-title">
            {page === 'login' && '账号登录'}
            {page === 'register' && '注册账号'}
            {page === 'forgot' && '找回密码'}
          </div>

          <div className="form-group">
            <label htmlFor="email">邮箱</label>
            <div className="input-wrapper">
              <svg className="input-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 6L12 13L2 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <input
                id="email"
                type="email"
                placeholder="请输入邮箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                disabled={page === 'forgot' && countdown > 0}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">密码</label>
            <div className="input-wrapper">
              <svg className="input-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="12" cy="16" r="1" fill="currentColor"/>
                <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <input
                id="password"
                type="password"
                placeholder={page === 'forgot' ? '请输入新密码' : '请输入密码'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={page === 'login' ? 'current-password' : 'new-password'}
              />
            </div>
          </div>

          {/* 注册和找回密码页面显示验证码 */}
          {(page === 'register' || page === 'forgot') && (
            <div className="form-group">
              <label htmlFor="code">验证码</label>
              <div className="input-wrapper otp-input">
                <svg className="input-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="12" cy="16" r="1" fill="currentColor"/>
                  <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <input
                  id="code"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={6}
                  placeholder="6 位验证码"
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                />
                <button
                  type="button"
                  className="otp-btn"
                  onClick={sendOtp}
                  disabled={sendingOtp || countdown > 0 || !email}
                >
                  {sendingOtp ? (
                    <>
                      <span className="spinner spinner-sm"></span>
                      发送中
                    </>
                  ) : countdown > 0 ? (
                    `${countdown}s`
                  ) : (
                    '获取验证码'
                  )}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message" role="alert">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <circle cx="12" cy="16" r="1" fill="currentColor"/>
              </svg>
              {error}
            </div>
          )}

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                {page === 'login' ? '登录中...' : page === 'register' ? '注册中...' : '重置中...'}
              </>
            ) : (
              page === 'login' ? '登录' : page === 'register' ? '注册' : '重置密码'
            )}
          </button>

          {/* 注册页面提示 */}
          {page === 'register' && (
            <div className="login-tip">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="16" height="16">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 16V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <circle cx="12" cy="8" r="1" fill="currentColor"/>
              </svg>
              <span>首次注册需验证邮箱，验证码 5 分钟有效</span>
            </div>
          )}
        </form>

        <div className="login-footer">
          {page === 'login' ? (
            <>
              <p>
                还没有账号？{' '}
                <button type="button" onClick={() => switchPage('register')}>
                  立即注册
                </button>
              </p>
              <p className="forgot-link">
                <button type="button" onClick={() => switchPage('forgot')}>
                  忘记密码？
                </button>
              </p>
            </>
          ) : page === 'register' ? (
            <p>
              已有账号？{' '}
              <button type="button" onClick={() => switchPage('login')}>
                立即登录
              </button>
            </p>
          ) : (
            <p>
              返回{' '}
              <button type="button" onClick={() => switchPage('login')}>
                登录页面
              </button>
            </p>
          )}
        </div>
      </div>

      <GradeSelectorModal
        isOpen={showGradeSelector}
        onClose={() => setShowGradeSelector(false)}
        onSelect={updateGrade}
      />
    </div>
  )
}
