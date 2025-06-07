<template>
  <div class="user-profile">
    <!-- 顶部导航栏 -->
    <div class="profile-header">
      <div class="header-content">
        <div class="back-nav" @click="goBack">
          <el-icon class="back-icon">
            <ArrowLeft />
          </el-icon>
          <span class="back-text">返回</span>
        </div>
        <div class="header-info">
          <h1 class="page-title">个人资料</h1>
          <p class="page-subtitle">管理您的个人信息和头像设置</p>
        </div>
      </div>
    </div>

    <div class="profile-content">
      <!-- 左侧：头像管理 -->
      <div class="left-section">
        <el-card class="avatar-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>头像设置</span>
            </div>
          </template>

          <div class="avatar-section">
            <AvatarUpload
              :size="120"
              @upload-success="handleAvatarSuccess"
              @delete-success="handleAvatarSuccess"
            />
          </div>
        </el-card>
      </div>

      <!-- 右侧：基本信息和密码设置 -->
      <div class="right-section">
        <!-- 基本信息卡片 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
              <el-button
                type="primary"
                size="small"
                @click="editMode = !editMode"
                :icon="editMode ? Close : Edit"
              >
                {{ editMode ? '取消编辑' : '编辑信息' }}
              </el-button>
            </div>
          </template>

          <div class="info-content">
            <!-- 查看模式 -->
            <div v-if="!editMode" class="view-mode">
              <div class="info-item">
                <label>邮箱地址：</label>
                <span>{{ userInfo.email }}</span>
              </div>

              <div class="info-item">
                <label>姓名：</label>
                <span>{{ userInfo.full_name || userInfo.short_name || '未设置' }}</span>
              </div>

              <div class="info-item">
                <label>注册时间：</label>
                <span>{{ formatDate(userInfo.date_joined) }}</span>
              </div>

              <div class="info-item">
                <label>最后登录：</label>
                <span>{{ formatDate(userInfo.last_login) || '从未登录' }}</span>
              </div>

              <div class="info-item">
                <label>账户状态：</label>
                <el-tag :type="userInfo.is_active ? 'success' : 'danger'" size="small">
                  {{ userInfo.is_active ? '正常' : '已禁用' }}
                </el-tag>
              </div>

              <div class="info-item">
                <label>用户类型：</label>
                <el-tag v-if="userInfo.is_superuser" type="danger" size="small">超级管理员</el-tag>
                <el-tag v-else-if="userInfo.is_staff" type="warning" size="small">管理员</el-tag>
                <el-tag v-else type="info" size="small">普通用户</el-tag>
              </div>
            </div>

            <!-- 编辑模式 -->
            <div v-else class="edit-mode">
              <el-form
                ref="formRef"
                :model="editForm"
                :rules="formRules"
                label-width="100px"
                label-position="left"
              >
                <el-form-item label="邮箱地址">
                  <el-input v-model="editForm.email" disabled placeholder="邮箱地址不可修改" />
                </el-form-item>

                <el-form-item label="名字" prop="first_name">
                  <el-input v-model="editForm.first_name" placeholder="请输入名字" clearable />
                </el-form-item>

                <el-form-item label="姓氏" prop="last_name">
                  <el-input v-model="editForm.last_name" placeholder="请输入姓氏" clearable />
                </el-form-item>
              </el-form>

              <div class="edit-actions">
                <el-button type="primary" @click="handleSaveInfo" :loading="saving">
                  保存修改
                </el-button>
                <el-button @click="cancelEdit">取消</el-button>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 密码修改卡片 -->
        <el-card class="password-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Lock /></el-icon>
              <span>密码设置</span>
            </div>
          </template>

          <div class="password-content">
            <el-button type="warning" @click="showPasswordDialog = true" :icon="Key">
              修改密码
            </el-button>
            <p class="password-tip">为了账户安全，建议定期更换密码</p>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="current_password">
          <el-input
            v-model="passwordForm.current_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, InfoFilled, Edit, Close, Lock, Key, ArrowLeft } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import AvatarUpload from '@/components/AvatarUpload.vue'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const editMode = ref(false)
const saving = ref(false)
const showPasswordDialog = ref(false)
const changingPassword = ref(false)

// 表单引用
const formRef = ref()
const passwordFormRef = ref()

// 用户信息
const userInfo = computed(() => authStore.user || {})

// 编辑表单
const editForm = reactive({
  email: '',
  first_name: '',
  last_name: '',
})

// 密码表单
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

// 表单验证规则
const formRules = {
  first_name: [{ max: 30, message: '名字长度不能超过30个字符', trigger: 'blur' }],
  last_name: [{ max: 30, message: '姓氏长度不能超过30个字符', trigger: 'blur' }],
}

