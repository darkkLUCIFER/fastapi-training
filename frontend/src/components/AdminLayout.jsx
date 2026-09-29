import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export default function AdminLayout({ onBack, title, subtitle, children }) {
  const { logout, user } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="todo-app admin-panel">
      <div className="admin-topbar">
        <button className="btn-admin-back" onClick={onBack}>
          ← Back
        </button>
        <div className="header-actions">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
          <div className="user-info">
            <div className="user-avatar">{user?.username?.charAt(0)}</div>
            <span>{user?.username}</span>
            <button className="btn-logout" onClick={logout}>
              Logout
            </button>
          </div>
        </div>
      </div>

      <header>
        <h1>{title}</h1>
        {subtitle && <p className="admin-subtitle">{subtitle}</p>}
      </header>

      {children}
    </div>
  );
}
