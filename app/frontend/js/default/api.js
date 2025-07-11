import { USE_LOCAL_STORAGE_FOR_TOKEN } from '../config.js';

export async function fetchWithAuth(url, options = {}) {
  const headers = options.headers || {};

  if (USE_LOCAL_STORAGE_FOR_TOKEN) {
    const token = localStorage.getItem('authToken');
    if (token) headers['Authorization'] = token;
  }

  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  return fetch(url, {
    ...options,
    headers,
    credentials: 'include'
  });
}

export function logout() {
  localStorage.clear();
  sessionStorage.clear();
  window.location.href = 'login.html';
}
