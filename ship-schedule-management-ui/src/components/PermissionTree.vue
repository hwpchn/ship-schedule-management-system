<template>
  <div class="permission-tree">
    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="treeProps"
      :check-strictly="checkStrictly"
      show-checkbox
      node-key="code"
      :default-expand-all="true"
      :default-checked-keys="checkedKeys"
      @check="handleCheck"
      class="permission-tree-component"
    >
      <template #default="{ node, data }">
        <span class="tree-node">
          <el-icon v-if="data.category" class="category-icon">
            <Folder />
          </el-icon>
          <el-icon v-else class="permission-icon">
            <Key />
          </el-icon>
          <span class="node-label">{{ node.label }}</span>
          <span v-if="data.description" class="node-description">{{ data.description }}</span>
        </span>
      </template>
    </el-tree>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Folder, Key } from '@element-plus/icons-vue'

const props = defineProps({
  permissions: {
    type: Object,
    default: () => ({}),
  },
  checkedPermissions: {
    type: Array,
    default: () => [],
  },
  checkStrictly: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:checkedPermissions', 'change'])

const treeRef = ref()

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

// 转换为树形数据
const treeData = computed(() => {
  const tree = []

  // 遍历权限分类
  for (const [categoryKey, permissionList] of Object.entries(props.permissions)) {
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
          code: permission.code,
          name: permission.name,
          description: permission.description,
          category: false,
        })
      })
    }

    tree.push(categoryNode)
  }

  return tree
})

// 已选中的权限码
const checkedKeys = computed(() => {
  return props.checkedPermissions || []
})

// 处理权限选择变化
const handleCheck = (data, checkState) => {
  const checkedNodes = checkState.checkedNodes

  // 过滤出权限节点（非分类节点）
  const permissionCodes = checkedNodes.filter(node => !node.category).map(node => node.code)

  emit('update:checkedPermissions', permissionCodes)
  emit('change', permissionCodes, checkedNodes)
}

// 设置选中的权限
const setCheckedKeys = keys => {
  nextTick(() => {
    if (treeRef.value) {
      treeRef.value.setCheckedKeys(keys)
    }
  })
}

// 获取选中的权限
const getCheckedKeys = () => {
  if (treeRef.value) {
    return treeRef.value.getCheckedKeys()
  }
  return []
}

// 获取选中的权限节点
const getCheckedNodes = () => {
  if (treeRef.value) {
    return treeRef.value.getCheckedNodes()
  }
  return []
}

// 监听外部权限变化
watch(
  () => props.checkedPermissions,
  newKeys => {
    setCheckedKeys(newKeys)
  },
  { immediate: true }
)

// 暴露方法
defineExpose({
  setCheckedKeys,
  getCheckedKeys,
  getCheckedNodes,
})
</script>

<style lang="scss" scoped>
.permission-tree {
  .permission-tree-component {
    background: transparent;

    :deep(.el-tree-node) {
      margin-bottom: 4px;

      .el-tree-node__content {
        height: 36px;
        border-radius: 6px;
        transition: all 0.3s ease;

        &:hover {
          background: rgba(64, 158, 255, 0.1);
        }
      }

      .el-checkbox {
        margin-right: 8px;
      }

      .el-tree-node__expand-icon {
        color: #666;
        font-size: 14px;
      }
    }

    // 分类节点样式
    :deep(.el-tree-node[data-category='true']) {
      .el-tree-node__content {
        font-weight: 600;
        background: rgba(64, 158, 255, 0.05);

        &:hover {
          background: rgba(64, 158, 255, 0.15);
        }
      }
    }
  }

  .tree-node {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    overflow: hidden;

    .category-icon {
      color: #e6a23c;
      font-size: 16px;
    }

    .permission-icon {
      color: #409eff;
      font-size: 14px;
    }

    .node-label {
      font-size: 14px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .node-description {
      font-size: 12px;
      color: #999;
      margin-left: auto;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 200px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .permission-tree {
    .tree-node {
      .node-description {
        display: none;
      }
    }
  }
}
</style>
