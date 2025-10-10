import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const user = ref({
    username: '',
    token: 'this-is-the-test-token',
  })
  const logout = () => {
    user.value = {
      username: '',
      token: '',
    }
  }

  return { user, logout }
})
