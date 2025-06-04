const loginForm = document.getElementById('login-form');
const loginPage = document.getElementById('login-page');
const mainPage = document.getElementById('main-page');
const bookList = document.getElementById('book-list');
const bookForm = document.getElementById('book-form');
const modal = document.getElementById('addEditBookModal');

let authToken = null;
const apiUrl = 'http://localhost:5000/books';

// 登录事件
loginForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  const res = await fetch('http://localhost:5000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  if (res.ok) {
    const data = await res.json();
    authToken = data.token || null;  // 假设返回的是 { token: "xxx" }

    loginPage.style.display = 'none';
    mainPage.style.display = 'block';

    displayBooks();
  } else {
    alert('登录失败，请检查用户名或密码');
  }
});

// 显示图书
async function displayBooks() {
  const res = await fetch(apiUrl, {
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    }
  });
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

// Function to open add book modal
function openAddBookModal() {
  document.getElementById('modal-title').textContent = '添加书籍';
  bookForm.reset();
  modal.style.display = 'block';
}

// Function to close add/edit book modal
function closeAddEditBookModal() {
  modal.style.display = 'none';
}

// Function to open edit book modal
async function openEditBookModal(id) {
  const response = await fetch(`${apiUrl}/${id}`);
  const book = await response.json();
  if (!book) return;
  document.getElementById('modal-title').textContent = '编辑书籍';
  document.getElementById('book-id').value = book._id;
  document.getElementById('title').value = book.title;
  document.getElementById('author').value = book.author;
  modal.style.display = 'block';
}

// Function to add or edit book
bookForm.addEventListener('submit', async function(event) {
  event.preventDefault();
  const id = document.getElementById('book-id').value;
  const title = document.getElementById('title').value.trim();
  const author = document.getElementById('author').value.trim();

  const bookData = { title, author };

  if (id) {
    // Edit existing book
    await fetch(`${apiUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(bookData)
    });
  } else {
    // Add new book
    await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(bookData)
    });
  }

  displayBooks();
  closeAddEditBookModal();
});

// Function to delete book
async function deleteBook(id) {
  await fetch(`${apiUrl}/${id}`, {
    method: 'DELETE'
  });
  displayBooks();
}

// Display initial books
displayBooks();
