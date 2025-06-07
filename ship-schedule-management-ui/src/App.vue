<template>
  <div id="app">
    <!-- 应用初始化加载状态 -->
    <div v-if="isInitializing" class="app-initializing">
      <div class="loading-spinner">
        <el-icon class="spin" :size="40">
          <Loading />
        </el-icon>
        <p>正在初始化应用...</p>
      </div>
    </div>

    <!-- 主应用内容 -->
    <router-view v-else />
  </div>
</template>

<script setup>
import { onMounted, ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import { Loading } from '@element-plus/icons-vue'

const isInitializing = ref(true)
let authStore = null
let permissionStore = null

// 网络状态监听
const handleOnline = () => {
  if (authStore && authStore.authStatus === 'network_error') {
    authStore.restoreFromNetworkError()
    // 如果有token，尝试重新初始化认证状态
    if (authStore.token) {
      authStore.initAuth().then(async success => {
        if (success) {
          // 恢复认证后重新加载权限
          try {
            if (permissionStore) {
              await permissionStore.loadUserPermissions()
            }
          } catch (permError) {
            console.warn('权限恢复失败:', permError)
          }
        }
      })
    }
  }
}

const handleOffline = () => {
  // 设置网络错误状态，但保持认证信息
  if (authStore && authStore.isAuthenticated) {
    authStore.setNetworkError()
  }
}

// 应用启动时初始化认证状态
onMounted(async () => {
  // 初始化 store
  authStore = useAuthStore()
  permissionStore = usePermissionStore()

  // 添加网络状态监听
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)

  try {
    // 检查localStorage中是否有token
    const hasToken = localStorage.getItem('token')
    const hasRefreshToken = localStorage.getItem('refreshToken')

    if (hasToken && authStore.authStatus === 'unknown') {
      // 预先检查认证数据完整性
      if (!hasRefreshToken) {
        // 不立即清理，先尝试用现有token验证身份
        try {
          // 允许使用部分token进行验证
          const success = await authStore.initAuth(true)
          if (success) {
            // 认证成功后初始化权限
            try {
              await permissionStore.loadUserPermissions()
            } catch (permError) {
              console.warn('权限初始化失败，但不影响应用启动:', permError)
            }
          } else {
            // 只有在验证失败后才清理
            authStore.validateAndCleanAuthData()
          }
        } catch (error) {
          console.error('token验证过程出错:', error)
          // 出错时也清理认证信息
          authStore.validateAndCleanAuthData()
        }
      } else {
        // 认证信息完整，正常初始化
        const success = await authStore.initAuth()
        if (success) {
          // 认证成功后初始化权限
          try {
            await permissionStore.loadUserPermissions()
          } catch (permError) {
            console.warn('权限初始化失败，但不影响应用启动:', permError)
          }
        }
      }
    } else if (!hasToken) {
      // 使用 validateAndCleanAuthData 来正确设置状态
      authStore.validateAndCleanAuthData()
    }
  } catch (error) {
    console.error('认证状态初始化失败:', error)

    // 判断错误类型
    if (authStore.isNetworkErrorType(error)) {
      authStore.setNetworkError()
    }
  } finally {
    // 初始化完成，隐藏加载状态
    isInitializing.value = false
  }
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script>

<style lang="scss">
#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.app-initializing {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  .loading-spinner {
    text-align: center;
    color: white;

    .spin {
      animation: spin 1s linear infinite;
    }

    p {
      margin-top: 16px;
      font-size: 16px;
      opacity: 0.9;
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
