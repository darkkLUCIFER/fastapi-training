import { useState, useEffect } from 'react';
import { todos } from '../api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import AddTodo from './AddTodo';
import TodoItem from './TodoItem';

export default function TodoList() {
  const { logout, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [todoList, setTodoList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchTodos = async () => {
    try {
      const data = await todos.list();
      setTodoList(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  const addTodo = async (data) => {
    const newTodo = await todos.create(data);
    setTodoList([newTodo, ...todoList]);
  };

  const updateTodo = async (id, data) => {
    const updated = await todos.update(id, data);
    setTodoList(todoList.map((t) => (t.id === id ? updated : t)));
  };

  const deleteTodo = async (id) => {
    await todos.delete(id);
    setTodoList(todoList.filter((t) => t.id !== id));
  };

  return (
    <div className="todo-app">
      <header>
        <h1>Todos</h1>
        <div className="header-actions">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19'}
          </button>
          <div className="user-info">
            <div className="user-avatar">
              {user?.username?.charAt(0)}
            </div>
            <span>{user?.username}</span>
            <button className="btn-logout" onClick={logout}>Logout</button>
          </div>
        </div>
      </header>
      {error && <div className="error">{error}</div>}
      <AddTodo onAdd={addTodo} />
      {loading ? (
        <p className="loading">Loading tasks...</p>
      ) : todoList.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">&#9744;</div>
          <p>No tasks yet</p>
          <p className="empty-hint">Create your first task above to get started</p>
        </div>
      ) : (
        <ul>
          {todoList.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onUpdate={updateTodo}
              onDelete={deleteTodo}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
