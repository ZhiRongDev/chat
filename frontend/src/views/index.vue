<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar" :class="{ hidden: !sidebarOpen }">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="newChat">
          <span>+ New chat</span>
        </button>
      </div>
      <div class="sidebar-content">
        <div v-if="chatHistories.length === 0" class="no-history">No chat history yet</div>
        <div v-else class="chat-history-list">
          <div
            v-for="chat in chatHistories"
            :key="chat.id"
            class="chat-history-item"
            :class="{ active: currentChatId === chat.id }"
            @click="loadChat(chat.id)"
          >
            <div class="chat-history-title">{{ chat.title }}</div>
            <button class="delete-chat-btn" @click.stop="deleteChat(chat.id)" title="Delete chat">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                ></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      <div class="sidebar-footer">
        <div v-if="userStore.user.username" class="user-info">
          <div class="user-avatar">{{ userStore.user.username.charAt(0).toUpperCase() }}</div>
          <div class="user-details">
            <div class="user-name">{{ userStore.user.username }}</div>
            <button class="logout-link" @click="handleLogout">Logout</button>
          </div>
        </div>
        <template v-else>
          <button class="sidebar-btn" @click="showModal('login')">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
              ></path>
            </svg>
            <span>Login</span>
          </button>
          <button class="sidebar-btn" @click="showModal('register')">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
              ></path>
            </svg>
            <span>Register</span>
          </button>
        </template>
        <button class="sidebar-btn" @click="showModal('settings')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            ></path>
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            ></path>
          </svg>
          <span>Settings</span>
        </button>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="main-container">
      <!-- Header -->
      <div class="header">
        <button class="menu-btn" @click="toggleSidebar">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            ></path>
          </svg>
        </button>
        <div class="header-title">ChatGPT</div>
        <div class="spacer"></div>
      </div>

      <!-- Messages -->
      <div class="messages-container">
        <div class="messages-wrapper">
          <div
            v-for="(msg, index) in messages"
            :key="msg.id || index"
            class="message-group"
            :class="msg.sender"
          >
            <div class="message-bubble">
              {{ msg.text }}
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
        <div class="input-wrapper">
          <input
            v-model="currentMessage"
            @keypress.enter="sendMessage"
            type="text"
            class="input-field"
            placeholder="Message ChatGPT..."
            :disabled="loading"
          />
          <button
            @click="sendMessage"
            class="send-btn"
            :disabled="!currentMessage.trim() || loading"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              ></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="modalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ modalTitle }}</h2>
          <button class="close-btn" @click="closeModal">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>

        <!-- Login Form -->
        <template v-if="modalType === 'login'">
          <div class="modal-body">
            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label for="login-username">Username</label>
                <input
                  v-model="loginForm.username"
                  type="text"
                  id="login-username"
                  placeholder="Enter your username"
                  required
                  :disabled="formLoading"
                />
              </div>
              <div class="form-group">
                <label for="login-password">Password</label>
                <input
                  v-model="loginForm.password"
                  type="password"
                  id="login-password"
                  placeholder="Enter your password"
                  required
                  :disabled="formLoading"
                />
              </div>
              <div class="modal-footer">
                <button type="submit" class="modal-btn-confirm" :disabled="formLoading">
                  {{ formLoading ? 'Logging in...' : 'Login' }}
                </button>
                <button
                  type="button"
                  class="modal-btn-cancel"
                  @click="closeModal"
                  :disabled="formLoading"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </template>

        <!-- Register Form -->
        <template v-if="modalType === 'register'">
          <div class="modal-body">
            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
            <form @submit.prevent="handleRegister">
              <div class="form-group">
                <label for="register-username">Username</label>
                <input
                  v-model="registerForm.username"
                  type="text"
                  id="register-username"
                  placeholder="Enter your username"
                  required
                  :disabled="formLoading"
                />
              </div>
              <div class="form-group">
                <label for="register-password">Password</label>
                <input
                  v-model="registerForm.password"
                  type="password"
                  id="register-password"
                  placeholder="Enter your password"
                  required
                  :disabled="formLoading"
                />
              </div>
              <div class="form-group">
                <label for="register-confirm">Confirm Password</label>
                <input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  id="register-confirm"
                  placeholder="Confirm your password"
                  required
                  :disabled="formLoading"
                />
              </div>
              <div class="modal-footer">
                <button type="submit" class="modal-btn-confirm" :disabled="formLoading">
                  {{ formLoading ? 'Registering...' : 'Register' }}
                </button>
                <button
                  type="button"
                  class="modal-btn-cancel"
                  @click="closeModal"
                  :disabled="formLoading"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </template>

        <!-- Settings -->
        <template v-if="modalType === 'settings'">
          <div class="modal-body">
            <p>{{ modalContent }}</p>
            <div class="modal-footer">
              <button class="modal-btn-cancel" @click="closeModal">Cancel</button>
              <button class="modal-btn-confirm">Confirm</button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { chatApi, type Message, type ChatHistoryItem } from '@/api/chat'

const userStore = useUserStore()
const isLoggedIn = computed(() => !!userStore.user.username)

const messages = ref<Message[]>([
  { id: '1', text: 'Hello! How can I help you today?', sender: 'bot' },
])
const currentMessage = ref('')
const loading = ref(false)
const sidebarOpen = ref(true)
const endOfMessages = ref<HTMLElement | null>(null)
const modalOpen = ref(false)
const modalType = ref('')
const modalTitle = ref('')
const modalContent = ref('')
const chatHistories = ref<ChatHistoryItem[]>([])
const currentChatId = ref<string | null>(null)
const formLoading = ref(false)
const errorMessage = ref('')
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

