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
        <div class="header-title">ChatGPT</div>
        <div class="spacer"></div>
      </div>

      <!-- Messages -->
      <div class="messages-container">
        <div class="messages-wrapper">
          <div v-for="(msg, index) in messages" :key="msg.id || index" class="message-group" :class="msg.sender">
            <div class="message-bubble">
              <MarkdownRenderer v-if="msg.sender === 'bot'" :content="msg.text" />
              <span v-else>{{ msg.text }}</span>
            </div>
          </div>

          <div v-if="loading" class="message-group bot">
            <div class="typing-indicator">
              <div class="typing-dot"></div>
              <div class="typing-dot"></div>
              <div class="typing-dot"></div>
            </div>
          </div>

          <div ref="endOfMessages"></div>
        </div>
      </div>

      <!-- Input -->
      <div class="input-area">
        <div v-if="chatSettings.useRag" class="rag-indicator">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style="width: 16px; height: 16px;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4">
            </path>
          </svg>
          Gemini File Search RAG Active
        </div>
        <div class="input-wrapper">
          <input v-model="currentMessage" @keypress.enter="sendMessage" type="text" class="input-field"
            placeholder="Message ChatGPT..." :disabled="loading" />
          <button @click="sendMessage" class="send-btn" :disabled="!currentMessage.trim() || loading">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8">
              </path>
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
                  <input v-model="loginForm.username" type="text" class="form-control" id="login-username"
                    placeholder="Enter your username" required :disabled="formLoading" />
                </div>
                <div class="mb-3">
                  <label for="login-password" class="form-label">Password</label>
                  <input v-model="loginForm.password" type="password" class="form-control" id="login-password"
                    placeholder="Enter your password" required :disabled="formLoading" />
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
                  <input v-model="registerForm.username" type="text" class="form-control" id="register-username"
                    placeholder="Enter your username" required :disabled="formLoading" />
                </div>
                <div class="mb-3">
                  <label for="register-password" class="form-label">Password</label>
                  <input v-model="registerForm.password" type="password" class="form-control" id="register-password"
                    placeholder="Enter your password" required :disabled="formLoading" />
                </div>
                <div class="mb-3">
                  <label for="register-confirm" class="form-label">Confirm Password</label>
                  <input v-model="registerForm.confirmPassword" type="password" class="form-control"
                    id="register-confirm" placeholder="Confirm your password" required :disabled="formLoading" />
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
                  <input v-model="forgotPasswordForm.username" type="text" class="form-control mb-2" id="forgot-username"
                    placeholder="Enter your username/email" required :disabled="formLoading" />
                  <div class="form-text">We'll send a password reset link to your email address.</div>
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
            <div class="modal-body p-0" style="max-height: 70vh; overflow-y: auto;">
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
    provider: '',
    model: '',
    temperature: 0.7,
    geminiApiKey: '',
    openaiApiKey: '',
    anthropicApiKey: '',
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
const sidebarOpen = ref(true)
const endOfMessages = ref<HTMLElement | null>(null)
const modalType = ref('')
const modalTitle = ref('')
const chatHistories = ref<ChatHistoryItem[]>([])
const currentChatId = ref<string | null>(null)
const formLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
let msgIdCounter = 2  // Temporary local counter for new messages (will be replaced with backend IDs)

const loginForm = ref({
  username: '',
  password: '',
})

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
})

const forgotPasswordForm = ref({
  username: '',
})

