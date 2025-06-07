<template>
  <div class="permission-management">
    <div class="page-header">
      <div class="header-left">
        <h2>权限管理</h2>
        <p>查看系统权限结构和详细信息</p>
      </div>
      <div class="header-right">
        <el-button @click="loadPermissions">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="content-card">
      <!-- 统计信息 -->
      <div class="stats-row">
        <el-row :gutter="24">
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-number">{{ totalPermissions }}</div>
              <div class="stat-label">总权限数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-number">{{ totalCategories }}</div>
              <div class="stat-label">权限分类</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-number">{{ userPermissionCount }}</div>
              <div class="stat-label">我的权限</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-number">{{ roleCount }}</div>
              <div class="stat-label">系统角色</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索权限名称或代码"
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="selectedCategory"
          placeholder="选择权限分类"
          clearable
          style="width: 200px"
          @change="handleCategoryFilter"
        >
          <el-option v-for="(label, key) in categoryMap" :key="key" :label="label" :value="key" />
        </el-select>
      </div>

      <!-- 权限树 -->
      <div class="permission-tree-section" v-loading="loading">
        <el-card class="tree-card">
          <template #header>
            <div class="tree-header">
              <span>系统权限结构</span>
              <div class="tree-actions">
                <el-button size="small" @click="expandAll">展开全部</el-button>
                <el-button size="small" @click="collapseAll">收起全部</el-button>
              </div>
            </div>
          </template>

          <el-tree
            ref="permissionTreeRef"
            :data="filteredTreeData"
            :props="treeProps"
            node-key="code"
            :default-expand-all="false"
            :expand-on-click-node="false"
            class="permission-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <div class="node-content">
                  <el-icon v-if="data.category" class="category-icon">
                    <Folder />
                  </el-icon>
                  <el-icon v-else class="permission-icon">
                    <Key />
                  </el-icon>

                  <div class="node-info">
                    <span class="node-name">{{ data.name }}</span>
                    <span v-if="!data.category" class="node-code">{{ data.code }}</span>
                  </div>
                </div>

                <div class="node-actions">
                  <el-tag
                    v-if="!data.category"
                    :type="hasCurrentPermission(data.code) ? 'success' : 'info'"
                    size="small"
                  >
                    {{ hasCurrentPermission(data.code) ? '已拥有' : '无权限' }}
                  </el-tag>

                  <el-button
                    v-if="!data.category"
                    size="small"
                    link
                    @click="showPermissionDetail(data)"
                  >
                    详情
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </el-card>

        <!-- 空状态 -->
        <el-empty
          v-if="!loading && (!permissions || Object.keys(permissions).length === 0)"
          description="暂无权限数据"
          :image-size="120"
        />
      </div>
    </div>

    <!-- 权限详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="权限详情" width="600px">
      <div v-if="currentPermission" class="permission-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="权限代码">
            <el-tag type="primary">{{ currentPermission.code }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="权限名称">
            {{ currentPermission.name }}
          </el-descriptions-item>
          <el-descriptions-item label="权限描述">
            {{ currentPermission.description || '暂无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="权限分类">
            {{ categoryMap[currentPermission.category] || currentPermission.category }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentPermission.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="拥有状态">
            <el-tag :type="hasCurrentPermission(currentPermission.code) ? 'success' : 'danger'">
              {{ hasCurrentPermission(currentPermission.code) ? '已拥有' : '无权限' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="related-roles" v-if="currentPermissionRoles.length > 0">
          <h4>拥有此权限的角色</h4>
          <div class="role-list">
            <el-tag
              v-for="role in currentPermissionRoles"
              :key="role.id"
              type="primary"
              class="role-item"
            >
              {{ role.name }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { Refresh, Search, Folder, Key } from '@element-plus/icons-vue'

const authStore = useAuthStore()

// 数据状态
const permissions = ref(null)
const roles = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')

// 对话框状态
const detailDialogVisible = ref(false)
const currentPermission = ref(null)
const currentPermissionRoles = ref([])

// 树组件引用
const permissionTreeRef = ref()

// 树组件属性
const treeProps = {
  children: 'children',
  label: 'name',
}

// 权限分类映射
const categoryMap = {
  user_management: '用户管理',
  role_management: '角色管理',
  permission_management: '权限管理',
  user_role_management: '用户角色管理',
  schedule_management: '船期管理',
  system_management: '系统管理',
}

// 计算属性
const totalPermissions = computed(() => {
  if (!permissions.value) return 0
  let count = 0
  Object.values(permissions.value).forEach(categoryPermissions => {
    if (Array.isArray(categoryPermissions)) {
      count += categoryPermissions.length
    }
  })
  return count
})

const totalCategories = computed(() => {
  return permissions.value ? Object.keys(permissions.value).length : 0
})

const userPermissionCount = computed(() => {
  return authStore.permissions?.length || 0
})

const roleCount = computed(() => {
  return roles.value.length
})

// 转换为树形数据
const treeData = computed(() => {
  if (!permissions.value) return []

  const tree = []

  // 遍历权限分类
  for (const [categoryKey, permissionList] of Object.entries(permissions.value)) {
    const categoryNode = {
      code: categoryKey,
      name: categoryMap[categoryKey] || categoryKey,
      category: true,
      children: [],
    }

    // 添加分类下的权限
    if (Array.isArray(permissionList)) {
      permissionList.forEach(permission => {
        categoryNode.children.push({
          ...permission,
          category: false,
        })
      })
    }

    tree.push(categoryNode)
  }

  return tree
})

// 过滤后的树数据
const filteredTreeData = computed(() => {
  let data = treeData.value

  // 分类过滤
  if (selectedCategory.value) {
    data = data.filter(node => node.code === selectedCategory.value)
  }

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data
      .map(categoryNode => {
        const filteredChildren = categoryNode.children.filter(
          permission =>
            permission.name.toLowerCase().includes(query) ||
            permission.code.toLowerCase().includes(query) ||
            (permission.description && permission.description.toLowerCase().includes(query))
        )

        if (filteredChildren.length > 0) {
          return {
            ...categoryNode,
            children: filteredChildren,
          }
        }
        return null
      })
      .filter(Boolean)
  }

  return data
})

// 检查当前用户是否拥有权限
const hasCurrentPermission = permissionCode => {
  return authStore.hasPermission(permissionCode)
}

// 格式化日期
const formatDate = dateString => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 加载权限列表
const loadPermissions = async () => {
  try {
    loading.value = true
    const response = await authApi.getPermissions()
    if (response.code === 200) {
      permissions.value = response.data.permissions || {}
    }
  } catch (error) {
    console.error('加载权限列表失败:', error)
    ElMessage.error('加载权限列表失败')
  } finally {
    loading.value = false
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    const response = await authApi.getRoles()
    if (response.code === 200) {
      roles.value = response.data.results || []
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

// 搜索处理
const handleSearch = () => {
  // 搜索在计算属性中处理
}

// 分类过滤处理
const handleCategoryFilter = () => {
  // 过滤在计算属性中处理
}

// 展开全部
const expandAll = () => {
  if (permissionTreeRef.value) {
    const allNodes = permissionTreeRef.value.store.nodesMap
    Object.values(allNodes).forEach(node => {
      node.expanded = true
    })
  }
}

// 收起全部
const collapseAll = () => {
  if (permissionTreeRef.value) {
    const allNodes = permissionTreeRef.value.store.nodesMap
    Object.values(allNodes).forEach(node => {
      node.expanded = false
    })
  }
}

// 显示权限详情
const showPermissionDetail = async permission => {
  currentPermission.value = permission

  // 查找拥有此权限的角色
  currentPermissionRoles.value = roles.value.filter(role => {
    // 这里需要根据实际API返回的数据结构来判断
    // 暂时返回空数组，实际实现时需要调用相应的API
    return false
  })

  detailDialogVisible.value = true
}

// 页面初始化
onMounted(async () => {
  await Promise.all([loadPermissions(), loadRoles()])
})
</script>

<style lang="scss" scoped>
.permission-management {
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

  .stats-row {
    margin-bottom: 24px;

    .stat-card {
      text-align: center;
      padding: 20px;
      background: linear-gradient(135deg, #409eff, #5470c6);
      border-radius: 12px;
      color: white;

      .stat-number {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 8px;
      }

      .stat-label {
        font-size: 14px;
        opacity: 0.9;
      }
    }
  }

  .search-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
  }

  .permission-tree-section {
    .tree-card {
      .tree-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .tree-actions {
          display: flex;
          gap: 8px;
        }
      }
    }

    .permission-tree {
      margin-top: 16px;

      :deep(.el-tree-node) {
        margin-bottom: 4px;

        .el-tree-node__content {
          height: 40px;
          border-radius: 6px;
          transition: all 0.3s ease;

          &:hover {
            background: rgba(64, 158, 255, 0.1);
          }
        }
      }
    }

    .tree-node {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      padding-right: 16px;

      .node-content {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;

        .category-icon {
          color: #e6a23c;
          font-size: 16px;
        }

        .permission-icon {
          color: #409eff;
          font-size: 14px;
        }

        .node-info {
          display: flex;
          flex-direction: column;
          align-items: flex-start;

          .node-name {
            font-size: 14px;
            color: #333;
          }

          .node-code {
            font-size: 12px;
            color: #666;
            font-family: 'Courier New', monospace;
          }
        }
      }

      .node-actions {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }
  }

  .permission-detail {
    .related-roles {
      margin-top: 24px;

      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        color: #333;
      }

      .role-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .role-item {
          margin: 0;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .permission-management {
    .stats-row {
      :deep(.el-col) {
        margin-bottom: 12px;
      }
    }

    .search-bar {
      flex-direction: column;
    }

    .tree-node {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;

      .node-actions {
        align-self: flex-end;
      }
    }
  }
}
</style>
