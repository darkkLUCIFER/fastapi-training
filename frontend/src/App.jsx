import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Login from './components/Login';
import Register from './components/Register';
import TodoList from './components/TodoList';
import AdminPanel from './components/AdminPanel';
import AdminPermissions from './components/AdminPermissions';
import AdminRolePermissions from './components/AdminRolePermissions';
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

  if (isAdmin) {
    if (page === 'admin') {
      return (
        <AdminPanel
          onBack={() => setPage('todos')}
          onOpenPermissions={() => setPage('admin-permissions')}
          onOpenRolePermissions={() => setPage('admin-role-permissions')}
        />
      );
    }
    if (page === 'admin-permissions') {
      return <AdminPermissions onBack={() => setPage('admin')} />;
    }
    if (page === 'admin-role-permissions') {
      return <AdminRolePermissions onBack={() => setPage('admin')} />;
    }
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
