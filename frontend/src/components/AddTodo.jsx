import { useState } from 'react';

export default function AddTodo({ onAdd }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await onAdd({
        title,
        description: description || undefined,
        priority: priority ? Number(priority) : undefined,
      });
      setTitle('');
      setDescription('');
      setPriority('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {error && <div className="error">{error}</div>}
      <div className="add-todo-card">
        <div className="card-label">New Task</div>
        <form className="add-todo" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="What needs to be done?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Add a description..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <div className="form-row">
            <select value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="">Priority</option>
              <option value="1">1 - Low</option>
              <option value="2">2 - Below Medium</option>
              <option value="3">3 - Medium</option>
              <option value="4">4 - Above Medium</option>
              <option value="5">5 - High</option>
            </select>
            <button type="submit" className="btn-add" disabled={loading}>
              {loading ? 'Adding...' : '+ Add Task'}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