// Load chat histories on mount (only if logged in)
onMounted(async () => {
  try {
    // Initialize Bootstrap modal
    const modalElement = document.getElementById('appModal')
    if (modalElement) {
      bootstrapModal = new Modal(modalElement)
    }

    // Check if we have reset token in URL query params
    const token = route.query.token as string
    const username = route.query.username as string
    if (token && username) {
      // Redirect to reset password page
      router.push({
        path: '/reset-password',
        query: { token, username }
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
})

const scrollToBottom = async () => {
  await nextTick()
  if (endOfMessages.value) {
    endOfMessages.value.scrollIntoView({ behavior: 'smooth' })
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
  await scrollToBottom()

  // Create a new bot message that will be updated with streaming response
  const botMessageId = String(msgIdCounter++)
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
          botMessage.text = 'RAG mode requires authentication. Please log in to use document search. Continuing without RAG...\n\n'
        }
        // Don't add RAG parameters
      } else {
        // User is logged in, add RAG parameters
        payload.use_rag = true
        payload.max_output_tokens = chatSettings.value.maxOutputTokens
      }
    }

    // Add LLM provider settings if specified
    if (chatSettings.value.provider) {
      payload.provider = chatSettings.value.provider
    }
    if (chatSettings.value.model) {
      payload.model = chatSettings.value.model
    }
    if (chatSettings.value.temperature !== 0.7) {
      payload.temperature = chatSettings.value.temperature
    }

    // Add API keys if provided
    if (chatSettings.value.geminiApiKey) {
      payload.gemini_api_key = chatSettings.value.geminiApiKey
    }
    if (chatSettings.value.openaiApiKey) {
      payload.openai_api_key = chatSettings.value.openaiApiKey
    }
    if (chatSettings.value.anthropicApiKey) {
      payload.anthropic_api_key = chatSettings.value.anthropicApiKey
    }

    // Build headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    // Add authorization token if user is logged in (for personal RAG store)
    const token = localStorage.getItem('token')
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const res = await fetch('http://localhost:5000/api/v1/chat', {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    })

    // Ensure the response body is available and the request was successful
    if (!res.ok) {
      loading.value = false
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

      await nextTick()
      await scrollToBottom()
    }

    // Final decoding step in case of partial characters at the end
    const finalChunk = decoder.decode()
    const botMessage = messages.value.find((msg) => msg.id === botMessageId)
    if (botMessage && finalChunk) {
      botMessage.text += finalChunk
    }

    loading.value = false
    await scrollToBottom()

    // Save chat after successful message exchange
    await saveCurrentChat()
  } catch (error) {
    console.error('Error sending message:', error)
    loading.value = false
    // Update bot message with error
    const botMessage = messages.value.find((msg) => msg.id === botMessageId)
    if (botMessage) {
      botMessage.text = 'Sorry, there was an error connecting to the server.'
    }
    await scrollToBottom()

    // Save chat even on error
    await saveCurrentChat()
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
    console.log('saveCurrentChat called, messages count:', messages.value.length)

    // Only save if logged in
    if (!isLoggedIn.value) {
      console.log('Skipping save - user not logged in')
      return
    }

    // Only save if there are messages beyond the initial greeting
    if (messages.value.length <= 1) {
      console.log('Skipping save - not enough messages')
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
      console.log('Generated new chat ID:', currentChatId.value)
    }

    console.log('Saved chat history:', savedChat)
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
  forgotPasswordForm.value = { username: '' }

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
  loginForm.value = { username: '', password: '' }
  registerForm.value = { username: '', password: '', confirmPassword: '' }
  forgotPasswordForm.value = { username: '' }

  // Hide Bootstrap modal
  if (bootstrapModal) {
    bootstrapModal.hide()
  }
}

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    errorMessage.value = 'Please enter username and password'
    return
  }

  try {
    formLoading.value = true
    errorMessage.value = ''

    await userStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password,
    })

    // Show success message
    appendAlert(`Welcome back, ${userStore.user.username}!`, 'success')
    closeModal()

    // Load chat histories after login
    await loadChatHistories()
  } catch (error: any) {
    console.error('Login error:', error)
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else if (error.response?.status === 401) {
      errorMessage.value = 'Invalid username or password'
    } else {
      errorMessage.value = 'Failed to login. Please try again.'
    }
  } finally {
    formLoading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    errorMessage.value = 'Please fill in all fields'
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    errorMessage.value = 'Passwords do not match!'
    return
  }

  if (registerForm.value.password.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters long'
    return
  }

  try {
    formLoading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    const response = await userApi.register({
      username: registerForm.value.username,
      password: registerForm.value.password,
    })

    // Show success message - user needs to verify email
    successMessage.value = response.message
    appendAlert(response.message, 'success')

    // Clear form
    registerForm.value = { username: '', password: '', confirmPassword: '' }

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
}

