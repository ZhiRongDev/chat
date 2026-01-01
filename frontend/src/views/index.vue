<template>
  <div class="app-container">
    <!-- Sidebar -->
    <Sidebar :is-open="sidebarOpen" :chat-histories="chatHistories" :current-chat-id="currentChatId" @new-chat="newChat"
      @load-chat="loadChat" @delete-chat="deleteChat" @logout="handleLogout" @show-modal="showModal" />

    <!-- Main Chat Area -->
    <div class="main-container">
      <!-- Header -->
      <div class="header">
        <button class="menu-btn" @click="toggleSidebar">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
        <div class="header-title">Chat</div>
        <div class="spacer"></div>
      </div>

      <!-- Messages -->
      <div class="messages-container" ref="messagesContainer">
        <div class="messages-wrapper">
          <div v-for="(msg, index) in messages" :key="msg.id || index" class="message-group" :class="msg.sender">
            <div class="message-bubble" :class="{ thinking: msg.sender === 'bot' && msg.id === streamingMessageId }">
              <MarkdownRenderer v-if="msg.sender === 'bot'" :content="msg.text" />
              <span v-else>{{ msg.text }}</span>
              <!-- Animated dots for thinking state -->
              <span v-if="msg.sender === 'bot' && msg.id === streamingMessageId && !msg.text" class="thinking-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </span>
            </div>
          </div>

          <div ref="endOfMessages"></div>
        </div>

        <!-- Scroll to Bottom Button -->
        <button v-show="showScrollButton" @click="scrollToBottom" class="scroll-to-bottom-btn"
          aria-label="Scroll to bottom">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
          </svg>
        </button>
      </div>

      <!-- Input -->
      <div class="input-area">
        <div v-if="chatSettings.useRag && !ragWarning" class="rag-indicator">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 16px; height: 16px">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4">
            </path>
          </svg>
          Gemini File Search RAG Active
        </div>
        <div v-if="ragWarning" class="rag-warning">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 16px; height: 16px">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z">
            </path>
          </svg>
          RAG enabled but no documents found. Upload documents in Settings.
        </div>
        <div class="input-wrapper">
          <input v-model="currentMessage" @keypress.enter="sendMessage" type="text" class="input-field"
            placeholder="Message Chat..." :disabled="loading" />
          <button @click="loading ? stopMessage() : sendMessage()" class="send-btn" :class="{ 'stop-btn': loading }"
            :disabled="!loading && !currentMessage.trim()">
            <!-- Stop icon when loading -->
            <svg v-if="loading" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <!-- Send icon when not loading -->
            <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Bootstrap Modal -->
    <div class="modal fade" id="appModal" tabindex="-1" aria-labelledby="appModalLabel" aria-hidden="true"
      data-bs-keyboard="false">
      <div class="modal-dialog modal-dialog-centered" :class="{ 'modal-lg': modalType === 'documents' }">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="appModalLabel">{{ modalTitle }}</h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>

          <!-- Login Form -->
          <template v-if="modalType === 'login'">
            <div class="modal-body">
              <div v-if="errorMessage" class="alert alert-danger mb-3" role="alert">
                {{ errorMessage }}
              </div>
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="login-username" class="form-label">Username</label>
                  <input v-model="loginUsername" type="text" class="form-control" id="login-username"
                    placeholder="Enter your username" :disabled="formLoading" />
                  <div v-if="loginErrors.username" class="invalid-feedback d-block">
                    {{ loginErrors.username }}
                  </div>
                </div>
                <div class="mb-3">
                  <label for="login-password" class="form-label">Password</label>
                  <div class="password-input-wrapper">
                    <input v-model="loginPassword" :type="showLoginPassword ? 'text' : 'password'" class="form-control"
                      id="login-password" placeholder="Enter your password" :disabled="formLoading" />
                    <button type="button" class="password-toggle-btn" @click="showLoginPassword = !showLoginPassword"
                      :disabled="formLoading">
                      <svg v-if="!showLoginPassword" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        style="width: 20px; height: 20px">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21">
                        </path>
                      </svg>
                      <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        style="width: 20px; height: 20px">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z">
                        </path>
                      </svg>
                    </button>
                  </div>
                  <div v-if="loginErrors.password" class="invalid-feedback d-block">
                    {{ loginErrors.password }}
                  </div>
                </div>
                <div class="mb-3 text-end">
                  <a href="#" class="forgot-password-link" @click.prevent="showForgotPasswordModal">
                    Forgot Password?
                  </a>
                </div>
                <div class="modal-footer border-0 px-0 pb-0">
                  <button type="button" class="btn btn-secondary" @click="closeModal" :disabled="formLoading">
                    Cancel
                  </button>
                  <button type="submit" class="btn btn-primary" :disabled="formLoading">
                    <span v-if="formLoading" class="spinner-border spinner-border-sm me-2" role="status"
                      aria-hidden="true"></span>
                    {{ formLoading ? 'Logging in...' : 'Login' }}
                  </button>
                </div>
              </form>
            </div>
          </template>

          <!-- Register Form -->
          <template v-if="modalType === 'register'">
            <div class="modal-body">
              <div v-if="errorMessage" class="alert alert-danger mb-3" role="alert">
                {{ errorMessage }}
              </div>
              <div v-if="successMessage" class="alert alert-success mb-3" role="alert">
                {{ successMessage }}
              </div>
              <form @submit.prevent="handleRegister">
                <div class="mb-3">
                  <label for="register-username" class="form-label">Username</label>
                  <input v-model="registerUsername" type="text" class="form-control" id="register-username"
                    placeholder="Enter your username" :disabled="formLoading" />
                  <div v-if="registerErrors.username" class="invalid-feedback d-block">
                    {{ registerErrors.username }}
                  </div>
                </div>
                <div class="mb-3">
                  <label for="register-password" class="form-label">Password</label>
                  <div class="password-input-wrapper">
                    <input v-model="registerPassword" :type="showRegisterPassword ? 'text' : 'password'"
                      class="form-control" id="register-password" placeholder="Enter your password"
                      :disabled="formLoading" />
                    <button type="button" class="password-toggle-btn"
                      @click="showRegisterPassword = !showRegisterPassword" :disabled="formLoading">
                      <svg v-if="!showRegisterPassword" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        style="width: 20px; height: 20px">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21">
                        </path>
                      </svg>
                      <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        style="width: 20px; height: 20px">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z">
                        </path>
                      </svg>
                    </button>
                  </div>
                  <div v-if="registerErrors.password" class="invalid-feedback d-block">
                    {{ registerErrors.password }}
                  </div>
                </div>
                <div class="mb-3">
                  <label for="register-confirm" class="form-label">Confirm Password</label>
                  <div class="password-input-wrapper">
                    <input v-model="registerConfirmPassword" :type="showRegisterConfirmPassword ? 'text' : 'password'"
                      class="form-control" id="register-confirm" placeholder="Confirm your password"
                      :disabled="formLoading" />
                    <button type="button" class="password-toggle-btn"
                      @click="showRegisterConfirmPassword = !showRegisterConfirmPassword" :disabled="formLoading">
                      <svg v-if="!showRegisterConfirmPassword" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        style="width: 20px; height: 20px">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21">
                        </path>
                      </svg>
                      <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        style="width: 20px; height: 20px">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z">
                        </path>
                      </svg>
                    </button>
                  </div>
                  <div v-if="registerErrors.confirmPassword" class="invalid-feedback d-block">
                    {{ registerErrors.confirmPassword }}
                  </div>
                </div>
                <div class="modal-footer border-0 px-0 pb-0">
                  <button type="button" class="btn btn-secondary" @click="closeModal" :disabled="formLoading">
                    Cancel
                  </button>
                  <button type="submit" class="btn btn-primary" :disabled="formLoading">
                    <span v-if="formLoading" class="spinner-border spinner-border-sm me-2" role="status"
                      aria-hidden="true"></span>
                    {{ formLoading ? 'Registering...' : 'Register' }}
                  </button>
                </div>
              </form>
            </div>
          </template>

          <!-- Forgot Password Form -->
          <template v-if="modalType === 'forgot-password'">
            <div class="modal-body">
              <div v-if="errorMessage" class="alert alert-danger mb-3" role="alert">
                {{ errorMessage }}
              </div>
              <div v-if="successMessage" class="alert alert-success mb-3" role="alert">
                {{ successMessage }}
              </div>
              <form @submit.prevent="handleForgotPassword">
                <div class="mb-3">
                  <label for="forgot-username" class="form-label">Username (Email)</label>
                  <input v-model="forgotPasswordUsername" type="text" class="form-control mb-2" id="forgot-username"
                    placeholder="Enter your username/email" :disabled="formLoading" />
                  <div v-if="forgotPasswordErrors.username" class="invalid-feedback d-block">
                    {{ forgotPasswordErrors.username }}
                  </div>
                  <div class="form-text">
                    We'll send a password reset link to your email address.
                  </div>
                </div>
                <div class="modal-footer border-0 px-0 pb-0">
                  <button type="button" class="btn btn-secondary" @click="closeModal" :disabled="formLoading">
                    Cancel
                  </button>
                  <button type="submit" class="btn btn-primary" :disabled="formLoading">
                    <span v-if="formLoading" class="spinner-border spinner-border-sm me-2" role="status"
                      aria-hidden="true"></span>
                    {{ formLoading ? 'Sending...' : 'Send Reset Link' }}
                  </button>
                </div>
              </form>
            </div>
          </template>

          <!-- Settings -->
          <template v-if="modalType === 'settings'">
            <div class="modal-body">
              <ChatSettings v-model="chatSettings" @show-documents="showDocumentManager" />
            </div>
          </template>

          <!-- Document Manager -->
          <template v-if="modalType === 'documents'">
            <div class="modal-body p-0" style="max-height: 70vh; overflow-y: auto">
              <DocumentManager />
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed, onUnmounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { chatApi, type Message, type ChatHistoryItem } from '@/api/chat'
import { userApi } from '@/api/user'
import Sidebar from '@/components/Sidebar.vue'
import ChatSettings, { type ChatSettings as ChatSettingsType } from '@/components/ChatSettings.vue'
import DocumentManager from '@/components/DocumentManager.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { appendAlert } from '@/utils/alert'
import { Modal } from 'bootstrap'
import { useRoute, useRouter } from 'vue-router'
import { useForm, useField } from 'vee-validate'
import { loginSchema, registerSchema, forgotPasswordSchema } from '@/utils/validation'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const isLoggedIn = computed(() => !!userStore.user.username)

