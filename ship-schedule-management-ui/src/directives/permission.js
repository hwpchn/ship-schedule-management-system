/**
 * 权限指令
 * 用于在模板中进行权限控制
 *
 * 使用方式:
 * v-permission="'user.create'" - 检查单个权限
 * v-permission="['user.create', 'user.update']" - 检查多个权限(任一)
 * v-permission:all="['user.create', 'user.update']" - 检查多个权限(全部)
 * v-permission:role="'admin'" - 检查角色
 */

import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  hasRole,
} from '@/utils/permissionChecker'

/**
 * 检查权限并控制元素显示/隐藏
 * @param {HTMLElement} el DOM元素
 * @param {Object} binding 指令绑定对象
 */
const checkPermission = (el, binding) => {
  const { value, arg, modifiers } = binding

  if (!value) {
    console.warn('v-permission 指令需要提供权限值')
    return
  }

  let hasPermissionResult = false

  try {
    if (arg === 'role') {
      // 角色检查
      hasPermissionResult = hasRole(value)
    } else if (arg === 'all') {
      // 检查所有权限
      hasPermissionResult = hasAllPermissions(Array.isArray(value) ? value : [value])
    } else {
      // 默认检查权限（单个或任一）
      if (Array.isArray(value)) {
        hasPermissionResult = hasAnyPermission(value)
      } else {
        hasPermissionResult = hasPermission(value)
      }
    }

    // 根据权限结果控制元素
    if (hasPermissionResult) {
      // 有权限，显示元素
      el.style.display = ''
      el.removeAttribute('disabled')

      // 移除无权限样式
      el.classList.remove('permission-disabled')
    } else {
      // 无权限，根据修饰符决定处理方式
      if (modifiers.hide) {
        // 隐藏元素
        el.style.display = 'none'
      } else if (modifiers.disable) {
        // 禁用元素
        el.setAttribute('disabled', 'disabled')
        el.classList.add('permission-disabled')
      } else {
        // 默认隐藏
        el.style.display = 'none'
      }
    }
  } catch (error) {
    console.error('权限指令检查失败:', error)
    // 发生错误时隐藏元素，确保安全
    el.style.display = 'none'
  }
}

/**
 * 权限指令定义
 */
export const permission = {
  // Vue 3 指令生命周期
  mounted(el, binding) {
    checkPermission(el, binding)
  },

  updated(el, binding) {
    checkPermission(el, binding)
  },

  // Vue 2 兼容（如果需要）
  inserted(el, binding) {
    checkPermission(el, binding)
  },

  update(el, binding) {
    checkPermission(el, binding)
  },
}

/**
 * 简化的权限检查指令
 * v-show-permission - 有权限时显示
 * v-hide-permission - 无权限时隐藏
 */
export const showPermission = {
  mounted(el, binding) {
    const hasPermissionResult = Array.isArray(binding.value)
      ? hasAnyPermission(binding.value)
      : hasPermission(binding.value)

    if (!hasPermissionResult) {
      el.style.display = 'none'
    }
  },

  updated(el, binding) {
    const hasPermissionResult = Array.isArray(binding.value)
      ? hasAnyPermission(binding.value)
      : hasPermission(binding.value)

    el.style.display = hasPermissionResult ? '' : 'none'
  },
}

export const hidePermission = {
  mounted(el, binding) {
    const hasPermissionResult = Array.isArray(binding.value)
      ? hasAnyPermission(binding.value)
      : hasPermission(binding.value)

    if (hasPermissionResult) {
      el.style.display = 'none'
    }
  },

  updated(el, binding) {
    const hasPermissionResult = Array.isArray(binding.value)
      ? hasAnyPermission(binding.value)
      : hasPermission(binding.value)

    el.style.display = hasPermissionResult ? 'none' : ''
  },
}

/**
 * 安装所有权限指令
 * @param {Object} app Vue应用实例
 */
export const installPermissionDirectives = app => {
  app.directive('permission', permission)
  app.directive('show-permission', showPermission)
  app.directive('hide-permission', hidePermission)
}

export default permission
