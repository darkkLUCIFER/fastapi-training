import { useState, useEffect, useCallback } from 'react';
import { permissions, rolePermissions } from '../api';
import AdminLayout from './AdminLayout';

const ROLES = ['admin', 'user'];

function roleValue(role) {
  return role && typeof role === 'object' ? role.value : role;
}

const emptyDraft = { role: 'admin', permissionId: '', access: true };

export default function AdminRolePermissions({ onBack }) {
  const [rolePermissionList, setRolePermissionList] = useState([]);
  const [permissionList, setPermissionList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [success, setSuccess] = useState('');
  const [draft, setDraft] = useState(emptyDraft);
  const [submitting, setSubmitting] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editDraft, setEditDraft] = useState(emptyDraft);
  const [detail, setDetail] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [rowError, setRowError] = useState('');

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await rolePermissions.list();
      setRolePermissionList(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const bootstrap = async () => {
      try {
        const data = await permissions.list();
        if (!cancelled) setPermissionList(Array.isArray(data) ? data : []);
      } catch {
        if (!cancelled) setPermissionList([]);
      }
    };
    bootstrap();
    load();
    return () => {
      cancelled = true;
    };
  }, [load]);

  const permissionKeyById = permissionList.reduce((acc, item) => {
    acc[item.id] = item.key;
    return acc;
  }, {});

  // Every action starts from a clean slate, so a stale message from a previous
  // action never sits next to a fresh result.
  const clearFeedback = () => {
    setFormError('');
    setRowError('');
    setSuccess('');
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    clearFeedback();
    if (!draft.permissionId) {
      setFormError('Pick a permission first.');
      return;
    }
    setSubmitting(true);
    try {
      await rolePermissions.create({
        role: draft.role,
        permission_id: draft.permissionId,
        access: draft.access,
      });
      setSuccess(`Granted "${draft.permissionId}" to "${draft.role}".`);
      setDraft(emptyDraft);
      await load();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const startEdit = (row) => {
    clearFeedback();
    setDetail(null);
    setEditingId(row.id);
    setEditDraft({
      role: roleValue(row.role),
      permissionId: String(row.permission_id),
      access: Boolean(row.access),
    });
  };

  const handleUpdate = async (id) => {
    clearFeedback();
    setSubmitting(true);
    try {
      await rolePermissions.update(id, {
        id,
        role: editDraft.role,
        permission_id: Number(editDraft.permissionId),
        access: editDraft.access,
      });
      setEditingId(null);
      setSuccess(`Role permission #${id} updated.`);
      await load();
    } catch (err) {
      setRowError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleAccess = async (row) => {
    clearFeedback();
    setBusyId(row.id);
    try {
      await rolePermissions.update(row.id, {
        id: row.id,
        role: roleValue(row.role),
        permission_id: row.permission_id,
        access: !row.access,
      });
      await load();
    } catch (err) {
      setRowError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  const handleDetail = async (row) => {
    clearFeedback();
    setDetail(null);
    setEditingId(null);
    setBusyId(row.id);
    try {
      setDetail(await rolePermissions.detail(row.id));
    } catch (err) {
      setRowError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (row) => {
    clearFeedback();
    setDetail(null);
    setBusyId(row.id);
    try {
      await rolePermissions.remove(row.id);
      if (editingId === row.id) setEditingId(null);
      setSuccess(`Role permission #${row.id} removed.`);
      await load();
    } catch (err) {
      setRowError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <AdminLayout
      onBack={onBack}
      title="Role Permissions"
      subtitle="Control which permissions each role is allowed to use."
    >
      {error && <div className="error">{error}</div>}

      <section className="add-todo-card">
        <p className="card-label">Grant permission to role</p>
        <form className="add-todo admin-form" onSubmit={handleCreate}>
          {formError && <div className="error">{formError}</div>}
          {success && <div className="success">{success}</div>}
          <div className="form-row">
            <select
              value={draft.role}
              onChange={(e) => setDraft({ ...draft, role: e.target.value })}
              aria-label="Role"
            >
              {ROLES.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
            <select
              value={draft.permissionId}
              onChange={(e) => setDraft({ ...draft, permissionId: e.target.value })}
              aria-label="Permission"
            >
              <option value="">Select a permission</option>
              {permissionList.map((permission) => (
                <option key={permission.id} value={permission.key}>
                  {permission.key}
                </option>
              ))}
            </select>
            <label className="admin-access">
              <input
                type="checkbox"
                checked={draft.access}
                onChange={(e) => setDraft({ ...draft, access: e.target.checked })}
              />
              access
            </label>
          </div>
          <button type="submit" className="btn-add" disabled={submitting || permissionList.length === 0}>
            {submitting ? 'Saving...' : 'Grant permission'}
          </button>
        </form>
      </section>

      {rowError && <div className="error">{rowError}</div>}

      {detail && (
        <section className="add-todo-card">
          <p className="card-label">Role permission #{detail.id}</p>
          <ul className="admin-list">
            <li className="admin-list-item">
              <span className="admin-key">role</span>
              <span>{roleValue(detail.role)}</span>
            </li>
            <li className="admin-list-item">
              <span className="admin-key">access</span>
              <span className={`admin-status ${detail.access ? 'active' : 'inactive'}`}>
                {detail.access ? 'granted' : 'revoked'}
              </span>
            </li>
            {detail.permission && (
              <li className="admin-list-item">
                <span className="admin-key">permission</span>
                <span>{detail.permission.key}</span>
              </li>
            )}
          </ul>
          <button className="btn-admin-back" onClick={() => setDetail(null)}>
            Close detail
          </button>
        </section>
      )}

      <section className="add-todo-card">
        <p className="card-label">All role permissions</p>
        {loading ? (
          <p className="loading">Loading role permissions...</p>
        ) : rolePermissionList.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🛡️</div>
            <p>No role permissions found</p>
          </div>
        ) : (
          <ul className="admin-list">
            {rolePermissionList.map((row) =>
              editingId === row.id ? (
                <li key={row.id} className="admin-list-item admin-list-item-edit">
                  <span className="admin-key">#{row.id}</span>
                  <div className="admin-row-controls">
                    <select
                      value={editDraft.role}
                      onChange={(e) => setEditDraft({ ...editDraft, role: e.target.value })}
                      aria-label="Role"
                    >
                      {ROLES.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                    <select
                      value={editDraft.permissionId}
                      onChange={(e) => setEditDraft({ ...editDraft, permissionId: e.target.value })}
                      aria-label="Permission"
                    >
                      {permissionList.map((permission) => (
                        <option key={permission.id} value={permission.id}>
                          {permission.key}
                        </option>
                      ))}
                    </select>
                    <label className="admin-access">
                      <input
                        type="checkbox"
                        checked={editDraft.access}
                        onChange={(e) => setEditDraft({ ...editDraft, access: e.target.checked })}
                      />
                      access
                    </label>
                    <button onClick={() => handleUpdate(row.id)} disabled={submitting}>
                      Save
                    </button>
                    <button onClick={() => setEditingId(null)} disabled={submitting}>
                      Cancel
                    </button>
                  </div>
                </li>
              ) : (
                <li key={row.id} className="admin-list-item">
                  <span className="admin-key admin-key-role">
                    {roleValue(row.role)} &middot; {permissionKeyById[row.permission_id] || `permission #${row.permission_id}`}
                  </span>
                  <span className="admin-row-actions">
                    <span className={`admin-status ${row.access ? 'active' : 'inactive'}`}>
                      {row.access ? 'granted' : 'revoked'}
                    </span>
                    <button onClick={() => handleToggleAccess(row)} disabled={busyId === row.id}>
                      {row.access ? 'Revoke' : 'Grant'}
                    </button>
                    <button onClick={() => handleDetail(row)} disabled={busyId === row.id}>
                      Detail
                    </button>
                    <button onClick={() => startEdit(row)} disabled={busyId === row.id}>
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(row)}
                      disabled={busyId === row.id}
                      className="btn-delete"
                    >
                      Delete
                    </button>
                  </span>
                </li>
              ),
            )}
          </ul>
        )}
      </section>
    </AdminLayout>
  );
}
