/**
 * 认证存储工厂 - 创建可复用的 token 管理逻辑
 */

export interface AuthStorage {
  getToken: () => string | null
  setToken: (token: string) => void
  clearToken: () => void
}

/**
 * 创建认证存储实例
 * @param key - localStorage 的 key
 */
export function createAuthStorage(key: string): AuthStorage {
  return {
    getToken: () => {
      try {
        return localStorage.getItem(key)
      } catch {
        // SSR 或 localStorage 不可用时返回 null
        return null
      }
    },
    setToken: (token: string) => {
      try {
        localStorage.setItem(key, token)
      } catch (e) {
        console.error('Failed to save token:', e)
      }
    },
    clearToken: () => {
      try {
        localStorage.removeItem(key)
      } catch (e) {
        console.error('Failed to clear token:', e)
      }
    },
  }
}

/**
 * 创建带认证的 fetch 封装
 * @param auth - AuthStorage 实例
 * @param timeout - 超时时间（毫秒），0 表示不设置超时
 * @param on401 - 401 响应时的回调
 */
export function createFetchWithAuth(
  auth: AuthStorage,
  timeout: number = 0,
  on401?: () => void
) {
  return async function fetchWithAuth(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const token = auth.getToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const controller = new AbortController()
    const timeoutId = timeout > 0 ? setTimeout(() => controller.abort(), timeout) : 0

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      })

      if (timeoutId) clearTimeout(timeoutId)

      // 401 未授权处理
      if (response.status === 401 && on401) {
        auth.clearToken()
        on401()
      }

      return response
    } catch (error) {
      if (timeoutId) clearTimeout(timeoutId)
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('请求超时，请稍后重试')
      }
      throw error
    }
  }
}
