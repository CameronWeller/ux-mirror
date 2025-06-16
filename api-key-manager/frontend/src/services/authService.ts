import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(email: string, password: string) {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  async verify2FA(code: string) {
    const response = await api.post('/auth/verify-2fa', { code });
    return response.data;
  },

  async logout() {
    await api.post('/auth/logout');
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data.user;
  },

  async setup2FA() {
    const response = await api.post('/auth/setup-2fa');
    return response.data;
  },

  async enable2FA(code: string) {
    const response = await api.post('/auth/enable-2fa', { code });
    return response.data;
  },

  async disable2FA(password: string) {
    const response = await api.post('/auth/disable-2fa', { password });
    return response.data;
  },
};

export default api;