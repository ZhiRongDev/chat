<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar" :class="{ hidden: !sidebarOpen }">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="newChat">
          <span>+ New chat</span>
        </button>
      </div>
      <div class="sidebar-content">Chat history would appear here</div>
      <div class="sidebar-footer">
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
          <div v-for="msg in messages" :key="msg.id" class="message-group" :class="msg.sender">
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
            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label for="login-email">Email</label>
                <input
                  v-model="loginForm.email"
                  type="email"
                  id="login-email"
                  placeholder="Enter your email"
                  required
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
                />
              </div>
              <div class="modal-footer">
                <button type="submit" class="modal-btn-confirm">Login</button>
                <button type="button" class="modal-btn-cancel" @click="closeModal">Cancel</button>
              </div>
            </form>
          </div>
        </template>

        <!-- Register Form -->
        <template v-if="modalType === 'register'">
          <div class="modal-body">
            <form @submit.prevent="handleRegister">
              <div class="form-group">
                <label for="register-name">Full Name</label>
                <input
                  v-model="registerForm.name"
                  type="text"
                  id="register-name"
                  placeholder="Enter your full name"
                  required
                />
              </div>
              <div class="form-group">
                <label for="register-email">Email</label>
                <input
                  v-model="registerForm.email"
                  type="email"
                  id="register-email"
                  placeholder="Enter your email"
                  required
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
                />
              </div>
              <div class="modal-footer">
                <button type="submit" class="modal-btn-confirm">Register</button>
                <button type="button" class="modal-btn-cancel" @click="closeModal">Cancel</button>
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

<script setup>
import { ref, nextTick } from 'vue'

const messages = ref([{ id: 1, text: 'Hello! How can I help you today?', sender: 'bot' }])
const currentMessage = ref('')
const loading = ref(false)
const sidebarOpen = ref(true)
const endOfMessages = ref(null)
const modalOpen = ref(false)
const modalType = ref('')
const modalTitle = ref('')
const modalContent = ref('')
let msgId = 2

const loginForm = ref({
  email: '',
  password: '',
})

const registerForm = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const scrollToBottom = async () => {
  await nextTick()
  if (endOfMessages.value) {
    endOfMessages.value.scrollIntoView({ behavior: 'smooth' })
  }
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || loading.value) return

  messages.value.push({
    id: msgId++,
    text: currentMessage.value,
    sender: 'user',
  })

  currentMessage.value = ''
  loading.value = true
  await scrollToBottom()

  setTimeout(async () => {
    messages.value.push({
      id: msgId++,
      text: 'This is a simulated response. In a real app, this would connect to an API.',
      sender: 'bot',
    })
    loading.value = false
    await scrollToBottom()
  }, 800)
}

const newChat = () => {
  messages.value = [{ id: 1, text: 'Hello! How can I help you today?', sender: 'bot' }]
  currentMessage.value = ''
  msgId = 2
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const showModal = (type) => {
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
  loginForm.value = { email: '', password: '' }
  registerForm.value = { name: '', email: '', password: '', confirmPassword: '' }
}

const handleLogin = () => {
  if (loginForm.value.email && loginForm.value.password) {
    alert(`Login successful for ${loginForm.value.email}`)
    closeModal()
  }
}

const handleRegister = () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    alert('Passwords do not match!')
    return
  }
  if (registerForm.value.name && registerForm.value.email && registerForm.value.password) {
    alert(`Registration successful for ${registerForm.value.name}`)
    closeModal()
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
  padding: 16px;
  font-size: 13px;
  color: #888;
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
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(0, 0, 0, 0.05);
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
</style>