// Load chat histories on mount (only if logged in)
onMounted(async () => {
  try {
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
    const res = await fetch('http://localhost:5000/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessageText }),
    })

    // Ensure the response body is available and the request was successful
    if (!res.body || !res.ok) {
      loading.value = false
      console.error('Failed to get a streaming response:', res.statusText)
      // Update bot message with error
      const botMessage = messages.value.find((msg) => msg.id === botMessageId)
      if (botMessage) {
        botMessage.text = 'Sorry, there was an error processing your request.'
      }
      await scrollToBottom()
      // Save chat even on error
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

  alert('You have been logged out successfully')
}

const showModal = (type: string) => {
  modalType.value = type
  modalOpen.value = true

  if (type === 'login') {
    modalTitle.value = 'Login'
    modalContent.value = 'Enter your credentials to login'
  } else if (type === 'register') {
    modalTitle.value = 'Register'
    modalContent.value = 'Create a new account'
  } else if (type === 'settings') {
    modalTitle.value = 'Settings'
    modalContent.value = 'Manage your preferences'
  }
}

const closeModal = () => {
  modalOpen.value = false
  errorMessage.value = ''
  formLoading.value = false
  loginForm.value = { username: '', password: '' }
  registerForm.value = { username: '', password: '', confirmPassword: '' }
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
    alert(`Welcome back, ${userStore.user.username}!`)
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

    await userStore.register({
      username: registerForm.value.username,
      password: registerForm.value.password,
    })

    // Show success and auto-login
    alert(`Registration successful! Please login with your credentials.`)
    closeModal()
    // Switch to login modal
    showModal('login')
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

.sidebar {
  width: 260px;
  background-color: #1a1a1a;
  color: white;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border-right: 1px solid #333;
  overflow: hidden;
}

.sidebar.hidden {
  width: 0;
  border-right: none;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #333;
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 6px;
  background-color: #2a2a2a;
  color: white;
  border: 1px solid #444;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background-color: #333;
  border-color: #555;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  font-size: 13px;
  color: #888;
}

.no-history {
  padding: 16px;
  text-align: center;
  color: #666;
  font-size: 13px;
}

.chat-history-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: transparent;
  position: relative;
  gap: 8px;
}

.chat-history-item:hover {
  background-color: #2a2a2a;
}

.chat-history-item.active {
  background-color: #333;
}

.chat-history-title {
  flex: 1;
  font-size: 13px;
  color: #ccc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-history-item:hover .chat-history-title,
.chat-history-item.active .chat-history-title {
  color: white;
}

.delete-chat-btn {
  width: 24px;
  height: 24px;
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s;
  flex-shrink: 0;
}

.chat-history-item:hover .delete-chat-btn {
  opacity: 1;
}

.delete-chat-btn:hover {
  background-color: #ff4444;
}

.delete-chat-btn svg {
  width: 16px;
  height: 16px;
  stroke: #ccc;
}

.delete-chat-btn:hover svg {
  stroke: white;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid #333;
}

.sidebar-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background-color: transparent;
  color: #ccc;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.sidebar-btn:hover {
  background-color: #2a2a2a;
  color: white;
}

.sidebar-btn svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
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
  max-width: 500px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-group.bot .message-bubble {
  background-color: #f0f0f0;
  color: #000;
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
  justify-content: center;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal {
  display: block;
  background: white;
  border-radius: 12px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(0, 0, 0, 0.05);
  max-width: 440px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

.modal-body {
  padding: 24px;
  max-height: calc(90vh - 160px);
  overflow-y: auto;
  overflow-x: hidden;
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

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #111;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  border-radius: 6px;
  color: #666;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #111;
}

.close-btn:active {
  transform: scale(0.95);
}

.close-btn svg {
  width: 20px;
  height: 20px;
  stroke: currentColor;
}

.modal-content {
  padding: 20px;
  color: #666;
  font-size: 14px;
  display: flex;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  justify-content: flex-end;
}

.modal-btn-cancel {
  padding: 10px 20px;
  background-color: white;
  color: #333;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.modal-btn-cancel:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

.modal-btn-cancel:active {
  transform: scale(0.98);
}

.modal-btn-confirm {
  padding: 10px 20px;
  background-color: #111;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.modal-btn-confirm:hover {
  background-color: #000;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-btn-confirm:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.form-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
}

.form-group:last-of-type {
  margin-bottom: 0;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #111;
  margin-bottom: 8px;
}

.form-group input {
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.15s ease;
  background-color: #fff;
}

.form-group input:hover {
  border-color: #d1d5db;
}

.form-group input:focus {
  outline: none;
  border-color: #111;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.modal-content form {
  display: flex;
  flex-direction: column;
}

.modal-footer {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  padding-top: 0;
  border-top: none;
  justify-content: flex-start;
}

.modal-footer button {
  flex: 1;
}

.modal-footer button:first-child {
  order: 1;
}

.modal-footer button:last-child {
  order: 2;
}

.error-message {
  padding: 12px 16px;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
  color: #c33;
  font-size: 14px;
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #2a2a2a;
  border-radius: 8px;
  margin-bottom: 8px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  color: white;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.logout-link {
  background: none;
  border: none;
  color: #999;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.logout-link:hover {
  color: #fff;
  text-decoration: underline;
}

.modal-btn-confirm:disabled,
.modal-btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
