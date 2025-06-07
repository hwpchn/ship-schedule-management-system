import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { permissionLogger } from '@/utils/logger'

// 全局状态，用于避免循环依赖
let authStoreRef = null

/**
 * 权限管理Store
 */
export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const userPermissions = ref(null)
  const permissionsLoaded = ref(false)
  const loading = ref(false)

  // 计算属性
  const canEditVesselInfo = computed(() => {
    return hasPermission('vessel_info.update')
  })

  const canEditLocalFee = computed(() => {
    return (
      hasPermission('local_fee.create') ||
      hasPermission('local_fee.update') ||
      hasPermission('local_fee.edit')
    )
  })

  const canViewLocalFee = computed(() => {
    return (
      hasPermission('local_fee.query') ||
      hasPermission('local_fee.list') ||
      hasPermission('local_fee.detail') ||
      hasPermission('local_fee.view')
    )
  })

  const canDeleteLocalFee = computed(() => {
    return hasPermission('local_fee.delete')
  })

  const canCreateLocalFee = computed(() => {
    return hasPermission('local_fee.create')
  })

  const canQueryLocalFee = computed(() => {
    return hasPermission('local_fee.query')
  })

  const isAdmin = computed(() => {
    // 优先从authStore获取用户信息
    if (authStoreRef?.user?.is_superuser === true) {
      permissionLogger.debug('用户是超级管理员', {
        email: authStoreRef.user.email,
        source: 'authStore',
      })
      return true
    }

    // 从权限数据中获取用户信息
    if (userPermissions.value?.user?.is_superuser === true) {
      permissionLogger.debug('用户是超级管理员', {
        email: userPermissions.value.user.email,
        source: 'permissionData',
      })
      return true
    }

    return false
  })

  /**
   * 设置authStore引用（避免循环依赖）
   * @param {Object} authStore authStore实例
   */
  const setAuthStoreRef = authStore => {
    authStoreRef = authStore
  }

  /**
   * 检查用户是否有特定权限
   * @param {string} permission 权限代码
   * @returns {boolean} 是否有权限
   */
  const hasPermission = permission => {
    if (!permission) {
      permissionLogger.warn('权限代码为空')
      return false
    }

    // 超级管理员拥有所有权限
    if (isAdmin.value) {
      permissionLogger.debug('超级管理员拥有所有权限', { permission })
      return true
    }

    // 检查权限数据是否已加载
    if (!userPermissions.value?.permissions) {
      permissionLogger.debug('权限数据未加载，拒绝访问', { permission })
      return false
    }

    // 检查具体权限
    const hasSpecificPermission = checkSpecificPermission(
      permission,
      userPermissions.value.permissions
    )

    permissionLogger.debug('权限检查结果', {
      permission,
      result: hasSpecificPermission,
    })

    return hasSpecificPermission
  }

  /**
   * 检查具体权限
   * @param {string} permission 权限代码
   * @param {Object|Array} permissions 权限数据
   * @returns {boolean} 是否有权限
   */
  const checkSpecificPermission = (permission, permissions) => {
    if (Array.isArray(permissions)) {
      // 数组格式权限检查
      return permissions.some(perm => {
        if (typeof perm === 'string') {
          return perm === permission
        }
        if (typeof perm === 'object' && perm.code) {
          return perm.code === permission
        }
        return false
      })
    }

    // 对象格式权限检查（按分类）
    for (const category in permissions) {
      const perms = permissions[category]
      if (Array.isArray(perms)) {
        const found = perms.some(perm => {
          if (typeof perm === 'string') {
            return perm === permission
          }
          if (typeof perm === 'object' && perm.code) {
            return perm.code === permission
          }
          return false
        })
        if (found) return true
      }
    }

    return false
  }

  /**
   * 检查用户是否有任一权限
   * @param {Array} permissionList 权限代码列表
   * @returns {boolean} 是否有任一权限
   */
  const hasAnyPermission = permissionList => {
    if (isAdmin.value) return true

    return permissionList.some(permission => hasPermission(permission))
  }

  /**
   * 加载用户权限
   * @returns {Promise<Object|null>} 权限数据
   */
  const loadUserPermissions = async () => {
    try {
      loading.value = true
      permissionLogger.info('开始加载用户权限')

      const token = localStorage.getItem('token')
      if (!token) {
        permissionLogger.warn('没有token，无法获取权限')
        userPermissions.value = null
        permissionsLoaded.value = true
        return null
      }

      const response = await authApi.getUserPermissions()

      if (response.code === 200) {
        userPermissions.value = response.data
        permissionsLoaded.value = true

        permissionLogger.info('用户权限加载成功', {
          user: response.data.user?.email,
          permissionCount: Object.keys(response.data.permissions || {}).length,
        })

        return response.data
      } else {
        permissionLogger.error('权限加载失败', { code: response.code, message: response.message })
        throw new Error(response.message || '权限加载失败')
      }
    } catch (error) {
      permissionLogger.error('权限加载错误', error)

      // 设置权限加载完成状态，避免阻塞系统使用
      permissionsLoaded.value = true

      // 网络错误不清除已有权限信息
      if (error.code === -1 || error.message?.includes('网络')) {
        permissionLogger.warn('网络错误，保持现有权限状态')
        ElMessage.warning('网络错误，权限信息可能已过期')
      } else {
        // 其他错误时，如果用户已有权限信息，不清除
        if (!userPermissions.value) {
          permissionLogger.warn('权限加载失败，但不阻止系统使用')
          ElMessage.warning('权限加载失败，部分功能可能受限')
        }
      }

      return userPermissions.value
    } finally {
      loading.value = false
    }
  }

  /**
   * 清除权限信息
   */
  const clearPermissions = () => {
    permissionLogger.info('清除权限信息')
    userPermissions.value = null
    permissionsLoaded.value = false
  }

  /**
   * 刷新权限信息
   * @returns {Promise<Object|null>} 权限数据
   */
  const refreshPermissions = async () => {
    permissionsLoaded.value = false
    return await loadUserPermissions()
  }

  /**
   * 检查权限是否已初始化
   * @returns {boolean} 是否已初始化
   */
  const isPermissionsInitialized = computed(() => {
    return permissionsLoaded.value
  })

  return {
    // 状态
    userPermissions,
    permissionsLoaded,
    loading,

    // 计算属性
    canEditVesselInfo,
    canEditLocalFee,
    canViewLocalFee,
    canDeleteLocalFee,
    canCreateLocalFee,
    canQueryLocalFee,
    isAdmin,
    isPermissionsInitialized,

    // 方法
    hasPermission,
    hasAnyPermission,
    checkSpecificPermission,
    loadUserPermissions,
    clearPermissions,
    refreshPermissions,
    setAuthStoreRef,
  }
})

/**
 * 权限工具函数
 */
export const usePermissionUtils = () => {
  const permissionStore = usePermissionStore()

  return {
    /**
     * 检查权限并显示提示
     * @param {string} permission 权限代码
     * @param {string} message 无权限时的提示信息
     * @returns {boolean} 是否有权限
     */
    checkPermissionWithMessage: (permission, message = '您没有执行此操作的权限') => {
      const hasPermission = permissionStore.hasPermission(permission)
      if (!hasPermission) {
        ElMessage.warning(message)
      }
      return hasPermission
    },

    /**
     * 确保权限已加载
     * @returns {Promise<boolean>} 是否加载成功
     */
    ensurePermissionsLoaded: async () => {
      if (!permissionStore.permissionsLoaded) {
        const result = await permissionStore.loadUserPermissions()
        return !!result
      }
      return true
    },
  }
}
