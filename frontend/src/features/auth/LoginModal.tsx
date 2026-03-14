import { useState, useEffect, useRef } from 'react'
import { setToken } from '@/core/auth/userAuth'
import './LoginModal.css'

const API_BASE = '/api'

interface Props {
  onClose: () => void
  onSuccess: () => void
  mode?: 'register' | 'login'
}

export default function LoginModal({ onClose, onSuccess, mode: initialMode = 'register' }: Props) {
  const [mode, setMode] = useState<'register' | 'login'>(initialMode)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [sendingOtp, setSendingOtp] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const timerRef = useRef<number | null>(null)
  const modalRef = useRef<HTMLDivElement>(null)

  // 响应外部传入的 mode 变化
  useEffect(() => {
    setMode(initialMode)
  }, [initialMode])

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

  // 点击遮罩关闭
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onClose])

  // ESC 关闭
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    document.addEventListener('keydown', handleEsc)
    return () => document.removeEventListener('keydown', handleEsc)
  }, [onClose])

  // 验证邮箱格式
  const isValidEmail = (email: string) => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return pattern.test(email)
  }

  // 验证密码强度
  const isValidPassword = (pwd: string) => {
    if (pwd.length < 8 || pwd.length > 32) {
      return false
    }
    if (!/[A-Za-z]/.test(pwd) || !/\d/.test(pwd)) {
      return false
    }
    return true
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
          purpose: 'register'
        }),
      })
      let data: any
      const contentType = res.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        data = await res.json()
      } else {
        data = { detail: `服务器错误 (${res.status})` }
      }
      if (!res.ok) {
        throw new Error(data.detail || '发送失败')
      }
      setCountdown(60)
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

    if (mode === 'register') {
      if (!emailVal || !passwordVal || !codeVal) {
        setError('请输入邮箱、密码和验证码')
        return
      }
      if (!isValidEmail(emailVal)) {
        setError('邮箱格式无效')
        return
      }
      if (!isValidPassword(passwordVal)) {
        setError('密码至少 8 个字符，且必须包含字母和数字')
        return
      }
      if (codeVal.length !== 6 || !/^\d+$/.test(codeVal)) {
        setError('验证码为 6 位数字')
        return
      }

      setLoading(true)
      try {
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: emailVal, password: passwordVal, code: codeVal }),
        })
        let data: any
        const contentType = res.headers.get('content-type')
        if (contentType && contentType.includes('application/json')) {
          data = await res.json()
        } else {
          data = { detail: `服务器错误 (${res.status})` }
        }
        if (!res.ok) {
          throw new Error(data.detail || '注册失败')
        }
        setToken((data as { access_token: string }).access_token)
        onSuccess()
      } catch (e) {
        setError(e instanceof Error ? e.message : '注册失败')
      } finally {
        setLoading(false)
      }
    } else {
      // 登录模式
      if (!emailVal || !passwordVal) {
        setError('请输入邮箱和密码')
        return
      }
      if (!isValidEmail(emailVal)) {
        setError('邮箱格式无效')
        return
      }
      if (!isValidPassword(passwordVal)) {
        setError('密码至少 8 个字符，且必须包含字母和数字')
        return
      }

      setLoading(true)
      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: emailVal, password: passwordVal }),
        })
        let data: any
        const contentType = res.headers.get('content-type')
        if (contentType && contentType.includes('application/json')) {
          data = await res.json()
        } else {
          data = { detail: `服务器错误 (${res.status})` }
        }
        if (!res.ok) {
          throw new Error(data.detail || '登录失败')
        }
        setToken((data as { access_token: string }).access_token)
        onSuccess()
      } catch (e) {
        setError(e instanceof Error ? e.message : '登录失败')
      } finally {
        setLoading(false)
      }
    }
  }

  // 切换模式时清空错误和验证码
  const toggleMode = () => {
    setMode(mode === 'register' ? 'login' : 'register')
    setError('')
    setCode('')
    setPassword('')
    setCountdown(0)
  }

  return (
    <div className="login-modal-overlay">
      <div className="login-modal" ref={modalRef}>
        <button className="login-modal-close" onClick={onClose}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>

        <div className="login-modal-header">
          <div className="login-modal-logo">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3L1 9L12 15L21 9L12 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2>{mode === 'register' ? '注册账号' : '登录账号'}</h2>
          <p className="login-modal-hint">
            {mode === 'register' ? (
              <>
                已有账号？{' '}
                <button type="button" onClick={toggleMode}>登录</button>
              </>
            ) : (
              <>
                还没有账号？{' '}
                <button type="button" onClick={toggleMode}>注册</button>
              </>
            )}
          </p>
        </div>

        <form onSubmit={submit} className="login-modal-form">
          <div className="form-group">
            <label htmlFor="modal-email">邮箱</label>
            <input
              id="modal-email"
              type="email"
              placeholder="请输入邮箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={mode === 'login' && countdown > 0}
            />
          </div>

          <div className="form-group">
            <label htmlFor="modal-password">密码</label>
            <input
              id="modal-password"
              type="password"
              placeholder="请输入密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="modal-code">验证码</label>
              <div className="otp-input-wrapper">
                <input
                  id="modal-code"
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
                {mode === 'register' ? '注册中...' : '登录中...'}
              </>
            ) : (
              mode === 'register' ? '立即注册' : '立即登录'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
