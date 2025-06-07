// 前端API配置文件
// 请将此文件复制到你的前端项目中

// API配置常量
export const API_CONFIG = {
  // 后端服务器地址
  BASE_URL: 'http://localhost:8000',
  
  // API端点
  API_URL: 'http://localhost:8000/api/',
  
  // 媒体文件基础URL
  MEDIA_URL: 'http://localhost:8000/media/',
  
  // 认证相关端点
  AUTH: {
    LOGIN: 'http://localhost:8000/api/auth/login/',
    REGISTER: 'http://localhost:8000/api/auth/register/',
    ME: 'http://localhost:8000/api/auth/me/',
    AVATAR: 'http://localhost:8000/api/auth/me/avatar/',
  }
}

/**
 * 构建完整的媒体文件URL
 * @param {string} relativePath - 相对路径，如 "/media/user_avatars/1/avatar_1.png"
 * @returns {string|null} 完整的媒体文件URL
 */
export const buildMediaUrl = (relativePath) => {
  if (!relativePath) return null
  
  // 如果已经是完整URL，直接返回
  if (relativePath.startsWith('http')) {
    return relativePath
  }
  
  // 移除开头的斜杠，避免双斜杠
  const cleanPath = relativePath.replace(/^\//, '')
  
  // 如果路径已经包含media，直接拼接到BASE_URL
  if (cleanPath.startsWith('media/')) {
    return `${API_CONFIG.BASE_URL}/${cleanPath}`
  }
  
  // 否则拼接到MEDIA_URL
  return `${API_CONFIG.MEDIA_URL}${cleanPath}`
}

/**
 * 构建API请求URL
 * @param {string} endpoint - API端点
 * @returns {string} 完整的API URL
 */
export const buildApiUrl = (endpoint) => {
  if (endpoint.startsWith('http')) {
    return endpoint
  }
  
  const cleanEndpoint = endpoint.replace(/^\//, '')
  return `${API_CONFIG.API_URL}${cleanEndpoint}`
}

/**
 * 获取认证请求头
 * @param {string} token - JWT访问令牌
 * @returns {object} 请求头对象
 */
export const getAuthHeaders = (token) => {
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

/**
 * 获取文件上传请求头
 * @param {string} token - JWT访问令牌
 * @returns {object} 请求头对象（不包含Content-Type，让浏览器自动设置）
 */
export const getUploadHeaders = (token) => {
  return {
    'Authorization': `Bearer ${token}`
  }
}

// 导出默认配置
export default API_CONFIG
