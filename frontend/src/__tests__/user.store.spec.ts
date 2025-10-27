import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '../stores/user'
import api from '../api/service'

// Mock the API
vi.mock('../api/service', () => ({
  default: {
    post: vi.fn(),
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
    expect(store.user.token).toBe('')
  })

  it('loads user from localStorage on initialization', () => {
    localStorage.setItem('username', 'testuser')
    localStorage.setItem('token', 'testtoken')

    const store = useUserStore()
    store.initializeUser()

    expect(store.user.username).toBe('testuser')
    expect(store.user.token).toBe('testtoken')
  })

  it('logs in successfully', async () => {
    const mockResponse = {
      data: {
        access_token: 'mocktoken',
        user: { username: 'testuser' },
      },
    }

    vi.mocked(api.post).mockResolvedValue(mockResponse)

    const store = useUserStore()
    await store.login({ username: 'testuser', password: 'password' })

    expect(store.user.username).toBe('testuser')
    expect(store.user.token).toBe('mocktoken')
    expect(localStorage.getItem('username')).toBe('testuser')
    expect(localStorage.getItem('token')).toBe('mocktoken')
  })

  it('registers successfully', async () => {
    const mockResponse = {
      data: {
        username: 'newuser',
        id: '123',
      },
    }

    vi.mocked(api.post).mockResolvedValue(mockResponse)

    const store = useUserStore()
    await store.register({ username: 'newuser', password: 'password' })

    expect(api.post).toHaveBeenCalledWith('/user/register', {
      username: 'newuser',
      password: 'password',
    })
  })

  it('logs out successfully', () => {
    localStorage.setItem('username', 'testuser')
    localStorage.setItem('token', 'testtoken')

    const store = useUserStore()
    store.user.username = 'testuser'
    store.user.token = 'testtoken'

    store.logout()

    expect(store.user.username).toBe('')
    expect(store.user.token).toBe('')
    expect(localStorage.getItem('username')).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
  })
})
