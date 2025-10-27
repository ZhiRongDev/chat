<template>
  <div class="login-container">
    <div class="card">
      <div class="card-body">
        <h3 class="card-title text-center mb-4">Login</h3>

        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input
              type="text"
              class="form-control"
              id="username"
              placeholder="Enter your username"
              v-model="username"
              required
              :disabled="loading"
            />
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input
              type="password"
              class="form-control"
              id="password"
              placeholder="Enter your password"
              v-model="password"
              required
              :disabled="loading"
            />
          </div>
          <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
          <div class="text-center">
            <router-link to="/auth/forgot-password" class="d-block mb-2">
              Forgot Password?
            </router-link>
            <router-link to="/auth/register">
              Don't have an account? Register
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    await userStore.login({
      username: username.value,
      password: password.value,
    })

    // Redirect to home after successful login
    router.push('/')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Login failed. Please try again.'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f8f9fa;
  padding: 1rem;
}

.card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
