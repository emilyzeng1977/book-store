// config.js

// 环境变量，控制当前运行环境
const ENV = 'production'; // 可选 'development' 或 'production'

// 根据不同环境配置不同的 API 地址
const CONFIG = {
  development: {
    API_BASE_URL: "http://localhost:5000",
    USE_LOCAL_STORAGE_FOR_TOKEN: true,  // 开发环境用 localStorage 存 token
  },
  production: {
    API_BASE_URL: "https://dev.be-devops.shop",
    USE_LOCAL_STORAGE_FOR_TOKEN: false, // 生产环境用 Cookie 存 token
  }
};

// 导出当前环境的配置
const { API_BASE_URL, USE_LOCAL_STORAGE_FOR_TOKEN } = CONFIG[ENV];

export { API_BASE_URL, USE_LOCAL_STORAGE_FOR_TOKEN, ENV };