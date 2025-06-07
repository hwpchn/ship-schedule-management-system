<template>
  <div class="role-management">
    <div class="page-header">
      <div class="header-left">
        <h2>角色管理</h2>
        <p>管理系统角色和权限分配</p>
      </div>
      <div class="header-right">
        <el-button
          type="primary"
          @click="handleCreate"
          v-if="authStore.hasPermission('role.create')"
        >
          <el-icon><Plus /></el-icon>
          新建角色
        </el-button>
      </div>
    </div>

    <div class="content-card">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索角色名称或描述"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadRoles">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <!-- 角色列表 -->
      <el-row :gutter="24" class="role-grid">
        <el-col
          v-for="role in filteredRoles"
          :key="role.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          class="role-card-wrapper"
        >
          <el-card class="role-card" shadow="hover">
            <div class="role-info">
              <div class="role-header">
                <h3>{{ role.name }}</h3>
                <el-tag :type="role.is_active ? 'success' : 'danger'" size="small">
                  {{ role.is_active ? '启用' : '禁用' }}
                </el-tag>
              </div>
              <p class="role-description">{{ role.description || '暂无描述' }}</p>
              <div class="role-meta">
                <span class="permission-count">
                  <el-icon><Key /></el-icon>
                  {{ role.permission_count || 0 }} 个权限
                </span>
                <span class="created-time">创建于 {{ formatDate(role.created_at) }}</span>
              </div>
            </div>
            <div class="role-actions">
              <el-button
                size="small"
                @click="handleEdit(role)"
                v-if="authStore.hasPermission('role.update')"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                @click="handleViewPermissions(role)"
                v-if="authStore.hasPermission('role.detail')"
              >
                查看权限
              </el-button>
              <el-popconfirm
                title="确定要删除这个角色吗？"
                @confirm="handleDelete(role.id)"
                v-if="authStore.hasPermission('role.delete')"
              >
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && filteredRoles.length === 0"
        description="暂无角色数据"
        :image-size="120"
      />
    </div>

    <!-- 角色编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="roleForm"
        :rules="formRules"
        label-width="100px"
        class="role-form"
      >
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="角色名称" prop="name">
              <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch v-model="roleForm.is_active" active-text="启用" inactive-text="禁用" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>

        <el-form-item label="权限配置">
          <div class="permission-section">
            <div class="permission-actions">
              <el-button size="small" @click="selectAllPermissions">全选</el-button>
              <el-button size="small" @click="clearAllPermissions">清空</el-button>
            </div>
            <PermissionTree
              v-if="allPermissions"
              :permissions="allPermissions"
              v-model:checkedPermissions="roleForm.permission_codes"
              :check-strictly="false"
              @change="handlePermissionChange"
            />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 权限查看对话框 -->
    <el-dialog v-model="permissionDialogVisible" title="角色权限详情" width="600px">
      <div v-if="currentRolePermissions">
        <PermissionTree
          :permissions="currentRolePermissions"
          :checkedPermissions="currentRolePermissionCodes"
          :check-strictly="true"
          disabled
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import PermissionTree from '@/components/PermissionTree.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Key } from '@element-plus/icons-vue'

const authStore = useAuthStore()

// 数据状态
const roles = ref([])
const allPermissions = ref(null)
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')

// 对话框状态
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const isEdit = ref(false)
const currentRole = ref(null)
const currentRolePermissions = ref(null)
const currentRolePermissionCodes = ref([])

