import HistoryDropdown from '@/features/history/HistoryList'
// CSS is imported from MainContent.tsx

interface HeaderProps {
  email: string
  onLogout: () => void
  fetchUser: () => void
  historyOpen: boolean
  onHistoryToggle: () => void
}

export default function Header({
  email,
  onLogout,
  fetchUser,
  historyOpen,
  onHistoryToggle
}: HeaderProps) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo-small">
            <img src="/icon64.svg" alt="logo" width="24" height="24" />
          </div>
          <h1>题小宝</h1>
        </div>
        <div className="header-right">
          <div
            className={`history-dropdown-wrapper ${historyOpen ? 'open' : ''}`}
          >
            <button
              className={`btn-history history-dropdown-trigger ${historyOpen ? 'active' : ''}`}
              onClick={onHistoryToggle}
              title="历史记录"
              aria-label="历史记录"
            >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>
            <HistoryDropdown isOpen={historyOpen} onClose={() => onHistoryToggle()} />
          </div>
          <div className="user-info">
            <div className="user-avatar">
              {email.charAt(0).toUpperCase()}
            </div>
            <span className="username">{email}</span>
          </div>
          <button type="button" className="btn-logout" onClick={onLogout} title="退出登录" aria-label="退出登录">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M16 17L21 12L16 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  )
}
