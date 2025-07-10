import { API_BASE_URL, USE_LOCAL_STORAGE_FOR_TOKEN } from './config.js';

const bookList = document.getElementById('book-list');
const bookForm = document.getElementById('book-form');
const modal = document.getElementById('addEditBookModal');
const addBookBtn = document.getElementById('add-book-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const logoutBtn = document.getElementById('logout-btn');

let currentUserRole = null;

// 通用 fetch 包装（含 token 认证）
async function fetchWithAuth(url, options = {}) {
  const headers = options.headers || {};

  if (USE_LOCAL_STORAGE_FOR_TOKEN) {
    const token = localStorage.getItem('authToken');
    if (token) {
      headers['Authorization'] = token;
    }
  }

  // 自动添加 Content-Type 仅当发送了 body 且未指定 Content-Type
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  return fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });
}

// 显示所有书籍
async function displayBooks() {
  const res = await fetchWithAuth(`${API_BASE_URL}/books`, {
    method: 'GET'
  });

  if (!res.ok) {
    alert('获取书籍失败');
    return;
  }

  const data = await res.json();
  bookList.innerHTML = ''; // 清空 tbody 内容

  // 获取当前用户角色
  const isUser = currentUserRole === 'user'; // 假设 currentUserRole 已经被设置

    data.books.forEach(book => {
        const tr = document.createElement('tr');

        // 根据状态返回带样式的 HTML 字段
        const isAvailable = book.status === 'available';
        const statusLabel = isAvailable
        ? `<span class="status available">可借阅</span>`
        : `<span class="status borrowed">已借出</span>`;

        // 如果是 admin，不显示状态内容
        const statusCellContent = isUser ? statusLabel : '';

        tr.innerHTML = `
          <td>${book.title}</td>
          <td>${book.author}</td>
          <td>${book.description}</td>
          <td>
            <button class="btn edit-btn" data-id="${book._id}" ${isUser ? 'disabled' : ''}>编辑</button>
          </td>
          <td>
            ${statusCellContent}
          </td>
        `;
        bookList.appendChild(tr);
    });
}

// 打开添加书籍弹窗
function openAddBookModal() {
  document.getElementById('modal-title').textContent = '添加书籍';
  document.getElementById('title').readOnly = false; // ✅ 恢复可编辑
  bookForm.reset();
  document.getElementById('book-id').value = '';
  modal.style.display = 'block';
}

// 打开编辑弹窗
async function openEditBookModal(id) {
  const res = await fetchWithAuth(`${API_BASE_URL}/books/${id}`, { method: 'GET' });
  if (!res.ok) {
    alert('获取书籍信息失败');
    return;
  }

  const book = await res.json();
  document.getElementById('modal-title').textContent = '编辑书籍';
  document.getElementById('book-id').value = book._id;
  document.getElementById('title').value = book.title;
  document.getElementById('title').readOnly = true; // ✅ 设置为不可编辑
  document.getElementById('author').value = book.author;
  document.getElementById('description').value = book.description;
  modal.style.display = 'block';
}

// 关闭弹窗
function closeAddEditBookModal() {
  modal.style.display = 'none';
}

// 编辑书籍请求
async function editBook(id, bookData) {
  const res = await fetchWithAuth(`${API_BASE_URL}/books/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookData)
  });
  return res.ok;
}

// 删除书籍
async function deleteBook(id) {
  const res = await fetchWithAuth(`${API_BASE_URL}/books/${id}`, {
    method: 'DELETE'
  });

  if (!res.ok) {
    alert('删除失败');
    return;
  }

  displayBooks();
}

// 表单提交处理
bookForm.addEventListener('submit', async function(event) {
  event.preventDefault();

  const id = document.getElementById('book-id').value;
  const title = document.getElementById('title').value.trim();
  const author = document.getElementById('author').value.trim();
  const description = document.getElementById('description').value.trim();

  if (!title || !author) {
    alert('书名和作者不能为空');
    return;
  }

  const bookData = { title, author, description };
  let success = false;

  if (id) {
    success = await editBook(id, bookData, description);
  } else {
    success = await addBook(bookData);
  }

  if (success) {
    displayBooks();
    closeAddEditBookModal();
  } else {
    alert('保存失败');
  }
});

async function checkUserRole() {
  try {
    const res = await fetchWithAuth(`${API_BASE_URL}/users/current`, {
      method: 'GET'
    });

    if (!res.ok) {
      console.error('无法获取用户信息, 将跳转到登录页');
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 1000); // 1 秒后跳转
      return;
    }

    const user = await res.json();
    currentUserRole = user.role;

    // ✅ 显示当前用户信息
    document.getElementById('current-username').textContent = user.username;
    document.getElementById('current-role').textContent = user.role;

    if (currentUserRole === 'admin') {
      const userSection = document.getElementById('user-section');
      if (userSection) {
        userSection.style.display = 'block'; // ✅ 显示用户区块
      }
      displayUsers(); // 获取并显示用户列表
    } else {
      addBookBtn.disabled = true;
      addBookBtn.title = '无权限添加';
    }
  } catch (err) {
    console.error('用户角色获取失败', err);
  }
}

async function displayUsers() {
  const res = await fetchWithAuth(`${API_BASE_URL}/users`, {
    method: 'GET'
  });

  if (!res.ok) {
    alert('获取用户列表失败');
    return;
  }

  const users = await res.json();
  const userList = document.getElementById('user-list');
  userList.innerHTML = '';

  users.forEach(user => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${user.username}</td>
      <td>${user.role}</td>
      <td>${new Date(user.created_at).toLocaleString()}</td>
    `;
    userList.appendChild(tr);
  });
}

// 事件代理处理 编辑/删除 按钮点击
bookList.addEventListener('click', async (event) => {
  const editBtn = event.target.closest('.edit-btn');
  const deleteBtn = event.target.closest('.delete-btn');

  if (editBtn) {
    const id = editBtn.getAttribute('data-id');
    openEditBookModal(id);
  } else if (deleteBtn) {
    const id = deleteBtn.getAttribute('data-id');
    deleteBook(id);
  }
});

// 页面初始化加载：确保 DOM 完成
document.addEventListener('DOMContentLoaded', () => {
    checkUserRole();
    displayBooks();

    // 绑定添加和关闭按钮
    addBookBtn.addEventListener('click', openAddBookModal);
    closeModalBtn.addEventListener('click', closeAddEditBookModal);

    logoutBtn.addEventListener('click', () => {
        // 清除登录信息（如果有 token 或本地存储）
        localStorage.removeItem('token');          // 如果使用了 token 存储
        localStorage.removeItem('currentUser');    // 如果有用户信息
        sessionStorage.clear();                    // 可选，清除 session 中所有内容

        // 跳转到登录页面
        window.location.href = 'login.html';
  });
});