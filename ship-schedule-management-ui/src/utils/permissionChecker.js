/**
 * 权限检查工具函数
 * 提供统一的权限验证逻辑
 */

import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

/**
 * 检查用户是否为超级管理员
 * @param {Object} user 用户对象
 * @returns {boolean} 是否为超级管理员
 */
export const isSuperAdmin = user => {
  return user?.is_superuser === true
}

/**
 * 检查用户是否有管理员角色
 * @param {Object} user 用户对象
 * @param {Array} roles 用户角色列表
 * @returns {boolean} 是否为管理员
 */
export const isAdmin = (user, roles = []) => {
  // 超级管理员
  if (isSuperAdmin(user)) {
    return true
  }

  // 检查角色中是否包含管理员角色
  const adminRoles = ['admin', 'administrator', 'super_admin']
  return roles.some(role => {
    const roleName = typeof role === 'string' ? role : role.name || role.code
    return adminRoles.includes(roleName?.toLowerCase())
  })
}

/**
 * 检查用户是否有特定权限
 * @param {string} permission 权限代码
 * @param {Object} options 选项
 * @param {boolean} options.allowSuperAdmin 是否允许超级管理员跳过权限检查
 * @returns {boolean} 是否有权限
 */
export const hasPermission = (permission, options = { allowSuperAdmin: true }) => {
  try {
    const authStore = useAuthStore()
    const permissionStore = usePermissionStore()

    // 检查超级管理员
    if (options.allowSuperAdmin && isSuperAdmin(authStore.user)) {
      return true
    }

    // 检查具体权限
    return permissionStore.hasPermission(permission)
  } catch (error) {
    console.error('权限检查失败:', error)
    return false
  }
}

/**
 * 检查用户是否有任一权限
 * @param {Array} permissions 权限代码列表
 * @param {Object} options 选项
 * @returns {boolean} 是否有任一权限
 */
export const hasAnyPermission = (permissions, options = { allowSuperAdmin: true }) => {
  try {
    const authStore = useAuthStore()
    const permissionStore = usePermissionStore()

    // 检查超级管理员
    if (options.allowSuperAdmin && isSuperAdmin(authStore.user)) {
      return true
    }

    // 检查具体权限
    return permissionStore.hasAnyPermission(permissions)
  } catch (error) {
    console.error('权限检查失败:', error)
    return false
  }
}

/**
 * 检查用户是否有所有权限
 * @param {Array} permissions 权限代码列表
 * @param {Object} options 选项
 * @returns {boolean} 是否有所有权限
 */
export const hasAllPermissions = (permissions, options = { allowSuperAdmin: true }) => {
  try {
    const authStore = useAuthStore()

    // 检查超级管理员
    if (options.allowSuperAdmin && isSuperAdmin(authStore.user)) {
      return true
    }

    // 检查所有权限
    return permissions.every(permission => hasPermission(permission, { allowSuperAdmin: false }))
  } catch (error) {
    console.error('权限检查失败:', error)
    return false
  }
}

/**
 * 权限检查装饰器（用于组合式函数）
 * @param {string|Array} permissions 权限代码或权限列表
 * @param {Function} fn 要执行的函数
 * @param {Object} options 选项
 * @returns {Function} 包装后的函数
 */
export const withPermission = (permissions, fn, options = {}) => {
  return (...args) => {
    const hasRequiredPermission = Array.isArray(permissions)
      ? hasAnyPermission(permissions, options)
      : hasPermission(permissions, options)

    if (hasRequiredPermission) {
      return fn(...args)
    } else {
      console.warn('权限不足，操作被拒绝:', permissions)
      throw new Error('权限不足')
    }
  }
}

/**
 * 路由权限检查
 * @param {Object} route 路由对象
 * @param {Object} user 用户对象
 * @returns {boolean} 是否有访问权限
 */
export const canAccessRoute = (route, user = null) => {
  try {
    const authStore = useAuthStore()
    const currentUser = user || authStore.user

    // 如果没有权限要求，允许访问
    if (!route.meta?.permission) {
      return true
    }

    // 检查超级管理员
    if (isSuperAdmin(currentUser)) {
      return true
    }

    // 检查具体权限
    return hasPermission(route.meta.permission, { allowSuperAdmin: false })
  } catch (error) {
    console.error('路由权限检查失败:', error)
    return false
  }
}

/**
 * 基于角色的权限检查（RBAC）
 * @param {string|Array} requiredRoles 需要的角色
 * @param {Array} userRoles 用户角色
 * @returns {boolean} 是否有权限
 */
export const hasRole = (requiredRoles, userRoles = []) => {
  try {
    const authStore = useAuthStore()
    const roles = userRoles.length > 0 ? userRoles : authStore.roles

    if (isSuperAdmin(authStore.user)) {
      return true
    }

    const required = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]

    return required.some(requiredRole => {
      return roles.some(userRole => {
        const roleName = typeof userRole === 'string' ? userRole : userRole.name || userRole.code
        return roleName === requiredRole
      })
    })
  } catch (error) {
    console.error('角色检查失败:', error)
    return false
  }
}

/**
 * 检查用户是否可以访问管理页面
 * @returns {boolean} 是否可以访问
 */
export const canAccessAdmin = () => {
  try {
    const authStore = useAuthStore()

    // 超级管理员可以访问
    if (isSuperAdmin(authStore.user)) {
      return true
    }

    // 检查管理员角色
    if (isAdmin(authStore.user, authStore.roles)) {
      return true
    }

    // 检查管理相关权限
    const adminPermissions = ['user.list', 'role.list', 'permission.list', 'admin.access']

    return hasAnyPermission(adminPermissions, { allowSuperAdmin: false })
  } catch (error) {
    console.error('管理页面权限检查失败:', error)
    return false
  }
}

export default {
  isSuperAdmin,
  isAdmin,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  withPermission,
  canAccessRoute,
  hasRole,
  canAccessAdmin,
}
