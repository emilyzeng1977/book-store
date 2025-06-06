const loginForm = document.getElementById('login-form');

loginForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  const res = await fetch('http://localhost:5000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    credentials: 'include', // 确保 Cookie 发送和接收
  });

  if (res.ok) {
    const data = await res.json();
    // 假设服务器返回 token 或者设置了 cookie 以保持登录状态
    // 登录成功后跳转到主页
    window.location.href = 'index.html';
    console.log('登录成功', data);
  } else {
    alert('登录失败，请检查用户名或密码');
  }
});
