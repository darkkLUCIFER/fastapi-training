import { useState } from 'react';

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function TodoItem({ todo, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(todo.title);
  const [description, setDescription] = useState(todo.description || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleToggle = async () => {
    setError('');
    setLoading(true);
    try {
      await onUpdate(todo.id, { completed: !todo.completed });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setError('');
    setLoading(true);
    try {
      await onUpdate(todo.id, {
        title,
        description: description || null,
      });
      setEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setTitle(todo.title);
    setDescription(todo.description || '');
    setEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    }
    if (e.key === 'Escape') {
      handleCancel();
    }
  };

  const handleDelete = async () => {
    setError('');
    setLoading(true);
    try {
      await onDelete(todo.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <li className={`todo-item ${todo.completed ? 'completed' : ''} ${editing ? 'editing' : ''}`}>
      {error && <div className="todo-error">{error}</div>}
      <div className="todo-row">
        <label className="todo-checkbox">
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={handleToggle}
            disabled={loading}
          />
          <span className="checkmark" />
        </label>
        {editing ? (
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />
        ) : (
          <span className="todo-title" onDoubleClick={() => setEditing(true)}>
            {todo.title}
          </span>
        )}
        {todo.priority && (
          <span className={`priority priority-${todo.priority}`}>P{todo.priority}</span>
        )}
        <div className="actions">
          {editing ? (
            <>
              <button onClick={handleSave} disabled={loading}>Save</button>
              <button onClick={handleCancel} disabled={loading}>Cancel</button>
            </>
          ) : (
            <button onClick={() => setEditing(true)} disabled={loading}>Edit</button>
          )}
          <button onClick={handleDelete} disabled={loading} className="btn-delete">
            Delete
          </button>
        </div>
      </div>
      {editing ? (
        <div className="todo-edit-meta">
          <textarea
            className="todo-edit-description"
            placeholder="Add a description..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
          />
          <div className="edit-hint">Enter to save &middot; Esc to cancel</div>
        </div>
      ) : (todo.description || todo.created_at) ? (
        <div className="todo-meta">
          {todo.description && <p className="todo-description">{todo.description}</p>}
          <div className="todo-dates">
            {todo.created_at && <span>Created {formatDate(todo.created_at)}</span>}
            {todo.updated_at && <span>Updated {formatDate(todo.updated_at)}</span>}
          </div>
        </div>
      ) : null}
    </li>
  );
}
