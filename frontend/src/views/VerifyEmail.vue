<template>
  <div class="verify-email-container">
    <div class="verify-email-card">
      <div class="card-header">
        <h2 class="title">Email Verification</h2>
        <p class="subtitle">
          {{ verificationStatus === 'loading' ? 'Verifying your email...' : '' }}
        </p>
      </div>

      <div class="card-body">
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="alert alert-success" role="alert">
          {{ successMessage }}
        </div>

        <div v-if="verificationStatus === 'loading'" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-muted">Please wait while we verify your email...</p>
        </div>

        <div v-if="verificationStatus === 'success'" class="text-center py-4">
          <div class="success-icon mb-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="64"
              height="64"
              fill="currentColor"
              class="bi bi-check-circle-fill"
              viewBox="0 0 16 16"
            >
              <path
                d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"
              />
            </svg>
          </div>
          <p class="mb-4">{{ successMessage }}</p>
        </div>

        <div v-if="verificationStatus === 'error'" class="text-center py-4">
          <div class="error-icon mb-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="64"
              height="64"
              fill="currentColor"
              class="bi bi-x-circle-fill"
              viewBox="0 0 16 16"
            >
              <path
                d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293z"
              />
            </svg>
          </div>
          <p class="mb-4">{{ errorMessage }}</p>
        </div>

        <div class="d-grid gap-2">
          <button type="button" class="btn btn-primary" @click="goToHome">
            {{ verificationStatus === 'success' ? 'Go to Login' : 'Back to Home' }}
          </button>
        </div>
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

const verificationStatus = ref<'loading' | 'success' | 'error'>('loading')
const errorMessage = ref('')
const successMessage = ref('')

onMounted(async () => {
  // Validate that we have the required token
  const token = route.query.token as string
  const username = route.query.username as string

  if (!token || !username) {
    verificationStatus.value = 'error'
    errorMessage.value =
      'Invalid or missing verification token. Please check your email for the correct link.'
    return
  }

  // Automatically verify on mount
  await handleVerifyEmail(token)
})

const handleVerifyEmail = async (token: string) => {
  try {
    verificationStatus.value = 'loading'
    errorMessage.value = ''
    successMessage.value = ''

    const response = await userApi.verifyEmail({ token })

    verificationStatus.value = 'success'
    successMessage.value = response.message
    appendAlert(response.message, 'success')

    // Redirect to home after 3 seconds
    setTimeout(() => {
      router.push('/')
    }, 3000)
  } catch (error: any) {
    console.error('Email verification error:', error)
    verificationStatus.value = 'error'

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'Failed to verify email. The link may be invalid or expired.'
    }
  }
}

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.verify-email-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.verify-email-card {
  width: 100%;
  max-width: 500px;
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

/* Icon Styles */
.success-icon {
  color: #16a34a;
}

.error-icon {
  color: #dc2626;
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

/* Spinner */
.spinner-border {
  width: 3rem;
  height: 3rem;
}

/* Text Utilities */
.text-muted {
  color: #6b7280;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Responsive */
@media (max-width: 576px) {
  .verify-email-card {
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
