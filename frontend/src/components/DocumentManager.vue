<template>
  <div class="document-manager">
    <div class="document-header">
      <h3>Document Library</h3>
      <button class="btn btn-primary" @click="showUploadModal = true">
        <i class="bi bi-upload"></i> Upload Document
      </button>
    </div>

    <!-- Statistics -->
    <div v-if="stats" class="stats-cards">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_documents }}</div>
        <div class="stat-label">Total Documents</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_chunks }}</div>
        <div class="stat-label">Total Chunks</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ formatBytes(stats.total_size_bytes) }}</div>
        <div class="stat-label">Total Size</div>
      </div>
    </div>

    <!-- Documents List -->
    <div class="documents-list">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else-if="documents.length === 0" class="empty-state">
        <i class="bi bi-folder2-open"></i>
        <p>No documents yet. Upload your first document to get started!</p>
      </div>

      <div v-else class="document-items">
        <div
          v-for="doc in documents"
          :key="doc.id"
          class="document-item"
          :class="{ 'processing': doc.status === 'processing' }"
        >
          <div class="document-icon">
            <i :class="getDocumentIcon(doc.content_type)"></i>
          </div>
          <div class="document-info">
            <div class="document-title">{{ doc.title }}</div>
            <div class="document-meta">
              <span class="badge" :class="getStatusClass(doc.status)">
                {{ doc.status }}
              </span>
              <span class="text-muted">{{ doc.total_chunks }} chunks</span>
              <span class="text-muted">{{ formatBytes(doc.file_size || 0) }}</span>
              <span class="text-muted">{{ formatDate(doc.created_at) }}</span>
            </div>
            <div v-if="doc.error_message" class="error-message">
              {{ doc.error_message }}
            </div>
          </div>
          <div class="document-actions">
            <button
              class="btn btn-sm btn-outline-primary"
              @click="viewDocument(doc)"
              :disabled="doc.status !== 'completed'"
            >
              <i class="bi bi-eye"></i>
            </button>
            <button
              class="btn btn-sm btn-outline-danger"
              @click="deleteDocument(doc)"
            >
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click="closeUploadModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>Upload Document</h4>
          <button class="btn-close" @click="closeUploadModal"></button>
        </div>
        <div class="modal-body">
          <div class="upload-tabs">
            <button
              :class="{ active: uploadTab === 'file' }"
              @click="uploadTab = 'file'"
            >
              File Upload
            </button>
            <button
              :class="{ active: uploadTab === 'text' }"
              @click="uploadTab = 'text'"
            >
              Text Input
            </button>
            <button
              :class="{ active: uploadTab === 'url' }"
              @click="uploadTab = 'url'"
            >
              From URL
            </button>
          </div>

          <!-- File Upload Tab -->
          <div v-if="uploadTab === 'file'" class="upload-section">
            <div class="file-drop-zone" @drop.prevent="handleFileDrop" @dragover.prevent>
              <input
                type="file"
                ref="fileInput"
                @change="handleFileSelect"
                accept=".pdf,.txt,.md"
                style="display: none"
              />
              <i class="bi bi-cloud-upload"></i>
              <p>Drag and drop a file here, or</p>
              <button class="btn btn-outline-primary" @click="$refs.fileInput.click()">
                Choose File
              </button>
              <small class="text-muted">Supported: PDF, TXT, MD (Max 10MB)</small>
            </div>
            <div v-if="selectedFile" class="selected-file">
              <i class="bi bi-file-earmark-text"></i>
              <span>{{ selectedFile.name }}</span>
              <button class="btn btn-sm btn-link" @click="selectedFile = null">
                <i class="bi bi-x"></i>
              </button>
            </div>
          </div>

          <!-- Text Input Tab -->
          <div v-if="uploadTab === 'text'" class="upload-section">
            <div class="mb-3">
              <label class="form-label">Title</label>
              <input
                v-model="textTitle"
                type="text"
                class="form-control"
                placeholder="Enter document title"
              />
            </div>
            <div class="mb-3">
              <label class="form-label">Content</label>
              <textarea
                v-model="textContent"
                class="form-control"
                rows="10"
                placeholder="Paste or type your content here..."
              ></textarea>
            </div>
          </div>

          <!-- URL Input Tab -->
          <div v-if="uploadTab === 'url'" class="upload-section">
            <div class="mb-3">
              <label class="form-label">URL</label>
              <input
                v-model="urlInput"
                type="url"
                class="form-control"
                placeholder="https://example.com/article"
              />
            </div>
            <div class="mb-3">
              <label class="form-label">Title (optional)</label>
              <input
                v-model="urlTitle"
                type="text"
                class="form-control"
                placeholder="Auto-detected from page"
              />
            </div>
          </div>

          <div v-if="uploadError" class="alert alert-danger">
            {{ uploadError }}
          </div>
          <div v-if="uploading" class="upload-progress">
            <div class="spinner-border spinner-border-sm" role="status"></div>
            <span>Uploading and processing document...</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeUploadModal" :disabled="uploading">
            Cancel
          </button>
          <button
            class="btn btn-primary"
            @click="handleUpload"
            :disabled="!canUpload || uploading"
          >
            <span v-if="uploading">Uploading...</span>
            <span v-else>Upload</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Document Detail Modal -->
    <div v-if="showDetailModal && selectedDocument" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content modal-lg" @click.stop>
        <div class="modal-header">
          <h4>{{ selectedDocument.title }}</h4>
          <button class="btn-close" @click="closeDetailModal"></button>
        </div>
        <div class="modal-body">
          <div class="document-details">
            <div class="detail-row">
              <strong>Type:</strong> {{ selectedDocument.content_type }}
            </div>
            <div class="detail-row">
              <strong>Source:</strong> {{ selectedDocument.source_type }}
            </div>
            <div v-if="selectedDocument.source_url" class="detail-row">
              <strong>URL:</strong>
              <a :href="selectedDocument.source_url" target="_blank">
                {{ selectedDocument.source_url }}
              </a>
            </div>
            <div class="detail-row">
              <strong>Chunks:</strong> {{ selectedDocument.total_chunks }}
            </div>
            <div class="detail-row">
              <strong>Created:</strong> {{ formatDate(selectedDocument.created_at) }}
            </div>
          </div>

          <div class="info-message">
            <i class="bi bi-info-circle"></i>
            <p>Document content is managed by Gemini File Search. Chunks are processed and indexed automatically.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { documentsApi, type Document, type DocumentDetail, type DocumentStats } from '@/api/documents'

