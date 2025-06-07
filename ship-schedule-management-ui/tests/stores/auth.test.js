import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

// Mock auth API
vi.mock('@/api/auth')

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const authStore = useAuthStore()

      expect(authStore.user).toBeNull()
      expect(authStore.token).toBe('')
      expect(authStore.loading).toBe(false)
      expect(authStore.permissions).toEqual([])
      expect(authStore.roles).toEqual([])
      expect(authStore.authStatus).toBe('unknown')
      expect(authStore.lastAuthCheck).toBeNull()
      expect(authStore.networkAvailable).toBe(true)
      expect(authStore.avatarVersion).toBeTypeOf('number')
    })
  })

  describe('computed properties', () => {
    it('should return correct isAuthenticated value initially', () => {
      const authStore = useAuthStore()

      // Not authenticated initially
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('should return correct isInitializing value initially', () => {
      const authStore = useAuthStore()

      expect(authStore.isInitializing).toBe(false)
    })

    it('should return correct isSuperAdmin value initially', () => {
      const authStore = useAuthStore()

      expect(authStore.isSuperAdmin).toBe(false)
    })
  })

  describe('permission methods', () => {
    it('should check permissions correctly with no permissions', () => {
      const authStore = useAuthStore()

      expect(authStore.hasPermission('vessel.edit')).toBe(false)
      expect(authStore.hasPermission('vessel.delete')).toBe(false)
    })

    it('should check any permission correctly with no permissions', () => {
      const authStore = useAuthStore()

      expect(authStore.hasAnyPermission(['vessel.edit', 'vessel.delete'])).toBe(false)
      expect(authStore.hasAnyPermission(['vessel.delete', 'admin.access'])).toBe(false)
    })
  })

  describe('login action', () => {
    it('should login successfully', async () => {
      const authStore = useAuthStore()
      const mockResponse = {
        code: 200,
        data: {
          access: 'access-token',
          refresh: 'refresh-token',
          user: {
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
          },
        },
      }

      authApi.login.mockResolvedValue(mockResponse)
      authApi.getUserPermissions.mockResolvedValue({
        code: 200,
        data: {
          permissions: ['vessel.edit'],
          roles: ['operator'],
        },
      })

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      }

      const result = await authStore.login(credentials)

      expect(result.success).toBe(true)
      expect(authStore.token).toBe('access-token')
      expect(authStore.user).toEqual(mockResponse.data.user)
      expect(authStore.authStatus).toBe('authenticated')
      expect(authStore.permissions).toEqual(['vessel.edit'])
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'access-token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'refresh-token')
    })

    it('should handle login failure', async () => {
      const authStore = useAuthStore()
      const mockError = new Error('Invalid credentials')

      authApi.login.mockRejectedValue(mockError)

      const credentials = {
        email: 'invalid@example.com',
        password: 'wrongpassword',
      }

      const result = await authStore.login(credentials)

      expect(result.success).toBe(false)
      expect(result.message).toBe('Invalid credentials')
      expect(authStore.token).toBe('')
      expect(authStore.user).toBeNull()
    })

    it('should handle tokens format variation', async () => {
      const authStore = useAuthStore()
      const mockResponse = {
        code: 200,
        data: {
          tokens: {
            access: 'access-token',
            refresh: 'refresh-token',
          },
          user: {
            id: 1,
            email: 'test@example.com',
          },
        },
      }

      authApi.login.mockResolvedValue(mockResponse)
      authApi.getUserPermissions.mockResolvedValue({
        code: 200,
        data: { permissions: [], roles: [] },
      })

      const result = await authStore.login({
        email: 'test@example.com',
        password: 'password123',
      })

      expect(result.success).toBe(true)
      expect(authStore.token).toBe('access-token')
    })
  })

  describe('logout action', () => {
    it('should logout successfully', async () => {
      const authStore = useAuthStore()

      authApi.logout.mockResolvedValue({ code: 200 })

      await authStore.logout()

      expect(authStore.token).toBe('')
      expect(authStore.user).toBeNull()
      expect(authStore.permissions).toEqual([])
      expect(authStore.roles).toEqual([])
      expect(authStore.authStatus).toBe('unauthenticated')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken')
    })

    it('should clear state even if API call fails', async () => {
      const authStore = useAuthStore()

      authApi.logout.mockRejectedValue(new Error('Network error'))

      await authStore.logout()

      expect(authStore.token).toBe('')
      expect(authStore.authStatus).toBe('unauthenticated')
    })
  })

  describe('getUserInfo action', () => {
    it('should handle no token', async () => {
      const authStore = useAuthStore()
      // Token is empty by default

      const result = await authStore.getUserInfo()

      expect(result).toBe(false)
      expect(authApi.getMe).not.toHaveBeenCalled()
    })
  })

  describe('refreshAccessToken action', () => {
    it('should handle no refresh token', async () => {
      const authStore = useAuthStore()
      // No refresh token by default

      const result = await authStore.refreshAccessToken()

      expect(result).toBe(false)
      expect(authApi.refreshToken).not.toHaveBeenCalled()
    })
  })
})
