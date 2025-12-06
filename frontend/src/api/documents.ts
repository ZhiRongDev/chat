// src/api/documents.ts
import api from './service'

export interface Document {
  id: string  // Snowflake ID as string
  user_id: string
  title: string
  content_type: string
  source_type: 'file' | 'text' | 'url'
  source_url?: string
  file_path?: string
  file_size?: number
  total_chunks: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  metadata?: Record<string, any>
  created_at: number
  updated_at: number
}

export interface DocumentDetail extends Document {
  // No chunks needed - Gemini File Search handles chunking internally
}

export interface DocumentStats {
  total_documents: number
  total_chunks: number
  total_size_bytes: number
  documents_by_status: Record<string, number>
  documents_by_source: Record<string, number>
}

export interface UploadDocumentResponse {
  document: Document
  message: string
}

export interface IngestTextPayload {
  title: string
  content: string
  metadata?: Record<string, any>
}

export interface IngestUrlPayload {
  url: string
  title?: string
  metadata?: Record<string, any>
}

export interface DocumentApiOptions {
  geminiApiKey?: string
}

export const documentsApi = {
  /**
   * Upload a document file (PDF, TXT, MD)
   */
  uploadDocument: async (file: File, options?: DocumentApiOptions): Promise<UploadDocumentResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const headers: Record<string, string> = {
      'Content-Type': 'multipart/form-data',
    }

    if (options?.geminiApiKey) {
      headers['x-gemini-api-key'] = options.geminiApiKey
    }

    const response = await api.post<UploadDocumentResponse>(
      '/documents/upload',
      formData,
      { headers }
    )
    return response.data
  },

  /**
   * Ingest text content directly
   */
  ingestText: async (payload: IngestTextPayload, options?: DocumentApiOptions): Promise<UploadDocumentResponse> => {
    const headers: Record<string, string> = {}

    if (options?.geminiApiKey) {
      headers['x-gemini-api-key'] = options.geminiApiKey
    }

    const response = await api.post<UploadDocumentResponse>(
      '/documents/ingest/text',
      payload,
      Object.keys(headers).length > 0 ? { headers } : undefined
    )
    return response.data
  },

  /**
   * Ingest content from a URL
   */
  ingestUrl: async (payload: IngestUrlPayload, options?: DocumentApiOptions): Promise<UploadDocumentResponse> => {
    const headers: Record<string, string> = {}

    if (options?.geminiApiKey) {
      headers['x-gemini-api-key'] = options.geminiApiKey
    }

    const response = await api.post<UploadDocumentResponse>(
      '/documents/ingest/url',
      payload,
      Object.keys(headers).length > 0 ? { headers } : undefined
    )
    return response.data
  },

  /**
   * Get all documents for the authenticated user
   */
  getDocuments: async (
    skip: number = 0,
    limit: number = 100
  ): Promise<Document[]> => {
    const response = await api.get<Document[]>('/documents/', {
      params: { skip, limit },
    })
    return response.data
  },

  /**
   * Get a specific document with all chunks
   */
  getDocumentDetail: async (documentId: string): Promise<DocumentDetail> => {
    const response = await api.get<DocumentDetail>(`/documents/${documentId}`)
    return response.data
  },

  /**
   * Delete a document and all its chunks
   */
  deleteDocument: async (documentId: string, options?: DocumentApiOptions): Promise<void> => {
    const headers: Record<string, string> = {}

    if (options?.geminiApiKey) {
      headers['x-gemini-api-key'] = options.geminiApiKey
    }

    await api.delete(`/documents/${documentId}`, Object.keys(headers).length > 0 ? { headers } : undefined)
  },

  /**
   * Get document statistics
   */
  getStats: async (): Promise<DocumentStats> => {
    const response = await api.get<DocumentStats>('/documents/stats/overview')
    return response.data
  },

  /**
   * Get store information
   */
  getStoreInfo: async (options?: DocumentApiOptions): Promise<any> => {
    const headers: Record<string, string> = {}

    if (options?.geminiApiKey) {
      headers['x-gemini-api-key'] = options.geminiApiKey
    }

    const response = await api.get('/documents/stores/info', Object.keys(headers).length > 0 ? { headers } : undefined)
    return response.data
  },
}
