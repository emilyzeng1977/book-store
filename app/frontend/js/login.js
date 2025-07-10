import { API_BASE_URL, USE_LOCAL_STORAGE_FOR_TOKEN } from './config.js';

const loginForm = document.getElementById('login-form');

loginForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    credentials: 'include', // 确保 Cookie 发送和接收
  });

  if (res.ok) {
    const data = await res.json();

    if (USE_LOCAL_STORAGE_FOR_TOKEN) {
      // 开发环境：将 TokenType + AccessToken 存入 localStorage 供前端使用
      const token = `${data.TokenType} ${data.AccessToken}`;
      localStorage.setItem('authToken', token);
    } else {
      // 生产环境：推荐由后端设置 HttpOnly Cookie，前端不存 token
      console.log('生产环境：token 已由 Cookie 存储');
    }

    // 登录成功后跳转到主页
    window.location.href = 'index.html';
    console.log('登录成功', data);
  } else {
    const err = await res.json();
    alert(err.message || err.error || '登录失败，请检查用户名或密码');
  }
});