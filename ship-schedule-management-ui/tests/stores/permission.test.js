import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePermissionStore } from '@/stores/permission'

// Mock authApi
vi.mock('@/api/auth', () => ({
  authApi: {
    getUserPermissions: vi.fn(),
  },
}))

// Mock ElMessage
vi.mock('element-plus', () => ({
  ElMessage: {
    warning: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock logger
vi.mock('@/utils/logger', () => ({
  permissionLogger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}))

describe('Permission Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('hasPermission', () => {
    it('should return false for empty permission', () => {
      const store = usePermissionStore()
      expect(store.hasPermission('')).toBe(false)
      expect(store.hasPermission(null)).toBe(false)
      expect(store.hasPermission(undefined)).toBe(false)
    })

    it('should return true for super admin', () => {
      const store = usePermissionStore()

      // Mock authStore with super admin user
      const mockAuthStore = {
        user: {
          email: 'admin@example.com',
          is_superuser: true,
        },
      }
      store.setAuthStoreRef(mockAuthStore)

      expect(store.hasPermission('any.permission')).toBe(true)
    })

    it('should return false when permissions not loaded', () => {
      const store = usePermissionStore()

      // Mock authStore with regular user
      const mockAuthStore = {
        user: {
          email: 'user@example.com',
          is_superuser: false,
        },
      }
      store.setAuthStoreRef(mockAuthStore)

      expect(store.hasPermission('some.permission')).toBe(false)
    })

    it('should check specific permissions correctly', () => {
      const store = usePermissionStore()

      // Mock authStore with regular user
      const mockAuthStore = {
        user: {
          email: 'user@example.com',
          is_superuser: false,
        },
      }
      store.setAuthStoreRef(mockAuthStore)

      // Mock permissions data
      store.userPermissions = {
        permissions: ['user.list', 'user.view'],
      }

      expect(store.hasPermission('user.list')).toBe(true)
      expect(store.hasPermission('user.view')).toBe(true)
      expect(store.hasPermission('user.delete')).toBe(false)
    })
  })

  describe('checkSpecificPermission', () => {
    it('should handle array format permissions', () => {
      const store = usePermissionStore()
      const permissions = ['user.list', 'user.view', 'role.list']

      expect(store.checkSpecificPermission('user.list', permissions)).toBe(true)
      expect(store.checkSpecificPermission('user.delete', permissions)).toBe(false)
    })

    it('should handle object format permissions', () => {
      const store = usePermissionStore()
      const permissions = [
        { code: 'user.list', name: 'User List' },
        { code: 'user.view', name: 'User View' },
      ]

      expect(store.checkSpecificPermission('user.list', permissions)).toBe(true)
      expect(store.checkSpecificPermission('user.delete', permissions)).toBe(false)
    })

    it('should handle categorized permissions', () => {
      const store = usePermissionStore()
      const permissions = {
        user: ['user.list', 'user.view'],
        role: [{ code: 'role.list', name: 'Role List' }],
      }

      expect(store.checkSpecificPermission('user.list', permissions)).toBe(true)
      expect(store.checkSpecificPermission('role.list', permissions)).toBe(true)
      expect(store.checkSpecificPermission('permission.list', permissions)).toBe(false)
    })
  })

  describe('isAdmin', () => {
    it('should return true for super admin from authStore', () => {
      const store = usePermissionStore()

      const mockAuthStore = {
        user: {
          email: 'admin@example.com',
          is_superuser: true,
        },
      }
      store.setAuthStoreRef(mockAuthStore)

      expect(store.isAdmin).toBe(true)
    })

    it('should return true for super admin from permission data', () => {
      const store = usePermissionStore()

      store.userPermissions = {
        user: {
          email: 'admin@example.com',
          is_superuser: true,
        },
      }

      expect(store.isAdmin).toBe(true)
    })

    it('should return false for regular user', () => {
      const store = usePermissionStore()

      const mockAuthStore = {
        user: {
          email: 'user@example.com',
          is_superuser: false,
        },
      }
      store.setAuthStoreRef(mockAuthStore)

      expect(store.isAdmin).toBe(false)
    })
  })
})
