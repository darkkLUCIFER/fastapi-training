import { useState, useEffect, useRef } from 'react';
import { todos } from '../api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import AddTodo from './AddTodo';
import TodoItem from './TodoItem';

// Debounce utility function
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

export default function TodoList() {
  const { logout, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [todoList, setTodoList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Refs for abort controllers
  const fetchTodosAbortController = useRef(null);
  const addTodoAbortController = useRef(null);
  const updateTodoAbortController = useRef(null);
  const deleteTodoAbortController = useRef(null);

  // Debounced fetchTodos function
  const debouncedFetchTodos = debounce(async () => {
    // Cancel previous request if it exists
    if (fetchTodosAbortController.current) {
      fetchTodosAbortController.current.abort();
    }

    const controller = new AbortController();
    fetchTodosAbortController.current = controller;

    try {
      setLoading(true);
      setError('');
      const data = await todos.list({ signal: controller.signal });
      setTodoList(data);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      setLoading(false);
      fetchTodosAbortController.current = null;
    }
  }, 300); // 300ms debounce delay

  const addTodo = async (data) => {
    // Cancel previous request if it exists
    if (addTodoAbortController.current) {
      addTodoAbortController.current.abort();
    }

    const controller = new AbortController();
    addTodoAbortController.current = controller;

    try {
      const newTodo = await todos.create(data, { signal: controller.signal });
      setTodoList([newTodo, ...todoList]);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      addTodoAbortController.current = null;
    }
  };

  const updateTodo = async (id, data) => {
    // Cancel previous request if it exists
    if (updateTodoAbortController.current) {
      updateTodoAbortController.current.abort();
    }

    const controller = new AbortController();
    updateTodoAbortController.current = controller;

    try {
      const updated = await todos.update(id, data, user, { signal: controller.signal });
      setTodoList(todoList.map((t) => (t.id === id ? updated : t)));
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      updateTodoAbortController.current = null;
    }
  };

  const deleteTodo = async (id) => {
    // Cancel previous request if it exists
    if (deleteTodoAbortController.current) {
      deleteTodoAbortController.current.abort();
    }

    const controller = new AbortController();
    deleteTodoAbortController.current = controller;

    try {
      await todos.delete(id, user, { signal: controller.signal });
      setTodoList(todoList.filter((t) => t.id !== id));
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      deleteTodoAbortController.current = null;
    }
  };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (fetchTodosAbortController.current) {
        fetchTodosAbortController.current.abort();
      }
      if (addTodoAbortController.current) {
        addTodoAbortController.current.abort();
      }
      if (updateTodoAbortController.current) {
        updateTodoAbortController.current.abort();
      }
      if (deleteTodoAbortController.current) {
        deleteTodoAbortController.current.abort();
      }
    };
  }, []);

  useEffect(() => {
    debouncedFetchTodos();
  }, []);

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
            {theme === 'dark' ? '☀️' : '🌙'}
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
          <div className="empty-icon">📝</div>
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
              user={user}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
