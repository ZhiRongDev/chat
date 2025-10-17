// src/api/chat.ts
import api from './service'

export interface Message {
  id?: string  // Snowflake ID as string (JavaScript Number can't safely represent int64)
  sender: 'user' | 'bot'
  text: string
}

export interface ChatHistoryItem {
  id: string  // Snowflake ID as string for JavaScript safety
  title: string
  created_at: number
  updated_at: number
  message_count: number
}

export interface ChatDetail {
  id: string  // Snowflake ID as string for JavaScript safety
  title: string
  created_at: number
  updated_at: number
  messages: Message[]
}

export interface SaveChatPayload {
  chat_id?: string  // Snowflake ID as string for JavaScript safety
  title: string
  messages: Message[]
}

export const chatApi = {
  /**
   * Get all chat histories for the authenticated user
   */
  getChatHistories: async (limit: number = 100): Promise<ChatHistoryItem[]> => {
    const response = await api.get<ChatHistoryItem[]>('/chat/history', {
      params: { limit },
    })
    console.log('getChatHistories response:', response.data);
    return response.data
  },

  /**
   * Get a specific chat history with all messages
   */
  getChatDetail: async (chatId: string): Promise<ChatDetail> => {
    const response = await api.get<ChatDetail>(`/chat/history/${chatId}`)
    return response.data
  },

  /**
   * Save or update a chat history with messages
   */
  saveChatHistory: async (payload: SaveChatPayload): Promise<ChatDetail> => {
    const response = await api.post<ChatDetail>('/chat/history', payload)
    return response.data
  },

  /**
   * Delete a chat history and all its messages
   */
  deleteChatHistory: async (chatId: string): Promise<void> => {
    await api.delete(`/chat/history/${chatId}`)
  },
}
