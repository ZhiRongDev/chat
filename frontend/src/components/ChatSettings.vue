<template>
  <div class="chat-settings">
    <h4>Chat Settings</h4>

    <!-- LLM Provider Settings -->
    <div class="settings-section">
      <h5>
        <i class="bi bi-robot"></i>
        LLM Provider
      </h5>

      <div class="setting-item">
        <label for="provider">Provider</label>
        <select v-model="localSettings.provider" class="form-select" id="provider">
          <option value="">Auto-detect (uses first available API key)</option>
          <option value="gemini">Google Gemini (Required for RAG)</option>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic Claude</option>
        </select>
        <small class="text-muted">
          <strong>Note:</strong> RAG mode requires Gemini provider. Auto-detect priority: Gemini →
          OpenAI → Anthropic
        </small>
      </div>

      <div class="setting-item">
        <label for="model">Model (optional)</label>
        <input v-model="localSettings.model" type="text" class="form-control" id="model"
          placeholder="e.g., gpt-4, gemini-pro, gemini-2.5-flash-lite" />
        <small class="text-muted"> Leave empty to use provider's default model </small>
      </div>

      <div class="setting-item">
        <label for="temperature">Temperature: {{ localSettings.temperature.toFixed(1) }}</label>
        <input v-model.number="localSettings.temperature" type="range" class="form-range" id="temperature" min="0"
          max="2" step="0.1" />
        <small class="text-muted"> Lower = more focused, Higher = more creative (0.0-2.0) </small>
      </div>
    </div>

    <!-- API Keys Settings -->
    <div class="settings-section">
      <h5>
        <i class="bi bi-key"></i>
        API Keys
      </h5>
      <small class="text-muted mb-3 d-block">
        Enter your API keys to use the respective LLM providers. Keys are stored locally in your
        browser.
      </small>

      <div class="setting-item">
        <label for="geminiApiKey">Google Gemini API Key <span class="text-danger">*Required for RAG</span></label>
        <input v-model="localSettings.geminiApiKey" type="password" class="form-control" id="geminiApiKey"
          placeholder="Enter your Gemini API key" />
        <small class="text-muted">
          Get your API key from
          <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a>
        </small>
      </div>

      <div class="setting-item">
        <label for="openaiApiKey">OpenAI API Key</label>
        <input v-model="localSettings.openaiApiKey" type="password" class="form-control" id="openaiApiKey"
          placeholder="Enter your OpenAI API key" />
        <small class="text-muted">
          Get your API key from
          <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI Platform</a>
        </small>
      </div>

      <div class="setting-item">
        <label for="anthropicApiKey">Anthropic Claude API Key</label>
        <input v-model="localSettings.anthropicApiKey" type="password" class="form-control" id="anthropicApiKey"
          placeholder="Enter your Anthropic API key" />
        <small class="text-muted">
          Get your API key from
          <a href="https://console.anthropic.com/settings/keys" target="_blank">Anthropic Console</a>
        </small>
      </div>
    </div>

    <!-- RAG Settings (Only show when logged in) -->
    <div v-if="isLoggedIn" class="settings-section">
      <h5>
        <i class="bi bi-database"></i>
        RAG (Retrieval-Augmented Generation)
      </h5>

      <div class="setting-item">
        <div class="setting-header">
          <label class="form-check-label"> Enable RAG Mode </label>
          <div class="form-check form-switch">
            <input v-model="localSettings.useRag" class="form-check-input" type="checkbox" id="ragToggle" />
          </div>
        </div>
        <small class="text-muted">
          Use Gemini File Search to enhance responses with your uploaded documents
        </small>
      </div>

      <div v-if="localSettings.useRag" class="rag-options">
        <div class="alert alert-info" role="alert">
          <i class="bi bi-info-circle me-2"></i>
          <strong>Gemini File Search:</strong> Document retrieval and relevance are automatically
          optimized by Google's Gemini API.
        </div>

        <div class="setting-item">
          <label for="maxOutputTokens">Max Response Length: {{ localSettings.maxOutputTokens }}</label>
          <input v-model.number="localSettings.maxOutputTokens" type="range" class="form-range" id="maxOutputTokens"
            min="512" max="8192" step="256" />
          <small class="text-muted">
            Maximum tokens in RAG response (512-8192). Higher = longer, more detailed responses.
          </small>
        </div>
      </div>
    </div>

    <!-- Document Library (Only show when logged in) -->
    <div v-if="isLoggedIn" class="settings-section">
      <div class="section-header">
        <h5>
          <i class="bi bi-folder"></i>
          Document Library
        </h5>
        <button class="btn-refresh" @click="fetchDocuments" :disabled="loadingDocuments" title="Refresh document list">
          <i :class="['bi bi-arrow-clockwise', { spinning: loadingDocuments }]"></i>
        </button>
      </div>

      <!-- Document List -->
      <div v-if="documents.length > 0" class="document-list">
        <div v-for="doc in documents" :key="doc.id" class="document-item">
          <div class="document-info">
            <div class="document-header">
              <i :class="getFileIcon(doc.file_type)"></i>
              <div class="document-details">
                <strong>{{ doc.filename }}</strong>
                <div class="document-meta">
                  <span class="file-size">{{ formatFileSize(doc.file_size) }}</span>
                  <span class="separator">•</span>
                  <span class="upload-date">{{ formatDate(doc.created_at) }}</span>
                  <span v-if="doc.gemini_file_id" class="separator">•</span>
                  <span v-if="doc.gemini_file_id" class="gemini-badge">
                    <i class="bi bi-cloud-check"></i> Gemini
                  </span>
                </div>
              </div>
            </div>
            <div class="document-status">
              <span :class="['status-badge', doc.status]">
                <i :class="getStatusIcon(doc.status)"></i>
                {{ doc.status }}
              </span>
            </div>
          </div>
          <div class="document-actions">
            <button class="btn-action btn-delete" @click="confirmDeleteDocument(doc.id)" title="Delete document">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="!loadingDocuments" class="empty-state">
        <i class="bi bi-inbox"></i>
        <p v-if="!isLoggedIn">Please log in to manage documents</p>
        <p v-else>No documents uploaded yet</p>
        <small v-if="!isLoggedIn">Document management requires authentication</small>
        <small v-else>Upload your first document to enable RAG</small>
      </div>

      <div v-if="loadingDocuments" class="loading-state">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading documents...</p>
      </div>

      <!-- Upload Section -->
      <div class="upload-section">
        <div class="upload-tabs">
          <button :class="['tab-btn', { active: uploadTab === 'file' }]" @click="uploadTab = 'file'">
            <i class="bi bi-file-earmark-arrow-up"></i>
            Upload File
          </button>
          <button :class="['tab-btn', { active: uploadTab === 'text' }]" @click="uploadTab = 'text'">
            <i class="bi bi-file-text"></i>
            Add Text
          </button>
        </div>

        <!-- File Upload Tab -->
        <div v-if="uploadTab === 'file'" class="upload-content">
          <div class="file-upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <input ref="fileInput" type="file" accept=".pdf,.txt,.md,.docx,.json,.csv" @change="handleFileSelect"
              style="display: none" />
            <i class="bi bi-cloud-upload"></i>
            <p>Click to upload or drag and drop</p>
            <small class="text-muted">Supports PDF, TXT, MD, DOCX, JSON, CSV (max 100MB)</small>
          </div>
          <div v-if="selectedFile" class="selected-file">
            <i class="bi bi-file-earmark"></i>
            <span>{{ selectedFile.name }}</span>
            <button class="btn-remove" @click="clearFile">
              <i class="bi bi-x"></i>
            </button>
          </div>
          <button v-if="selectedFile" class="btn btn-primary w-100 mt-3" @click="uploadFile" :disabled="uploading">
            <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
            {{ uploading ? 'Uploading...' : 'Upload Document' }}
          </button>
        </div>

        <!-- Text Upload Tab -->
        <div v-if="uploadTab === 'text'" class="upload-content">
          <div class="setting-item">
            <label for="textTitle">Document Title</label>
            <input v-model="textDocument.title" type="text" class="form-control" id="textTitle"
              placeholder="Enter document title" />
          </div>
          <div class="setting-item">
            <label for="textContent">Content</label>
            <textarea v-model="textDocument.content" class="form-control" id="textContent" rows="6"
              placeholder="Paste or type your content here..."></textarea>
          </div>
          <button class="btn btn-primary w-100" @click="uploadText"
            :disabled="!textDocument.title || !textDocument.content || uploading">
            <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
            {{ uploading ? 'Adding...' : 'Add Document' }}
          </button>
        </div>

        <!-- Upload Status -->
        <div v-if="uploadStatus" :class="['upload-status', uploadStatus.type]">
          <i :class="uploadStatus.type === 'success' ? 'bi bi-check-circle' : 'bi bi-exclamation-circle'
            "></i>
          {{ uploadStatus.message }}
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="settings-actions">
      <button class="btn btn-primary" @click="saveSettings">
        <i class="bi bi-check-lg me-1"></i>
        <span>Save Settings</span>
      </button>
      <button class="btn btn-secondary" @click="resetSettings">
        <i class="bi bi-arrow-clockwise me-1"></i>
        <span>Reset to Defaults</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { appendAlert } from '@/utils/alert'
