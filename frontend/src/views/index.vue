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
        Chat history would appear here
      </div>
    </div>

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
          <input v-model="currentMessage" @keypress.enter="sendMessage" type="text" class="input-field"
            placeholder="Message ChatGPT..." :disabled="loading" />
          <button @click="sendMessage" class="send-btn" :disabled="!currentMessage.trim() || loading">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const messages = ref([
  { id: 1, text: 'Hello! How can I help you today?', sender: 'bot' }
])
const currentMessage = ref('')
const loading = ref(false)
const sidebarOpen = ref(true)
const endOfMessages = ref(null)
let msgId = 2

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
    sender: 'user'
  })

  currentMessage.value = ''
  loading.value = true
  await scrollToBottom()

  setTimeout(async () => {
    messages.value.push({
      id: msgId++,
      text: 'This is a simulated response. In a real app, this would connect to an API.',
      sender: 'bot'
    })
    loading.value = false
    await scrollToBottom()
  }, 800)
}

const newChat = () => {
  messages.value = [
    { id: 1, text: 'Hello! How can I help you today?', sender: 'bot' }
  ]
  currentMessage.value = ''
  msgId = 2
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
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
</style>