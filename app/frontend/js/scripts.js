import { API_BASE_URL, USE_LOCAL_STORAGE_FOR_TOKEN } from './config.js';

const bookList = document.getElementById('book-list');
const bookForm = document.getElementById('book-form');
const modal = document.getElementById('addEditBookModal');
const addBookBtn = document.getElementById('add-book-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const apiUrl = `${API_BASE_URL}/books`;

// 通用 fetch 包装（含 token 认证）
async function fetchWithAuth(url, options = {}) {
  const headers = options.headers || {};

  if (USE_LOCAL_STORAGE_FOR_TOKEN) {
    const token = localStorage.getItem('authToken');
    if (token) {
      headers['Authorization'] = token;
    }
  }

  return fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });
}

// 显示所有书籍
async function displayBooks() {
  const res = await fetchWithAuth(apiUrl, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });

  if (!res.ok) {
    alert('获取书籍失败');
    return;
  }

  const data = await res.json();
  bookList.innerHTML = '';

  data.books.forEach(book => {
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${book.title}</strong> by ${book.author}<br>
      ID: ${book._id}<br>
      <button class="btn edit-btn" data-id="${book._id}">编辑</button>
      <button class="btn btn-danger delete-btn" data-id="${book._id}">删除</button>
    `;
    bookList.appendChild(li);
  });
}

// 打开添加书籍弹窗
function openAddBookModal() {
  document.getElementById('modal-title').textContent = '添加书籍';
  bookForm.reset();
  document.getElementById('book-id').value = '';
  modal.style.display = 'block';
}

// 打开编辑弹窗
async function openEditBookModal(id) {
  const res = await fetchWithAuth(`${apiUrl}/${id}`, { method: 'GET' });
  if (!res.ok) {
    alert('获取书籍信息失败');
    return;
  }

  const book = await res.json();
  document.getElementById('modal-title').textContent = '编辑书籍';
  document.getElementById('book-id').value = book._id;
  document.getElementById('title').value = book.title;
  document.getElementById('author').value = book.author;
  modal.style.display = 'block';
}

// 关闭弹窗
function closeAddEditBookModal() {
  modal.style.display = 'none';
}

// 添加书籍请求
async function addBook(bookData) {
  const res = await fetchWithAuth(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookData)
  });
  return res.ok;
}

// 编辑书籍请求
async function editBook(id, bookData) {
  const res = await fetchWithAuth(`${apiUrl}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookData)
  });
  return res.ok;
}

// 删除书籍
async function deleteBook(id) {
  const res = await fetchWithAuth(`${apiUrl}/${id}`, {
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

  if (!title || !author) {
    alert('书名和作者不能为空');
    return;
  }

  const bookData = { title, author };
  let success = false;

  if (id) {
    success = await editBook(id, bookData);
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

// 绑定添加和关闭按钮
addBookBtn.addEventListener('click', openAddBookModal);
closeModalBtn.addEventListener('click', closeAddEditBookModal);

// 页面初始化加载
displayBooks();
