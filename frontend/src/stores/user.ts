import { ref } from 'vue'
import { defineStore } from 'pinia'
import { userApi, type LoginPayload, type RegisterPayload } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const user = ref({
    username: '',
    token: '',
  })

  const login = async (payload: LoginPayload) => {
    const response = await userApi.login(payload)
    user.value = {
      username: response.user.username,
      token: response.access_token,
    }
    // Store token in localStorage for persistence
    localStorage.setItem('token', response.access_token)
    localStorage.setItem('username', response.user.username)
    return response
  }

  const register = async (payload: RegisterPayload) => {
    const response = await userApi.register(payload)
    return response
  }

  const logout = () => {
    user.value = {
      username: '',
      token: '',
    }
    // Clear localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('username')
  }

  const initializeUser = () => {
    // Restore user from localStorage if available
    const token = localStorage.getItem('token')
    const username = localStorage.getItem('username')
    if (token && username) {
      user.value = {
        username,
        token,
      }
    }
  }

  // Initialize on store creation
  initializeUser()

  return { user, login, register, logout, initializeUser }
})
