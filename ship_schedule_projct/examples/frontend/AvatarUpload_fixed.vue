<template>
  <div class="avatar-upload">
    <!-- 头像显示 -->
    <div class="avatar-container">
      <img 
        v-if="fullAvatarUrl"
        :src="fullAvatarUrl"
        :alt="user?.full_name || '用户头像'"
        class="avatar-image"
        @error="handleAvatarError"
        @load="handleAvatarLoad"
      />
      <div v-else class="avatar-placeholder">
        <i class="avatar-icon">👤</i>
      </div>
    </div>

    <!-- 上传按钮 -->
    <div class="upload-controls">
      <input
        ref="fileInputRef"
        type="file"
        accept="image/jpeg,image/png,image/gif"
        style="display: none"
        @change="handleFileSelect"
      />
      
      <button 
        @click="triggerFileSelect"
        :disabled="uploading"
        class="upload-btn"
      >
        {{ uploading ? '上传中...' : '更换头像' }}
      </button>
      
      <button 
        v-if="user?.avatar_url"
        @click="deleteAvatar"
        :disabled="uploading"
        class="delete-btn"
      >
        删除头像
      </button>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <span class="progress-text">{{ uploadProgress }}%</span>
    </div>

    <!-- 错误信息 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth' // 根据你的项目调整路径
import { API_CONFIG, buildMediaUrl, getUploadHeaders } from '@/config/api' // 使用上面的配置文件

// 响应式数据
const fileInputRef = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const avatarVersion = ref(Date.now()) // 用于强制刷新头像

// 使用认证store
const authStore = useAuthStore()
const user = computed(() => authStore.user)

// 计算完整的头像URL
const fullAvatarUrl = computed(() => {
  if (!user.value?.avatar_url) return null
  
  const baseUrl = buildMediaUrl(user.value.avatar_url)
  // 添加版本参数强制刷新
  return `${baseUrl}?v=${avatarVersion.value}`
})

// 触发文件选择
const triggerFileSelect = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

// 处理文件选择
const handleFileSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  // 验证文件
  if (!validateFile(file)) {
    return
  }

  await uploadAvatar(file)
  
  // 清空文件输入
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 文件验证
const validateFile = (file) => {
  errorMessage.value = ''
  
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    errorMessage.value = '请选择 JPG、PNG 或 GIF 格式的图片'
    return false
  }
  
  // 检查文件大小 (5MB)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    errorMessage.value = '图片大小不能超过 5MB'
    return false
  }
  
  return true
}

// 上传头像
const uploadAvatar = async (file) => {
  uploading.value = true
  uploadProgress.value = 0
  errorMessage.value = ''
  
  try {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await fetch(API_CONFIG.AUTH.AVATAR, {
      method: 'POST',
      headers: getUploadHeaders(authStore.accessToken),
      body: formData
    })
    
    const result = await response.json()
    
    if (response.ok && result.success) {
      console.log('✅ 头像上传成功:', result.data.avatar_url)
      
      // 更新用户信息
      await authStore.fetchUserInfo()
      
      // 更新头像版本，强制刷新
      avatarVersion.value = Date.now()
      
      // 验证文件是否真的可以访问
      await verifyUploadedFile(result.data.avatar_url)
      
    } else {
      throw new Error(result.message || '头像上传失败')
    }
    
  } catch (error) {
    console.error('❌ 头像上传失败:', error)
    errorMessage.value = error.message || '头像上传失败，请重试'
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

// 验证上传的文件是否可以访问
const verifyUploadedFile = async (relativePath) => {
  try {
    const fullUrl = buildMediaUrl(relativePath)
    console.log('🔍 验证头像文件:', fullUrl)
    
    const response = await fetch(fullUrl, { method: 'HEAD' })
    
    if (response.ok) {
      console.log('✅ 头像文件验证成功')
    } else {
      console.warn('⚠️ 头像文件验证失败:', response.status)
      errorMessage.value = '头像上传成功，但文件访问异常，请刷新页面'
    }
  } catch (error) {
    console.error('❌ 头像文件验证异常:', error)
  }
}

// 删除头像
const deleteAvatar = async () => {
  if (!confirm('确定要删除头像吗？')) return
  
  uploading.value = true
  errorMessage.value = ''
  
  try {
    const response = await fetch(API_CONFIG.AUTH.AVATAR, {
      method: 'DELETE',
      headers: getUploadHeaders(authStore.accessToken)
    })
    
    const result = await response.json()
    
    if (response.ok && result.success) {
      console.log('✅ 头像删除成功')
      await authStore.fetchUserInfo()
      avatarVersion.value = Date.now()
    } else {
      throw new Error(result.message || '头像删除失败')
    }
    
  } catch (error) {
    console.error('❌ 头像删除失败:', error)
    errorMessage.value = error.message || '头像删除失败，请重试'
  } finally {
    uploading.value = false
  }
}

// 头像加载错误处理
const handleAvatarError = (event) => {
  console.warn('🖼️ 头像加载失败:', {
    src: event.target.src,
    user: user.value,
    avatarVersion: avatarVersion.value
  })
  
  // 可以设置默认头像或重试逻辑
  event.target.style.display = 'none'
}

// 头像加载成功处理
const handleAvatarLoad = (event) => {
  console.log('✅ 头像加载成功:', event.target.src)
  event.target.style.display = 'block'
}

// 组件挂载时的初始化
onMounted(() => {
  console.log('🔧 AvatarUpload 组件已挂载，验证状态:', {
    fileInputRef: !!fileInputRef.value,
    authStore: !!authStore,
    user: !!user.value,
    avatarUrl: fullAvatarUrl.value,
    userAvatar: user.value?.avatar_url,
    apiConfig: API_CONFIG
  })
})
</script>

<style scoped>
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-container {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #e0e0e0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  font-size: 40px;
}

.upload-controls {
  display: flex;
  gap: 12px;
}

.upload-btn, .delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.upload-btn {
  background-color: #007bff;
  color: white;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.upload-btn:disabled, .delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-progress {
  width: 200px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background-color: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #007bff;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  text-align: center;
}
</style>
