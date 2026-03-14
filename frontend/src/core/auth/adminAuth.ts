import { createAuthStorage, createFetchWithAuth } from './authFactory'

const ADMIN_TOKEN_KEY = 'admin_token'

// 管理员认证存储
const auth = createAuthStorage(ADMIN_TOKEN_KEY)

export const getAdminToken = auth.getToken
export const setAdminToken = auth.setToken
export const clearAdminToken = auth.clearToken

export function isAdminLoggedIn(): boolean {
  return !!getAdminToken()
}

// 带 401 处理的 fetch 封装
export const fetchWithAdminAuth = createFetchWithAuth(
  auth,
  0, // 不设置超时
  () => {
    window.location.href = '/admin/login'
  }
)