// Bootstrap modal instance
let bootstrapModal: Modal | null = null

// Load chat settings from localStorage or use defaults
const loadChatSettings = (): ChatSettingsType => {
  const saved = localStorage.getItem('chatSettings')
  if (saved) {
    try {
      return JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load chat settings:', e)
    }
  }
  // Return defaults if no saved settings
  return {
    useRag: false,
    maxOutputTokens: 2048,
  }
}

// Chat settings with RAG configuration
const chatSettings = ref<ChatSettingsType>(loadChatSettings())

// Watch for login state changes - disable RAG if user logs out
watch(isLoggedIn, (newValue) => {
  if (!newValue && chatSettings.value.useRag) {
    // User logged out while RAG was enabled, disable it
    chatSettings.value.useRag = false
    localStorage.setItem('chatSettings', JSON.stringify(chatSettings.value))
  }
})

const messages = ref<Message[]>([
  { id: '1', text: 'Hello! How can I help you today?', sender: 'bot' },
])
const currentMessage = ref('')
const loading = ref(false)
const sidebarOpen = ref(window.innerWidth >= 768)
const endOfMessages = ref<HTMLElement | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const modalType = ref('')
const modalTitle = ref('')
const chatHistories = ref<ChatHistoryItem[]>([])
const currentChatId = ref<string | null>(null)
const formLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const streamingMessageId = ref<string | null>(null) // Track which message is currently streaming
const showScrollButton = ref(false) // Show/hide scroll to bottom button
const ragWarning = ref(false) // Warning when RAG is enabled but no documents found
let msgIdCounter = 2 // Temporary local counter for new messages (will be replaced with backend IDs)
let abortController: AbortController | null = null // Controller to abort ongoing requests

