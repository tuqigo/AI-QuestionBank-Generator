/**
 * Admin 认证工具
 * 管理管理员 Token 的存储和读取
 */

const ADMIN_TOKEN_KEY = 'admin_token'

/**
 * 获取管理员 Token
 */
export function getAdminToken(): string | null {
  return localStorage.getItem(ADMIN_TOKEN_KEY)
}

/**
 * 设置管理员 Token
 */
export function setAdminToken(token: string): void {
  localStorage.setItem(ADMIN_TOKEN_KEY, token)
}

/**
 * 清除管理员 Token
 */
export function clearAdminToken(): void {
  localStorage.removeItem(ADMIN_TOKEN_KEY)
}

/**
 * 带认证的 fetch 封装
 */
export async function fetchWithAdminAuth(
  url: string,
  options?: RequestInit
): Promise<Response> {
  const token = getAdminToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  // Token 过期或无效时清除
  if (response.status === 401) {
    clearAdminToken()
    window.location.href = '/admin/login'
  }

  return response
}
