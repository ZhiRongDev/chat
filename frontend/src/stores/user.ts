import { ref } from 'vue'
import { defineStore } from 'pinia'
import { userApi, type LoginPayload, type RegisterPayload } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const user = ref({
    username: '',
  })

  const login = async (payload: LoginPayload) => {
    const response = await userApi.login(payload)
    user.value = {
      username: response.user.username,
    }
    // Store username in localStorage for persistence
    // Session cookie is set by backend automatically
    localStorage.setItem('username', response.user.username)
    return response
  }

  const register = async (payload: RegisterPayload) => {
    const response = await userApi.register(payload)
    return response
  }

  const logout = async () => {
    try {
      // Call logout endpoint to clear session cookie
      // This might fail if cookie is already cleared/expired, which is fine
      await userApi.logout()
    } catch (e: any) {
      // Ignore 401 errors (cookie already invalid), but log other errors
      if (e?.response?.status !== 401) {
        console.error('Logout API call failed:', e)
      }
    }
    user.value = {
      username: '',
    }
    // Clear localStorage
    localStorage.removeItem('username')
  }

  const initializeUser = () => {
    // Restore username from localStorage if available
    // Session validity is checked by backend via cookie
    const username = localStorage.getItem('username')
    if (username) {
      user.value = {
        username,
      }
    }
  }

  // Initialize on store creation
  initializeUser()

  return { user, login, register, logout, initializeUser }
})
