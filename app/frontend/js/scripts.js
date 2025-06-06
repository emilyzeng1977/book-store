const bookList = document.getElementById('book-list');
const bookForm = document.getElementById('book-form');
const modal = document.getElementById('addEditBookModal');

const apiUrl = 'http://localhost:5000/books';

// 加载所有书籍并显示
async function displayBooks() {
  const res = await fetch(apiUrl, {
    method: 'GET',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  });

  if (!res.ok) {
    alert('获取书籍失败');
    return;
  }

  const books = await res.json();
  bookList.innerHTML = '';

  books.books.forEach(book => {
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${book.title}</strong> by ${book.author}<br>
      ID: ${book._id}<br>
      <button class="btn" onclick="openEditBookModal('${book._id}')">编辑</button>
      <button class="btn btn-danger" onclick="deleteBook('${book._id}')">删除</button>
    `;
    bookList.appendChild(li);
  });
}

// 打开添加书籍弹窗
function openAddBookModal() {
  document.getElementById('modal-title').textContent = '添加书籍';
  bookForm.reset();
  document.getElementById('book-id').value = ''; // 清空ID，标识添加操作
  modal.style.display = 'block';
}

// 打开编辑书籍弹窗
async function openEditBookModal(id) {
  const res = await fetch(`${apiUrl}/${id}`, { credentials: 'include' });

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
  const res = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookData),
    credentials: 'include'
  });

  if (!res.ok) {
    alert('添加书籍失败');
    return false;
  }
  return true;
}

// 编辑书籍请求
async function editBook(id, bookData) {
  const res = await fetch(`${apiUrl}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookData),
    credentials: 'include'
  });

  if (!res.ok) {
    alert('编辑书籍失败');
    return false;
  }
  return true;
}

// 删除书籍
async function deleteBook(id) {
  const res = await fetch(`${apiUrl}/${id}`, {
    method: 'DELETE',
    credentials: 'include'
  });

  if (!res.ok) {
    alert('删除失败');
    return;
  }

  displayBooks();
}

// 表单提交事件监听
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
    // 编辑书籍
    success = await editBook(id, bookData);
  } else {
    // 添加书籍
    success = await addBook(bookData);
  }

  if (success) {
    displayBooks();
    closeAddEditBookModal();
  }
});

// 页面加载时直接显示书籍列表
displayBooks();