import { useUserStore } from '@/stores/user'
import api from '@/api/service'

export interface ChatSettings {
  useRag: boolean
  maxOutputTokens: number
  provider: string
  model: string
  temperature: number
  geminiApiKey: string
  openaiApiKey: string
  anthropicApiKey: string
}

const props = defineProps<{
  modelValue: ChatSettings
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ChatSettings): void
}>()

const localSettings = ref<ChatSettings>({ ...props.modelValue })

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    localSettings.value = { ...newValue }
  },
  { deep: true },
)

const saveSettings = () => {
  emit('update:modelValue', { ...localSettings.value })
  // Save to localStorage for persistence
  localStorage.setItem('chatSettings', JSON.stringify(localSettings.value))
  // Show success alert
  appendAlert('Settings saved successfully!', 'success')
}

const resetSettings = () => {
  const defaults: ChatSettings = {
    useRag: false,
    maxOutputTokens: 2048,
    provider: '',
    model: '',
    temperature: 0.7,
    geminiApiKey: '',
    openaiApiKey: '',
    anthropicApiKey: '',
  }
  localSettings.value = { ...defaults }
  saveSettings()
}

// Document state
interface DocumentItem {
  id: string
  filename: string
  file_type: string
  file_size: number
  status: string
  gemini_file_id?: string
  created_at: number
  updated_at: number
}

