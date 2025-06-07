<template>
  <div class="register-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="wave wave1"></div>
      <div class="wave wave2"></div>
      <div class="wave wave3"></div>
    </div>

    <!-- 注册卡片 -->
    <div class="register-card">
      <div class="register-header">
        <div class="logo">
          <el-icon :size="40" color="#409eff">
            <Ship />
          </el-icon>
        </div>
        <h1 class="title">加入我们</h1>
        <p class="subtitle">创建您的船期管理账户</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        size="large"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            :prefix-icon="Message"
            clearable
            autocomplete="email"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            :prefix-icon="Lock"
            show-password
            autocomplete="new-password"
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-btn"
            :loading="authStore.loading"
            @click="handleRegister"
          >
            <span v-if="!authStore.loading">注册</span>
            <span v-else>注册中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <span>已有账户？</span>
        <el-link type="primary" underline="never" @click="$router.push('/login')">立即登录</el-link>
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
const registerFormRef = ref()

// 表单数据
const registerForm = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

// 自定义验证函数
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
    { max: 20, message: '密码长度不能超过20位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
    const result = await authStore.register({
      email: registerForm.email,
      password: registerForm.password,
      confirmPassword: registerForm.confirmPassword,
    })

    if (result.success) {
      // 注册成功，跳转到登录页面
      router.push('/login')
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}
</script>

<style lang="scss" scoped>
.register-container {
  position: relative;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
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

// 注册卡片
.register-card {
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

.register-header {
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

.register-form {
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

  .register-btn {
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

.register-footer {
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
  .register-card {
    width: 90%;
    padding: 30px 20px;
    margin: 0 20px;
  }

  .register-header .title {
    font-size: 24px;
  }
}
</style>
