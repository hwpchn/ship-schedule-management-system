<template>
  <div class="admin-layout">
    <el-container>
      <!-- 头部 -->
      <el-header class="admin-header">
        <div class="header-left">
          <el-icon :size="24" color="#1f4e79">
            <Van />
          </el-icon>
          <span class="title">环海运通管理系统 - 系统管理</span>
        </div>
        <div class="header-right">
          <el-button link @click="$router.push('/dashboard')" class="back-btn">
            <el-icon><ArrowLeft /></el-icon>
            返回首页
          </el-button>

          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="32" :src="userAvatarUrl">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ authStore.user?.email || '用户' }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToProfile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-container class="admin-body">
        <!-- 左侧导航 -->
        <el-aside class="admin-aside" width="240px">
          <el-menu :default-active="$route.path" class="admin-menu" router :unique-opened="true">
            <el-menu-item index="/admin/users" v-if="authStore.hasPermission('user.list')">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>

            <el-menu-item index="/admin/roles" v-if="authStore.hasPermission('role.list')">
              <el-icon><UserFilled /></el-icon>
              <span>角色管理</span>
            </el-menu-item>

            <el-menu-item
              index="/admin/permissions"
              v-if="authStore.hasPermission('permission.list')"
            >
              <el-icon><Lock /></el-icon>
              <span>权限管理</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="admin-main">
          <div class="content-wrapper">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Van,
  User,
  UserFilled,
  Lock,
  ArrowLeft,
  ArrowDown,
  SwitchButton,
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { getUserAvatarUrl } from '@/utils/avatar'

const router = useRouter()
const authStore = useAuthStore()

// 计算头像URL
const userAvatarUrl = computed(() =>
  getUserAvatarUrl(authStore.user, 'http://127.0.0.1:8000', authStore.avatarVersion)
)

// 跳转到个人资料页面
const goToProfile = () => {
  router.push('/profile')
}

// 处理登出
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await authStore.logout()
    router.push('/login')
  } catch (error) {
    // 用户取消操作
  }
}
</script>

<style lang="scss" scoped>
.admin-layout {
  height: 100vh;
  background: #f5f5f5;
}

.admin-header {
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .back-btn {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #409eff;

      &:hover {
        background: rgba(64, 158, 255, 0.1);
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.3s ease;

      &:hover {
        background: #f5f5f5;
      }

      .username {
        font-size: 14px;
        color: #333;
      }

      .arrow {
        font-size: 12px;
        color: #666;
      }
    }
  }
}

.admin-body {
  height: calc(100vh - 60px);
}

.admin-aside {
  background: white;
  border-right: 1px solid #e8e8e8;
  overflow: hidden;

  .admin-menu {
    border: none;
    height: 100%;

    :deep(.el-menu-item) {
      height: 56px;
      line-height: 56px;
      margin: 4px 8px;
      border-radius: 8px;

      &:hover {
        background: rgba(64, 158, 255, 0.1);
        color: #409eff;
      }

      &.is-active {
        background: #409eff;
        color: white;

        &:hover {
          background: #337ecc;
        }
      }
    }
  }
}

.admin-main {
  padding: 24px;
  background: #f5f5f5;
  overflow-y: auto;

  .content-wrapper {
    max-width: 1200px;
    margin: 0 auto;
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 响应式设计
@media (max-width: 768px) {
  .admin-aside {
    width: 200px !important;
  }

  .header-left .title {
    display: none;
  }

  .admin-main {
    padding: 16px;
  }
}
</style>
