const API_BASE = 'http://localhost:8000';

function parseError(error) {
  if (Array.isArray(error.detail)) {
    return error.detail.map((e) => e.msg).join(', ');
  }
  return error.detail || 'Request failed';
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    ...options.headers,
  };

  if (!(options.body instanceof URLSearchParams)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 || response.status === 403) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.reload();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(parseError(error));
  }

  if (response.status === 204) return null;
  return response.json();
}

export const auth = {
  register: (data) => request('/auth/register/', { method: 'POST', body: JSON.stringify(data) }),
  login: async (username, password) => {
    const response = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(parseError(error));
    }
    return response.json();
  },
  me: () => request('/auth/me/'),
};

export const todos = {
  list: () => request('/todo/'),
  create: (data) => request('/todo/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/todo/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => request(`/todo/${id}/`, { method: 'DELETE' }),
};
