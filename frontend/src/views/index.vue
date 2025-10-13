<template>
  <div class="chat-layout">
    <aside class="sidebar">
      <Sidebar />
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <div class="chat-title">ChatGPT</div>
        <div class="chat-actions">
          <button class="btn secondary">New chat</button>
        </div>
      </header>

      <section class="chat-body" ref="chatBody">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="headline">Where should we begin?</div>
          <div class="starter-bar">
            <button class="starter" @click="useStarter('Explain this code:')">Explain this code</button>
            <button class="starter" @click="useStarter('Write a unit test for:')">Write a unit test</button>
            <button class="starter" @click="useStarter('How do I fix:')">How do I fix</button>
          </div>
        </div>

        <div v-else class="messages">
          <div
            v-for="(m, idx) in messages"
            :key="idx"
            class="message"
            :class="m.role"
          >
            <div class="avatar">{{ m.role === 'user' ? 'You' : 'AI' }}</div>
            <div class="bubble">{{ m.content }}</div>
          </div>
        </div>
      </section>

      <footer class="composer">
        <div class="composer-inner">
          <textarea
            ref="inputRef"
            v-model="input"
            placeholder="Ask anything"
            @keydown.enter.exact.prevent="onSubmit"
            @input="autoResize"
            rows="1"
          />
          <button class="btn primary" :disabled="sending || !input.trim()" @click="onSubmit">Send</button>
        </div>
        <div class="composer-hint">Press Enter to send</div>
      </footer>
    </main>
  </div>
</template>

<style lang="scss" scoped>
.chat-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  height: 100vh;
  background: #0f172a;
  color: #e5e7eb;
}

.sidebar {
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  background: #0b1220;
  overflow: hidden;
}

.chat-main {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100%;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.chat-title {
  font-weight: 600;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.btn {
  height: 34px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #111827;
  color: #e5e7eb;
}

.btn.primary {
  background: #2563eb;
  border-color: transparent;
}

.btn.primary:disabled {
  opacity: 0.5;
}

.btn.secondary {
  background: #1f2937;
}

.chat-body {
  overflow-y: auto;
  padding: 24px 0 8px 0;
}

.empty-state {
  display: grid;
  place-items: center;
  height: 100%;
}

.headline {
  font-size: 28px;
  font-weight: 600;
  color: #cbd5e1;
  margin-bottom: 24px;
}

.starter-bar {
  display: flex;
  gap: 12px;
}

.starter {
  background: #111827;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  border-radius: 999px;
  padding: 8px 14px;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px 20px 20px;
}

.message {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 12px;
}

.message .avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #1f2937;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.message .bubble {
  background: #0b1220;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 12px 14px;
  white-space: pre-wrap;
}

.message.user .bubble {
  background: #111827;
}

.composer {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding: 12px 20px 18px 20px;
}

.composer-inner {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  max-width: 900px;
  margin: 0 auto;
  background: #0b1220;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 10px 10px 10px 14px;
}

.composer textarea {
  flex: 1;
  resize: none;
  outline: none;
  border: none;
  color: #e5e7eb;
  background: transparent;
  max-height: 200px;
}

.composer-hint {
  text-align: center;
  color: #6b7280;
  font-size: 12px;
  margin-top: 8px;
}

@media (max-width: 920px) {
  .chat-layout { grid-template-columns: 1fr; }
  .sidebar { display: none; }
}
</style>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import Sidebar from '@/components/Sidebar.vue'

type Msg = { role: 'user' | 'assistant'; content: string }

const messages = ref<Msg[]>([])
const input = ref('')
const sending = ref(false)
const chatBody = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

function scrollToBottom() {
  if (!chatBody.value) return
  chatBody.value.scrollTo({ top: chatBody.value.scrollHeight, behavior: 'smooth' })
}

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

async function onSubmit() {
  if (sending.value) return
  const text = input.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  await nextTick()
  autoResize()
  scrollToBottom()
  sending.value = true
  setTimeout(async () => {
    messages.value.push({ role: 'assistant', content: 'This is a placeholder response.' })
    await nextTick()
    scrollToBottom()
    sending.value = false
  }, 400)
}

function useStarter(prefix: string) {
  input.value = prefix + ' '
  nextTick(() => {
    inputRef.value?.focus()
    autoResize()
  })
}

onMounted(() => {
  autoResize()
})
</script>