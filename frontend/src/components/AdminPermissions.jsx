import { useState, useEffect } from 'react';
import { permissions } from '../api';
import AdminLayout from './AdminLayout';

export default function AdminPermissions({ onBack }) {
  const [permissionList, setPermissionList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;
    const fetchPermissions = async () => {
      try {
        setLoading(true);
        setError('');
        const data = await permissions.list();
        if (!cancelled) setPermissionList(Array.isArray(data) ? data : []);
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

  const term = search.trim().toLowerCase();
  const visible = term
    ? permissionList.filter(
        (item) =>
          item.key?.toLowerCase().includes(term) || (item.description || '').toLowerCase().includes(term),
      )
    : permissionList;

  return (
    <AdminLayout
      onBack={onBack}
      title="Permissions"
      subtitle="Every permission key registered in the system."
    >
      {error && <div className="error">{error}</div>}

      <section className="add-todo-card">
        <p className="card-label">Search</p>
        <div className="add-todo">
          <input
            type="text"
            placeholder="Filter by key or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </section>

      <section className="add-todo-card">
        <p className="card-label">All permissions</p>
        {loading ? (
          <p className="loading">Loading permissions...</p>
        ) : visible.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔒</div>
            <p>{permissionList.length === 0 ? 'No permissions found' : 'No permission matches your search'}</p>
          </div>
        ) : (
          <ul className="admin-list">
            {visible.map((permission) => (
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
    </AdminLayout>
  );
}
