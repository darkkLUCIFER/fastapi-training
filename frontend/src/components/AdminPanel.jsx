import { useState, useEffect } from 'react';
import { permissions } from '../api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const PERMISSION_KEYS = [
  'todo.list.view',
  'todo.create',
  'todo.detail.view',
  'todo.update',
  'todo.delete',
  'auth.token-refresh.view',
  'auth.me.view',
  'permission.list.view',
  'permission.create',
  'permission.update',
  'permission.delete',
];

export default function AdminPanel({ onBack }) {
  const { logout, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [permissionList, setPermissionList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [success, setSuccess] = useState('');
  const [role, setRole] = useState('admin');
  const [permissionKey, setPermissionKey] = useState(PERMISSION_KEYS[0]);
  const [access, setAccess] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const fetchPermissions = async () => {
      try {
        setLoading(true);
        setError('');
        const data = await permissions.list();
        if (!cancelled) setPermissionList(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchPermissions();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setFormError('');
    setSuccess('');
    setSubmitting(true);
    try {
      await permissions.create({
        role,
        permission_id: permissionKey,
        access,
      });
      setSuccess(`Permission "${permissionKey}" granted to "${role}".`);
      const data = await permissions.list();
      setPermissionList(data);
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

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

      {error && <div className="error">{error}</div>}

      <section className="add-todo-card">
        <p className="card-label">Grant permission to role</p>
        <form className="add-todo admin-form" onSubmit={handleCreate}>
          {formError && <div className="error">{formError}</div>}
          {success && <div className="success">{success}</div>}
          <div className="form-row">
            <select value={role} onChange={(e) => setRole(e.target.value)} aria-label="Role">
              <option value="admin">admin</option>
              <option value="user">user</option>
            </select>
            <select
              value={permissionKey}
              onChange={(e) => setPermissionKey(e.target.value)}
              aria-label="Permission"
            >
              {PERMISSION_KEYS.map((key) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
            </select>
            <label className="admin-access">
              <input
                type="checkbox"
                checked={access}
                onChange={(e) => setAccess(e.target.checked)}
              />
              access
            </label>
          </div>
          <button type="submit" className="btn-add" disabled={submitting}>
            {submitting ? 'Saving...' : 'Grant permission'}
          </button>
        </form>
      </section>

      <section className="add-todo-card">
        <p className="card-label">All permissions</p>
        {loading ? (
          <p className="loading">Loading permissions...</p>
        ) : permissionList.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔒</div>
            <p>No permissions found</p>
          </div>
        ) : (
          <ul className="admin-list">
            {permissionList.map((permission) => (
              <li key={permission.id} className="admin-list-item">
                <span className="admin-key">{permission.key}</span>
                <span className={`admin-status ${permission.is_active ? 'active' : 'inactive'}`}>
                  {permission.is_active ? 'active' : 'inactive'}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
