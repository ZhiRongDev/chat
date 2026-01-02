import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '../stores/user'
import { userApi } from '../api/user'

// Mock the user API
vi.mock('../api/user', () => ({
  userApi: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
  },
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('initializes with empty user', () => {
    const store = useUserStore()
    expect(store.user.username).toBe('')
  })

  it('loads user from localStorage on initialization', () => {
    localStorage.setItem('username', 'testuser')

    const store = useUserStore()
    store.initializeUser()

    expect(store.user.username).toBe('testuser')
  })

  it('logs in successfully', async () => {
    const mockResponse = {
      user: { username: 'testuser', id: '123', created_at: 123456789 },
    }

    vi.mocked(userApi.login).mockResolvedValue(mockResponse)

    const store = useUserStore()
    await store.login({ username: 'testuser', password: 'password' })

    expect(store.user.username).toBe('testuser')
    expect(localStorage.getItem('username')).toBe('testuser')
  })

  it('registers successfully', async () => {
    const mockResponse = {
      message: 'Registration successful',
    }

    vi.mocked(userApi.register).mockResolvedValue(mockResponse)

    const store = useUserStore()
    await store.register({ username: 'newuser', password: 'password' })

    expect(userApi.register).toHaveBeenCalledWith({
      username: 'newuser',
      password: 'password',
    })
  })

  it('logs out successfully', async () => {
    localStorage.setItem('username', 'testuser')

    vi.mocked(userApi.logout).mockResolvedValue({ message: 'Logged out' })

    const store = useUserStore()
    store.user.username = 'testuser'

    await store.logout()

    expect(store.user.username).toBe('')
    expect(localStorage.getItem('username')).toBeNull()
    expect(userApi.logout).toHaveBeenCalled()
  })
})
