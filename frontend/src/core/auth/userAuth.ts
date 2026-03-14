import { createAuthStorage, createFetchWithAuth } from './authFactory'

const TOKEN_KEY = 'qbank_token'
const REQUEST_TIMEOUT = 120 * 1000

// 用户认证存储
const auth = createAuthStorage(TOKEN_KEY)

export const getToken = auth.getToken
export const setToken = auth.setToken
export const clearToken = auth.clearToken

// 带超时的 fetch 封装
export const fetchWithAuth = createFetchWithAuth(
  auth,
  REQUEST_TIMEOUT
)
