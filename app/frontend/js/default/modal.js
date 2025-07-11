import { editBook, displayBooks } from './books.js';
import { fetchWithAuth } from './api.js';
import { API_BASE_URL } from '../config.js';

const modal = document.getElementById('addEditBookModal');
const bookForm = document.getElementById('book-form');

// 弹窗打开、关闭、表单提交等。
export async function openEditBookModal(id) {
  try {
    const res = await fetchWithAuth(`${API_BASE_URL}/books/${id}`);
    if (!res.ok) {
      alert('获取书籍信息失败');
      return;
    }
    const book = await res.json();

    document.getElementById('modal-title').textContent = '编辑书籍';
    document.getElementById('book-id').value = book.book_id;
    document.getElementById('title').value = book.title;
    document.getElementById('author').value = book.author;
    document.getElementById('description').value = book.description || '';
    document.getElementById('title').readOnly = true;
    modal.style.display = 'block';

  } catch (error) {
    alert('获取书籍信息出错');
    console.error(error);
  }
}

export function bindUIEvents() {
  document.getElementById('add-book-btn').addEventListener('click', openAddBookModal);
  document.getElementById('close-modal-btn').addEventListener('click', closeAddEditBookModal);

  bookForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const id = document.getElementById('book-id').value;
    const title = document.getElementById('title').value.trim();
    const author = document.getElementById('author').value.trim();
    const description = document.getElementById('description').value.trim();

    const bookData = { title, author, description };
    const success = await editBook(id, bookData);
    if (success) {
      await displayBooks();
      closeAddEditBookModal();
    } else {
      alert('保存失败');
    }
  });
}

function closeAddEditBookModal() {
  modal.style.display = 'none';
}

function openAddBookModal() {
  document.getElementById('modal-title').textContent = '添加书籍';
  document.getElementById('title').readOnly = false;
  bookForm.reset();
  document.getElementById('book-id').value = '';
  modal.style.display = 'block';
}
