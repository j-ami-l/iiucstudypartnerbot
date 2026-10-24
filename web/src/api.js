/**
 * API client for SnapStudy Portal.
 * All requests include credentials (signed HttpOnly session cookie).
 * Tokens are never stored in localStorage or sessionStorage.
 */

export class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function request(url, options = {}) {
  const defaultHeaders = {
    Accept: 'application/json',
  };
  if (options.body && typeof options.body === 'string') {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    credentials: 'include',
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    throw new ApiError('Session expired or unauthorized', 401, 'unauthorized');
  }

  if (response.status === 404) {
    throw new ApiError('Resource not found', 404, 'not_found');
  }

  let data = null;
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    try {
      data = await response.json();
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const detail = data?.detail || response.statusText || 'Unknown error';
    throw new ApiError(`API Error (${response.status}): ${detail}`, response.status, detail);
  }

  return data;
}

export const api = {
  // Exchange single-use token from fragment for session cookie
  exchangeToken: (token) =>
    request('/api/auth/exchange', {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),

  // Clear session cookie and log out
  logout: () =>
    request('/api/auth/logout', {
      method: 'POST',
    }),

  // Get current user profile
  getMe: () => request('/api/me'),

  // Get dashboard metrics and recent notes
  getDashboard: () => request('/api/dashboard'),

  // Get paginated notes list
  getNotes: (limit = 20, offset = 0) =>
    request(`/api/notes?limit=${encodeURIComponent(limit)}&offset=${encodeURIComponent(offset)}`),

  // Get note detail with summary and MCQs
  getNoteDetail: (noteId) => request(`/api/notes/${encodeURIComponent(noteId)}`),

  // Get weak topics
  getWeakTopics: () => request('/api/weak-topics'),

  // Get mistake notebook
  getMistakes: () => request('/api/mistakes'),

  // Get history and weekly progress
  getHistory: () => request('/api/history'),
};
