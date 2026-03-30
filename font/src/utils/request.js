// utils/request.js
import axios from 'axios';

// 创建一个 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API || process.env.VUE_APP_BASE_API, // 从环境变量中读取基础路径
  timeout: 15000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求前做些什么，例如添加 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么，例如直接返回数据
    return response.data;
  },
  error => {
    // 对响应错误做点什么，例如统一处理 401 未授权
    if (error.response && error.response.status === 401) {
      // 跳转到登录页
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default service;