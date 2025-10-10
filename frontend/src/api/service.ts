// src/services/service.ts
import axios, { type AxiosInstance, type InternalAxiosRequestConfig , type AxiosResponse } from 'axios';
import { useUserStore } from '@/stores/user'; // assume you have token utils

const userStore = useUserStore()

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // your API base URL
  timeout: 10000, // request timeout in ms
});

// Request interceptor: add Authorization header
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = userStore.user?.token; // get token from storage
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    // You can also add other common headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: check status code and handle errors globally
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // You can do some global processing here, e.g. logging
    return response;
  },
  (error) => {
    if (error.response) {
      const status = error.response.status;
      switch (status) {
        case 401:
          // Unauthorized, maybe redirect to login
          userStore.logout(); // remove token and redirect
          break;
        case 403:
          // Forbidden, show a message
          alert('You do not have permission to perform this action.');
          break;
        case 500:
          // Internal server error
          console.error('Server error:', error.response.data);
          break;
        default:
          console.warn('Unhandled error status:', status);
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Request setup error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