const documents = ref<Document[]>([])
const stats = ref<DocumentStats | null>(null)
const loading = ref(false)
const showUploadModal = ref(false)
const showDetailModal = ref(false)
const selectedDocument = ref<DocumentDetail | null>(null)
const uploading = ref(false)
const uploadError = ref('')

// Upload form state
const uploadTab = ref<'file' | 'text' | 'url'>('file')
const selectedFile = ref<File | null>(null)
const textTitle = ref('')
const textContent = ref('')
const urlInput = ref('')
const urlTitle = ref('')

const canUpload = computed(() => {
  if (uploadTab.value === 'file') return selectedFile.value !== null
  if (uploadTab.value === 'text') return textTitle.value && textContent.value
  if (uploadTab.value === 'url') return urlInput.value
  return false
})

onMounted(() => {
  loadDocuments()
  loadStats()
})

const loadDocuments = async () => {
  try {
    loading.value = true
    documents.value = await documentsApi.getDocuments()
  } catch (error: any) {
    console.error('Failed to load documents:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    stats.value = await documentsApi.getStats()
  } catch (error: any) {
    console.error('Failed to load stats:', error)
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

const handleFileDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

const handleUpload = async () => {
  uploadError.value = ''
  uploading.value = true

  try {
    if (uploadTab.value === 'file' && selectedFile.value) {
      await documentsApi.uploadDocument(selectedFile.value)
    } else if (uploadTab.value === 'text') {
      await documentsApi.ingestText({
        title: textTitle.value,
        content: textContent.value,
      })
    } else if (uploadTab.value === 'url') {
      await documentsApi.ingestUrl({
        url: urlInput.value,
        title: urlTitle.value || undefined,
      })
    }

    closeUploadModal()
    await loadDocuments()
    await loadStats()
  } catch (error: any) {
    uploadError.value = error.response?.data?.detail || 'Upload failed. Please try again.'
    console.error('Upload error:', error)
  } finally {
    uploading.value = false
  }
}

const viewDocument = async (doc: Document) => {
  try {
    selectedDocument.value = await documentsApi.getDocumentDetail(doc.id)
    showDetailModal.value = true
  } catch (error: any) {
    console.error('Failed to load document details:', error)
    alert('Failed to load document details')
  }
}

const deleteDocument = async (doc: Document) => {
  if (!confirm(`Are you sure you want to delete "${doc.title}"?`)) return

  try {
    await documentsApi.deleteDocument(doc.id)
    await loadDocuments()
    await loadStats()
  } catch (error: any) {
    console.error('Failed to delete document:', error)
    alert('Failed to delete document')
  }
}

const closeUploadModal = () => {
  showUploadModal.value = false
  uploadError.value = ''
  selectedFile.value = null
  textTitle.value = ''
  textContent.value = ''
  urlInput.value = ''
  urlTitle.value = ''
  uploadTab.value = 'file'
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedDocument.value = null
}

const getDocumentIcon = (contentType: string): string => {
  if (!contentType) return 'bi bi-file-earmark'
  if (contentType.includes('pdf')) return 'bi bi-file-pdf'
  if (contentType.includes('text')) return 'bi bi-file-text'
  if (contentType.includes('markdown')) return 'bi bi-file-earmark-code'
  return 'bi bi-file-earmark'
}

const getStatusClass = (status: string): string => {
  const classes: Record<string, string> = {
    completed: 'bg-success',
    processing: 'bg-warning',
    pending: 'bg-secondary',
    failed: 'bg-danger',
  }
  return classes[status] || 'bg-secondary'
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (timestamp: number): string => {
  return new Date(timestamp * 1000).toLocaleString()
}
</script>

<style scoped>
.document-manager {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bs-light);
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--bs-primary);
}

.stat-label {
  color: var(--bs-secondary);
  margin-top: 0.5rem;
}

.documents-list {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--bs-secondary);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.document-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  transition: all 0.2s;
}

.document-item:hover {
  background: var(--bs-light);
  border-color: var(--bs-primary);
}

.document-item.processing {
  opacity: 0.7;
}

.document-icon {
  font-size: 2rem;
  color: var(--bs-primary);
}

.document-info {
  flex: 1;
}

.document-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.document-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
}