const handleForgotPassword = async () => {
  if (!forgotPasswordForm.value.username) {
    errorMessage.value = 'Please enter your username/email'
    return
  }

  try {
    formLoading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    const response = await userApi.forgotPassword({
      username: forgotPasswordForm.value.username,
    })

    successMessage.value = response.message
    appendAlert(response.message, 'success')

    // Clear form
    forgotPasswordForm.value.username = ''
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
}
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
  background: #fff;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.menu-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-btn:hover {
  background-color: #f3f4f6;
}

.menu-btn svg {
  width: 24px;
  height: 24px;
  stroke: #000;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #000;
}

.spacer {
  width: 40px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 32px 24px;
  display: flex;
  justify-content: center;
  background: #fff;
}

.messages-wrapper {
  max-width: 700px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-group {
  display: flex;
  margin-bottom: 8px;
}

.message-group.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 600px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-group.bot .message-bubble {
  background-color: #f9fafb;
  color: #000;
  border: 1px solid #e5e7eb;
}

.message-group.user .message-bubble {
  background-color: #2563eb;
  color: white;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background-color: #f0f0f0;
  border-radius: 8px;
  width: fit-content;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  animation: bounce 1.4s infinite;
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
  padding: 16px 24px 24px;
  border-top: 1px solid #e5e7eb;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rag-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
}

.input-wrapper {
  max-width: 700px;
  width: 100%;
  display: flex;
  gap: 12px;
}

.input-field {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 15px;
  font-family: inherit;
  transition: all 0.2s;
  resize: none;
  max-height: 100px;
}

.input-field:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.send-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.send-btn:disabled {
  background-color: #d1d5db;
  cursor: not-allowed;
  opacity: 0.5;
}

.send-btn svg {
  width: 20px;
  height: 20px;
  stroke: white;
  stroke-width: 2;
}

/* Bootstrap Modal Custom Styles */
.modal-dialog {
  margin: 1.75rem auto;
  max-width: 500px;
}

.modal-dialog.modal-lg {
  max-width: 800px;
}

.modal-dialog-centered {
  display: flex;
  align-items: center;
  min-height: calc(100% - 3.5rem);
}

.modal-content {
  border: none;
  border-radius: 12px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(0, 0, 0, 0.05);
  margin: 0 auto;
  width: 100%;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  background-color: #fff;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #111;
}

.modal-body {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.btn-close {
  padding: 8px;
  opacity: 0.5;
  transition: all 0.15s ease;
}

.btn-close:hover {
  opacity: 1;
  transform: scale(1.1);
}

.btn-close:focus {
  box-shadow: none;
}

/* Bootstrap fade animation override for smoother transition */
.modal.fade .modal-dialog {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Form Input Styles - Modern Dark Theme */
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

/* Forgot Password Link */
.forgot-password-link {
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s ease;
}

.forgot-password-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

/* Modal Footer Styles */
.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
}

/* Button Styles - Modern Dark Theme */
.btn {
  padding: 10px 20px;
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

.btn-primary:active:not(:disabled) {
  background-color: #1f2937;
  border-color: #1f2937;
}

.btn-primary:focus {
  outline: 2px solid #374151;
  outline-offset: 2px;
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

.btn-secondary:active:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.btn-secondary:focus {
  outline: 2px solid #d1d5db;
  outline-offset: 2px;
}

.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Spinner Styles */
.spinner-border-sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
}
</style>