// 表单数据
const formRef = ref()
const roleForm = ref({
  name: '',
  description: '',
  is_active: true,
  permission_codes: [],
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  description: [{ max: 200, message: '描述长度不能超过 200 个字符', trigger: 'blur' }],
}

// 计算属性
const dialogTitle = computed(() => (isEdit.value ? '编辑角色' : '新建角色'))

const filteredRoles = computed(() => {
  if (!searchQuery.value) return roles.value

  const query = searchQuery.value.toLowerCase()
  return roles.value.filter(
    role =>
      role.name.toLowerCase().includes(query) ||
      (role.description && role.description.toLowerCase().includes(query))
  )
})

// 格式化日期
const formatDate = dateString => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 加载角色列表
const loadRoles = async () => {
  try {
    loading.value = true
    const response = await authApi.getRoles()
    if (response.code === 200) {
      roles.value = response.data.results || []
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

// 加载所有权限
const loadAllPermissions = async () => {
  try {
    const response = await authApi.getPermissions()
    if (response.code === 200) {
      allPermissions.value = response.data.permissions || {}
    }
  } catch (error) {
    console.error('加载权限列表失败:', error)
    ElMessage.error('加载权限列表失败')
  }
}

// 搜索处理
const handleSearch = () => {
  // 搜索在计算属性中处理，这里可以添加防抖逻辑
}

// 创建角色
const handleCreate = async () => {
  await loadAllPermissions()
  isEdit.value = false
  roleForm.value = {
    name: '',
    description: '',
    is_active: true,
    permission_codes: [],
  }
  dialogVisible.value = true
}

// 编辑角色
const handleEdit = async role => {
  try {
    await loadAllPermissions()

    // 获取角色详情
    const response = await authApi.getRoleDetail(role.id)
    if (response.code === 200) {
      const roleDetail = response.data

      isEdit.value = true
      currentRole.value = role
      roleForm.value = {
        name: roleDetail.name,
        description: roleDetail.description || '',
        is_active: roleDetail.is_active,
        permission_codes: roleDetail.permissions?.map(p => p.code) || [],
      }
      dialogVisible.value = true
    }
  } catch (error) {
    console.error('获取角色详情失败:', error)
    ElMessage.error('获取角色详情失败')
  }
}

// 查看权限
const handleViewPermissions = async role => {
  try {
    const response = await authApi.getRoleDetail(role.id)
    if (response.code === 200) {
      const roleDetail = response.data

      // 构建权限树数据结构
      const permissionsByCategory = {}
      roleDetail.permissions?.forEach(permission => {
        const category = permission.category || 'other'
        if (!permissionsByCategory[category]) {
          permissionsByCategory[category] = []
        }
        permissionsByCategory[category].push(permission)
      })

      currentRolePermissions.value = permissionsByCategory
      currentRolePermissionCodes.value = roleDetail.permissions?.map(p => p.code) || []
      permissionDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取角色权限失败:', error)
    ElMessage.error('获取角色权限失败')
  }
}

// 删除角色
const handleDelete = async roleId => {
  try {
    console.log('🗑️ 开始删除角色:', roleId)

    const response = await authApi.deleteRole(roleId)
    console.log('📝 删除角色API响应:', response)

    if (response.code === 200) {
      ElMessage.success('角色删除成功')
      await loadRoles()
    } else {
      console.error('❌ 删除角色失败，响应码:', response.code, '消息:', response.message)
      ElMessage.error(response.message || '删除角色失败')
    }
  } catch (error) {
    console.error('💥 删除角色异常:', error)

    // 更详细的错误处理
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      console.log('🔍 错误详情:', {
        status,
        data: errorData,
        roleId,
      })

      let errorMessage = '删除角色失败'

      if (status === 400) {
        if (errorData.message) {
          errorMessage = errorData.message
        } else if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (errorData.error) {
          errorMessage = errorData.error
        } else {
          errorMessage = '该角色无法删除，可能是系统预设角色或正在被用户使用'
        }
      } else if (status === 403) {
        errorMessage = '权限不足，无法删除角色'
      } else if (status === 404) {
        errorMessage = '角色不存在'
      } else if (status === 409) {
        errorMessage = '角色正在被使用，无法删除'
      }

      ElMessage.error(errorMessage)
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('删除角色失败')
    }
  }
}

// 权限变化处理
const handlePermissionChange = permissionCodes => {
  roleForm.value.permission_codes = permissionCodes
}

// 全选权限
const selectAllPermissions = () => {
  if (!allPermissions.value) return

  const allCodes = []
  Object.values(allPermissions.value).forEach(categoryPermissions => {
    if (Array.isArray(categoryPermissions)) {
      categoryPermissions.forEach(permission => {
        allCodes.push(permission.code)
      })
    }
  })

  roleForm.value.permission_codes = allCodes
}

// 清空权限
const clearAllPermissions = () => {
  roleForm.value.permission_codes = []
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    const submitData = {
      name: roleForm.value.name,
      description: roleForm.value.description,
      is_active: roleForm.value.is_active,
      permission_codes: roleForm.value.permission_codes,
    }

    let response
    if (isEdit.value) {
      response = await authApi.updateRole(currentRole.value.id, submitData)
    } else {
      response = await authApi.createRole(submitData)
    }

    if (response.code === 200 || response.code === 201) {
      ElMessage.success(`角色${isEdit.value ? '更新' : '创建'}成功`)
      dialogVisible.value = false
      await loadRoles()
    }
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

// 页面初始化
onMounted(() => {
  loadRoles()
})
</script>

<style lang="scss" scoped>
.role-management {
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
  }

  .role-grid {
    .role-card-wrapper {
      margin-bottom: 24px;
    }

    .role-card {
      height: 220px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
      }

      :deep(.el-card__body) {
        padding: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }
    }
  }

  .role-info {
    flex: 1;

    .role-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
    }

    .role-description {
      margin: 0 0 16px 0;
      color: #666;
      font-size: 14px;
      line-height: 1.5;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }

    .role-meta {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .permission-count {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #409eff;
        font-size: 12px;
      }

      .created-time {
        color: #999;
        font-size: 12px;
      }
    }
  }

  .role-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .loading-container {
    padding: 40px 0;
  }

  .role-form {
    .permission-section {
      border: 1px solid #e0e6ed;
      border-radius: 8px;
      padding: 16px;
      max-height: 400px;
      overflow-y: auto;

      .permission-actions {
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #f0f0f0;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .role-management {
    .page-header {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
    }

    .search-bar {
      flex-direction: column;
    }

    .role-actions {
      justify-content: center;
    }
  }
}
</style>
