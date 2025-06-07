<template>
  <div class="avatar-upload">
    <!-- 头像显示区域 -->
    <div class="avatar-display">
      <el-avatar :size="size" :src="avatarUrl" class="avatar-image" @error="handleAvatarError">
        <el-icon><User /></el-icon>
      </el-avatar>

      <!-- 上传遮罩层 -->
      <div class="upload-overlay" @click="triggerUpload">
        <el-icon><Camera /></el-icon>
        <span>更换头像</span>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".jpg,.jpeg,.png,.gif"
      style="display: none"
      @change="handleFileSelect"
    />

    <!-- 操作按钮 -->
    <div class="avatar-actions">
      <el-button
        type="primary"
        size="small"
        :icon="Upload"
        @click="triggerUpload"
        :loading="uploading"
      >
        {{ uploading ? '上传中...' : '上传头像' }}
      </el-button>

      <el-button
        v-if="avatarUrl"
        type="danger"
        size="small"
        :icon="Delete"
        @click="handleDeleteAvatar"
        :loading="deleting"
      >
        删除头像
      </el-button>
    </div>

    <!-- 上传提示 -->
    <div class="upload-tips">
      <p>支持 JPG、PNG、GIF 格式</p>
      <p>文件大小不超过 5MB</p>
      <p>建议尺寸：200x200 像素</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Delete, Camera, User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { getUserAvatarUrl } from '@/utils/avatar'

defineProps({
  size: {
    type: Number,
    default: 100,
  },
  showActions: {
    type: Boolean,
    default: true,
  },
  showTips: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['upload-success', 'delete-success', 'upload-error'])

const authStore = useAuthStore()
const fileInputRef = ref()
const uploading = ref(false)
const deleting = ref(false)

// 计算头像URL
const avatarUrl = computed(() => {
  // 在开发环境中，使用空字符串让浏览器通过 Vite 代理访问
  // 在生产环境中，应该使用实际的后端服务器地址
  const baseURL = import.meta.env.DEV ? '' : 'http://localhost:8000'
  return getUserAvatarUrl(authStore.user, baseURL, authStore.avatarVersion)
})

// 触发文件选择
const triggerUpload = () => {
  console.log('🖱️ 触发文件上传，当前状态:', {
    uploading: uploading.value,
    deleting: deleting.value,
    fileInputRef: !!fileInputRef.value,
  })

  if (uploading.value || deleting.value) {
    console.log('⏸️ 上传被阻止：正在进行其他操作')
    ElMessage.warning('请等待当前操作完成')
    return
  }

  if (!fileInputRef.value) {
    console.error('❌ 文件输入元素未找到')
    ElMessage.error('文件选择器初始化失败，请刷新页面重试')
    return
  }

  try {
    console.log('📁 尝试打开文件选择器...')
    fileInputRef.value.click()
    console.log('✅ 文件选择器已触发')
  } catch (error) {
    console.error('💥 触发文件选择器失败:', error)
    ElMessage.error('无法打开文件选择器，请检查浏览器设置')
  }
}

// 处理文件选择
const handleFileSelect = event => {
  console.log('📁 文件选择事件触发:', event)
  const file = event.target.files[0]
  if (!file) {
    console.log('❌ 没有选择文件')
    return
  }

  console.log('📄 选择的文件:', {
    name: file.name,
    type: file.type,
    size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
  })

  // 验证文件
  if (!validateFile(file)) {
    console.log('❌ 文件验证失败')
    // 清空input值，允许重新选择同一文件
    event.target.value = ''
    return
  }

  console.log('✅ 文件验证通过，显示确认对话框')

  // 确认上传
  ElMessageBox.confirm('确定要上传这张图片作为头像吗？', '确认上传', {
    confirmButtonText: '确定上传',
    cancelButtonText: '取消',
    type: 'info',
  })
    .then(() => {
      console.log('✅ 用户确认上传')
      uploadAvatar(file)
    })
    .catch(() => {
      console.log('❌ 用户取消上传')
      // 用户取消，清空input值
      event.target.value = ''
    })
}

// 验证文件
const validateFile = file => {
  // 检查文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('请选择 JPG、PNG 或 GIF 格式的图片')
    return false
  }

  // 检查文件大小 (5MB)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }

  return true
}

