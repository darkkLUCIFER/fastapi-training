import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Login from './components/Login';
import Register from './components/Register';
import TodoList from './components/TodoList';
import './App.css';

function AppContent() {
  const { user, loading } = useAuth();
  const [showLogin, setShowLogin] = useState(true);

  if (loading) return <div className="loading">Loading...</div>;

  if (!user) {
    return showLogin ? (
      <Login onSwitch={() => setShowLogin(false)} />
    ) : (
      <Register onSwitch={() => setShowLogin(true)} />
    );
  }

  return <TodoList />;
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
