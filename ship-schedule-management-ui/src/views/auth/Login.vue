<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="wave wave1"></div>
      <div class="wave wave2"></div>
      <div class="wave wave3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <el-icon :size="40" color="#409eff">
            <Ship />
          </el-icon>
        </div>
        <h1 class="title">船期管理系统</h1>
        <p class="subtitle">专业的物流管理平台</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="email">
          <el-input
            v-model="loginForm.email"
            placeholder="请输入邮箱地址"
            :prefix-icon="Message"
            clearable
            autocomplete="email"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="authStore.loading"
            @click="handleLogin"
          >
            <span v-if="!authStore.loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>还没有账户？</span>
        <el-link type="primary" underline="never" @click="$router.push('/register')">
          立即注册
        </el-link>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="footer-info">
      <p>&copy; 2025 船期管理系统. 保留所有权利.</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Message, Lock, Ship } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref()

// 表单数据
const loginForm = reactive({
  email: '',
  password: '',
})

// 表单验证规则
const loginRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    console.log('📝 表单验证通过，开始登录...')

    const result = await authStore.login(loginForm)

    if (result.success) {
      console.log('🎯 登录返回成功，结果:', result)

      // 等待一小段时间确保状态完全更新
      await new Promise(resolve => setTimeout(resolve, 100))

      // 再次检查认证状态
      const currentAuthState = {
        isAuthenticated: authStore.isAuthenticated,
        token: !!authStore.token,
        user: !!authStore.user,
        userEmail: authStore.user?.email,
      }

      console.log('🔍 跳转前认证状态检查:', currentAuthState)

      if (!authStore.isAuthenticated) {
        console.error('⚠️ 登录成功但认证状态异常')
        ElMessage.error('登录状态异常，请重试')

        // 调试信息：输出到控制台供用户检查
        console.group('🛠️ 调试信息')
        console.log('Token值:', authStore.token)
        console.log('用户信息:', authStore.user)
        console.log('计算属性isAuthenticated:', authStore.isAuthenticated)
        console.groupEnd()

        return
      }

      console.log('✅ 认证状态正常，准备跳转到dashboard')
      // 登录成功，跳转到仪表盘
      await router.push('/dashboard')
      console.log('🎯 路由跳转完成')
    } else {
      console.log('❌ 登录失败:', result.message)
    }
  } catch (error) {
    console.error('💥 登录处理异常:', error)
    ElMessage.error('登录处理失败，请重试')
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  position: relative;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

// 背景装饰
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;

  .wave {
    position: absolute;
    width: 200%;
    height: 200%;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 45%;
    animation: wave 20s linear infinite;

    &.wave1 {
      top: -60%;
      left: -50%;
      animation-duration: 25s;
    }

    &.wave2 {
      top: -70%;
      right: -50%;
      animation-duration: 30s;
      animation-direction: reverse;
    }

    &.wave3 {
      bottom: -60%;
      left: -30%;
      animation-duration: 35s;
    }
  }
}

@keyframes wave {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

// 登录卡片
.login-card {
  position: relative;
  z-index: 1;
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  animation: cardSlideIn 0.8s ease-out;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;

  .logo {
    margin-bottom: 20px;
    animation: logoFloat 3s ease-in-out infinite;
  }

  .title {
    font-size: 28px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
    letter-spacing: 1px;
  }

  .subtitle {
    color: #666;
    font-size: 14px;
    margin: 0;
  }
}

@keyframes logoFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;

    :deep(.el-input__inner) {
      height: 50px;
      border-radius: 12px;
      border: 1px solid #e0e6ed;
      transition: all 0.3s ease;

      &:focus {
        border-color: #409eff;
        box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
      }
    }

    :deep(.el-input__prefix) {
      display: flex;
      align-items: center;
    }
  }

  .login-btn {
    width: 100%;
    height: 50px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 500;
    background: linear-gradient(135deg, #409eff, #5470c6);
    border: none;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(64, 158, 255, 0.3);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  color: #666;
  font-size: 14px;

  .el-link {
    margin-left: 8px;
    font-weight: 500;
  }
}

.footer-info {
  position: absolute;
  bottom: 30px;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  z-index: 1;
}

// 响应式设计
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    padding: 30px 20px;
    margin: 0 20px;
  }

  .login-header .title {
    font-size: 24px;
  }
}
</style>
