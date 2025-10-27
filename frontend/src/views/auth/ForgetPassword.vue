<template>
  <div class="forgot-password-container">
    <div class="card">
      <div class="card-body">
        <h3 class="card-title text-center mb-4">Reset Password</h3>

        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <div v-if="success" class="alert alert-success" role="alert">
          {{ success }}
        </div>

        <!-- Step 1: Request Reset Token -->
        <form v-if="!resetToken" @submit.prevent="requestReset">
          <p class="text-muted mb-3">
            Enter your username to receive a password reset token.
          </p>
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input
              type="text"
              class="form-control"
              id="username"
              placeholder="Your username"
              v-model="username"
              required
              :disabled="loading"
            />
          </div>
          <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Sending...' : 'Request Reset Token' }}
          </button>
          <div class="text-center">
            <router-link to="/auth/login">Back to Login</router-link>
          </div>
        </form>

        <!-- Step 2: Reset Password with Token -->
        <form v-else @submit.prevent="resetPassword">
          <p class="text-muted mb-3">
            Enter the reset token and your new password.
          </p>
          <div class="mb-3">
            <label for="token" class="form-label">Reset Token</label>
            <input
              type="text"
              class="form-control"
              id="token"
              placeholder="Paste your reset token here"
              v-model="resetToken"
              required
              :disabled="loading"
            />
            <small class="form-text text-muted">
              Check the response message from the previous step
            </small>
          </div>
          <div class="mb-3">
            <label for="newPassword" class="form-label">New Password</label>
            <input
              type="password"
              class="form-control"
              id="newPassword"
              placeholder="Enter new password"
              v-model="newPassword"
              required
              minlength="6"
              :disabled="loading"
            />
          </div>
          <div class="mb-3">
            <label for="confirmNewPassword" class="form-label">Confirm New Password</label>
            <input
              type="password"
              class="form-control"
              id="confirmNewPassword"
              placeholder="Confirm new password"
              v-model="confirmNewPassword"
              required
              :disabled="loading"
            />
          </div>
          <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Resetting...' : 'Reset Password' }}
          </button>
          <div class="text-center">
            <button type="button" class="btn btn-link" @click="resetForm">
              Request New Token
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/service'

const router = useRouter()

const username = ref('')
const resetToken = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const requestReset = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const response = await api.post('/user/forgot-password', {
      username: username.value,
    })

    success.value = response.data.message
    // Automatically extract token from response if it's in dev mode
    const tokenMatch = response.data.message.match(/: (.+)$/)
    if (tokenMatch) {
      resetToken.value = tokenMatch[1]
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to request reset token. Please try again.'
    console.error('Reset request error:', err)
  } finally {
    loading.value = false
  }
}

const resetPassword = async () => {
  error.value = ''
  success.value = ''

  if (newPassword.value !== confirmNewPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (newPassword.value.length < 6) {
    error.value = 'Password must be at least 6 characters long'
    return
  }

  loading.value = true

  try {
    const response = await api.post('/user/reset-password', {
      token: resetToken.value,
      new_password: newPassword.value,
    })

    success.value = response.data.message + ' Redirecting to login...'

    setTimeout(() => {
      router.push('/auth/login')
    }, 2000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to reset password. Please try again.'
    console.error('Reset password error:', err)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  resetToken.value = ''
  newPassword.value = ''
  confirmNewPassword.value = ''
  error.value = ''
  success.value = ''
}
</script>

<style lang="scss" scoped>
.forgot-password-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f8f9fa;
  padding: 1rem;
}

.card {
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
