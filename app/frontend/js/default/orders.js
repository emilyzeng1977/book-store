import { API_BASE_URL } from '../config.js';
import { fetchWithAuth } from './api.js';
import { displayBooks } from './books.js';

const orderList = document.getElementById('order-list');

// 获取所有订单（管理员使用）
export async function displayAllOrders() {
  const res = await fetchWithAuth(`${API_BASE_URL}/orders`);
  if (!res.ok) {
    alert('获取订单失败');
    return;
  }

  const orders = await res.json();
  orders.sort((a, b) => {
    // 先按 username 排序（字母顺序）
    if (a.username < b.username) return -1;
    if (a.username > b.username) return 1;

    // username 相同则按 book_id 排序
    if (a.book_id < b.book_id) return -1;
    if (a.book_id > b.book_id) return 1;

    return 0;
  });

  orderList.innerHTML = '';

  orders.forEach(order => {
    orderList.insertAdjacentHTML('beforeend', `
      <tr>
        <td>${order.username}</td>
        <td>${order.book_id}</td>
        <td>${new Date(order.created_at).toLocaleString()}</td>
      </tr>
    `);
  });
}

export async function toggleOrder(bookId, isAlreadyPurchased) {
  const url = isAlreadyPurchased ? `${API_BASE_URL}/orders/${bookId}` : `${API_BASE_URL}/orders`;
  const method = isAlreadyPurchased ? 'DELETE' : 'POST';

  const res = await fetchWithAuth(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ book_id: bookId })
  });

  if (!res.ok) {
    alert(`${isAlreadyPurchased ? '取消失败' : '购买失败'}`);
    return;
  }

  // 重新渲染书籍列表
  await displayBooks();
}

export async function displayOrdersIfAdmin() {
  if (currentUserRole !== 'admin') return;

  const orderSection = document.getElementById('order-section');
  const orderList = document.getElementById('order-list');

  const res = await fetchWithAuth(`${API_BASE_URL}/orders`);
  if (!res.ok) {
    alert('获取订单列表失败');
    return;
  }

  const orders = await res.json();
  orderList.innerHTML = '';

  orders.forEach(order => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${order.username}</td>
      <td>${order.book_id}</td>
    `;
    orderList.appendChild(tr);
  });

  orderSection.style.display = 'block';
}
