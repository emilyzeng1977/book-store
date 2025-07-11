import { API_BASE_URL } from '../config.js';
import { fetchWithAuth } from './api.js';
import { getCurrentRole } from './users.js';
import { toggleOrder } from './orders.js';
const bookList = document.getElementById('book-list');

export async function displayBooks() {
  const res = await fetchWithAuth(`${API_BASE_URL}/books`);
  if (!res.ok) return alert('获取书籍失败');

  const data = await res.json();

  // 按 book_id 排序（升序）
  data.books.sort((a, b) => {
    if (a.book_id < b.book_id) return -1;
    if (a.book_id > b.book_id) return 1;
    return 0;
  });

  bookList.innerHTML = '';
  const isUser = getCurrentRole() === 'user';

  const ordersRes = await fetchWithAuth(`${API_BASE_URL}/orders/my`);
  if (!ordersRes.ok) return alert('获取订单失败');
  const orderData = await ordersRes.json();

  data.books.forEach(book => {
      // 判断用户是否已购买当前书籍
      const hasOrdered = orderData.some(order => order.book_id === book.book_id);

      const statusLabel = hasOrdered
        ? `<span class="status borrowed">已购买</span>`
        : `<span class="status available">未购买</span>`;

      const actionBtn = isUser
        ? `<button class="btn purchase-btn" data-id="${book.book_id}" data-purchased="${hasOrdered}">
             ${hasOrdered ? '取消' : '购买'}
           </button>`
        : `<button class="btn edit-btn" data-id="${book.book_id}">编辑</button>`;

    bookList.insertAdjacentHTML('beforeend', `
      <tr>
        <td>${book.book_id}</td>
        <td>${book.title}</td>
        <td>${book.author}</td>
        <td>${book.description}</td>
        <td>${actionBtn}</td>
        <td>${isUser ? statusLabel : ''}</td>
      </tr>
    `);
  });
}

export async function editBook(id, bookData) {
  const res = await fetchWithAuth(`${API_BASE_URL}/books/${id}`, {
    method: 'PUT',
    body: JSON.stringify(bookData)
  });
  return res.ok;
}

export function bindBookListEvents(openEditBookModal) {
    bookList.addEventListener('click', async (event) => {
      const purchaseBtn = event.target.closest('.purchase-btn');
      const editBtn = event.target.closest('.edit-btn');

      if (editBtn) {
        openEditBookModal(editBtn.dataset.id);
      } else if (purchaseBtn) {
        const bookId = purchaseBtn.dataset.id;
        const purchased = purchaseBtn.dataset.purchased === 'true';
        await toggleOrder(bookId, purchased);
      }
    });
}
