// src/services/service.ts
import axios, {
  type AxiosInstance,
  type InternalAxiosRequestConfig,
  type AxiosResponse,
} from 'axios'
import { useUserStore } from '@/stores/user'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000, // request timeout in ms
  withCredentials: true, // Send cookies with requests
})

// Request interceptor: No need to add Authorization header manually
// Cookies are sent automatically with withCredentials: true
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // You can add other common headers here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor: check status code and handle errors globally
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // You can do some global processing here, e.g. logging
    return response
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      const url = error.config?.url || ''

      switch (status) {
        case 401:
          // Don't trigger logout if we're already on the logout endpoint
          // This prevents infinite loop when cookie is already invalid
          if (!url.includes('/user/logout')) {
            // Unauthorized, clear user data (cookie is httpOnly, cleared by server)
            localStorage.removeItem('username')
            // Try to get the user store if available
            try {
              const userStore = useUserStore()
              // Clear local state without calling API
              userStore.user.username = ''
            } catch (e) {
              // Store not available yet, just clear localStorage
            }
          }
          break
        case 403:
          // Forbidden, show a message
          alert('You do not have permission to perform this action.')
          break
        case 500:
          // Internal server error
          console.error('Server error:', error.response.data)
          break
        default:
          console.warn('Unhandled error status:', status)
      }
    } else if (error.request) {
      console.error('No response received:', error.request)
    } else {
      console.error('Request setup error:', error.message)
    }
    return Promise.reject(error)
  },
)

export default api
