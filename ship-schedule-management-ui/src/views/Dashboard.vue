<template>
  <div class="dashboard">
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="24" color="#1f4e79">
            <Van />
          </el-icon>
          <span class="title">环海运通管理系统</span>
        </div>
        <div class="header-right">
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

      <!-- 主体内容 -->
      <el-main class="main">
        <div class="welcome-card">
          <div class="welcome-content">
            <h1>欢迎来到环海运通管理系统！</h1>
            <p>您已成功登录，现在可以开始使用我们的专业国际物流运输管理平台。</p>

            <div class="feature-grid">
              <!-- 船期管理功能 -->
              <div
                v-if="
                  authStore.user?.is_superuser ||
                  permissionStore.hasPermission('vessel_schedule_list')
                "
                class="feature-card"
                @click="navigateToFeature('shipping')"
              >
                <div class="feature-icon shipping">
                  <el-icon :size="32"><Van /></el-icon>
                </div>
                <h3>船期管理</h3>
                <p>查看和管理船期信息，跟踪货物运输状态</p>
              </div>

              <!-- 系统管理功能 -->
              <div
                v-if="
                  authStore.user?.is_superuser ||
                  authStore.user?.is_staff ||
                  authStore.user?.email === 'admin@example.com' ||
                  authStore.hasAnyPermission(['user.list', 'role.list', 'permission.list'])
                "
                class="feature-card admin"
                @click="navigateToFeature('admin')"
              >
                <div class="feature-icon admin">
                  <el-icon :size="32"><Setting /></el-icon>
                </div>
                <h3>系统管理</h3>
                <p>用户管理、角色分配、权限配置</p>
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import { Van, User, ArrowDown, SwitchButton, Setting } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getUserAvatarUrl } from '@/utils/avatar'

const router = useRouter()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

// 计算头像URL
const userAvatarUrl = computed(() =>
  getUserAvatarUrl(authStore.user, 'http://127.0.0.1:8000', authStore.avatarVersion)
)

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

// 跳转到个人资料页面
const goToProfile = () => {
  router.push('/profile')
}

// 导航到功能页面
const navigateToFeature = feature => {
  switch (feature) {
    case 'admin':
      router.push('/admin')
      break
    case 'shipping':
      router.push('/schedule')
      break
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  width: 100%;
  height: 100vh;
  background: #f5f5f5;
}

.header {
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

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

.main {
  padding: 24px;
}

.welcome-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  animation: slideIn 0.6s ease-out;

  .welcome-content {
    text-align: center;

    h1 {
      font-size: 32px;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
      background: linear-gradient(135deg, #1f4e79, #2c5aa0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    p {
      font-size: 16px;
      color: #666;
      margin-bottom: 48px;
      line-height: 1.6;
    }

    .feature-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
      margin-top: 48px;

      .feature-card {
        text-align: center;
        padding: 32px 24px;
        border-radius: 16px;
        background: #f8f9fa;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
          border-color: #409eff;
        }

        .feature-icon {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 64px;
          height: 64px;
          margin: 0 auto 20px;
          border-radius: 16px;

          &.shipping {
            background: linear-gradient(135deg, #1f4e79, #2c5aa0);
            color: white;
          }

          &.admin {
            background: linear-gradient(135deg, #f56c6c, #f78989);
            color: white;
          }
        }

        h3 {
          font-size: 18px;
          font-weight: 600;
          color: #333;
          margin-bottom: 12px;
        }

        p {
          font-size: 14px;
          color: #666;
          line-height: 1.5;
          margin: 0;
        }
      }
    }
  }
}

// 动画
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header {
    padding: 0 16px;

    .header-left .title {
      display: none;
    }
  }

  .main {
    padding: 16px;
  }

  .welcome-card {
    padding: 24px 16px;

    .welcome-content {
      h1 {
        font-size: 24px;
      }

      .feature-grid {
        grid-template-columns: 1fr;
        gap: 16px;
        margin-top: 32px;
      }
    }
  }
}
</style>
