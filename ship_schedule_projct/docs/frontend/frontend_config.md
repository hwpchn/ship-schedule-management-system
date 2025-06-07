# 前端头像上传问题解决方案

## 问题诊断

头像上传功能的问题在于：

1. **后端问题**: Django的DEBUG设置为False，导致媒体文件服务被禁用
2. **前端问题**: 前端尝试访问错误的URL（localhost:3000而不是localhost:8000）

## 解决方案

### 1. 后端修复（已完成）

已将 `.env` 文件中的 `DEBUG=True` 来启用开发环境的媒体文件服务。

### 2. 前端配置修复

前端需要正确构建媒体文件URL。以下是修复建议：

#### 方案A：环境变量配置

在前端项目中创建环境变量文件（如 `.env` 或 `.env.local`）：

```env
# 后端API基础URL
VITE_API_BASE_URL=http://localhost:8000
# 或者如果使用Create React App
REACT_APP_API_BASE_URL=http://localhost:8000
```

#### 方案B：配置文件

创建 `src/config/api.js`：

```javascript
// API配置
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  MEDIA_URL: 'http://localhost:8000/media/',
  API_URL: 'http://localhost:8000/api/'
}

// 构建完整的媒体文件URL
export const buildMediaUrl = (relativePath) => {
  if (!relativePath) return null
  if (relativePath.startsWith('http')) return relativePath
  return `${API_CONFIG.MEDIA_URL}${relativePath.replace(/^\//, '')}`
}
```

#### 方案C：修复AvatarUpload组件

在你的 `AvatarUpload.vue` 组件中：

```vue
<script setup>
import { computed } from 'vue'
import { API_CONFIG, buildMediaUrl } from '@/config/api'

// 计算完整的头像URL
const fullAvatarUrl = computed(() => {
  if (!userAvatar.value) return null
  return buildMediaUrl(userAvatar.value)
})

// 文件验证函数
const verifyUploadedFile = async (relativePath) => {
  try {
    const fullUrl = buildMediaUrl(relativePath)
    const response = await fetch(fullUrl, { method: 'HEAD' })
    return response.ok
  } catch (error) {
    console.error('文件验证失败:', error)
    return false
  }
}
</script>

<template>
  <img 
    :src="fullAvatarUrl" 
    @error="handleAvatarError"
    alt="用户头像"
  />
</template>
```

### 3. 开发环境代理配置（推荐）

如果使用Vite，在 `vite.config.js` 中配置代理：

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

如果使用Create React App，在 `package.json` 中添加：

```json
{
  "proxy": "http://localhost:8000"
}
```

### 4. 验证修复

重启Django服务器后，测试以下URL：

```bash
# 测试媒体文件访问
curl -I "http://localhost:8000/media/user_avatars/1/avatar_1.png"

# 应该返回 200 OK
```

## 生产环境注意事项

在生产环境中：

1. **不要使用DEBUG=True**
2. **配置Web服务器**（如Nginx）来提供媒体文件服务
3. **使用CDN**来加速媒体文件访问
4. **配置CORS**允许跨域访问媒体文件

## 测试步骤

1. 重启Django服务器
2. 修复前端媒体文件URL构建逻辑
3. 测试头像上传功能
4. 验证头像显示是否正常
