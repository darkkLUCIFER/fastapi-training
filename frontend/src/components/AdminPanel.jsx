import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const ADMIN_SECTIONS = [
  {
    key: 'permissions',
    title: 'Permissions',
    description: 'Every permission key registered in the system and whether it is active.',
    icon: '🔑',
    onOpen: 'onOpenPermissions',
  },
  {
    key: 'role-permissions',
    title: 'Role Permissions',
    description: 'Grant, edit and revoke the permissions each role is allowed to use.',
    icon: '🛡️',
    onOpen: 'onOpenRolePermissions',
  },
];

export default function AdminPanel({ onBack, onOpenPermissions, onOpenRolePermissions }) {
  const { logout, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const handlers = { onOpenPermissions, onOpenRolePermissions };

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
        <h1>Admin Panel</h1>
      </header>

      <section className="admin-nav-grid">
        {ADMIN_SECTIONS.map((section) => (
          <button
            key={section.key}
            type="button"
            className="admin-nav-card"
            onClick={handlers[section.onOpen]}
          >
            <span className="admin-nav-icon">{section.icon}</span>
            <span className="admin-nav-body">
              <span className="admin-nav-title">{section.title}</span>
              <span className="admin-nav-desc">{section.description}</span>
            </span>
            <span className="admin-nav-go" aria-hidden="true">
              →
            </span>
          </button>
        ))}
      </section>
    </div>
  );
}