// Login form validation
const {
  handleSubmit: handleLoginSubmit,
  errors: loginErrors,
  resetForm: resetLoginForm,
} = useForm({
  validationSchema: loginSchema,
})
const { value: loginUsername } = useField<string>('username')
const { value: loginPassword } = useField<string>('password')

// Register form validation
const {
  handleSubmit: handleRegisterSubmit,
  errors: registerErrors,
  resetForm: resetRegisterForm,
} = useForm({
  validationSchema: registerSchema,
})
const { value: registerUsername } = useField<string>('username')
const { value: registerPassword } = useField<string>('password')
const { value: registerConfirmPassword } = useField<string>('confirmPassword')

// Forgot password form validation
const {
  handleSubmit: handleForgotPasswordSubmit,
  errors: forgotPasswordErrors,
  resetForm: resetForgotPasswordForm,
} = useForm({
  validationSchema: forgotPasswordSchema,
})
const { value: forgotPasswordUsername } = useField<string>('username')

// Password visibility toggles
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const showRegisterConfirmPassword = ref(false)

// Check if user is near bottom of messages container
const checkScrollPosition = () => {
  if (!messagesContainer.value) return

  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const threshold = 100 // Show button if more than 100px from bottom
  const isNearBottom = scrollHeight - scrollTop - clientHeight < threshold

  showScrollButton.value = !isNearBottom
}

