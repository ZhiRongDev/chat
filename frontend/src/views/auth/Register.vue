<template>
  <div class="register-container">
    <div class="card">
      <div class="card-body">
        <h3 class="card-title text-center mb-4">Create Account</h3>

        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <div v-if="success" class="alert alert-success" role="alert">
          {{ success }}
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input
              type="text"
              class="form-control"
              id="username"
              placeholder="Choose a username"
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
              placeholder="Choose a password"
              v-model="password"
              required
              minlength="6"
              :disabled="loading"
            />
            <small class="form-text text-muted">
              Password must be at least 6 characters long
            </small>
          </div>
          <div class="mb-3">
            <label for="confirmPassword" class="form-label">Confirm Password</label>
            <input
              type="password"
              class="form-control"
              id="confirmPassword"
              placeholder="Confirm your password"
              v-model="confirmPassword"
              required
              :disabled="loading"
            />
          </div>
          <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Creating Account...' : 'Register' }}
          </button>
          <div class="text-center">
            <router-link to="/auth/login">
              Already have an account? Login
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
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  error.value = ''
  success.value = ''

  // Validation
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters long'
    return
  }

  loading.value = true

  try {
    await userStore.register({
      username: username.value,
      password: password.value,
    })

    success.value = 'Account created successfully! Redirecting to login...'

    // Redirect to login page after 2 seconds
    setTimeout(() => {
      router.push('/auth/login')
    }, 2000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
    console.error('Registration error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-container {
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
