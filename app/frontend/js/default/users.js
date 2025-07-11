import { API_BASE_URL } from '../config.js';
import { fetchWithAuth } from './api.js';
import { displayBooks } from './books.js';

let currentUserRole = null;

export function setCurrentRole(role) {
  currentUserRole = role;
}

export function getCurrentRole() {
  return currentUserRole;
}

// 只负责获取当前用户并传回去
export async function checkUserRole(onSuccess) {
  try {
    const res = await fetchWithAuth(`${API_BASE_URL}/users/current`);
    if (!res.ok) {
      setTimeout(() => (window.location.href = 'login.html'), 1000);
      return null;
    }

    const user = await res.json();

    if (typeof onSuccess === 'function') {
      await onSuccess(user);
    }

    return user;
  } catch (err) {
    console.error('用户角色获取失败', err);
    return null;
  }
}

export async function displayUsers() {
  const res = await fetchWithAuth(`${API_BASE_URL}/users`);
  if (!res.ok) return alert('获取用户失败');

  const users = await res.json();
  const userList = document.getElementById('user-list');
  userList.innerHTML = '';

  users.forEach(user => {
    userList.insertAdjacentHTML('beforeend', `
      <tr>
        <td>${user.username}</td>
        <td>${user.role}</td>
        <td>${new Date(user.created_at).toLocaleString()}</td>
      </tr>
    `);
  });
}

export function logout() {
  localStorage.clear();
  sessionStorage.clear();
  window.location.href = 'login.html';
}
