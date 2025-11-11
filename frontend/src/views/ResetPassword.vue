<template>
  <div class="reset-password-container">
    <div class="reset-password-card">
      <div class="card-header">
        <div class="icon-wrapper">
          <svg
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            style="width: 48px; height: 48px"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
            ></path>
          </svg>
        </div>
        <h2 class="title">Reset Password</h2>
        <p class="subtitle">Enter your new password to secure your account</p>
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
            <div class="password-input-wrapper">
              <input
                v-model="resetPasswordForm.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                class="form-control"
                id="new-password"
                placeholder="Enter your new password"
                required
                :disabled="formLoading"
              />
              <button
                type="button"
                class="password-toggle-btn"
                @click="showNewPassword = !showNewPassword"
                :disabled="formLoading"
              >
                <svg
                  v-if="!showNewPassword"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  style="width: 20px; height: 20px"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  ></path>
                </svg>
                <svg
                  v-else
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  style="width: 20px; height: 20px"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  ></path>
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  ></path>
                </svg>
              </button>
            </div>
          </div>

          <div class="mb-3">
            <label for="confirm-password" class="form-label">Confirm New Password</label>
            <div class="password-input-wrapper">
              <input
                v-model="resetPasswordForm.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                class="form-control"
                id="confirm-password"
                placeholder="Confirm your new password"
                required
                :disabled="formLoading"
              />
              <button
                type="button"
                class="password-toggle-btn"
                @click="showConfirmPassword = !showConfirmPassword"
                :disabled="formLoading"
              >
                <svg
                  v-if="!showConfirmPassword"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  style="width: 20px; height: 20px"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  ></path>
                </svg>
                <svg
                  v-else
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  style="width: 20px; height: 20px"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  ></path>
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  ></path>
                </svg>
              </button>
            </div>
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
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.reset-password-card {
  width: 100%;
  max-width: 480px;
  background: #fff;
  border-radius: 20px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 10px 40px rgba(102, 126, 234, 0.3);
  overflow: hidden;
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  padding: 40px 32px 32px;
  text-align: center;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(to bottom, #fff, #f9fafb);
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 20px;
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 10px;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
  line-height: 1.5;
}

.card-body {
  padding: 32px;
  background: #fff;
}

/* Form Input Styles */
.form-control {
  padding: 14px 18px;
  font-size: 15px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.2s ease;
  background-color: #fff;
  font-family: inherit;
}

@media (max-width: 768px) {
  .form-control {
    padding: 12px 16px;
    font-size: 14px;
  }
}

.form-control:hover:not(:disabled) {
  border-color: #d1d5db;
}

.form-control:focus {
  border-color: #667eea;
  background-color: #fff;
  outline: none;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
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
  font-weight: 600;
  font-size: 14px;
  color: #374151;
  margin-bottom: 10px;
  display: block;
}

@media (max-width: 768px) {
  .form-label {
    font-size: 13px;
  }
}

/* Password Input Wrapper */
.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper .form-control {
  padding-right: 52px;
}

.password-toggle-btn {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  padding: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.password-toggle-btn:hover:not(:disabled) {
  color: #374151;
  background-color: #f3f4f6;
  transform: scale(1.05);
}

.password-toggle-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.password-toggle-btn:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.password-toggle-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

/* Alert Styles */
.alert {
  border-radius: 12px;
  border: none;
  padding: 14px 18px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

@media (max-width: 768px) {
  .alert {
    padding: 12px 16px;
    font-size: 13px;
  }
}

.alert-danger {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #dc2626;
  border-left: 4px solid #dc2626;
}

.alert-success {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  color: #16a34a;
  border-left: 4px solid #16a34a;
}

/* Button Styles */
.btn {
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  line-height: 1.5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .btn {
    padding: 10px 20px;
    font-size: 14px;
  }
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  color: #fff;
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  background: #d1d5db;
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  background-color: #fff;
  border: 2px solid #e5e7eb;
  color: #374151;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #111827;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
}

.btn-secondary:active:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
  transform: translateY(0);
}

/* Spinner Styles */
.spinner-border-sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

/* Responsive */
@media (max-width: 768px) {
  .reset-password-container {
    padding: 16px;
  }

  .reset-password-card {
    max-width: 100%;
    border-radius: 16px;
  }

  .card-header {
    padding: 32px 24px 24px;
  }

  .icon-wrapper {
    width: 64px;
    height: 64px;
    margin-bottom: 16px;
  }

  .icon-wrapper svg {
    width: 36px !important;
    height: 36px !important;
  }

  .card-body {
    padding: 24px;
  }

  .title {
    font-size: 24px;
  }

  .subtitle {
    font-size: 14px;
  }
}
</style>
