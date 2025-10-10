<template>
  <div class="chat-container">
    <h2>🤖 Gemini Chat</h2>

    <textarea v-model="message" placeholder="Type your question..." rows="3"></textarea>

    <button @click="sendMessage" :disabled="isLoading">
      {{ isLoading ? 'Generating...' : 'Send' }}
    </button>

    <div class="response">
      <pre>{{ response }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const message = ref('')
const response = ref('')
const isLoading = ref(false)

// .vue
async function sendMessage() {
  if (!message.value.trim()) return
  response.value = ''
  isLoading.value = true

  const res = await fetch('http://localhost:5000/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: message.value }),
  })

  // Ensure the response body is available and the request was successful
  if (!res.body || !res.ok) {
    isLoading.value = false
    // Handle error, e.g., throw or set an error message
    console.error('Failed to get a streaming response:', res.statusText)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break // Decode the Uint8Array value to a string

    const chunk = decoder.decode(value, { stream: true }) // Append the decoded text chunk immediately

    response.value += chunk

    await nextTick(); 

    console.log('Current Response:', response.value)
  }

  // Final decoding step in case of partial characters at the end
  const finalChunk = decoder.decode()
  response.value += finalChunk

  console.log('Final')
  console.log(response.value)

  isLoading.value = false
}
</script>

<style scoped>
.chat-container {
  max-width: 600px;
  margin: 60px auto;
  font-family: system-ui, sans-serif;
}

textarea {
  width: 100%;
  padding: 8px;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid #ccc;
}

button {
  margin-top: 10px;
  padding: 8px 16px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.response {
  margin-top: 20px;
  background: #f9fafb;
  border-radius: 8px;
  padding: 10px;
  min-height: 150px;
  white-space: pre-wrap;
  color: #000;
}
</style>
