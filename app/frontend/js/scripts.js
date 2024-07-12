// Hard-coded book data
let books = [
  { id: 1, title: '1984', author: 'George Orwell' },
  { id: 2, title: 'Brave New World', author: 'Aldous Huxley' }
];

const bookList = document.getElementById('book-list');
const bookForm = document.getElementById('book-form');
const modal = document.getElementById('addEditBookModal');
let nextId = 3; // ID for the next book to be added

// Function to display books
function displayBooks() {
  bookList.innerHTML = '';
  books.forEach(book => {
    const li = document.createElement('li');
    li.className = 'book-item';
    li.innerHTML = `<strong>${book.title}</strong> by ${book.author}
      <button class="btn" onclick="openEditBookModal(${book.id})">编辑</button>
      <button class="btn btn-danger" onclick="deleteBook(${book.id})">删除</button>`;
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
function openEditBookModal(id) {
  const book = books.find(b => b.id === id);
  if (!book) return;
  document.getElementById('modal-title').textContent = '编辑书籍';
  document.getElementById('book-id').value = book.id;
  document.getElementById('title').value = book.title;
  document.getElementById('author').value = book.author;
  modal.style.display = 'block';
}

// Function to add or edit book
bookForm.addEventListener('submit', function(event) {
  event.preventDefault();
  const id = parseInt(document.getElementById('book-id').value);
  const title = document.getElementById('title').value.trim();
  const author = document.getElementById('author').value.trim();

  if (id) {
    // Edit existing book
    const index = books.findIndex(b => b.id === id);
    if (index !== -1) {
      books[index].title = title;
      books[index].author = author;
    }
  } else {
    // Add new book
    books.push({ id: nextId++, title, author });
  }

  displayBooks();
  closeAddEditBookModal();
});

// Function to delete book
function deleteBook(id) {
  books = books.filter(book => book.id !== id);
  displayBooks();
}

// Display initial books
displayBooks();