// Load chat histories on mount (only if logged in)
onMounted(async () => {
  try {
    // Initialize Bootstrap modal
    const modalElement = document.getElementById('appModal')
    if (modalElement) {
      bootstrapModal = new Modal(modalElement)
    }

    // Add scroll listener to messages container
    if (messagesContainer.value) {
      messagesContainer.value.addEventListener('scroll', checkScrollPosition)
    }

    // Check if we have reset token in URL query params
    const token = route.query.token as string
    const username = route.query.username as string
    if (token && username) {
      // Redirect to reset password page
      router.push({
        path: '/reset-password',
        query: { token, username },
      })
      return
    }

    if (isLoggedIn.value) {
      await loadChatHistories()

      // Load the most recent chat if available
      if (chatHistories.value.length > 0 && chatHistories.value[0]) {
        const mostRecentChatId = chatHistories.value[0].id
        await loadChat(mostRecentChatId)
      }
    }
  } catch (error) {
    console.error('Failed to load chat histories:', error)
  }
})

// Cleanup on unmount
onUnmounted(() => {
  if (bootstrapModal) {
    bootstrapModal.dispose()
  }
  // Remove scroll listener
  if (messagesContainer.value) {
    messagesContainer.value.removeEventListener('scroll', checkScrollPosition)
  }
})

const scrollToBottom = async () => {
  await nextTick()
  if (endOfMessages.value) {
    endOfMessages.value.scrollIntoView({ behavior: 'smooth' })
  }
}