const documents = ref<DocumentItem[]>([])
const loadingDocuments = ref(false)
const deleteConfirmId = ref<string | null>(null)

// Check if user is logged in
const userStore = useUserStore()
const isLoggedIn = computed(() => !!userStore.user.username)

// Upload state
const uploadTab = ref<'file' | 'text'>('file')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadStatus = ref<{ type: 'success' | 'error'; message: string } | null>(null)
const textDocument = ref({
  title: '',
  content: '',
})

// Watch for login state changes - disable RAG if user logs out
watch(isLoggedIn, (newValue) => {
  if (!newValue && localSettings.value.useRag) {
    // User logged out while RAG was enabled, disable it
    localSettings.value.useRag = false
    saveSettings()
  }
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

    const headers: Record<string, string> = {
      'Content-Type': 'multipart/form-data',
    }

    // Add Gemini API key header if available
    if (localSettings.value.geminiApiKey) {
      headers['x-gemini-api-key'] = localSettings.value.geminiApiKey
    }

    await api.post('/documents/upload', formData, { headers })

    uploadStatus.value = {
      type: 'success',
      message: 'Document uploaded successfully to Gemini File Search!',
    }
    clearFile()
  } catch (error: any) {
    console.error('Upload error:', error)
    uploadStatus.value = {
      type: 'error',
      message: error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to upload document. Please try again.',
    }
  } finally {
    uploading.value = false
    // Refresh document list regardless of success or failure
    await fetchDocuments()
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
    const headers: Record<string, string> = {}

    // Add Gemini API key header if available
    if (localSettings.value.geminiApiKey) {
      headers['x-gemini-api-key'] = localSettings.value.geminiApiKey
    }

    await api.post('/documents/ingest/text', {
      title: textDocument.value.title,
      content: textDocument.value.content,
    }, Object.keys(headers).length > 0 ? { headers } : undefined)

    uploadStatus.value = {
      type: 'success',
      message: 'Text document added successfully to Gemini File Search!',
    }
    textDocument.value = { title: '', content: '' }
  } catch (error: any) {
    console.error('Upload error:', error)
    uploadStatus.value = {
      type: 'error',
      message: error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to add document. Please try again.',
    }
  } finally {
    uploading.value = false
    // Refresh document list regardless of success or failure
    await fetchDocuments()
    setTimeout(() => {
      uploadStatus.value = null
    }, 3000)
  }
}