// 上传头像
const uploadAvatar = async file => {
  try {
    uploading.value = true

    const result = await authStore.uploadAvatar(file)

    console.log('✅ 头像上传成功，验证文件可访问性...')

    // 验证头像文件是否真的可以访问
    setTimeout(async () => {
      try {
        const currentAvatarUrl = avatarUrl.value
        if (currentAvatarUrl) {
          const response = await window.fetch(currentAvatarUrl, { method: 'HEAD' })
          if (response.ok) {
            console.log('✅ 头像文件验证成功，可以正常访问')
          } else {
            console.warn('⚠️ 头像文件验证失败:', response.status, response.statusText)

            // 如果文件不存在，提供更详细的错误信息和解决建议
            if (response.status === 404) {
              ElMessage({
                type: 'warning',
                message:
                  '头像上传成功，但文件暂时无法访问。这可能是后端配置问题，请联系管理员或稍后重试。',
                duration: 8000,
                showClose: true,
              })

              // 尝试重新获取用户信息，看是否有更新
              setTimeout(() => {
                authStore.getUserInfo().catch(console.error)
              }, 3000)
            } else {
              ElMessage.warning('头像上传成功，但文件可能需要一些时间才能生效')
            }
          }
        }
      } catch (error) {
        console.warn('⚠️ 头像文件验证出错:', error)
      }
    }, 1000) // 延迟1秒验证，给后端时间处理文件

    ElMessage.success(result.message || '头像上传成功')
    emit('upload-success', result)

    // 清空input值
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error(error.message || '头像上传失败，请重试')
    emit('upload-error', error)

    // 清空input值
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  } finally {
    uploading.value = false
  }
}

// 删除头像
const handleDeleteAvatar = async () => {
  try {
    await ElMessageBox.confirm('确定要删除当前头像吗？删除后将显示默认头像。', '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })

    deleting.value = true

    const result = await authStore.deleteAvatar()

    ElMessage.success(result.message || '头像删除成功')
    emit('delete-success', result)
  } catch (error) {
    if (error === 'cancel') return

    console.error('头像删除失败:', error)
    ElMessage.error(error.message || '头像删除失败，请重试')
  } finally {
    deleting.value = false
  }
}

// 头像加载错误处理
const handleAvatarError = event => {
  console.warn('🖼️ 头像加载失败:', {
    src: event.target?.src,
    user: authStore.user,
    avatarVersion: authStore.avatarVersion,
  })

  // 尝试重新获取用户信息，可能头像URL已更新
  if (authStore.user && authStore.user.avatar) {
    console.log('🔄 尝试重新获取用户信息...')
    authStore.getUserInfo().catch(error => {
      console.error('重新获取用户信息失败:', error)
    })
  }
}

// 组件挂载后验证
onMounted(() => {
  console.log('🔧 AvatarUpload 组件已挂载，验证状态:', {
    fileInputRef: !!fileInputRef.value,
    authStore: !!authStore,
    user: !!authStore.user,
    avatarUrl: avatarUrl.value,
    userAvatar: authStore.user?.avatar,
    userAvatarUrl: authStore.user?.avatar_url,
    avatarVersion: authStore.avatarVersion,
    isDev: import.meta.env.DEV,
  })

  // 延迟验证，确保 DOM 完全渲染
  setTimeout(() => {
    if (!fileInputRef.value) {
      console.error('⚠️ 警告：文件输入元素在组件挂载后仍未找到')
    } else {
      console.log('✅ 文件输入元素验证成功')
    }

    // 输出最终的头像URL用于调试
    console.log('🖼️ 最终头像URL:', avatarUrl.value)
  }, 100)
})
</script>

<style scoped>
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-display {
  position: relative;
  cursor: pointer;

  .avatar-image {
    border: 3px solid #e4e7ed;
    transition: all 0.3s ease;
  }

  .upload-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    opacity: 0;
    transition: opacity 0.3s ease;
    font-size: 12px;
    gap: 4px;

    .el-icon {
      font-size: 20px;
    }
  }

  &:hover {
    .avatar-image {
      border-color: #409eff;
    }

    .upload-overlay {
      opacity: 1;
    }
  }
}

.avatar-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.upload-tips {
  text-align: center;
  color: #909399;
  font-size: 12px;
  line-height: 1.5;

  p {
    margin: 0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .avatar-actions {
    flex-direction: column;
    gap: 8px;

    .el-button {
      width: 120px;
    }
  }
}
</style>
