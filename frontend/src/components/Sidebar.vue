<template>
  <div class="sidebar" :class="{ hidden: !isOpen }">
    <div class="sidebar-header">
      <button class="new-chat-btn" @click="$emit('new-chat')">
        <span>+ New chat</span>
      </button>
    </div>
    <div class="sidebar-content">
      <div v-if="chatHistories.length === 0" class="no-history">No chat history yet</div>
      <div v-else class="chat-history-list">
        <div v-for="chat in chatHistories" :key="chat.id" class="chat-history-item"
          :class="{ active: currentChatId === chat.id }" @click="$emit('load-chat', chat.id)">
          <div class="chat-history-title">{{ chat.title }}</div>
          <button class="delete-chat-btn" @click.stop="$emit('delete-chat', chat.id)" title="Delete chat">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16">
              </path>
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
          <button class="logout-link" @click="$emit('logout')">Logout</button>
        </div>
      </div>
      <template v-else>
        <button class="sidebar-btn" @click="$emit('show-modal', 'login')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
          </svg>
          <span>Login</span>
        </button>
        <button class="sidebar-btn" @click="$emit('show-modal', 'register')">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
          </svg>
          <span>Register</span>
        </button>
      </template>
      <button class="sidebar-btn" @click="$emit('show-modal', 'settings')">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z">
          </path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z">
          </path>
        </svg>
        <span>Settings</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import type { ChatHistoryItem } from '@/api/chat'

const userStore = useUserStore()

defineProps<{
  isOpen: boolean
  chatHistories: ChatHistoryItem[]
  currentChatId: string | null
}>()

defineEmits<{
  'new-chat': []
  'load-chat': [chatId: string]
  'delete-chat': [chatId: string]
  'logout': []
  'show-modal': [type: string]
}>()
</script>

<style scoped>
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
</style>