// Document management functions
const fetchDocuments = async () => {
  loadingDocuments.value = true
  try {
    // If not logged in, just set empty array and return
    if (!isLoggedIn.value) {
      documents.value = []
      loadingDocuments.value = false
      return
    }

    const headers: Record<string, string> = {}

    // Add Gemini API key header if available
    if (localSettings.value.geminiApiKey) {
      headers['x-gemini-api-key'] = localSettings.value.geminiApiKey
    }

    const response = await api.get('/documents', Object.keys(headers).length > 0 ? { headers } : undefined)
    documents.value = response.data
  } catch (error: any) {
    console.error('Error fetching documents:', error)
    documents.value = []
    // Don't show error message if not authenticated
    if (error.response?.status === 401) {
      // Unauthorized, just clear documents silently
      return
    }
    const token = localStorage.getItem('token')
    if (token) {
      uploadStatus.value = {
        type: 'error',
        message: 'Failed to load documents',
      }
      setTimeout(() => {
        uploadStatus.value = null
      }, 3000)
    }
  } finally {
    loadingDocuments.value = false
  }
}

const confirmDeleteDocument = (documentId: string) => {
  deleteConfirmId.value = documentId
  if (
    confirm(
      'Are you sure you want to delete this document from Gemini File Search? This action cannot be undone.',
    )
  ) {
    deleteDocument(documentId)
  }
}

const deleteDocument = async (documentId: string) => {
  try {
    const headers: Record<string, string> = {}

    // Add Gemini API key header if available
    if (localSettings.value.geminiApiKey) {
      headers['x-gemini-api-key'] = localSettings.value.geminiApiKey
    }

    await api.delete(`/documents/${documentId}`, Object.keys(headers).length > 0 ? { headers } : undefined)

    uploadStatus.value = {
      type: 'success',
      message: 'Document deleted successfully',
    }
  } catch (error: any) {
    console.error('Error deleting document:', error)
    uploadStatus.value = {
      type: 'error',
      message: error.response?.data?.detail || error.response?.data?.message || 'Failed to delete document',
    }
  } finally {
    deleteConfirmId.value = null
    // Refresh document list regardless of success or failure
    await fetchDocuments()
    setTimeout(() => {
      uploadStatus.value = null
    }, 3000)
  }
}

// Helper functions
const getFileIcon = (fileType: string): string => {
  const iconMap: Record<string, string> = {
    pdf: 'bi bi-file-pdf text-danger',
    txt: 'bi bi-file-text text-primary',
    md: 'bi bi-markdown text-info',
    text: 'bi bi-file-text text-primary',
    docx: 'bi bi-file-word text-primary',
    json: 'bi bi-file-code text-warning',
    csv: 'bi bi-file-spreadsheet text-success',
  }
  return iconMap[fileType.toLowerCase()] || 'bi bi-file-earmark'
}

