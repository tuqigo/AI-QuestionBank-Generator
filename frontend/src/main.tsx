import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// PWA Service Worker 更新提示
// 注意：vite-plugin-pwa 会自动注册 Service Worker，这里只处理更新提示
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // 监听 Service Worker 更新
    navigator.serviceWorker.addEventListener('message', event => {
      if (event.data && event.data.type === 'WAITING') {
        // 有新版本可用，提示用户刷新
        if (confirm('有新版本可用，是否刷新页面？')) {
          window.location.reload()
        }
      }
    })
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
