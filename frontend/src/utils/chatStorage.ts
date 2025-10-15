// IndexedDB utility for chat history storage

export interface Message {
  id: number
  text: string
  sender: 'user' | 'bot'
}

export interface ChatHistory {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
}

const DB_NAME = 'ChatHistoryDB'
const DB_VERSION = 1
const STORE_NAME = 'chats'

class ChatStorage {
  private db: IDBDatabase | null = null

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log('Initializing IndexedDB...')
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        console.error('Failed to open IndexedDB:', request.error)
        reject(new Error('Failed to open IndexedDB'))
      }

      request.onsuccess = () => {
        this.db = request.result
        console.log('IndexedDB initialized successfully')
        resolve()
      }

      request.onupgradeneeded = (event) => {
        console.log('Upgrading IndexedDB schema...')
        const db = (event.target as IDBOpenDBRequest).result

        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const objectStore = db.createObjectStore(STORE_NAME, { keyPath: 'id' })
          objectStore.createIndex('createdAt', 'createdAt', { unique: false })
          objectStore.createIndex('updatedAt', 'updatedAt', { unique: false })
          console.log('Object store created')
        }
      }
    })
  }

  private async ensureDB(): Promise<IDBDatabase> {
    if (!this.db) {
      await this.init()
    }
    if (!this.db) {
      throw new Error('Database not initialized')
    }
    return this.db
  }

  async saveChat(chat: ChatHistory): Promise<void> {
    const db = await this.ensureDB()
    return new Promise((resolve, reject) => {
      console.log('Saving chat to IndexedDB:', chat.id, chat.title)
      const transaction = db.transaction([STORE_NAME], 'readwrite')
      const objectStore = transaction.objectStore(STORE_NAME)
      const request = objectStore.put(chat)

      request.onsuccess = () => {
        console.log('Chat saved successfully:', chat.id)
        resolve()
      }
      request.onerror = () => {
        console.error('Failed to save chat:', request.error)
        reject(new Error('Failed to save chat'))
      }
    })
  }

  async getChat(id: string): Promise<ChatHistory | null> {
    const db = await this.ensureDB()
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_NAME], 'readonly')
      const objectStore = transaction.objectStore(STORE_NAME)
      const request = objectStore.get(id)

      request.onsuccess = () => {
        resolve(request.result || null)
      }
      request.onerror = () => reject(new Error('Failed to get chat'))
    })
  }

  async getAllChats(): Promise<ChatHistory[]> {
    const db = await this.ensureDB()
    return new Promise((resolve, reject) => {
      console.log('Getting all chats from IndexedDB...')
      const transaction = db.transaction([STORE_NAME], 'readonly')
      const objectStore = transaction.objectStore(STORE_NAME)
      const index = objectStore.index('updatedAt')
      const request = index.openCursor(null, 'prev') // Sort by updatedAt descending

      const chats: ChatHistory[] = []

      request.onsuccess = () => {
        const cursor = request.result
        if (cursor) {
          chats.push(cursor.value)
          cursor.continue()
        } else {
          console.log('Retrieved chats:', chats.length)
          resolve(chats)
        }
      }

      request.onerror = () => {
        console.error('Failed to get all chats:', request.error)
        reject(new Error('Failed to get all chats'))
      }
    })
  }

  async deleteChat(id: string): Promise<void> {
    const db = await this.ensureDB()
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_NAME], 'readwrite')
      const objectStore = transaction.objectStore(STORE_NAME)
      const request = objectStore.delete(id)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(new Error('Failed to delete chat'))
    })
  }

  async clearAllChats(): Promise<void> {
    const db = await this.ensureDB()
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_NAME], 'readwrite')
      const objectStore = transaction.objectStore(STORE_NAME)
      const request = objectStore.clear()

      request.onsuccess = () => resolve()
      request.onerror = () => reject(new Error('Failed to clear chats'))
    })
  }

  generateChatId(): string {
    return `chat_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`
  }

  generateChatTitle(messages: Message[]): string {
    // Get the first user message as the title
    const firstUserMessage = messages.find((msg) => msg.sender === 'user')
    if (firstUserMessage && firstUserMessage.text) {
      // Truncate to 50 characters
      const title = firstUserMessage.text.trim()
      return title.length > 50 ? title.substring(0, 50) + '...' : title
    }
    return 'New Chat'
  }
}

// Export a singleton instance
export const chatStorage = new ChatStorage()