const passwordRules = {
  current_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 初始化编辑表单
const initEditForm = () => {
  editForm.email = userInfo.value.email || ''
  editForm.first_name = userInfo.value.first_name || ''
  editForm.last_name = userInfo.value.last_name || ''
}

// 监听编辑模式变化
const cancelEdit = () => {
  editMode.value = false
  initEditForm()
}

// 返回上一页
const goBack = () => {
  // 优先返回上一页，如果没有历史记录则返回首页
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/dashboard')
  }
}

// 格式化日期
const formatDate = dateString => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 头像操作成功回调
const handleAvatarSuccess = () => {
  // 头像已在store中更新，这里可以添加额外逻辑
  console.log('头像操作成功，当前用户信息:', userInfo.value)
}

// 保存基本信息
const handleSaveInfo = async () => {
  try {
    await formRef.value?.validate()

    saving.value = true

    const response = await authApi.updateUser({
      first_name: editForm.first_name,
      last_name: editForm.last_name,
    })

    if (response.code === 200) {
      // 更新store中的用户信息
      authStore.updateUserInfo(response.data)
      ElMessage.success('个人信息更新成功')
      editMode.value = false
    } else {
      ElMessage.error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error('更新失败，请重试')
  } finally {
    saving.value = false
  }
}

// 修改密码
const handleChangePassword = async () => {
  try {
    await passwordFormRef.value?.validate()

    changingPassword.value = true

    const response = await authApi.updateUser({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    })

    if (response.code === 200) {
      ElMessage.success('密码修改成功')
      showPasswordDialog.value = false

      // 清空密码表单
      Object.assign(passwordForm, {
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
    } else {
      ElMessage.error(response.message || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('密码修改失败，请重试')
  } finally {
    changingPassword.value = false
  }
}

// 初始化
initEditForm()
</script>

<style scoped>
.user-profile {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.profile-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .back-nav {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 8px 16px;
    border-radius: 8px;
    transition: all 0.3s ease;
    color: #606266;

    &:hover {
      background: #f5f7fa;
      color: #409eff;
      transform: translateX(-2px);
    }

    .back-icon {
      font-size: 18px;
      transition: transform 0.3s ease;
    }

    .back-text {
      font-size: 14px;
      font-weight: 500;
    }

    &:hover .back-icon {
      transform: translateX(-2px);
    }
  }

  .header-info {
    flex: 1;

    .page-title {
      margin: 0 0 4px 0;
      color: #303133;
      font-size: 28px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }

    .page-subtitle {
      margin: 0;
      color: #909399;
      font-size: 14px;
      line-height: 1.5;
    }
  }
}

.profile-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 32px;
  align-items: start;
}

.avatar-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;

  :deep(.el-card__header) {
    padding: 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;

    .card-header {
      color: white;
      font-weight: 600;

      .el-icon {
        color: white;
      }
    }
  }

  :deep(.el-card__body) {
    padding: 32px 24px;
    background: white;
  }
}

.info-card,
.password-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  margin-bottom: 24px;

  :deep(.el-card__header) {
    padding: 24px;
    background: #f8f9fa;
    border: none;

    .card-header {
      color: #303133;
      font-weight: 600;
      font-size: 16px;

      .el-button {
        border-radius: 8px;
        font-weight: 500;
      }
    }
  }

  :deep(.el-card__body) {
    padding: 24px;
    background: white;
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;

  .el-button {
    margin-left: auto;
  }
}

.avatar-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.info-content {
  .view-mode {
    .info-item {
      display: flex;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f5f5f5;

      &:last-child {
        border-bottom: none;
      }

      label {
        width: 100px;
        color: #606266;
        font-weight: 500;
        flex-shrink: 0;
      }

      span {
        color: #303133;
      }
    }
  }

  .edit-mode {
    .edit-actions {
      display: flex;
      gap: 12px;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #f0f0f0;
    }
  }
}

.password-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;

  .password-tip {
    margin: 0;
    color: #909399;
    font-size: 13px;
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .profile-content {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 24px 16px;
  }

  .profile-header .header-content {
    padding: 16px 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .back-nav {
    align-self: flex-start;
  }
}

@media (max-width: 768px) {
  .user-profile {
    background: #f5f7fa;
  }

  .profile-header .header-content {
    padding: 12px 16px;
  }

  .profile-content {
    padding: 16px 12px;
  }

  .header-info .page-title {
    font-size: 24px;
  }

  .info-content .view-mode .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;

    label {
      width: auto;
      font-size: 13px;
      color: #909399;
    }
  }

  .edit-actions {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }

  .avatar-card :deep(.el-card__body) {
    padding: 24px 16px;
  }

  .info-card :deep(.el-card__body),
  .password-card :deep(.el-card__body) {
    padding: 20px 16px;
  }
}
</style>
