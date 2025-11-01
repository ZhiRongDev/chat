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

    <!-- Document Library -->
    <div class="settings-section">
      <h5>
        <i class="bi bi-folder"></i>
        Document Library
      </h5>

      <!-- Upload Section -->
      <div class="upload-section">
        <div class="upload-tabs">
          <button
            :class="['tab-btn', { active: uploadTab === 'file' }]"
            @click="uploadTab = 'file'"
          >
            <i class="bi bi-file-earmark-arrow-up"></i>
            Upload File
          </button>
          <button
            :class="['tab-btn', { active: uploadTab === 'text' }]"
            @click="uploadTab = 'text'"
          >
            <i class="bi bi-file-text"></i>
            Add Text
          </button>
        </div>

        <!-- File Upload Tab -->
        <div v-if="uploadTab === 'file'" class="upload-content">
          <div class="file-upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <input
              ref="fileInput"
              type="file"
              accept=".pdf,.txt,.md"
              @change="handleFileSelect"
              style="display: none"
            />
            <i class="bi bi-cloud-upload"></i>
            <p>Click to upload or drag and drop</p>
            <small class="text-muted">Supports PDF, TXT, MD files</small>
          </div>
          <div v-if="selectedFile" class="selected-file">
            <i class="bi bi-file-earmark"></i>
            <span>{{ selectedFile.name }}</span>
            <button class="btn-remove" @click="clearFile">
              <i class="bi bi-x"></i>
            </button>
          </div>
          <button
            v-if="selectedFile"
            class="btn btn-primary w-100 mt-3"
            @click="uploadFile"
            :disabled="uploading"
          >
            <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
            {{ uploading ? 'Uploading...' : 'Upload Document' }}
          </button>
        </div>

        <!-- Text Upload Tab -->
        <div v-if="uploadTab === 'text'" class="upload-content">
          <div class="setting-item">
            <label for="textTitle">Document Title</label>
            <input
              v-model="textDocument.title"
              type="text"
              class="form-control"
              id="textTitle"
              placeholder="Enter document title"
            />
          </div>
          <div class="setting-item">
            <label for="textContent">Content</label>
            <textarea
              v-model="textDocument.content"
              class="form-control"
              id="textContent"
              rows="6"
              placeholder="Paste or type your content here..."
            ></textarea>
          </div>
          <button
            class="btn btn-primary w-100"
            @click="uploadText"
            :disabled="!textDocument.title || !textDocument.content || uploading"
          >
            <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
            {{ uploading ? 'Adding...' : 'Add Document' }}
          </button>
        </div>

        <!-- Upload Status -->
        <div v-if="uploadStatus" :class="['upload-status', uploadStatus.type]">
          <i :class="uploadStatus.type === 'success' ? 'bi bi-check-circle' : 'bi bi-exclamation-circle'"></i>
          {{ uploadStatus.message }}
        </div>
      </div>
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

// Upload state
const uploadTab = ref<'file' | 'text'>('file')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadStatus = ref<{ type: 'success' | 'error'; message: string } | null>(null)
const textDocument = ref({
  title: '',
  content: ''
})

// File upload handlers
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

const handleFileDrop = (event: DragEvent) => {
  const files = event.dataTransfer?.files
  if (files && files[0]) {
    selectedFile.value = files[0]
  }
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  uploadStatus.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const token = localStorage.getItem('token')
    const headers: HeadersInit = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch('http://localhost:5000/api/v1/documents/upload', {
      method: 'POST',
      headers,
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || errorData.message || 'Upload failed')
    }

    uploadStatus.value = {
      type: 'success',
      message: 'Document uploaded successfully!'
    }
    clearFile()
  } catch (error: any) {
    console.error('Upload error:', error)
    uploadStatus.value = {
      type: 'error',
      message: error.message || 'Failed to upload document. Please try again.'
    }
  } finally {
    uploading.value = false
    setTimeout(() => {
      uploadStatus.value = null
    }, 3000)
  }
}

const uploadText = async () => {
  if (!textDocument.value.title || !textDocument.value.content) return

  uploading.value = true
  uploadStatus.value = null

  try {
    const token = localStorage.getItem('token')
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch('http://localhost:5000/api/v1/documents/ingest/text', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        title: textDocument.value.title,
        content: textDocument.value.content,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || errorData.message || 'Upload failed')
    }

    uploadStatus.value = {
      type: 'success',
      message: 'Text document added successfully!'
    }
    textDocument.value = { title: '', content: '' }
  } catch (error: any) {
    console.error('Upload error:', error)
    uploadStatus.value = {
      type: 'error',
      message: error.message || 'Failed to add document. Please try again.'
    }
  } finally {
    uploading.value = false
    setTimeout(() => {
      uploadStatus.value = null
    }, 3000)
  }
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

/* Dark Theme Button Styles */
.btn {
  padding: 10px 20px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

/* Upload Section Styles */
.upload-section {
  margin-top: 1rem;
}

.upload-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.tab-btn:hover {
  color: #374151;
  background-color: #f9fafb;
}

.tab-btn.active {
  color: #111827;
  border-bottom-color: #111827;
}

.upload-content {
  padding: 1rem 0;
}

.file-upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #f9fafb;
}

.file-upload-area:hover {
  border-color: #111827;
  background-color: #f3f4f6;
}

.file-upload-area i {
  font-size: 3rem;
  color: #9ca3af;
  display: block;
  margin-bottom: 1rem;
}

.file-upload-area p {
  margin: 0.5rem 0;
  font-weight: 500;
  color: #374151;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f3f4f6;
  border-radius: 8px;
  margin-top: 1rem;
}

.selected-file i {
  color: #111827;
  font-size: 1.25rem;
}

.selected-file span {
  flex: 1;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-remove {
  background: transparent;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s ease;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove:hover {
  color: #dc2626;
}

textarea.form-control {
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

.upload-status {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.upload-status.success {
  background-color: #f0fdf4;
  color: #16a34a;
  border-left: 4px solid #16a34a;
}

.upload-status.error {
  background-color: #fef2f2;
  color: #dc2626;
  border-left: 4px solid #dc2626;
}

.upload-status i {
  font-size: 1.25rem;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
}
</style>