const getStatusIcon = (status: string): string => {
  const iconMap: Record<string, string> = {
    completed: 'bi bi-check-circle',
    processing: 'bi bi-hourglass-split',
    failed: 'bi bi-exclamation-circle',
    pending: 'bi bi-clock',
  }
  return iconMap[status] || 'bi bi-question-circle'
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp * 1000) // Convert from Unix timestamp
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? 'Just now' : `${minutes} minutes ago`
    }
    return hours === 1 ? '1 hour ago' : `${hours} hours ago`
  }
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`

  return date.toLocaleDateString()
}

// Load settings from localStorage on mount
const loadSettings = () => {
  const saved = localStorage.getItem('chatSettings')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      // Migrate old settings: remove topK and minScore, add maxOutputTokens
      if ('topK' in parsed || 'minScore' in parsed) {
        delete parsed.topK
        delete parsed.minScore
        if (!('maxOutputTokens' in parsed)) {
          parsed.maxOutputTokens = 2048
        }
      }
      localSettings.value = { ...localSettings.value, ...parsed }
      emit('update:modelValue', localSettings.value)
    } catch (e) {
      console.error('Failed to load settings:', e)
    }
  }
}

loadSettings()
// Load documents on mount
fetchDocuments()
</script>

<style scoped>
/* Keep all existing styles... */
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

.alert-info {
  background-color: #e3f2fd;
  border-color: #90caf9;
  color: #0d47a1;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.gemini-badge {
  color: #1976d2;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

/* Section Header with Refresh Button */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h5 {
  margin-bottom: 0;
}

.btn-refresh {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.btn-refresh:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #111827;
  color: #111827;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh i {
  font-size: 1.1rem;
}

.btn-refresh .spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* Document List Styles */
.document-list {
  margin-bottom: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.document-list::-webkit-scrollbar {
  width: 6px;
}

.document-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.document-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.document-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.document-item {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
}

.document-item:hover {
  border-color: #111827;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.document-info {
  flex: 1;
  min-width: 0;
}

.document-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.document-header>i {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.document-details {
  flex: 1;
  min-width: 0;
}

.document-details strong {
  display: block;
  font-size: 0.95rem;
  color: #111827;
  margin-bottom: 0.25rem;
  word-break: break-word;
}

.document-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6b7280;
  flex-wrap: wrap;
}

.document-meta .separator {
  color: #d1d5db;
}

.document-status {
  margin-top: 0.5rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge i {
  font-size: 0.9rem;
}

.status-badge.completed {
  background-color: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.status-badge.processing {
  background-color: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.status-badge.failed {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.status-badge.pending {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #dbeafe;
}

.document-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-action {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action i {
  font-size: 1.1rem;
}

.btn-action:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.btn-action:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-delete:hover:not(:disabled) {
  color: #dc2626;
  border-color: #dc2626;
  background-color: #fef2f2;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: #9ca3af;
}

.empty-state i {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
  color: #d1d5db;
}

.empty-state p {
  margin: 0.5rem 0;
  font-weight: 500;
  color: #6b7280;
  font-size: 1rem;
}

.empty-state small {
  color: #9ca3af;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.loading-state .spinner-border {
  margin-bottom: 1rem;
}

.loading-state p {
  margin: 0;
  font-size: 0.95rem;
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

/* Responsive adjustments */
@media (max-width: 640px) {
  .document-item {
    flex-direction: column;
    align-items: stretch;
  }

  .document-actions {
    justify-content: flex-end;
    width: 100%;
    padding-top: 0.5rem;
    border-top: 1px solid #f3f4f6;
  }

  .document-meta {
    font-size: 0.8rem;
  }
}
</style>
