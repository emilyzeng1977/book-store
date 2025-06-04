const bookList = document.getElementById('book-list');
const bookForm = document.getElementById('book-form');
const modal = document.getElementById('addEditBookModal');
let nextId = 3; // ID for the next book to be added

const apiUrl = 'http://127.0.0.1:5000/books';

// Function to display books
async function displayBooks() {
  const response = await fetch(apiUrl);
  const books = await response.json();
  bookList.innerHTML = '';

  books.books.forEach(book => {
    const li = document.createElement('li');
    li.className = 'book-item';

    // 显示 title, author, 和 _id
    li.innerHTML = `
      <strong>书名:</strong> ${book.title}<br>
      <strong>作者:</strong> ${book.author}<br>
      <strong>ID:</strong> ${book._id}<br>
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
