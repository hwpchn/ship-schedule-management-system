<template>
  <div class="user-management">
    <div class="page-header">
      <div class="header-left">
        <h2>用户管理</h2>
        <p>管理系统用户和角色分配</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateUser" v-if="canCreateUser">
          <el-icon><Plus /></el-icon>
          创建用户
        </el-button>
      </div>
    </div>

    <div class="content-card">
      <!-- 搜索和筛选栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户邮箱或姓名"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-button @click="loadUsers">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <!-- 用户表格 -->
      <el-table :data="filteredUsers" v-loading="loading" stripe class="user-table">
        <el-table-column type="index" label="序号" width="60" />

        <el-table-column prop="email" label="邮箱" min-width="200">
          <template #default="{ row }">
            <div class="user-email">
              <el-avatar :size="32" :src="getUserAvatar(row)" class="user-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span>{{ row.email }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="full_name" label="姓名" min-width="120">
          <template #default="{ row }">
            {{ row.full_name || row.short_name || '未设置' }}
          </template>
        </el-table-column>

        <el-table-column label="用户角色" min-width="200">
          <template #default="{ row }">
            <div class="user-roles">
              <!-- 超级管理员标签 -->
              <el-tag
                v-if="row.is_superuser"
                size="small"
                type="danger"
                class="role-tag system-tag"
              >
                超级管理员
              </el-tag>

              <!-- 业务角色标签 -->
              <el-tag
                v-for="role in getUserRoles(row.id)"
                :key="role.id"
                size="small"
                type="primary"
                class="role-tag"
              >
                {{ role.name }}
              </el-tag>

              <!-- 无角色提示 -->
              <span v-if="!getUserRoles(row.id).length && !row.is_superuser" class="no-roles">
                暂无角色
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="date_joined" label="注册时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>

        <el-table-column prop="last_login" label="最后登录" width="120">
          <template #default="{ row }">
            {{ formatLastLogin(row.last_login) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="handleAssignRoles(row)" v-if="canAssignRoles">
                分配角色
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteUser(row)"
                v-if="canDeleteUser && !row.is_superuser"
                :disabled="row.id === authStore.user?.id"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 角色分配对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      title="分配用户角色"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="currentUser" class="role-assignment">
        <div class="user-info">
          <el-avatar :size="40" :src="getUserAvatar(currentUser)">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <h3>{{ currentUser.email }}</h3>
            <p>{{ currentUser.full_name || currentUser.short_name || '未设置姓名' }}</p>
          </div>
        </div>

        <el-divider />

        <div class="role-selection">
          <h4>选择角色</h4>
          <el-checkbox-group v-model="selectedRoleIds" class="role-checkboxes">
            <el-checkbox
              v-for="role in allRoles"
              :key="role.id"
              :label="role.id"
              class="role-checkbox"
            >
              <div class="role-option">
                <span class="role-name">{{ role.name }}</span>
                <span class="role-description">{{ role.description || '暂无描述' }}</span>
              </div>
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </div>

      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSaveRoles">保存</el-button>
      </template>
    </el-dialog>

    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="createUserDialogVisible"
      title="创建新用户"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createUserFormRef"
        :model="createUserForm"
        :rules="createUserRules"
        label-width="80px"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="createUserForm.email" placeholder="请输入用户邮箱" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="createUserForm.password"
            type="password"
            placeholder="请输入密码（至少8位）"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="password_confirm">
          <el-input
            v-model="createUserForm.password_confirm"
            type="password"
            placeholder="请再次输入密码"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item label="姓氏" prop="last_name">
          <el-input v-model="createUserForm.last_name" placeholder="请输入姓氏" clearable />
        </el-form-item>

        <el-form-item label="名字" prop="first_name">
          <el-input v-model="createUserForm.first_name" placeholder="请输入名字" clearable />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createUserDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSaveUser">创建用户</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import { authApi } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserAvatarUrl } from '@/utils/avatar'
import { Search, Refresh, User, Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const permissionStore = usePermissionStore()

// 获取用户头像URL的函数
const getUserAvatar = user => {
  return getUserAvatarUrl(user, 'http://127.0.0.1:8000', authStore.avatarVersion)
}

// 数据状态
const users = ref([])
const allRoles = ref([])
const userRoles = ref({}) // 用户角色映射表
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')

// 分页状态
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框状态
const roleDialogVisible = ref(false)
const currentUser = ref(null)
const selectedRoleIds = ref([])

// 创建用户对话框状态
const createUserDialogVisible = ref(false)
const createUserFormRef = ref(null)
const createUserForm = ref({
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
})

// 计算属性
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value

  const query = searchQuery.value.toLowerCase()
  return users.value.filter(
    user =>
      user.email.toLowerCase().includes(query) ||
      (user.full_name && user.full_name.toLowerCase().includes(query)) ||
      (user.short_name && user.short_name.toLowerCase().includes(query))
  )
})

// 权限检查计算属性
const canAssignRoles = computed(() => {
  return authStore.user?.is_superuser || permissionStore.hasPermission('user.role.assign')
})

const canDeleteUser = computed(() => {
  return authStore.user?.is_superuser || permissionStore.hasPermission('user.delete')
})

const canCreateUser = computed(() => {
  return authStore.user?.is_superuser || permissionStore.hasPermission('user.create')
})

// 创建用户表单验证规则
const createUserRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少8位', trigger: 'blur' },
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== createUserForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 获取用户角色
const getUserRoles = userId => {
  return userRoles.value[userId] || []
}

// 格式化日期
const formatDate = dateString => {
  if (!dateString || dateString === 'null' || dateString === null) return ''

  try {
    const date = new Date(dateString)
    // 检查日期是否有效
    if (isNaN(date.getTime())) return ''

    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  } catch (error) {
    console.warn('日期格式化错误:', dateString, error)
    return ''
  }
}

// 格式化最后登录时间
const formatLastLogin = dateString => {
  if (!dateString || dateString === 'null' || dateString === null) {
    return '从未登录'
  }

  try {
    const date = new Date(dateString)
    // 检查日期是否有效
    if (isNaN(date.getTime())) return '从未登录'

    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  } catch (error) {
    console.warn('最后登录时间格式化错误:', dateString, error)
    return '从未登录'
  }
}

// 加载用户列表
const loadUsers = async () => {
  try {
    loading.value = true
    const response = await authApi.getUsers({
      page: currentPage.value,
      page_size: pageSize.value,
    })

    if (response.code === 200) {
      users.value = response.data.users || []
      total.value = response.data.total || 0

      // 调试：打印用户数据，检查last_login字段
      console.log(
        '📊 用户列表数据:',
        users.value.map(user => ({
          email: user.email,
          last_login: user.last_login,
          last_login_type: typeof user.last_login,
          date_joined: user.date_joined,
        }))
      )

      // 加载每个用户的角色信息
      await loadAllUserRoles()
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 加载所有用户的角色信息
const loadAllUserRoles = async () => {
  const rolePromises = users.value.map(async user => {
    try {
      const response = await authApi.getUserRoles(user.id)
      if (response.code === 200) {
        userRoles.value[user.id] = response.data.roles || []
      }
    } catch (error) {
      console.error(`加载用户 ${user.id} 角色失败:`, error)
      userRoles.value[user.id] = []
    }
  })

  await Promise.all(rolePromises)
}

// 加载所有角色
const loadAllRoles = async () => {
  try {
    const response = await authApi.getRoles()
    if (response.code === 200) {
      allRoles.value = response.data.results || []
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  }
}

// 搜索处理
const handleSearch = () => {
  // 搜索在计算属性中处理，这里可以添加防抖逻辑
}

// 分页处理
const handleSizeChange = size => {
  pageSize.value = size
  currentPage.value = 1
  loadUsers()
}

const handleCurrentChange = page => {
  currentPage.value = page
  loadUsers()
}

// 分配角色
const handleAssignRoles = async user => {
  console.log('🎯 开始分配角色:', user)
  currentUser.value = user

  // 加载角色列表
  await loadAllRoles()
  console.log('📋 可用角色列表:', allRoles.value)

  // 设置当前用户已有的角色
  const userCurrentRoles = getUserRoles(user.id)
  selectedRoleIds.value = userCurrentRoles.map(role => role.id)

  console.log('👤 用户当前角色:', userCurrentRoles)
  console.log('🔢 选中的角色ID:', selectedRoleIds.value)

  roleDialogVisible.value = true
}

// 保存角色分配
const handleSaveRoles = async () => {
  if (!currentUser.value) return

  try {
    submitting.value = true

    console.log('🔄 开始保存角色分配:', {
      userId: currentUser.value.id,
      userEmail: currentUser.value.email,
      selectedRoleIds: selectedRoleIds.value,
    })

    const response = await authApi.updateUserRoles(currentUser.value.id, selectedRoleIds.value)

    console.log('📝 角色分配API响应:', response)

    if (response.code === 200) {
      ElMessage.success('角色分配成功')
      roleDialogVisible.value = false

      // 更新本地用户角色数据
      userRoles.value[currentUser.value.id] = response.data.roles || []

      console.log('✅ 角色分配成功，更新本地数据:', userRoles.value[currentUser.value.id])
    } else {
      console.error('❌ 角色分配失败，响应码:', response.code, '消息:', response.message)
      ElMessage.error(response.message || '角色分配失败')
    }
  } catch (error) {
    console.error('💥 保存角色分配异常:', error)

    // 更详细的错误信息
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      console.log('🔍 角色分配错误详情:', {
        status,
        data: errorData,
        userId: currentUser.value?.id,
      })

      let errorMessage = '角色分配失败'

      if (status === 400) {
        errorMessage = errorData?.message || errorData?.detail || '请求参数错误'
      } else if (status === 403) {
        errorMessage = '权限不足，无法分配角色'
      } else if (status === 404) {
        errorMessage = '用户或角色不存在'
      } else {
        errorMessage = errorData?.message || errorData?.detail || '服务器错误'
      }

      ElMessage.error(errorMessage)
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('保存角色分配失败')
    }
  } finally {
    submitting.value = false
  }
}

// 删除用户
const handleDeleteUser = async user => {
  // 防止删除超级管理员
  if (user.is_superuser) {
    ElMessage.warning('不能删除超级管理员账户')
    return
  }

  // 防止删除自己
  if (user.id === authStore.user?.id) {
    ElMessage.warning('不能删除自己的账户')
    return
  }

  try {
    await ElMessageBox.confirm(`确定要删除用户 "${user.email}" 吗？此操作不可恢复。`, '删除用户', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger',
    })

    console.log('🗑️ 开始删除用户:', user)

    const response = await authApi.deleteUser(user.id)

    if (response.code === 200) {
      ElMessage.success('用户删除成功')

      // 从本地列表中移除用户
      users.value = users.value.filter(u => u.id !== user.id)

      // 清理用户角色数据
      delete userRoles.value[user.id]

      // 更新总数
      total.value = Math.max(0, total.value - 1)

      console.log('✅ 用户删除成功')
    } else {
      console.error('❌ 用户删除失败，响应码:', response.code, '消息:', response.message)
      ElMessage.error(response.message || '用户删除失败')
    }
  } catch (error) {
    if (error === 'cancel') {
      console.log('🚫 用户取消删除操作')
      return
    }

    console.error('💥 删除用户异常:', error)

    // 更详细的错误信息
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      console.log('🔍 删除用户错误详情:', {
        status,
        data: errorData,
        userId: user.id,
      })

      let errorMessage = '删除用户失败'

      if (status === 400) {
        errorMessage = errorData?.message || errorData?.detail || '请求参数错误'
      } else if (status === 403) {
        errorMessage = '权限不足，无法删除用户'
      } else if (status === 404) {
        errorMessage = '用户不存在'
      } else if (status === 409) {
        errorMessage = '用户正在使用中，无法删除'
      } else {
        errorMessage = errorData?.message || errorData?.detail || '服务器错误'
      }

      ElMessage.error(errorMessage)
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('删除用户失败')
    }
  }
}

// 创建用户
const handleCreateUser = () => {
  // 重置表单
  createUserForm.value = {
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  }

  // 清除表单验证
  if (createUserFormRef.value) {
    createUserFormRef.value.clearValidate()
  }

  createUserDialogVisible.value = true
}

// 保存新用户
const handleSaveUser = async () => {
  if (!createUserFormRef.value) return

  try {
    // 表单验证
    await createUserFormRef.value.validate()

    submitting.value = true

    console.log('🔄 开始创建用户:', createUserForm.value)

    const response = await authApi.createUser(createUserForm.value)

    console.log('📝 创建用户API响应:', response)

    if (response.code === 200) {
      ElMessage.success('用户创建成功')
      createUserDialogVisible.value = false

      // 重新加载用户列表
      await loadUsers()

      console.log('✅ 用户创建成功')
    } else {
      console.error('❌ 用户创建失败，响应码:', response.code, '消息:', response.message)
      ElMessage.error(response.message || '用户创建失败')
    }
  } catch (error) {
    if (error.fields) {
      // 表单验证错误
      console.log('📝 表单验证失败:', error.fields)
      return
    }

    console.error('💥 创建用户异常:', error)

    // 更详细的错误信息
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      console.log('🔍 创建用户错误详情:', {
        status,
        data: errorData,
      })

      let errorMessage = '创建用户失败'

      if (status === 400) {
        if (errorData?.email) {
          errorMessage = '邮箱已存在或格式不正确'
        } else if (errorData?.password) {
          errorMessage = '密码格式不符合要求'
        } else {
          errorMessage = errorData?.message || errorData?.detail || '请求参数错误'
        }
      } else if (status === 403) {
        errorMessage = '权限不足，无法创建用户'
      } else {
        errorMessage = errorData?.message || errorData?.detail || '服务器错误'
      }

      ElMessage.error(errorMessage)
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('创建用户失败')
    }
  } finally {
    submitting.value = false
  }
}

// 页面初始化
onMounted(() => {
  loadUsers()
})
</script>

<style lang="scss" scoped>
.user-management {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;

    .header-left {
      h2 {
        margin: 0 0 4px 0;
        font-size: 24px;
        font-weight: 600;
        color: #333;
      }

      p {
        margin: 0;
        color: #666;
        font-size: 14px;
      }
    }

    .header-right {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .content-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .search-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    align-items: center;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .user-table {
    margin-bottom: 24px;

    .user-email {
      display: flex;
      align-items: center;
      gap: 12px;

      .user-avatar {
        flex-shrink: 0;
      }
    }

    .user-roles {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;

      .role-tag {
        margin: 0;

        &.system-tag {
          font-weight: 600;
          border: 1px solid;

          &.el-tag--danger {
            background: #fef0f0;
            border-color: #f56c6c;
            color: #f56c6c;
          }

          &.el-tag--warning {
            background: #fdf6ec;
            border-color: #e6a23c;
            color: #e6a23c;
          }

          &.el-tag--info {
            background: #f4f4f5;
            border-color: #909399;
            color: #909399;
          }
        }
      }

      .no-roles {
        color: #999;
        font-size: 12px;
        font-style: italic;
      }
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }

  .role-assignment {
    .user-info {
      display: flex;
      align-items: center;
      gap: 16px;

      .user-details {
        h3 {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          color: #333;
        }

        p {
          margin: 0;
          color: #666;
          font-size: 14px;
        }
      }
    }

    .role-selection {
      h4 {
        margin: 0 0 16px 0;
        font-size: 14px;
        font-weight: 600;
        color: #333;
      }

      .role-checkboxes {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .role-checkbox {
          margin: 0;

          :deep(.el-checkbox__label) {
            width: 100%;
          }

          .role-option {
            display: flex;
            flex-direction: column;
            gap: 4px;

            .role-name {
              font-weight: 500;
              color: #333;
            }

            .role-description {
              font-size: 12px;
              color: #666;
            }
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .user-management {
    .search-bar {
      flex-direction: column;
      align-items: stretch;
    }

    .user-table {
      :deep(.el-table__body-wrapper) {
        overflow-x: auto;
      }
    }

    .pagination-wrapper {
      :deep(.el-pagination) {
        justify-content: center;
        flex-wrap: wrap;
      }
    }
  }
}
</style>
