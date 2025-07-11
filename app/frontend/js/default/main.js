import { checkUserRole, setCurrentRole, displayUsers, logout } from './users.js';
import { displayBooks, bindBookListEvents, setupPriceQueryUI } from './books.js';
import { bindUIEvents, openEditBookModal } from './modal.js';
import { displayAllOrders } from './orders.js';

// 页面初始化逻辑
document.addEventListener('DOMContentLoaded', async () => {
  // 检查当前登录用户信息，并传入回调
  checkUserRole(async (user) => {
    console.log('当前用户:', user.username, '角色:', user.role);

    // 设置全局角色变量供其他模块使用
    setCurrentRole(user.role);

    // 更新页面上的用户信息
    document.getElementById('current-username').textContent = user.username;
    document.getElementById('current-role').textContent = user.role;

    // 根据角色显示额外信息或禁用功能
    if (user.role === 'admin') {
      document.getElementById('user-section').style.display = 'block';
      await displayUsers();

      document.getElementById('order-section').style.display = 'block';
      await displayAllOrders(); // 获取并展示所有订单
    } else {
      document.getElementById('add-book-btn').disabled = true;
    }
    setupPriceQueryUI();

    // 显示书籍列表
    await displayBooks();
  });

  // 绑定书籍列表按钮事件（编辑/购买）
  bindBookListEvents(openEditBookModal);

  // 绑定“添加书籍”、“关闭弹窗”、“提交表单”等 UI 事件
  bindUIEvents();

  // 绑定登出按钮事件
  document.getElementById('logout-btn').addEventListener('click', logout);
});