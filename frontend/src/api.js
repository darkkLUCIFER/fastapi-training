const API_BASE = import.meta.env.VITE_API_BASE ?? '';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

function parseError(error) {
  if (Array.isArray(error.detail)) {
    return error.detail.map((e) => e.msg).join(', ');
  }
  return error.detail || 'Request failed';
}

// Unhandled server errors (500, proxy errors, gateway pages) come back as
// plain text or HTML, so fall back to the raw body for a readable message.
async function readErrorBody(response) {
  const raw = await response.text();
  if (!raw) return 'Request failed';
  try {
    return parseError(JSON.parse(raw));
  } catch {
    return raw.slice(0, 200).trim() || 'Request failed';
  }
}

function clearSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.reload();
}

async function send(endpoint, options = {}) {
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
    signal: options.signal,
  });

  if (response.status === 401) {
    clearSession();
    throw new ApiError('Your session has expired. Please log in again.', 401);
  }

  if (!response.ok) {
    throw new ApiError(await readErrorBody(response), response.status);
  }

  if (response.status === 204) return null;
  return response.json();
}

const inflight = new Map();

function request(endpoint, options = {}) {
  const method = (options.method ?? 'GET').toUpperCase();

  // Requests carrying a caller-owned AbortSignal are never shared: aborting one
  // caller must not cancel another's request.
  if (method !== 'GET' || options.signal) {
    return send(endpoint, options);
  }

  const key = `${localStorage.getItem('access_token') ?? ''} ${endpoint}`;
  const existing = inflight.get(key);
  if (existing) return existing;

  const promise = send(endpoint, options);
  inflight.set(key, promise);
  const release = () => {
    if (inflight.get(key) === promise) {
      inflight.delete(key);
    }
  };
  promise.then(release, release);
  return promise;
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
};

export const users = {
  me: () => request('/users/me/'),
};

export const permissions = {
  list: (options = {}) => request('/admin/permissions/', options),
};

export const rolePermissions = {
  list: (options = {}) => request('/admin/role-permission/', options),
  create: (data, options = {}) =>
    request('/admin/role-permission/create/', { method: 'POST', body: JSON.stringify(data), ...options }),
  detail: (id, options = {}) => request(`/admin/role-permission/${id}/`, options),
  update: (id, data, options = {}) =>
    request(`/admin/role-permission/${id}/`, { method: 'PATCH', body: JSON.stringify(data), ...options }),
  remove: (id, options = {}) => request(`/admin/role-permission/${id}/`, { method: 'DELETE', ...options }),
};

export const todos = {
  list: (options = {}) => request('/todo/', options),
  create: (data, options = {}) => request('/todo/', { method: 'POST', body: JSON.stringify(data), ...options }),
  update: (id, data, user, options = {}) => request(`/todo/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
    headers: {
      'X-User-Id': user.id,
      'X-User-Role': user.role,
    },
    ...options
  }),
  delete: (id, user, options = {}) => request(`/todo/${id}/`, {
    method: 'DELETE',
    headers: {
      'X-User-Id': user.id,
      'X-User-Role': user.role,
    },
    ...options
  }),
};