const stopMessage = () => {
  if (abortController) {
    abortController.abort()
    abortController = null
    loading.value = false
  }
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || loading.value) return

  const userMessageText = currentMessage.value

  messages.value.push({
    id: String(msgIdCounter++),
    text: userMessageText,
    sender: 'user',
  })

  currentMessage.value = ''
  loading.value = true

  // Create new AbortController for this request
  abortController = new AbortController()

  await scrollToBottom()

  // Create a new bot message that will be updated with streaming response
  const botMessageId = String(msgIdCounter++)
  streamingMessageId.value = botMessageId // Set streaming message ID for thinking animation
  messages.value.push({
    id: botMessageId,
    text: '',
    sender: 'bot',
  })

  try {
    // Build request payload with RAG settings
    const payload: any = {
      message: userMessageText,
    }

    // Add RAG parameters if enabled (only if user is logged in)
    if (chatSettings.value.useRag) {
      if (!isLoggedIn.value) {
        // User is not logged in, disable RAG for this request and show warning
        console.warn('RAG mode requires authentication. Sending request without RAG.')
        // Update bot message with warning
        const botMessage = messages.value.find((msg) => msg.id === botMessageId)
        if (botMessage) {
          botMessage.text =
            'RAG mode requires authentication. Please log in to use document search. Continuing without RAG...\n\n'
        }
        // Don't add RAG parameters
      } else {
        // User is logged in, add RAG parameters
        payload.use_rag = true
        payload.max_output_tokens = chatSettings.value.maxOutputTokens
      }
    }

    // use /chat/ but not /chat to prevent HTTP & HTTPS mixup errors (Dont know why this is needed) 
    const res = await fetch(`${import.meta.env.VITE_API_URL}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: abortController.signal,
      credentials: 'include', // Send cookies for authentication
    })

    // Ensure the response body is available and the request was successful
    if (!res.ok) {
      loading.value = false
      streamingMessageId.value = null // Clear streaming message ID
      // Try to parse error message from response
      let errorMessage = 'Sorry, there was an error processing your request.'
      try {
        const errorData = await res.json()
        if (errorData.detail) {
          errorMessage = errorData.detail
        }
      } catch (e) {
        console.error('Failed to parse error response:', e)
        errorMessage = `Error: ${res.statusText}`
      }
      console.error('Failed to get a streaming response:', errorMessage)

      // Update bot message with error
      const botMessage = messages.value.find((msg) => msg.id === botMessageId)
      if (botMessage) {
        botMessage.text = errorMessage
      }
      await scrollToBottom()
      // Save chat even on error
      await saveCurrentChat()
      return
    }

    if (!res.body) {
      loading.value = false
      streamingMessageId.value = null // Clear streaming message ID
      console.error('Response body is null')
      const botMessage = messages.value.find((msg) => msg.id === botMessageId)
      if (botMessage) {
        botMessage.text = 'Sorry, the server response was empty.'
      }
      await scrollToBottom()
      await saveCurrentChat()
      return
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })

      // Find and update the bot message
      const botMessage = messages.value.find((msg) => msg.id === botMessageId)
      if (botMessage) {
        botMessage.text += chunk
      }
    }

    // Final decoding step in case of partial characters at the end
    const finalChunk = decoder.decode()
    const botMessage = messages.value.find((msg) => msg.id === botMessageId)
    if (botMessage && finalChunk) {
      botMessage.text += finalChunk
    }

    loading.value = false
    streamingMessageId.value = null // Clear streaming message ID
    await scrollToBottom()

    // Save chat after successful message exchange
    await saveCurrentChat()
  } catch (error: any) {
    console.error('Error sending message:', error)
    loading.value = false
    streamingMessageId.value = null // Clear streaming message ID

    // Check if the request was aborted by user
    if (error.name === 'AbortError') {
      // Update bot message to indicate request was cancelled
      const botMessage = messages.value.find((msg) => msg.id === botMessageId)
      if (botMessage) {
        botMessage.text = botMessage.text || 'Request cancelled.'
      }
    } else {
      // Update bot message with error
      const botMessage = messages.value.find((msg) => msg.id === botMessageId)
      if (botMessage) {
        botMessage.text = 'Sorry, there was an error connecting to the server.'
      }
    }
    await scrollToBottom()

    // Save chat even on error
    await saveCurrentChat()
  } finally {
    // Clean up abort controller
    abortController = null
  }
}

const loadChatHistories = async () => {
  try {
    if (!isLoggedIn.value) {
      chatHistories.value = []
      return
    }
    chatHistories.value = await chatApi.getChatHistories()
  } catch (error) {
    console.error('Failed to load chat histories:', error)
    chatHistories.value = []
  }
}

const saveCurrentChat = async () => {
  try {
    // Only save if logged in
    if (!isLoggedIn.value) {
      return
    }

    // Only save if there are messages beyond the initial greeting
    if (messages.value.length <= 1) {
      return
    }

    // Generate title from first user message
    const firstUserMessage = messages.value.find((msg) => msg.sender === 'user')
    const title =
      firstUserMessage && firstUserMessage.text
        ? firstUserMessage.text.trim().substring(0, 50) +
        (firstUserMessage.text.length > 50 ? '...' : '')
        : 'New Chat'

    const savedChat = await chatApi.saveChatHistory({
      chat_id: currentChatId.value || undefined,
      title,
      messages: messages.value,
    })

    // Update current chat ID if it was a new chat
    if (!currentChatId.value) {
      currentChatId.value = savedChat.id
    }

    await loadChatHistories()
  } catch (error) {
    console.error('Failed to save chat:', error)
  }
}

const loadChat = async (chatId: string) => {
  try {
    // Save current chat before loading a new one
    await saveCurrentChat()

    const chat = await chatApi.getChatDetail(chatId)
    if (chat) {
      messages.value = chat.messages
      currentChatId.value = chat.id
      // Reset counter for new temporary messages
      msgIdCounter = 2
      // Wait for next tick to ensure DOM is updated, then scroll
      await nextTick()
      await scrollToBottom()
    }
  } catch (error) {
    console.error('Failed to load chat:', error)
  }
}

const deleteChat = async (chatId: string) => {
  try {
    // If we're deleting the current chat, clear it first before deleting
    if (currentChatId.value === chatId) {
      // Reset current chat state without saving
      messages.value = [{ id: '1', text: 'Hello! How can I help you today?', sender: 'bot' }]
      currentMessage.value = ''
      currentChatId.value = null
      msgIdCounter = 2
    }

    // Delete from PostgreSQL
    await chatApi.deleteChatHistory(chatId)
    await loadChatHistories()
  } catch (error) {
    console.error('Failed to delete chat:', error)
  }
}

const newChat = async () => {
  // Save current chat before starting a new one (only if it has content)
  await saveCurrentChat()

  // Reset to initial state
  messages.value = [{ id: '1', text: 'Hello! How can I help you today?', sender: 'bot' }]
  currentMessage.value = ''
  currentChatId.value = null
  msgIdCounter = 2
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const handleLogout = async () => {
  // Save current chat before logging out
  await saveCurrentChat()

  userStore.logout()

  // Clear chat histories and reset to initial state
  chatHistories.value = []
  messages.value = [{ id: '1', text: 'Hello! How can I help you today?', sender: 'bot' }]
  currentMessage.value = ''
  currentChatId.value = null
  msgIdCounter = 2

  appendAlert('You have been logged out successfully', 'info')
}

const showModal = (type: string) => {
  modalType.value = type

  if (type === 'login') {
    modalTitle.value = 'Login'
  } else if (type === 'register') {
    modalTitle.value = 'Register'
  } else if (type === 'settings') {
    modalTitle.value = 'Settings'
  } else if (type === 'documents') {
    modalTitle.value = 'Document Library'
  } else if (type === 'forgot-password') {
    modalTitle.value = 'Forgot Password'
  }

  // Show Bootstrap modal
  if (bootstrapModal) {
    bootstrapModal.show()
  }
}

const showForgotPasswordModal = () => {
  errorMessage.value = ''
  successMessage.value = ''
  resetForgotPasswordForm()

  // Close current modal and show forgot password modal
  if (bootstrapModal) {
    bootstrapModal.hide()
  }

  // Wait a bit for the modal to close before opening new one
  setTimeout(() => {
    showModal('forgot-password')
  }, 300)
}

const showDocumentManager = () => {
  // Simply change the modal type without closing/reopening
  modalType.value = 'documents'
  modalTitle.value = 'Document Library'
}

const closeModal = () => {
  errorMessage.value = ''
  successMessage.value = ''
  formLoading.value = false
  resetLoginForm()
  resetRegisterForm()
  resetForgotPasswordForm()

  // Reset password visibility toggles
  showLoginPassword.value = false
  showRegisterPassword.value = false
  showRegisterConfirmPassword.value = false

  // Hide Bootstrap modal
  if (bootstrapModal) {
    bootstrapModal.hide()
  }
}

const handleLogin = handleLoginSubmit(async (values) => {
  try {
    formLoading.value = true
    errorMessage.value = ''

    await userStore.login({
      username: values.username,
      password: values.password,
    })

    // Show success message
    appendAlert(`Welcome back, ${userStore.user.username}!`, 'success')
    closeModal()

    // Load chat histories after login
    await loadChatHistories()
  } catch (error: any) {
    console.error('Login error:', error)
    if (error.response?.status === 403) {
      // Email verification required
      errorMessage.value = error.response?.data?.detail || 'Please verify your email before logging in.'
    } else if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else if (error.response?.status === 401) {
      errorMessage.value = 'Invalid username or password'
    } else {
      errorMessage.value = 'Failed to login. Please try again.'
    }
  } finally {
    formLoading.value = false
  }
})

const handleRegister = handleRegisterSubmit(async (values) => {
  try {
    formLoading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    const response = await userApi.register({
      username: values.username,
      password: values.password,
    })

    // Show success message - user needs to verify email
    successMessage.value = response.message

    // Clear form
    resetRegisterForm()

    // Close modal after 3 seconds
    setTimeout(() => {
      closeModal()
    }, 3000)
  } catch (error: any) {
    console.error('Registration error:', error)
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else if (error.response?.status === 409) {
      errorMessage.value = 'Username already exists'
    } else {
      errorMessage.value = 'Failed to register. Please try again.'
    }
  } finally {
    formLoading.value = false
  }
})

const handleForgotPassword = handleForgotPasswordSubmit(async (values) => {
  try {
    formLoading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    const response = await userApi.forgotPassword({
      username: values.username,
    })

    successMessage.value = response.message

    // Clear form
    resetForgotPasswordForm()
  } catch (error: any) {
    console.error('Forgot password error:', error)
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'Failed to send reset link. Please try again.'
    }
  } finally {
    formLoading.value = false
  }
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 0;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Mobile: Sidebar overlay on small screens */
@media (max-width: 768px) {
  .main-container {
    border-radius: 0;
  }
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(to right, #fff, #f9fafb);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

@media (max-width: 768px) {
  .header {
    padding: 12px 16px;
  }
}

.menu-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-btn:hover {
  background-color: #f3f4f6;
  transform: scale(1.05);
}

.menu-btn:active {
  transform: scale(0.95);
}

.menu-btn svg {
  width: 24px;
  height: 24px;
  stroke: #374151;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.5px;
}

@media (max-width: 768px) {
  .header-title {
    font-size: 18px;
  }
}

.spacer {
  width: 40px;
}

@media (max-width: 768px) {
  .spacer {
    width: 0;
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px 16px;
  display: flex;
  justify-content: center;
  background: linear-gradient(to bottom, #f9fafb, #ffffff);
  position: relative;
}

@media (min-width: 769px) {
  .messages-container {
    padding: 32px 24px;
  }
}

@media (min-width: 1024px) {
  .messages-container {
    padding: 40px 32px;
  }
}

.messages-wrapper {
  max-width: 700px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (min-width: 1024px) {
  .messages-wrapper {
    max-width: 800px;
  }
}

.message-group {
  display: flex;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-group.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 85%;
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .message-bubble {
    max-width: 90%;
    padding: 12px 16px;
    font-size: 14px;
  }
}

.message-bubble:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.message-group.bot .message-bubble {
  background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
  color: #1f2937;
  border: 1px solid #e5e7eb;
  border-radius: 16px 16px 16px 4px;
}

.message-group.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 4px 16px;
}

/* Thinking/Processing animation for bot messages */
.message-bubble.thinking {
  position: relative;
  border: 2px solid transparent;
  background:
    linear-gradient(135deg, #ffffff 0%, #f9fafb 100%) padding-box,
    linear-gradient(90deg, #667eea, #764ba2, #667eea) border-box;
  background-size:
    100%,
    300% 100%;
  animation:
    thinkingBorder 2s linear infinite,
    thinkingPulse 2s ease-in-out infinite;
}

@keyframes thinkingBorder {
  0% {
    background-position:
      0% 0%,
      0% 0%;
  }

  100% {
    background-position:
      0% 0%,
      300% 0%;
  }
}

@keyframes thinkingPulse {

  0%,
  100% {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transform: scale(1);
  }

  50% {
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    transform: scale(1.01);
  }
}

/* Thinking dots animation */
.thinking-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 4px;
}

.thinking-dots .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #667eea;
  animation: dotBounce 1.4s infinite ease-in-out;
}

.thinking-dots .dot:nth-child(1) {
  animation-delay: 0s;
}

.thinking-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotBounce {

  0%,
  60%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }

  30% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-radius: 16px 16px 16px 4px;
  width: fit-content;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #6b7280;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: 0s;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {

  0%,
  60%,
  100% {
    opacity: 0.3;
    transform: translateY(0);
  }

  30% {
    opacity: 1;
    transform: translateY(-8px);
  }
}

.input-area {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: linear-gradient(to top, #ffffff, #f9fafb);
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.04);
}

@media (min-width: 769px) {
  .input-area {
    padding: 20px 24px 24px;
  }
}

.rag-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.15);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.85;
  }
}

@media (max-width: 768px) {
  .rag-indicator {
    font-size: 12px;
    padding: 6px 12px;
  }
}

.input-wrapper {
  max-width: 700px;
  width: 100%;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

@media (min-width: 1024px) {
  .input-wrapper {
    max-width: 800px;
  }
}

.input-field {
  flex: 1;
  padding: 14px 18px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  transition: all 0.2s ease;
  resize: none;
  max-height: 120px;
  background: #fff;
}

@media (max-width: 768px) {
  .input-field {
    padding: 12px 16px;
    font-size: 14px;
  }
}

.input-field:hover:not(:disabled) {
  border-color: #d1d5db;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.input-field:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.6;
}

.send-btn {
  width: 48px;
  height: 48px;
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-btn.stop-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.send-btn.stop-btn:hover:not(:disabled) {
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

@media (max-width: 768px) {
  .send-btn {
    width: 44px;
    height: 44px;
  }
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.send-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  opacity: 0.5;
  box-shadow: none;
}

.send-btn svg {
  width: 22px;
  height: 22px;
  stroke: white;
  stroke-width: 2;
}

@media (max-width: 768px) {
  .send-btn svg {
    width: 20px;
    height: 20px;
  }
}

/* Bootstrap Modal Custom Styles */
.modal-dialog {
  margin: 1.75rem auto;
  max-width: 500px;
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
}

.modal-dialog.modal-lg {
  max-width: 800px;
}

@media (max-width: 768px) {
  .modal-dialog.modal-lg {
    max-width: calc(100% - 1rem);
  }
}

.modal-dialog-centered {
  display: flex;
  align-items: center;
  min-height: calc(100% - 3.5rem);
}

@media (max-width: 768px) {
  .modal-dialog-centered {
    min-height: calc(100% - 1rem);
  }
}

.modal-content {
  border: none;
  border-radius: 16px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(0, 0, 0, 0.05);
  margin: 0 auto;
  width: 100%;
  overflow: hidden;
}

@media (max-width: 768px) {
  .modal-content {
    border-radius: 12px;
  }
}

.modal-header {
  padding: 24px 28px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(to right, #fff, #f9fafb);
}

@media (max-width: 768px) {
  .modal-header {
    padding: 20px 20px;
  }
}

.modal-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.5px;
}

@media (max-width: 768px) {
  .modal-title {
    font-size: 18px;
  }
}

.modal-body {
  padding: 28px;
  max-height: 70vh;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .modal-body {
    padding: 20px;
    max-height: 60vh;
  }
}

.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.modal-body::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
}

.btn-close {
  padding: 8px;
  opacity: 0.5;
  transition: all 0.2s ease;
  border-radius: 8px;
}

.btn-close:hover {
  opacity: 1;
  transform: scale(1.1);
  background-color: #f3f4f6;
}

.btn-close:focus {
  box-shadow: none;
}

/* Bootstrap fade animation override for smoother transition */
.modal.fade .modal-dialog {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Form Input Styles - Modern Theme */
.form-control {
  padding: 14px 18px;
  font-size: 15px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.2s ease;
  background-color: #fff;
  font-family: inherit;
}

.form-control.is-invalid {
  border-color: #dc2626;
}

.form-control.is-invalid:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.1);
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

.form-text {
  font-size: 13px;
  color: #6b7280;
  margin-top: 6px;
}

@media (max-width: 768px) {
  .form-text {
    font-size: 12px;
  }
}

/* Alert Styles */
.alert {
  border-radius: 12px;
  border: none;
  padding: 14px 18px;
  font-size: 14px;
  font-weight: 500;
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

/* Validation Feedback */
.invalid-feedback {
  color: #dc2626;
  font-size: 13px;
  margin-top: 6px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .invalid-feedback {
    font-size: 12px;
    margin-top: 4px;
  }
}

/* Forgot Password Link */
.forgot-password-link {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

@media (max-width: 768px) {
  .forgot-password-link {
    font-size: 13px;
  }
}

.forgot-password-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Modal Footer Styles */
.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 24px;
}

@media (max-width: 768px) {
  .modal-footer {
    padding-top: 20px;
    gap: 10px;
  }
}

/* Button Styles - Modern Theme */
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

.btn-primary:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
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

.btn-secondary:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(209, 213, 219, 0.3);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Spinner Styles */
.spinner-border-sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
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

/* Smooth scroll for messages container */
.messages-container {
  scroll-behavior: smooth;
}

/* Add custom scrollbar for messages container */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
}

/* Scroll to Bottom Button */
.scroll-to-bottom-btn {
  position: fixed;
  bottom: 120px;
  right: 32px;
  width: 48px;
  height: 48px;
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.3s ease-out;
}

@media (max-width: 768px) {
  .scroll-to-bottom-btn {
    bottom: 90px;
    right: 20px;
    width: 44px;
    height: 44px;
  }
}

.scroll-to-bottom-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

.scroll-to-bottom-btn:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.scroll-to-bottom-btn svg {
  width: 24px;
  height: 24px;
  stroke: white;
  stroke-width: 2.5;
}

@media (max-width: 768px) {
  .scroll-to-bottom-btn svg {
    width: 20px;
    height: 20px;
  }
}
</style>
