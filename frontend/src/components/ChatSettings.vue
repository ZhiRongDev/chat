<template>
  <div class="chat-settings">
    <h4>Chat Settings</h4>

    <!-- RAG Settings -->
    <div class="settings-section">
      <h5>
        <i class="bi bi-database"></i>
        RAG (Retrieval-Augmented Generation)
      </h5>

      <div class="setting-item">
        <div class="setting-header">
          <label class="form-check-label">
            Enable RAG Mode
          </label>
          <div class="form-check form-switch">
            <input
              v-model="localSettings.useRag"
              class="form-check-input"
              type="checkbox"
              id="ragToggle"
            />
          </div>
        </div>
        <small class="text-muted">
          Use document knowledge base to enhance responses
        </small>
      </div>

      <div v-if="localSettings.useRag" class="rag-options">
        <div class="setting-item">
          <label for="topK">Top-K Results: {{ localSettings.topK }}</label>
          <input
            v-model.number="localSettings.topK"
            type="range"
            class="form-range"
            id="topK"
            min="1"
            max="10"
            step="1"
          />
          <small class="text-muted">
            Number of relevant document chunks to retrieve (1-10)
          </small>
        </div>

        <div class="setting-item">
          <label for="minScore">Minimum Relevance Score: {{ localSettings.minScore.toFixed(2) }}</label>
          <input
            v-model.number="localSettings.minScore"
            type="range"
            class="form-range"
            id="minScore"
            min="0"
            max="1"
            step="0.05"
          />
          <small class="text-muted">
            Minimum similarity threshold (0.0 = any relevance, 1.0 = exact match)
          </small>
        </div>
      </div>
    </div>

    <!-- LLM Provider Settings -->
    <div class="settings-section">
      <h5>
        <i class="bi bi-robot"></i>
        LLM Provider
      </h5>

      <div class="setting-item">
        <label for="provider">Provider</label>
        <select
          v-model="localSettings.provider"
          class="form-select"
          id="provider"
        >
          <option value="">Auto-detect</option>
          <option value="gemini">Google Gemini</option>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic Claude</option>
        </select>
        <small class="text-muted">
          Choose your preferred LLM provider
        </small>
      </div>

      <div class="setting-item">
        <label for="model">Model (optional)</label>
        <input
          v-model="localSettings.model"
          type="text"
          class="form-control"
          id="model"
          placeholder="e.g., gpt-4, gemini-pro"
        />
        <small class="text-muted">
          Leave empty to use provider's default model
        </small>
      </div>

      <div class="setting-item">
        <label for="temperature">Temperature: {{ localSettings.temperature.toFixed(1) }}</label>
        <input
          v-model.number="localSettings.temperature"
          type="range"
          class="form-range"
          id="temperature"
          min="0"
          max="2"
          step="0.1"
        />
        <small class="text-muted">
          Lower = more focused, Higher = more creative (0.0-2.0)
        </small>
      </div>
    </div>

    <!-- Document Library Link -->
    <div class="settings-section">
      <h5>
        <i class="bi bi-folder"></i>
        Document Library
      </h5>
      <button class="btn btn-outline-primary w-100" @click="$emit('show-documents')">
        <i class="bi bi-folder-open"></i>
        Manage Documents
      </button>
      <small class="text-muted d-block mt-2">
        Upload and manage documents for RAG
      </small>
    </div>

    <!-- Save Button -->
    <div class="settings-actions">
      <button class="btn btn-primary" @click="saveSettings">
        <i class="bi bi-check-lg"></i>
        Save Settings
      </button>
      <button class="btn btn-secondary" @click="resetSettings">
        <i class="bi bi-arrow-clockwise"></i>
        Reset to Defaults
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

export interface ChatSettings {
  useRag: boolean
  topK: number
  minScore: number
  provider: string
  model: string
  temperature: number
}

const props = defineProps<{
  modelValue: ChatSettings
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ChatSettings): void
  (e: 'show-documents'): void
}>()

const localSettings = ref<ChatSettings>({ ...props.modelValue })

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  localSettings.value = { ...newValue }
}, { deep: true })

const saveSettings = () => {
  emit('update:modelValue', { ...localSettings.value })
  // Save to localStorage for persistence
  localStorage.setItem('chatSettings', JSON.stringify(localSettings.value))
}

const resetSettings = () => {
  const defaults: ChatSettings = {
    useRag: false,
    topK: 5,
    minScore: 0.3,
    provider: '',
    model: '',
    temperature: 0.7,
  }
  localSettings.value = { ...defaults }
  saveSettings()
}

// Load settings from localStorage on mount
const loadSettings = () => {
  const saved = localStorage.getItem('chatSettings')
  if (saved) {
    try {
      localSettings.value = JSON.parse(saved)
      emit('update:modelValue', localSettings.value)
    } catch (e) {
      console.error('Failed to load settings:', e)
    }
  }
}

loadSettings()
</script>

<style scoped>
.chat-settings {
  padding: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.chat-settings h4 {
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.settings-section {
  background: var(--bs-light);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.settings-section h5 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.setting-item {
  margin-bottom: 1.5rem;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.setting-item label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.setting-item small {
  display: block;
  margin-top: 0.25rem;
}

.rag-options {
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 3px solid var(--bs-primary);
}

.settings-actions {
  display: flex;
  gap: 0.75rem;
}

.settings-actions .btn {
  flex: 1;
}

.form-check-input {
  cursor: pointer;
}

.form-check-input:checked {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}
</style>
