import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Login from './components/Login';
import Register from './components/Register';
import TodoList from './components/TodoList';
import AdminPanel from './components/AdminPanel';
import './App.css';

function isAdminRole(role) {
  const value = role && typeof role === 'object' ? role.value : role;
  return value === 'admin';
}

function AppContent() {
  const { user, loading } = useAuth();
  const [showLogin, setShowLogin] = useState(true);
  const [page, setPage] = useState('todos');

  if (loading) return <div className="loading">Loading...</div>;

  if (!user) {
    return showLogin ? (
      <Login onSwitch={() => setShowLogin(false)} />
    ) : (
      <Register onSwitch={() => setShowLogin(true)} />
    );
  }

  const isAdmin = isAdminRole(user.role);

  if (page === 'admin' && isAdmin) {
    return <AdminPanel onBack={() => setPage('todos')} />;
  }

  return <TodoList onGoAdmin={isAdmin ? () => setPage('admin') : undefined} />;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}
