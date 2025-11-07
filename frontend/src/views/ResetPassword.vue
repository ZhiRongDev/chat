<template>
  <div class="reset-password-container">
    <div class="reset-password-card">
      <div class="card-header">
        <h2 class="title">Reset Password</h2>
        <p class="subtitle">Enter your new password</p>
      </div>

      <div class="card-body">
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="alert alert-success" role="alert">
          {{ successMessage }}
        </div>

        <form @submit.prevent="handleResetPassword">
          <div class="mb-3">
            <label for="new-password" class="form-label">New Password</label>
            <input
              v-model="resetPasswordForm.newPassword"
              type="password"
              class="form-control"
              id="new-password"
              placeholder="Enter your new password"
              required
              :disabled="formLoading"
            />
          </div>

          <div class="mb-3">
            <label for="confirm-password" class="form-label">Confirm New Password</label>
            <input
              v-model="resetPasswordForm.confirmPassword"
              type="password"
              class="form-control"
              id="confirm-password"
              placeholder="Confirm your new password"
              required
              :disabled="formLoading"
            />
          </div>

          <div class="d-grid gap-2">
            <button type="submit" class="btn btn-primary" :disabled="formLoading">
              <span
                v-if="formLoading"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ formLoading ? 'Resetting...' : 'Reset Password' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="goToHome">Back to Home</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { userApi } from '@/api/user'
import { appendAlert } from '@/utils/alert'

const route = useRoute()
const router = useRouter()

const resetPasswordForm = ref({
  newPassword: '',
  confirmPassword: '',
})

const formLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

onMounted(() => {
  // Validate that we have the required token
  const token = route.query.token as string
  const username = route.query.username as string

  if (!token || !username) {
    errorMessage.value = 'Invalid or missing reset token. Please request a new password reset link.'
  }
})

const handleResetPassword = async () => {
  if (!resetPasswordForm.value.newPassword || !resetPasswordForm.value.confirmPassword) {
    errorMessage.value = 'Please fill in all fields'
    return
  }

  if (resetPasswordForm.value.newPassword !== resetPasswordForm.value.confirmPassword) {
    errorMessage.value = 'Passwords do not match!'
    return
  }

  if (resetPasswordForm.value.newPassword.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters long'
    return
  }

  try {
    formLoading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    const token = route.query.token as string
    if (!token) {
      errorMessage.value = 'Invalid or missing reset token'
      return
    }

    const response = await userApi.resetPassword({
      token,
      new_password: resetPasswordForm.value.newPassword,
    })

    successMessage.value = response.message
    appendAlert(response.message, 'success')

    // Redirect to home after successful reset
    setTimeout(() => {
      router.push('/')
    }, 2000)
  } catch (error: any) {
    console.error('Reset password error:', error)
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'Failed to reset password. The link may be invalid or expired.'
    }
  } finally {
    formLoading.value = false
  }
}

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.reset-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.reset-password-card {
  width: 100%;
  max-width: 450px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.card-header {
  padding: 32px 32px 24px;
  text-align: center;
  border-bottom: 1px solid #e9ecef;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #111;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}

.card-body {
  padding: 32px;
}

/* Form Input Styles */
.form-control {
  padding: 12px 16px;
  font-size: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
  background-color: #fff;
}

.form-control:hover:not(:disabled) {
  border-color: #d1d5db;
}

.form-control:focus {
  border-color: #111827;
  background-color: #fff;
  outline: 2px solid #111827;
  outline-offset: -1px;
}

.form-control:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.6;
}

.form-control::placeholder {
  color: #9ca3af;
}

.form-label {
  font-weight: 500;
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
}

/* Alert Styles */
.alert {
  border-radius: 8px;
  border: none;
  padding: 12px 16px;
  font-size: 14px;
  margin-bottom: 20px;
}

.alert-danger {
  background-color: #fef2f2;
  color: #dc2626;
  border-left: 4px solid #dc2626;
}

.alert-success {
  background-color: #f0fdf4;
  color: #16a34a;
  border-left: 4px solid #16a34a;
}

/* Button Styles */
.btn {
  padding: 12px 20px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  line-height: 1.5;
}

.btn-primary {
  background-color: #111827;
  border: 1px solid #111827;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background-color: #000;
  border-color: #000;
  color: #fff;
}

.btn-primary:disabled {
  background-color: #6b7280;
  border-color: #6b7280;
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: transparent;
  border: 1px solid #e5e7eb;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #111827;
}

/* Spinner Styles */
.spinner-border-sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

/* Responsive */
@media (max-width: 576px) {
  .reset-password-card {
    margin: 20px;
  }

  .card-header {
    padding: 24px 20px 16px;
  }

  .card-body {
    padding: 20px;
  }

  .title {
    font-size: 24px;
  }
}
</style>
