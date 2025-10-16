'use client'

import { useState, useEffect, useRef } from 'react'
import { chatStorage, type ChatHistory, type Message } from '@/lib/chatStorage'

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: 'Hello! How can I help you today?', sender: 'bot' },
  ])
  const [currentMessage, setCurrentMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [modalType, setModalType] = useState('')
  const [modalTitle, setModalTitle] = useState('')
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [registerForm, setRegisterForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  const endOfMessagesRef = useRef<HTMLDivElement>(null)
  const msgIdRef = useRef(2)

  // Initialize IndexedDB and load chat histories
  useEffect(() => {
    const initChat = async () => {
      try {
        await chatStorage.init()
        await loadChatHistories()

        // Load the most recent chat if available
        const histories = await chatStorage.getAllChats()
        if (histories.length > 0) {
          const mostRecentChat = histories[0]
          if (mostRecentChat) {
            setMessages(mostRecentChat.messages)
            setCurrentChatId(mostRecentChat.id)
            msgIdRef.current =
              mostRecentChat.messages.length > 0
                ? Math.max(...mostRecentChat.messages.map((m) => m.id)) + 1
                : 2
            setTimeout(scrollToBottom, 100)
          }
        }
      } catch (error) {
        console.error('Failed to initialize chat storage:', error)
      }
    }

    initChat()
  }, [])

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadChatHistories = async () => {
    try {
      const histories = await chatStorage.getAllChats()
      setChatHistories(histories)
    } catch (error) {
      console.error('Failed to load chat histories:', error)
    }
  }

  const saveCurrentChat = async () => {
    try {
      console.log('saveCurrentChat called, messages count:', messages.length)
      // Only save if there are messages beyond the initial greeting
      if (messages.length <= 1) {
        console.log('Skipping save - not enough messages')
        return
      }

      // Generate or reuse chat ID
      let chatId = currentChatId
      if (!chatId) {
        chatId = chatStorage.generateChatId()
        setCurrentChatId(chatId)
        console.log('Generated new chat ID:', chatId)
      }

      const title = chatStorage.generateChatTitle(messages)
      const now = Date.now()

      // Find existing chat to preserve createdAt timestamp
      const existingChat = chatHistories.find((c) => c.id === chatId)

      const chatHistory: ChatHistory = {
        id: chatId,
        title,
        messages,
        createdAt: existingChat?.createdAt || now,
        updatedAt: now,
      }

      console.log('Saving chat history:', chatHistory)
      await chatStorage.saveChat(chatHistory)
      await loadChatHistories()
    } catch (error) {
      console.error('Failed to save chat:', error)
    }
  }

  const loadChat = async (chatId: string) => {
    try {
      // Save current chat before loading a new one
      await saveCurrentChat()

      const chat = await chatStorage.getChat(chatId)
      if (chat) {
        setMessages(chat.messages)
        setCurrentChatId(chat.id)
        msgIdRef.current =
          chat.messages.length > 0 ? Math.max(...chat.messages.map((m) => m.id)) + 1 : 2
        setTimeout(scrollToBottom, 100)
      }
    } catch (error) {
      console.error('Failed to load chat:', error)
    }
  }

  const deleteChat = async (chatId: string) => {
    try {
      // If we're deleting the current chat, clear it first before deleting
      if (currentChatId === chatId) {
        setMessages([{ id: 1, text: 'Hello! How can I help you today?', sender: 'bot' }])
        setCurrentMessage('')
        setCurrentChatId(null)
        msgIdRef.current = 2
      }

      // Delete from IndexedDB
      await chatStorage.deleteChat(chatId)
      await loadChatHistories()
    } catch (error) {
      console.error('Failed to delete chat:', error)
    }
  }

  const newChat = async () => {
    // Save current chat before starting a new one (only if it has content)
    await saveCurrentChat()

    // Reset to initial state
    setMessages([{ id: 1, text: 'Hello! How can I help you today?', sender: 'bot' }])
    setCurrentMessage('')
    setCurrentChatId(null)
    msgIdRef.current = 2
  }

  const sendMessage = async () => {
    if (!currentMessage.trim() || loading) return

    const userMessageText = currentMessage

    setMessages((prev) => [
      ...prev,
      {
        id: msgIdRef.current++,
        text: userMessageText,
        sender: 'user',
      },
    ])

    setCurrentMessage('')
    setLoading(true)
    setTimeout(scrollToBottom, 100)

    // Create a new bot message that will be updated with streaming response
    const botMessageId = msgIdRef.current++
    setMessages((prev) => [
      ...prev,
      {
        id: botMessageId,
        text: '',
        sender: 'bot',
      },
    ])

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'
      const res = await fetch(`${apiUrl}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessageText }),
      })

      // Ensure the response body is available and the request was successful
      if (!res.body || !res.ok) {
        setLoading(false)
        console.error('Failed to get a streaming response:', res.statusText)
        // Update bot message with error
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId
              ? { ...msg, text: 'Sorry, there was an error processing your request.' }
              : msg
          )
        )
        setTimeout(scrollToBottom, 100)
        await saveCurrentChat()
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })

        // Update the bot message
        setMessages((prev) =>
          prev.map((msg) => (msg.id === botMessageId ? { ...msg, text: msg.text + chunk } : msg))
        )

        setTimeout(scrollToBottom, 100)
      }

      // Final decoding step in case of partial characters at the end
      const finalChunk = decoder.decode()
      if (finalChunk) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId ? { ...msg, text: msg.text + finalChunk } : msg
          )
        )
      }

      setLoading(false)
      setTimeout(scrollToBottom, 100)

      // Save chat after successful message exchange
      await saveCurrentChat()
    } catch (error) {
      console.error('Error sending message:', error)
      setLoading(false)
      // Update bot message with error
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === botMessageId
            ? { ...msg, text: 'Sorry, there was an error connecting to the server.' }
            : msg
        )
      )
      setTimeout(scrollToBottom, 100)

      // Save chat even on error
      await saveCurrentChat()
    }
  }

  const showModal = (type: string) => {
    setModalType(type)
    setModalOpen(true)

    if (type === 'login') {
      setModalTitle('Login')
    } else if (type === 'register') {
      setModalTitle('Register')
    } else if (type === 'settings') {
      setModalTitle('Settings')
    }
  }

  const closeModal = () => {
    setModalOpen(false)
    setLoginForm({ email: '', password: '' })
    setRegisterForm({ name: '', email: '', password: '', confirmPassword: '' })
  }

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    if (loginForm.email && loginForm.password) {
      alert(`Login successful for ${loginForm.email}`)
      closeModal()
    }
  }

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault()
    if (registerForm.password !== registerForm.confirmPassword) {
      alert('Passwords do not match!')
      return
    }
    if (registerForm.name && registerForm.email && registerForm.password) {
      alert(`Registration successful for ${registerForm.name}`)
      closeModal()
    }
  }

  return (
    <div className="flex h-screen w-full bg-white">
      {/* Sidebar */}
      <div
        className={`w-[260px] bg-[#1a1a1a] text-white flex flex-col transition-all duration-300 border-r border-[#333] overflow-hidden ${
          sidebarOpen ? '' : 'w-[0] border-r-0'
        }`}
      >
        <div className="p-4 border-b border-[#333]">
          <button
            onClick={newChat}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-md bg-[#2a2a2a] text-white border border-[#444] cursor-pointer text-sm transition-all hover:bg-[#333] hover:border-[#555]"
          >
            <span>+ New chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 text-[13px] text-[#888]">
          {chatHistories.length === 0 ? (
            <div className="p-4 text-center text-[#666] text-[13px]">No chat history yet</div>
          ) : (
            <div className="flex flex-col gap-1">
              {chatHistories.map((chat) => (
                <div
                  key={chat.id}
                  className={`flex items-center justify-between py-2.5 px-3 rounded-md cursor-pointer transition-all gap-2 group ${
                    currentChatId === chat.id ? 'bg-[#333]' : 'bg-transparent hover:bg-[#2a2a2a]'
                  }`}
                  onClick={() => loadChat(chat.id)}
                >
                  <div
                    className={`flex-1 text-[13px] whitespace-nowrap overflow-hidden text-ellipsis ${
                      currentChatId === chat.id ? 'text-white' : 'text-[#ccc]'
                    }`}
                  >
                    {chat.title}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteChat(chat.id)
                    }}
                    className="w-6 h-6 p-1 bg-transparent border-0 rounded cursor-pointer flex items-center justify-center opacity-0 group-hover:opacity-100 hover:bg-[#ff4444] transition-all flex-shrink-0"
                    title="Delete chat"
                  >
                    <svg
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      className="w-4 h-4 stroke-[#ccc] hover:stroke-white"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 p-4 border-t border-[#333]">
          <button
            onClick={() => showModal('login')}
            className="flex items-center gap-3 w-full py-2.5 px-3 bg-transparent text-[#ccc] border-0 rounded-md cursor-pointer text-sm transition-all hover:bg-[#2a2a2a] hover:text-white"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-[18px] h-[18px] flex-shrink-0">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
              />
            </svg>
            <span>Login</span>
          </button>
          <button
            onClick={() => showModal('register')}
            className="flex items-center gap-3 w-full py-2.5 px-3 bg-transparent text-[#ccc] border-0 rounded-md cursor-pointer text-sm transition-all hover:bg-[#2a2a2a] hover:text-white"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-[18px] h-[18px] flex-shrink-0">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
              />
            </svg>
            <span>Register</span>
          </button>
          <button
            onClick={() => showModal('settings')}
            className="flex items-center gap-3 w-full py-2.5 px-3 bg-transparent text-[#ccc] border-0 rounded-md cursor-pointer text-sm transition-all hover:bg-[#2a2a2a] hover:text-white"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-[18px] h-[18px] flex-shrink-0">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-10 h-10 p-0 bg-none border-0 cursor-pointer rounded-md transition-all flex items-center justify-center hover:bg-gray-100"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-6 h-6 stroke-black">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="text-xl font-semibold text-black">ChatGPT</div>
          <div className="w-10"></div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto py-8 px-6 flex justify-center bg-white">
          <div className="max-w-[700px] w-full flex flex-col gap-4">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex mb-2 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                <div
                  className={`max-w-[500px] py-3 px-4 rounded-lg text-[15px] leading-6 break-words ${
                    msg.sender === 'bot' ? 'bg-gray-100 text-black' : 'bg-blue-600 text-white'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex mb-2">
                <div className="flex gap-1 py-3 px-4 bg-gray-100 rounded-lg w-fit">
                  <div className="w-2 h-2 rounded-full bg-gray-600 animate-bounce [animation-delay:0s]"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-600 animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-600 animate-bounce [animation-delay:0.4s]"></div>
                </div>
              </div>
            )}

            <div ref={endOfMessagesRef}></div>
          </div>
        </div>

        {/* Input */}
        <div className="py-4 px-6 border-t border-gray-200 bg-white flex justify-center">
          <div className="max-w-[700px] w-full flex gap-3">
            <input
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              type="text"
              className="text-black flex-1 py-3 px-4 border border-gray-300 rounded-md text-[15px] font-sans transition-all resize-none max-h-[100px] focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
              placeholder="Message ChatGPT..."
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={!currentMessage.trim() || loading}
              className="w-10 h-10 p-0 bg-blue-600 text-white border-0 rounded-md cursor-pointer transition-all flex items-center justify-center flex-shrink-0 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5 stroke-white stroke-2">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[1000] p-5 animate-[fadeIn_0.2s_ease-out]"
          onClick={(e) => e.target === e.currentTarget && closeModal()}
        >
          <div className="block bg-white rounded-xl shadow-[0_20px_60px_rgba(0,0,0,0.3),0_0_0_1px_rgba(0,0,0,0.05)] max-w-[440px] w-full max-h-[90vh] overflow-hidden animate-[slideUp_0.3s_cubic-bezier(0.16,1,0.3,1)]">
            <div className="flex items-center justify-between py-5 px-6 border-b border-gray-100">
              <h2 className="text-xl font-semibold text-[#111] m-0">{modalTitle}</h2>
              <button
                onClick={closeModal}
                className="bg-none border-0 cursor-pointer p-1.5 flex items-center justify-center transition-all rounded-md text-[#666] hover:bg-gray-100 hover:text-[#111] active:scale-95"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Login Form */}
            {modalType === 'login' && (
              <div className="p-6 max-h-[calc(90vh-160px)] overflow-y-auto overflow-x-hidden">
                <form onSubmit={handleLogin}>
                  <div className="mb-[18px] flex flex-col">
                    <label htmlFor="login-email" className="text-sm font-medium text-[#111] mb-2">
                      Email
                    </label>
                    <input
                      value={loginForm.email}
                      onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                      type="email"
                      id="login-email"
                      placeholder="Enter your email"
                      required
                      className="py-3 px-3.5 border border-gray-200 rounded-lg text-sm font-sans transition-all bg-white hover:border-gray-300 focus:outline-none focus:border-[#111] focus:ring-2 focus:ring-black/5"
                    />
                  </div>
                  <div className="mb-[18px] flex flex-col">
                    <label htmlFor="login-password" className="text-sm font-medium text-[#111] mb-2">
                      Password
                    </label>
                    <input
                      value={loginForm.password}
                      onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                      type="password"
                      id="login-password"
                      placeholder="Enter your password"
                      required
                      className="py-3 px-3.5 border border-gray-200 rounded-lg text-sm font-sans transition-all bg-white hover:border-gray-300 focus:outline-none focus:border-[#111] focus:ring-2 focus:ring-black/5"
                    />
                  </div>
                  <div className="flex gap-2.5 mt-6">
                    <button
                      type="submit"
                      className="flex-1 py-2.5 px-5 bg-[#111] text-white border-0 rounded-lg cursor-pointer text-sm font-medium transition-all hover:bg-black hover:-translate-y-px hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)] active:translate-y-0 active:shadow-[0_2px_6px_rgba(0,0,0,0.15)]"
                    >
                      Login
                    </button>
                    <button
                      type="button"
                      onClick={closeModal}
                      className="flex-1 py-2.5 px-5 bg-white text-[#333] border border-gray-200 rounded-lg cursor-pointer text-sm font-medium transition-all hover:bg-gray-50 hover:border-gray-300 active:scale-[0.98]"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Register Form */}
            {modalType === 'register' && (
              <div className="p-6 max-h-[calc(90vh-160px)] overflow-y-auto overflow-x-hidden">
                <form onSubmit={handleRegister}>
                  <div className="mb-[18px] flex flex-col">
                    <label htmlFor="register-name" className="text-sm font-medium text-[#111] mb-2">
                      Full Name
                    </label>
                    <input
                      value={registerForm.name}
                      onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                      type="text"
                      id="register-name"
                      placeholder="Enter your full name"
                      required
                      className="py-3 px-3.5 border border-gray-200 rounded-lg text-sm font-sans transition-all bg-white hover:border-gray-300 focus:outline-none focus:border-[#111] focus:ring-2 focus:ring-black/5"
                    />
                  </div>
                  <div className="mb-[18px] flex flex-col">
                    <label htmlFor="register-email" className="text-sm font-medium text-[#111] mb-2">
                      Email
                    </label>
                    <input
                      value={registerForm.email}
                      onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                      type="email"
                      id="register-email"
                      placeholder="Enter your email"
                      required
                      className="py-3 px-3.5 border border-gray-200 rounded-lg text-sm font-sans transition-all bg-white hover:border-gray-300 focus:outline-none focus:border-[#111] focus:ring-2 focus:ring-black/5"
                    />
                  </div>
                  <div className="mb-[18px] flex flex-col">
                    <label htmlFor="register-password" className="text-sm font-medium text-[#111] mb-2">
                      Password
                    </label>
                    <input
                      value={registerForm.password}
                      onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                      type="password"
                      id="register-password"
                      placeholder="Enter your password"
                      required
                      className="py-3 px-3.5 border border-gray-200 rounded-lg text-sm font-sans transition-all bg-white hover:border-gray-300 focus:outline-none focus:border-[#111] focus:ring-2 focus:ring-black/5"
                    />
                  </div>
                  <div className="mb-[18px] flex flex-col">
                    <label htmlFor="register-confirm" className="text-sm font-medium text-[#111] mb-2">
                      Confirm Password
                    </label>
                    <input
                      value={registerForm.confirmPassword}
                      onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                      type="password"
                      id="register-confirm"
                      placeholder="Confirm your password"
                      required
                      className="py-3 px-3.5 border border-gray-200 rounded-lg text-sm font-sans transition-all bg-white hover:border-gray-300 focus:outline-none focus:border-[#111] focus:ring-2 focus:ring-black/5"
                    />
                  </div>
                  <div className="flex gap-2.5 mt-6">
                    <button
                      type="submit"
                      className="flex-1 py-2.5 px-5 bg-[#111] text-white border-0 rounded-lg cursor-pointer text-sm font-medium transition-all hover:bg-black hover:-translate-y-px hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)] active:translate-y-0 active:shadow-[0_2px_6px_rgba(0,0,0,0.15)]"
                    >
                      Register
                    </button>
                    <button
                      type="button"
                      onClick={closeModal}
                      className="flex-1 py-2.5 px-5 bg-white text-[#333] border border-gray-200 rounded-lg cursor-pointer text-sm font-medium transition-all hover:bg-gray-50 hover:border-gray-300 active:scale-[0.98]"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Settings */}
            {modalType === 'settings' && (
              <div className="p-6 max-h-[calc(90vh-160px)] overflow-y-auto overflow-x-hidden">
                <p className="text-[#666] text-sm">Manage your preferences</p>
                <div className="flex gap-2.5 mt-6">
                  <button
                    onClick={closeModal}
                    className="flex-1 py-2.5 px-5 bg-white text-[#333] border border-gray-200 rounded-lg cursor-pointer text-sm font-medium transition-all hover:bg-gray-50 hover:border-gray-300 active:scale-[0.98]"
                  >
                    Cancel
                  </button>
                  <button className="flex-1 py-2.5 px-5 bg-[#111] text-white border-0 rounded-lg cursor-pointer text-sm font-medium transition-all hover:bg-black hover:-translate-y-px hover:shadow-[0_4px_12px_rgba(0,0,0,0.15)] active:translate-y-0 active:shadow-[0_2px_6px_rgba(0,0,0,0.15)]">
                    Confirm
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