.error-message {
  color: var(--bs-danger);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.document-actions {
  display: flex;
  gap: 0.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-content.modal-lg {
  max-width: 900px;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.upload-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.upload-tabs button {
  padding: 0.5rem 1rem;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.upload-tabs button.active {
  border-bottom-color: var(--bs-primary);
  color: var(--bs-primary);
}

.upload-section {
  min-height: 300px;
}

.file-drop-zone {
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  transition: all 0.2s;
}

.file-drop-zone:hover {
  border-color: var(--bs-primary);
  background: var(--bs-light);
}

.file-drop-zone i {
  font-size: 3rem;
  color: var(--bs-primary);
  margin-bottom: 1rem;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bs-light);
  border-radius: 4px;
  margin-top: 1rem;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--bs-light);
  border-radius: 4px;
}

.document-details {
  background: var(--bs-light);
  padding: 1rem;
  border-radius: 4px;
}

.detail-row {
  padding: 0.5rem 0;
  border-bottom: 1px solid #dee2e6;
}

.detail-row:last-child {
  border-bottom: none;
}

.info-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bs-light);
  border-radius: 4px;
  margin-top: 1rem;
}

.info-message i {
  font-size: 1.5rem;
  color: var(--bs-info);
}

.info-message p {
  margin: 0;
  color: var(--bs-secondary);
}
</style>
