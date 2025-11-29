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

export const documentsApi = {
  /**
   * Upload a document file (PDF, TXT, MD)
   */
  uploadDocument: async (file: File): Promise<UploadDocumentResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<UploadDocumentResponse>(
      '/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  /**
   * Ingest text content directly
   */
  ingestText: async (payload: IngestTextPayload): Promise<UploadDocumentResponse> => {
    const response = await api.post<UploadDocumentResponse>(
      '/documents/ingest/text',
      payload
    )
    return response.data
  },

  /**
   * Ingest content from a URL
   */
  ingestUrl: async (payload: IngestUrlPayload): Promise<UploadDocumentResponse> => {
    const response = await api.post<UploadDocumentResponse>(
      '/documents/ingest/url',
      payload
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
  deleteDocument: async (documentId: string): Promise<void> => {
    await api.delete(`/documents/${documentId}`)
  },

  /**
   * Get document statistics
   */
  getStats: async (): Promise<DocumentStats> => {
    const response = await api.get<DocumentStats>('/documents/stats/overview')
    return response.data
  },
}
